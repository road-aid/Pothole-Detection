#!/usr/bin/python2

'''
Automation script to create the log file for kmz-creator.py to create the KML/KMZ files.

This script requires the images of the potholes detected to be in the pothole directory 
underneath the output.log that will be created.  


Usage:
    python2 run_test_shadow.py [DIR]

If DIR is omitted, then video files are searched in the current directory.
'''

import sys, shutil
from sys import argv
import os
import datetime
import glob

#script, gfilter = argv
python_cmd = "python2" # Set this to your system python command
log_dir = os.path.abspath(os.path.curdir);
img_dir = log_dir+"/potholes/"

video_exts = [".mp4"]
tracker_script_093 = "test_shadow093.py"
tracker_output = "tracker_output.log"
camera_log_name = "log.txt"
gps_log_name = "GPS.log"

pot_imgs = os.listdir(img_dir)
log_out=open("_output.log","a")
for imgs in pot_imgs:
    fname=imgs
    #print fname
    shutil.copy(img_dir+"/"+fname,log_dir)
    if len(fname) < 39:
        fname_search=fname[10:16]
        os.rename(log_dir+"/"+fname,log_dir+"/"+fname[0:16]+fname[25:29])
    elif len(fname) > 30:
        fname_search=fname[21:27]
        os.rename(log_dir+"/"+fname,log_dir+"/"+fname[11:27]+fname[36:40])
    for logs in glob.glob(log_dir+"/logs"+"/*.log"):
        log_data=open(logs,"r")
	for line in log_data:
	    if line.find(fname_search)!=-1:
	        print line
		log_out.write(line)
		#log_out.write("\n")
log_out.close()
		#if os.path.isfile(log_dir+"/output.log"):
		    #log_out=open("output.log","a")
		    #log_out.write(line)
		    #log_out.close()
		#else:
		    #log_out=open("output.log","w")
		    #log_out.write(line)
		    #log_out.close()

#white-line-image-test4a52e4-0.965000.png

