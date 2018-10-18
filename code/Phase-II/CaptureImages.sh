ROLL=$(cat /home/pi/series)
SAVEDIR=/home/pi/stills/$ROLL
python /home/pi/vidCount.py
count=$(cat /home/pi/count)
#timestamp=$( date --utc +%Y%m%d_%H%M%SZ)
timestamp=$(tail -1 /home/pi/Output-Monitor/GPS.log | cut -c -12)
#timestamp=$(tail -10 $SAVEDIR/"Output"-"$ROLL" | grep GPRMC | (awk -F, '/\$GPRMC/ {print (substr($10,0,9) (substr(2,0,7)))}')
#sleep 2
filename=$ROLL-$count-$timestamp
#filename=$ROLL-$count
# /opt/vc/bin/raspistill -t 900000 -tl 2000 -o $SAVEDIR/$filename+%04d.jpg -n 
#sudo raspivid -t 120000 -o $SAVEDIR/$filename.h264 -w 640 -h 480
raspivid -t 120000 -o $SAVEDIR/$filename.avi -w 852 -h 480 -fps 30
#raspivid -t 120000 -o $SAVEDIR/ -w 852 -h 480 -fps 30
#raspivid -o - -t 99999 -hf -w 640 -h 360 -fps 25|cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dst=:8090}' :demux=h264
#raspivid -o $SAVEDIR/$filename.h264 -t 99999 -hf -w 640 -h 360 -fps 25|cvlc -vvv stream:///dev/stdin --sout '#standard{access=http,mux=ts,dts=:8090}' :demux=h264
