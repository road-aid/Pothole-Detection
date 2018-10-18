#!/bin/bash
# Set time from ntp server and gps
# sudo service ntp restart
#
#
# Capture all files from last run before beginning new collection:
# log.txt, track-man, GPS, Output-"series"
#**********************************************************
OLDROLL=$(cat /home/pi/series)
filename="Output"-"$OLDROLL"

cp /home/pi/Output-Monitor/log.txt /home/pi/stills/$OLDROLL/log.txt
cp /home/pi/Output-Monitor/track-man.log /home/pi/stills/$OLDROLL/track-man.log
cp /home/pi/Output-Monitor/GPS.log /home/pi/stills/$OLDROLL/GPS.log
cp /home/pi/GPS/$filename /home/pi/stills/$OLDROLL/$filename

sudo rm /home/pi/Output-Monitor/log.txt
sudo rm /home/pi/Output-Monitor/track-man.log
sudo rm /home/pi/track-log2.txt
sudo rm /home/pi/Output-Monitor/GPS.log
sudo rm /home/pi/count

# echo "track starts" >> /home/pi/Output-Monitor/track-log2.txt
# sudo chmod 777 /home/pi/Output-Monitor/track-log2.txt

sleep 30 

sudo python /home/pi/majCompteur.py
ROLL=$(cat /home/pi/series)
#sudo python /home/pi/vidCount.py

SAVEDIR=/home/pi/stills/$ROLL/
mkdir $SAVEDIR

# Initialize track-man.log and log.txt
echo "$ROLL Begins" >> /home/pi/Output-Monitor/track-man.log
sudo chmod 777 /home/pi/Output-Monitor/track-man.log
echo "Begin Log file" >> /home/pi/Output-Monitor/log.txt
sudo chmod 777 /home/pi/Output-Monitor/log.txt

Ccount=1
echo "Count value equal $Ccount" >> /home/pi/Output-Monitor/track-man.log
echo "0" >> /home/pi/count

# Move trackpy manager to Video Directory
cp /home/pi/data-offload-manager.sh $SAVEDIR/data-offload-manager.sh
chmod 777 $SAVEDIR/data-offload-manager.sh
sh $SAVEDIR/data-offload-manager.sh &

# Kick off GPS collection script
# Collects All of GPS Output Sentences WITHOUT Parsing
/home/pi/CaptureGPS.sh &

# Kicks of GPS Collection Script Parsing Time and GPS
echo "Begin GPS and Time Collection" >> /home/pi/Output-Monitor/GPS.log
chmod 777 /home/pi/Output-Monitor/GPS.log
#awk -F, '/\$GPGGA/ {print (substr($2,0,9)), (substr($3,0,2) + (substr($3,3) / 60.0)) $4, (substr($5,0,3) + (substr($5,4) /60.0)) $6}' /dev/ttyACM0 > /home/pi/Output-Monitor/GPS.log &
awk -F, '/\$GPRMC/ {print (substr($10,0,9) (substr($2,0,7)), (substr($4,0,8)) $5, (substr($6,0,9)) $7)}' /dev/ttyACM0 > /home/pi/Output-Monitor/GPS.log &


while true ; do
	#timestamp=$(date +%Y%m%d_%H%M%S)
	timestamp=$(tail -1 /home/pi/Output-Monitor/GPS.log | cut -c -12)
	echo "$timestamp - Video $Ccount starts collection" >> /home/pi/Output-Monitor/log.txt
	/home/pi/CaptureImages.sh
	sleep 1
	Ccount=$(($Ccount+1))
	echo "# of videos collected = $Ccount" >> /home/pi/Output-Monitor/log.txt
	#*****************************************************************************
	#
	#	BEGIN DATA OFFLOAD CODE
	#1. Check for network connection
	#2. If connected begin offloading
	#3. If not conected do nothing
	#
	#wget -q --tries=10 --timeout=20 --spider http://google.com
	#if [[ $? -eq 0 ]]; then
	#if ifconfig wlan0 | grep -q "inet addr:" ; then
	#	echo "$timestamp - Network connection established. Beginning data offload." >> /home/pi/Output-Monitor/log.txt
	#else
	#	echo "$timestamp - Not connected. Waiting for connection." >> /home/pi/Output-Monitor/log.txt
	#	ifup --force wlan0
	#fi
done
