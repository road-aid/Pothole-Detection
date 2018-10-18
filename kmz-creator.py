#!/usr/bin/python2

'''
Automation script to create KML and KMZ files based on geo features identified in log files.

Usage:
    python2 kmz-creator.py [DIR]

If DIR is omitted, then log files are searched in the current directory.
'''

import sys
import os
import datetime
import math
from pykml.factory import KML_ElementMaker as KML
from lxml import etree
import zipfile

poi_kmz_output_file_name = "kmz-creator-poi.kmz"
poi_kml_output_file_name = "kmz-creator-poi.kml"
route_output_file_name = "kmz-creator-route.kml"
create_images_kmz = True # set this var to enable or disable KMZ with images generation
output_log_suffix = "_output.log"
image_prefix = "image-test"
gps_log_name = "GPS.log"
image_ext = ".png"

work_dir = os.path.abspath(os.path.curdir);
if (len(sys.argv) > 1):
    work_dir = sys.argv[1]
work_dir = os.path.abspath(work_dir)

print "Working on '" + work_dir + "'"

kml_poi_doc = KML.Document()
kml_poi = KML.kml(kml_poi_doc)

if (create_images_kmz):
    zipf = zipfile.ZipFile(poi_kmz_output_file_name, "w")

# helper func for coordinates conversion
# DDDMM.MMMMC -> +-DD.DDDD
def dms2dec(dms):
    dd = dms[:-8]
    mm = dms[-8:-1]
    c = dms[-1]
    res = float(dd) + float(mm) / 60.0
    if (c in ["W", "S"]):
        res = -res
    return str(res)

# create POI file based on output log files
for f in os.listdir(work_dir):
    f_path = os.path.abspath(os.path.join(work_dir, f))
    f_name_base = os.path.basename(f_path)
    f_name, f_ext = os.path.splitext(f_name_base)

    if (not f_name_base.endswith(output_log_suffix)):
        continue

    print "Procesing '" + f_name_base + "'"

    # group POIs by folder based on output log file name
    group_name = f_name_base[:-len(output_log_suffix)]
    kml_poi_folder = KML.Folder(KML.name(group_name))
    kml_poi_doc.append(kml_poi_folder)
    lines = open(f_path).readlines()
    for line in lines:
        lat, lon, time, frame, found, uid, pixelx, pixely = line.split(" ")
        lat = dms2dec(lat)
        lon = dms2dec(lon)
        coord = lon + "," + lat
        # create POI
        pml = KML.Placemark(KML.name(uid),KML.Point(KML.coordinates(coord)))
        # add all data as extended data
        ext = KML.ExtendedData()
        pml.append(ext)
        ext.append(KML.Data(KML.value(uid), name="uid"))
        ext.append(KML.Data(KML.value(time), name="time"))
        ext.append(KML.Data(KML.value(frame), name="frame"))
        ext.append(KML.Data(KML.value(pixelx), name="pixelX"))
        ext.append(KML.Data(KML.value(pixely), name="pixelY"))
        kml_poi_folder.append(pml)
        # find image by id and optionally put it in kmz
        img_name = image_prefix + uid + image_ext
        img_path = os.path.join(work_dir, img_name)	#added 4/23
        if (os.path.exists(img_path)):
            pml.append(KML.description("<img src='" + img_name + "' width='400' />"))
            if (create_images_kmz):
               zipf.write(img_path, img_name)

f_out_poi_kml = open(poi_kml_output_file_name, "w")
f_out_poi_kml.write(etree.tostring(kml_poi, pretty_print=True))
f_out_poi_kml.close()
print "POIs were written to '" + poi_kml_output_file_name + "'"

if (create_images_kmz):
    zipf.write(poi_kml_output_file_name)
    zipf.close()
    print "POIs with images were written to '" + poi_kmz_output_file_name + "'"

# create route file based on GPS log
gps_log_path = os.path.join(work_dir, gps_log_name)
if (not os.path.exists(gps_log_path)):
    exit("Cannot find GPS log in working directory")

kml_route_doc = KML.Document()
kml_route = KML.kml(kml_route_doc)

# group routes by placemarks based on output log file name
kml_route_pml = KML.Placemark()
kml_route_folder = KML.Folder(kml_route_pml)
kml_route_doc.append(kml_route_folder)
route_coords = ""

# helper function to convert timestamp to more readable format
def tspretty(stamp):
    return datetime.datetime.strptime(stamp,"%d%m%y%H%M%S").strftime("%Y-%m-%d %H:%M:%S")

# helper function to calculate distance between two coordinates
# taken from public domain
def coords_distance(lat1, lon1, lat2, lon2):

    # Convert latitude and longitude to
    # spherical coordinates in radians.
    degrees_to_radians = math.pi/180.0

    # phi = 90 - latitude
    phi1 = (90.0 - lat1)*degrees_to_radians
    phi2 = (90.0 - lat2)*degrees_to_radians

    # theta = longitude
    theta1 = lon1*degrees_to_radians
    theta2 = lon2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.

    # For two locations in spherical coordinates
    # (1, theta, phi) and (1, theta', phi')
    # cosine( arc length ) =
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length

    cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) +
           math.cos(phi1)*math.cos(phi2))
    # ensure that cos is in [-1.0,1.0]
    if (cos > 1.0):
        cos = 1.0
    elif (cos < -1.0):
        cos = -1.0
    arc = math.acos( cos )

    earth_radius = 3959 # miles
    return arc * earth_radius

coord_prev = None
mileage = 0.0
gps_log_file = open(gps_log_path)
gps_records = gps_log_file.readlines()
line_cnt = 0
for record in gps_records:
    record_split = record.strip().split(" ")
    if (len(record_split) != 3):
        print "Error in GPS log record on the line", line_cnt, ": " + record
        continue
    timestamp, lat, lon = record_split
    lat = dms2dec(lat)
    lon = dms2dec(lon)
    coord = lon + "," + lat
    # add point to route
    pml = KML.Placemark(KML.name(tspretty(timestamp)), KML.Point(KML.coordinates(coord)))
    kml_route_folder.append(pml)
    route_coords += coord + "\n"
    # calculate mileage
    latf = float(lat)
    lonf = float(lon)
    if (coord_prev):
        mileage += coords_distance(coord_prev[0], coord_prev[1], latf, lonf)
    coord_prev = [latf, lonf]
    line_cnt += 1

# append route coordinates
kml_route_pml.append(KML.LineString(KML.coordinates(route_coords)))

# append name and mileage
route_name = tspretty(gps_records[0].split(" ")[0])
kml_route_pml.append(KML.name(route_name))
kml_route_pml.append(KML.description("{:0.2f}".format(mileage) + "mi"))
kml_route_folder.append(KML.name(route_name))

f_out_route = open(route_output_file_name, "w")
f_out_route.write(etree.tostring(kml_route, pretty_print=True))
f_out_route.close()
print "Routes were written to '" + route_output_file_name + "'"



