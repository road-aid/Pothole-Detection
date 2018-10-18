#!/usr/bin/python

# increment the number stored in file "series"
# after each reboot

f = open('/home/pi/series','r+')
compteur = f.readline()
f.close()
compteur = int(compteur)+1
print compteur
compteur = "000%s"%compteur
f = open('/home/pi/series','w')
f.write(compteur)
f.close()
