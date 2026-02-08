
# shamelessly stolen from https://github.com/davabase/whisper_real_time/blob/master/transcribe_demo.py

import os
import numpy as np
import speech_recognition as sr
import whisper

from datetime import datetime, timedelta
from queue import Queue
from time import sleep

import serial
from openai import OpenAI

#FIXME disable me if causes problems
import pyttsx3

def main():
    # open serial connection using standard baudrate (TODO: check with Micheal)
    ser = serial.Serial('/dev/ttyUSB0', baudrate=115200)

    # should be fast, model will take the longest
    engine = pyttsx3.init()

    # chatGPT client
    client = OpenAI()

    # The last time a recording was retrieved from the queue.
    phrase_time = None
    # Thread safe Queue for passing data from the threaded recording callback.
    data_queue = Queue()
    # Bytes object which holds audio data for the current phrase
    phrase_bytes = bytes()
    # We use SpeechRecognizer to record our audio because it has a nice feature where it can detect when speech ends.
    recorder = sr.Recognizer()
    recorder.energy_threshold = 3200

    # Definitely do this, dynamic energy compensation lowers the energy threshold dramatically to a point where the SpeechRecognizer never stops recording.
    recorder.dynamic_energy_threshold = False

    source = sr.Microphone(device_index=0, sample_rate=16000)

    # Load / Download model
    audio_model = whisper.load_model("small.en", download_root="/mnt/pepper/Hacklahoma2026/model")

    # FIXME tune these values if we have the time
    record_timeout = 2
    phrase_timeout = 3

    transcription = ['']

    with source:
        recorder.adjust_for_ambient_noise(source)

    def record_callback(_, audio:sr.AudioData) -> None:
        """
        Threaded callback function to receive audio data when recordings finish.
        audio: An AudioData containing the recorded bytes.
        """
        # Grab the raw bytes and push it into the thread safe queue.
        data = audio.get_raw_data()
        data_queue.put(data)

    # Create a background thread that will pass us raw audio bytes.
    # We could do this manually but SpeechRecognizer provides a nice helper.

    #FIXME this isn't what we're doing right? if we just do button?
    recorder.listen_in_background(source, record_callback, phrase_time_limit=record_timeout)

    # Cue the user that we're ready to go.
    print("Model loaded.\n")

    # try to open serial connection to receive data
    while True:
        try:
            ser.open()
            break
        except serial.SerialException as e:
            print("failed to open serial port, retrying...")
            time.sleep(1)

    while True:
        try:
            mic_data = ser.read_until(b'ENDOFDATA')

            now = datetime.utcnow()
            # Pull raw recorded audio from the queue.
            if not data_queue.empty():
                phrase_complete = False
                # If enough time has passed between recordings, consider the phrase complete.
                # Clear the current working audio buffer to start over with the new data.
                if phrase_time and now - phrase_time > timedelta(seconds=phrase_timeout):
                    phrase_bytes = bytes()
                    phrase_complete = True
                # This is the last time we received new audio data from the queue.
                phrase_time = now

                # Combine audio data from queue
                audio_data = b''.join(data_queue.queue)
                data_queue.queue.clear()

                # Add the new audio data to the accumulated data for this phrase
                phrase_bytes += audio_data

                # Convert in-ram buffer to something the model can use directly without needing a temp file.
                # Convert data from 16 bit wide integers to floating point with a width of 32 bits.
                # Clamp the audio stream frequency to a PCM wavelength compatible default of 32768hz max.
                audio_np = np.frombuffer(phrase_bytes, dtype=np.int16).astype(np.float32) / 32768.0

                # Read the transcription.
                result = audio_model.transcribe(audio_np, fp16=False)
                text = result['text'].strip()
                print(text)

                #FIXME do we still need to keep this? or do this?
                # If we detected a pause between recordings, add a new item to our transcription.
                # Otherwise edit the existing one.
                #if phrase_complete:
                #    transcription.append(text)
                #else:
                #    transcription[-1] = text

                # send request to ChatGPT (ideally this would be running locally, but the Orin Nano simply isn't powerful/big enough.
                response = client.responses.create(
                    model="gpt-5.2",
                    instructions="You are Bing Bong from the videogame Peak, a helpful assistant that provides concise and informative to any questions that are asked. Please try to keep your responses fairly short, as response time will will matter to the individuals. So, in general, keep responses to at maximum two sentences.",
                    input=text
                )

                #TODO: say request out loud (would prefer to send this back but speaker isn't working rn so we improvise
                print(response.output_text)

                # Clear the console to reprint the updated transcription.
                #os.system('cls' if os.name=='nt' else 'clear')
                #for line in transcription:
                #    print(line)
                # Flush stdout.
                #print('', end='', flush=True)
            else:
                # Infinite loops are bad for processors, must sleep.
                sleep(0.25)
        except KeyboardInterrupt:
            ser.close() # remember to clean up after ourselves
            break

    print("\n\nTranscription:")
    for line in transcription:
        print(line)


if __name__ == "__main__":
    main()
