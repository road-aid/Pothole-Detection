GPSRoll=$(cat /home/pi/series)
SAVEDIR=/home/pi/GPS

filename="Output"-"$GPSRoll"
filenameParsed="OutputParsed"-"$GPSRoll"
cat /dev/ttyACM0 > $SAVEDIR/$filename &

#awk -F, '/\$GPRMC/ {print (substr($10,0,9) (substr($2,0,7)), (substr($4,0,8)) $5, (substr($6,0,9)) $7)}' /$SAVEDIR/$filename > $SAVEDIR/$filenameParsed &
