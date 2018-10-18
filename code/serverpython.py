import socket
import time
import os
START_RECORD = "start_record"
STOP_RECORD = "stop_record"
START_STREAMING = "start_streaming"
STOP_STREAMING = "stop_streaming"
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("",5000))
s.listen(5)
while True:
	connect, address = s.accept()
	resp = (connect.recv(1024)).strip()
	print "\nrecive: ",resp
	if resp == START_RECORD:
		command = "raspivid -t 0 -w 1280 -h 720 -fps 25 -o - | /home/pi/streaming/ffmpeg -i - -c:v copy -r 25 -vsync 1 -c:a aac -strict experimental -y " + time.strftime("%d%m%Y-%H%M%S") + ".mp4 -loglevel debug &"
		print (command)
		os.system(command)
		connect.send("OK")
	elif resp == STOP_RECORD:
		print ("stop record")
		os.system("/home/pi/streaming/kill_video.sh")
		connect.send("OK")
	elif resp == START_STREAMING:
		print ("start streaming")
		command = "raspivid -t 0 -h 720 -w 1280 -fps 15 -b 1300000 -awb auto -o - | gst-launch-1.0 -v fdsrc fd=0 ! h264parse !  rtph264pay config-interval=1 pt=96 ! udpsink host="+ address[0] +" port=6666 &"
		os.system(command)
		connect.send("OK")
	elif resp == STOP_STREAMING:
		print ("stop streaming")
		os.system("/home/pi/streaming/kill.sh");
		connect.send("OK")
	connect.close()
	print "\ndone",address
