#import whisper
import speech_recognition as sr
import time

def audio_callback(_, audio:sr.AudioData):
	data = audio.get_raw_data()

def main():
	recorder = sr.Recognizer()
	recorder.energy_threshold = 3200 #TODO FIXME

	source = sr.Microphone(sample_rate = 16000) #TODO FIXME
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

#model = whisper.load_model("small.en")
#result = model.transcribe("audio.mp3")
#print(result["text"])
