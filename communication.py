import serial

port = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

with open("audio_files/minecraft.mp3", "rb") as f:
	data = f.read()

port.write(data)

port.close()
