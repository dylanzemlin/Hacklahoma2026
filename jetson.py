import whisper
# fix alsalib errors?
#import sounddevice

import speech_recognition as sr
import time

model = whisper.load_model("small.en")

def audio_callback(_, audio:sr.AudioData):
	#global model

	data = audio.get_raw_data()

	# send to file so we can send that to whisper
	with open("tempaudiofile.wav", "wb") as f:
		f.write(audio.get_wav_data())
	#print(data)

	print(model.transcribe("tempaudiofile.wav"))

def main():
	# big boi
	#model = whisper.load_model("small.en")

	recorder = sr.Recognizer()
	recorder.energy_threshold = 3200 #TODO FIXME

	source = sr.Microphone(device_index=0, sample_rate = 16000) #TODO FIXME
	with source:
		recorder.adjust_for_ambient_noise(source, duration = 3)

	recorder.listen_in_background(source, audio_callback, phrase_time_limit = 5)

	while True:
		try:
			time.sleep(0.25)
		except KeyboardInterrupt:
			break

if __name__ == "__main__":
	main()

#result = model.transcribe("audio.mp3")
#print(result["text"])
