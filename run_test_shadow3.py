#!/usr/bin/python2

'''
Automation script to run tracker script on video files in a given folder.

The script requires 'test_shadow.py' to be in the current directory, 'GPS.log'
has to be in the directory with video files. Optionally, there may be a
'log.txt', but otherwise time in the video file name would be used.

Usage:
    python2 run_test_shadow.py [DIR]

If DIR is omitted, then video files are searched in the current directory.
'''

import sys, shutil
from sys import argv
import os
import datetime

#script, gfilter = argv
python_cmd = "python2" # Set this to your system python command
video_dir = os.path.abspath(os.path.curdir);
video_exts = [".mp4"]
tracker_script_093 = "test_shadow093.py"
tracker_output = "tracker_output.log"
camera_log_name = "log.txt"
gps_log_name = "GPS.log"

if (len(sys.argv) > 1):
    video_dir = sys.argv[1]

if (not os.path.exists(video_dir)):
    print "Invalid directory:", video_dir
    exit()

video_dir = os.path.abspath(video_dir)

print "Working in '" + video_dir + "'"

camera_log = None
if (os.path.exists(os.path.join(video_dir, camera_log_name))):
    camera_log = os.path.join(video_dir, camera_log_name)

gps_log = None
if (os.path.exists(os.path.join(video_dir, gps_log_name))):
    gps_log = os.path.join(video_dir, gps_log_name)
else:
    print "GPS log is not found, tried:", os.path.join(video_dir, gps_log_name)
    exit()

# preprocess gps log
gps_data = []
line_cnt = 0
for line in open(gps_log):
    gps_record_split = line.strip().split(' ')
    if (len(gps_record_split) != 3):
        print "Error in GPS log record on the line", line_cnt, ": " + line,
    else:
        tm, lat, lon = gps_record_split
        gps_data.append((int(tm), lat, lon))
    line_cnt += 1

print "Processed GPS log"

# clean up
if (os.path.exists(tracker_output)):
    os.remove(tracker_output)

for f in os.listdir(video_dir):
    f_path = os.path.abspath(os.path.join(video_dir, f))

    # check that this is a video file
    f_name, f_ext = os.path.splitext(os.path.basename(f_path))
    if (not os.path.isfile(f_path)):
        continue
    if (not f_ext in video_exts):
        continue

    #for gfilter in ["0.930", "0.965"]:
    for gfilter in ["0.900", "0.915"]:
        print "Working"
	
        # running a script on it
        print "Running tracker script on '" + f + "'"
        os.system(python_cmd + " " + tracker_script_093 + " " + f_path + " " + gfilter)
    
        #  check results
        if (not os.path.exists(tracker_output)):
            print "No tracker output, skipping"

        # extracting time
        f_name_parts = f_name.split('-')
        if (len(f_name_parts) != 3):
            print "Cannot process the video file name, skipping"
            continue

        start_time = None
        try:
            start_time = datetime.datetime.strptime(f_name_parts[2],"%d%m%y%H%M%S")
        except:
            try:
                video_num = int(f_name_parts[1])
                if (camera_log):
                    for line in open(camera_log):
                        if (line.count("Video " + str(video_num) + " starts collection") != 0):
                            start_time = datetime.datetime.strptime(line[:12],"%d%m%y%H%M%S")
                            break
            except:
                raise

        if (not start_time):
            print "Cannot determine the video start time, skipping"
            continue

        # find GPS point from the start
        cur_point = 0

        # adding start time to the tracker output
        print "Modifying the tracker output with GPS data"
        lines = open(tracker_output).readlines()
        f_out_name = f_name + "-" + str(gfilter[2:5]) + "_output.log"
	print f_out_name
        if (os.path.exists(f_out_name)):
            os.remove(f_out_name)
        f_out = open(f_out_name, "w")
        for line in lines:
            time_pos = line.find(' ')
            if (time_pos == -1):
                continue
            time_str = line[:time_pos + 1]
            time_sec = int(time_str.split('.')[0])
            time_num = int((start_time + datetime.timedelta(0, time_sec)).strftime("%d%m%y%H%M%S"))
            line_out = ""
            # finding the closest by time GPS point
            while ((cur_point < len(gps_data) - 1) and (gps_data[cur_point][0] < time_num)):
                cur_point += 1
            closest_point = cur_point
            if ((gps_data[cur_point][0] > time_num)
                and (cur_point > 0)
                and ((gps_data[cur_point][0] - time_num) > (time_num - gps_data[cur_point - 1][0]))):
                closest_point = cur_point - 1
            line_out = gps_data[closest_point][1] + " " + gps_data[closest_point][2] + " " + line
            f_out.write(line_out)
        f_out.close()
        print "The tracker output with GPS data was written to '" + f_out_name + "'"

        # clean up
        if (os.path.exists(tracker_output)):
            os.remove(tracker_output)
	
	# set extension
	if gfilter=="0.930":
	    g_ext="30000.png"
	elif gfilter=="0.965":
	    g_ext="65000.png"
	elif gfilter=="0.900":
	    g_ext="00000.png"
	elif gfilter=="0.915":
	    g_ext="15000.png"
	
	# move detects to appropriate folders
	for files in os.listdir(video_dir):
	    if files.endswith(g_ext):
	        try:
		    print "Moving files"
		    shutil.move(files,video_dir+"/"+gfilter+"/")
		except:
		    os.mkdir(video_dir+"/"+gfilter+"/")
		    print "Making new directory"
		    shutil.move(files,video_dir+"/"+gfilter+"/")

