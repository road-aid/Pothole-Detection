#!/usr/bin/env python


import cv2.cv as cv
import time
import cv2

from scipy import *
from scipy.cluster import vq
import numpy
import sys, os, random, hashlib


from math import *
from sys import argv

"""
Python Motion Tracker


Reads an incoming video stream and tracks motion in real time.
Detected motion events are logged to a text file.  Also has face detection.
"""


#
# BBoxes must be in the format:
# ( (topleft_x), (topleft_y) ), ( (bottomright_x), (bottomright_y) ) )
top = 0
bottom = 1
left = 0
right = 1


def merge_collided_bboxes( bbox_list ):
    # For every bbox...
    for this_bbox in bbox_list:


        # Collision detect every other bbox:
        for other_bbox in bbox_list:
            if this_bbox is other_bbox: continue  # Skip self


            # Assume a collision to start out with:
            has_collision = True


            # These coords are in screen coords, so > means
            # "lower than" and "further right than".  And <
            # means "higher than" and "further left than".


            # We also inflate the box size by 10% to deal with
            # fuzziness in the data.  (Without this, there are many times a bbox
            # is short of overlap by just one or two pixels.)
            if (this_bbox[bottom][0]*1.1 < other_bbox[top][0]*0.9): has_collision = False
            if (this_bbox[top][0]*.9 > other_bbox[bottom][0]*1.1): has_collision = False


            if (this_bbox[right][1]*1.1 < other_bbox[left][1]*0.9): has_collision = False
            if (this_bbox[left][1]*0.9 > other_bbox[right][1]*1.1): has_collision = False


            if has_collision:
                # merge these two bboxes into one, then start over:
                top_left_x = min( this_bbox[left][0], other_bbox[left][0] )
                top_left_y = min( this_bbox[left][1], other_bbox[left][1] )
                bottom_right_x = max( this_bbox[right][0], other_bbox[right][0] )
                bottom_right_y = max( this_bbox[right][1], other_bbox[right][1] )


                new_bbox = ( (top_left_x, top_left_y), (bottom_right_x, bottom_right_y) )


                bbox_list.remove( this_bbox )
                bbox_list.remove( other_bbox )
                bbox_list.append( new_bbox )


                # Start over with the new list:
                return merge_collided_bboxes( bbox_list )


    # When there are no collions between boxes, return that list:
    return bbox_list

def getthresholdedimg(im):
    #this fucntion takes the RGB image.  Then converts it into HSV for easy color detection and thresholds it with yellow part
    imghsv=cv.CreateImage(cv.GetSize(im),8,3)
    cv.CvtColor(im,imghsv,cv.CV_BGR2HSV)
    imgthreshold=cv.CreateImage(cv.GetSize(im),8,1)
    cv.InRangeS(imghsv,cv.Scalar(20,100,100),cv.Scalar(30,255,255),imgthreshold)
    return imgthreshold


def detect_faces( image, haar_cascade, mem_storage ):


    faces = []
    image_size = cv.GetSize( image )


    #faces = cv.HaarDetectObjects(grayscale, haar_cascade, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, (20, 20) )
    #faces = cv.HaarDetectObjects(image, haar_cascade, storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING )
    #faces = cv.HaarDetectObjects(image, haar_cascade, storage )
    #faces = cv.HaarDetectObjects(image, haar_cascade, mem_storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, ( 16, 16 ) )
    #faces = cv.HaarDetectObjects(image, haar_cascade, mem_storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, ( 4,4 ) )
    faces = cv.HaarDetectObjects(image, haar_cascade, mem_storage, 1.2, 2, cv.CV_HAAR_DO_CANNY_PRUNING, ( image_size[0]/10, image_size[1]/10) )


    for face in faces:
        box = face[0]
        cv.Rectangle(image, ( box[0], box[1] ),
            ( box[0] + box[2], box[1] + box[3]), cv.RGB(255, 0, 0), 1, 8, 0)




class Target:
    def __init__(self):

        if len( sys.argv ) > 1:
            #self.writer = None
            is_color = True
            fps=25
	    gfilter=sys.argv[2]
            self.capture = cv.CaptureFromFile( sys.argv[1] )
            frame = cv.QueryFrame(self.capture)
            frame_size = cv.GetSize(frame)
            print( frame_size )
#            self.writer = cv.CreateVideoWriter("C:\\Temp\\test7.mp4", cv.CV_FOURCC('D', 'I', 'V', 'X'), fps, frame_size, is_color )
#            self.writer = cv.CreateVideoWriter("C:\\Temp\\test10.avi", -1, fps, frame_size, is_color )
#            self.writer = cv.CreateVideoWriter("C:\\Temp\\test4.mp4", cv.CV_FOURCC('D', 'I', 'V', 'X'), fps, cv.GetSize(frame), is_color )
#            out = cv.CreateVideoWriter("C:\\Temp\\test4.mp4", cv.CV_FOURCC('D', 'I', 'V', 'X'), fps, cv.GetSize(frame), is_color )

#            self.writer = cv2.VideoWriter('video2.avi',-1, fps, frame_size, is_color )

        else:
            fps=25
            is_color = True

            self.capture = cv.CaptureFromCAM(0)
            #cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 640 );
            #cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 480 );
            cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, 320 );
            cv.SetCaptureProperty( self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, 240 );
            frame = cv.QueryFrame(self.capture)
#            frame_size = cv.GetSize(frame)

#            video = cv2.VideoWriter("C:\\Temp\\video.avi",cv2.cv.CV_FOURCC('D', 'I', 'V', 'X'), fps, frame_size, is_color )

#            self.writer = None
            #self.writer = cv.CreateVideoWriter("/dev/shm/test1.mp4", cv.CV_FOURCC('D', 'I', 'V', 'X'), fps, frame_size, is_color )
            #self.writer = cv.CreateVideoWriter("C:\Temp\test2.mpg", cv.CV_FOURCC('P', 'I', 'M', '1'), fps, frame_size, is_color )
#            self.writer = cv.CreateVideoWriter("C:\\Temp\\test5.mp4", cv.CV_FOURCC('D', 'I', 'V', 'X'), fps, cv.GetSize(frame), is_color )
            #self.writer = cv.CreateVideoWriter("test4.mpg", cv.CV_FOURCC('P', 'I', 'M', '1'), fps, (320, 240), is_color )
#            out = cv.CreateVideoWriter("C:\\Temp\\test4.mp4", cv.CV_FOURCC('D', 'I', 'V', 'X'), fps, cv.GetSize(frame), is_color )


            # These both gave no error message, but saved no file:
            ###self.writer = cv.CreateVideoWriter("test5.h263i", cv.CV_FOURCC('I', '2', '6', '3'), fps, cv.GetSize(frame), is_color )
            ###self.writer = cv.CreateVideoWriter("test6.fli",   cv.CV_FOURCC('F', 'L', 'V', '1'), fps, cv.GetSize(frame), is_color )
            # Can't play this one:
            ###self.writer = cv.CreateVideoWriter("test7.mp4",   cv.CV_FOURCC('D', 'I', 'V', '3'), fps, cv.GetSize(frame), is_color )


        # 320x240 15fpx in DIVX is about 4 gigs per day.


        frame = cv.QueryFrame(self.capture)
        cv.NamedWindow("Target", 1)
        #cv.NamedWindow("Target2", 1)




    def run(self):
        # Initialize
        log_file_name = "tracker_output.log"
        log_file = open( log_file_name, 'a' )
            #fps = 25

        #cap = cv2.VideoCapture( '../000104-.avi'

        frame = cv.QueryFrame( self.capture )
        frame_size = cv.GetSize( frame )
        foreground = cv.CreateImage(cv.GetSize(frame),8,1)
        foremat = cv.GetMat(foreground)
        Nforemat = numpy.array(foremat, dtype=numpy.float32)
	gfilter=sys.argv[2]
	gfilter_string=gfilter
	gfilter=float(gfilter)
	print "Processing Tracker with filter: " + str(gfilter)

        # Capture the first frame from webcam for image properties
        display_image = cv.QueryFrame( self.capture )

	# Create Background Subtractor
        fgbg = cv2.BackgroundSubtractorMOG()

        # Greyscale image, thresholded to create the motion mask:
        grey_image = cv.CreateImage( cv.GetSize(frame), cv.IPL_DEPTH_8U, 1 )


        # The RunningAvg() function requires a 32-bit or 64-bit image...
        running_average_image = cv.CreateImage( cv.GetSize(frame), cv.IPL_DEPTH_32F, 3 )
        # ...but the AbsDiff() function requires matching image depths:
        running_average_in_display_color_depth = cv.CloneImage( display_image )


        # RAM used by FindContours():
        mem_storage = cv.CreateMemStorage(0)


        # The difference between the running average and the current frame:
        difference = cv.CloneImage( display_image )


        target_count = 1
        last_target_count = 1
        last_target_change_t = 0.0
        k_or_guess = 1
        codebook=[]
        frame_count=0
        last_frame_entity_list = []
        fps = 25


        t0 = 165947


        # For toggling display:
        image_list = [ "camera", "shadow", "white", "threshold", "display", "yellow" ]
        image_index = 0   # Index into image_list




        # Prep for text drawing:
        text_font = cv.InitFont(cv.CV_FONT_HERSHEY_COMPLEX, .5, .5, 0.0, 1, cv.CV_AA )
        text_coord = ( 5, 15 )
        text_color = cv.CV_RGB(255,255,255)
        text_coord2 = ( 5, 30 )
        text_coord3 = ( 5, 45 )

        ###############################
        ### Face detection stuff
        #haar_cascade = cv.Load( 'haarcascades/haarcascade_frontalface_default.xml' )
        #haar_cascade = cv.Load( 'C:/OpenCV2.2/data/haarcascades/haarcascade_frontalface_alt.xml' )
        #haar_cascade = cv.Load( 'haarcascades/haarcascade_frontalface_alt2.xml' )
        #haar_cascade = cv.Load( 'haarcascades/haarcascade_mcs_mouth.xml' )
        #haar_cascade = cv.Load( 'haarcascades/haarcascade_eye.xml' )
        #haar_cascade = cv.Load( 'haarcascades/haarcascade_frontalface_alt_tree.xml' )
        #haar_cascade = cv.Load( 'haarcascades/haarcascade_upperbody.xml' )
        #haar_cascade = cv.Load( 'haarcascades/haarcascade_profileface.xml' )


        # Set this to the max number of targets to look for (passed to k-means):
        max_targets = 20


        while True:


            # Capture frame from webcam
            camera_image = cv.QueryFrame( self.capture )
            #ret, frame = cap.read()

            frame_count += 1
            frame_t0 = time.time()
            mat = cv.GetMat(camera_image)
            Nmat = numpy.array(mat, dtype=numpy.uint8)


            # Create an image with interactive feedback:
            display_image = cv.CloneImage( camera_image )

            # NEW INSERT - FGMASK
            fgmask = fgbg.apply(Nmat,Nforemat,-1)
            fgmask = cv.fromarray(fgmask)

            # Create a working "color image" to modify / blur
            color_image = cv.CloneImage( display_image )


            # Smooth to get rid of false positives
            cv.Smooth( color_image, color_image, cv.CV_GAUSSIAN, 19, 0 ) #Changed from 19 AND MADE MEDIAN FILTER


            # Smooth to get rid of false positives

#            color_image = numpy.asarray( cv.GetMat( color_image ) )
#            (mu, sigma) = cv2.meanStdDev(color_image)
#            edges = cv2.Canny(color_image, mu - sigma, mu + sigma)
#            lines = cv2.HoughLines(edges, 1, pi / 180, 70)


            # Use the Running Average as the static background
            # a = 0.020 leaves artifacts lingering way too long.
            # a = 0.320 works well at 320x240, 15fps.  (1/a is roughly num frames.)
            cv.RunningAvg( color_image, running_average_image, gfilter, None )


            # Convert the scale of the moving average.
            cv.ConvertScale( running_average_image, running_average_in_display_color_depth, 1.0, 0.0 )


            # Subtract the current frame from the moving average.
            cv.AbsDiff( color_image, running_average_in_display_color_depth, difference )


            # Convert the image to greyscale.
            cv.CvtColor( difference, grey_image, cv.CV_RGB2GRAY )
            # Smooth Before thresholding
            cv.Smooth( grey_image, grey_image, cv.CV_GAUSSIAN, 19, 19 )
            # Threshold the image to a black and white motion mask:
            cv.Threshold( grey_image, grey_image, 2, 255, cv.CV_THRESH_BINARY )
            # Smooth and threshold again to eliminate "sparkles"
            #cv.Smooth( grey_image, grey_image, cv.CV_GAUSSIAN, 19, 0 )  #changed from 19 - AND put smooth before threshold
            cv.Threshold( grey_image, grey_image, 240, 255, cv.CV_THRESH_BINARY)


            grey_image_as_array = numpy.asarray( cv.GetMat( grey_image ) )
            non_black_coords_array = numpy.where( grey_image_as_array > 3 )
            # Convert from numpy.where()'s two separate lists to one list of (x, y) tuples:
            non_black_coords_array = zip( non_black_coords_array[1], non_black_coords_array[0] )

            frame_hsv = cv.CreateImage(cv.GetSize(color_image),8,3)
            cv.CvtColor(color_image,frame_hsv,cv.CV_BGR2HSV)
            imgthreshold_yellow=cv.CreateImage(cv.GetSize(color_image),8,1)
            imgthreshold_white=cv.CreateImage(cv.GetSize(color_image),8,1)
            imgthreshold_white2=cv.CreateImage(cv.GetSize(color_image),8,1)
            cv.InRangeS(frame_hsv,cv.Scalar(0,0,196),cv.Scalar(255,255,255),imgthreshold_white)  # changed scalar from 255,15,255 to 255,255,255
            cv.InRangeS(frame_hsv,cv.Scalar(41,43,224),cv.Scalar(255,255,255),imgthreshold_white2)
            cv.InRangeS(frame_hsv,cv.Scalar(20,100,100),cv.Scalar(30,255,255),imgthreshold_yellow)
            #cvCvtColor(color_image, yellowHSV, CV_BGR2HSV)
            #lower_yellow = np.array([10, 100, 100], dtype=np.uint8)
            #upper_yellow = np.array([30, 255, 255], dtype=np.uint8)
            #mask_yellow = cv2.inRange(yellowHSV, lower_yellow, upper_yellow)
            #res_yellow = cv2.bitwise_and(color_image, color_image, mask_yellow = mask_yellow)


            points = []   # Was using this to hold either pixel coords or polygon coords.
            bounding_box_list = []


            # Now calculate movements using the white pixels as "motion" data
            contour = cv.FindContours( grey_image, mem_storage, cv.CV_RETR_CCOMP, cv.CV_CHAIN_APPROX_SIMPLE )

            i=0
            while contour:

#                c = contour[i]
#                m = cv2.moments(c)
#                Area  = m['m00']
#                print( Area )

                bounding_rect = cv.BoundingRect( list(contour) )
                point1 = ( bounding_rect[0], bounding_rect[1] )
                point2 = ( bounding_rect[0] + bounding_rect[2], bounding_rect[1] + bounding_rect[3] )


                bounding_box_list.append( ( point1, point2 ) )
                polygon_points = cv.ApproxPoly( list(contour), mem_storage, cv.CV_POLY_APPROX_DP )


                # To track polygon points only (instead of every pixel):
                #points += list(polygon_points)


                # Draw the contours:
                ###cv.DrawContours(color_image, contour, cv.CV_RGB(255,0,0), cv.CV_RGB(0,255,0), levels, 3, 0, (0,0) )
                cv.FillPoly( grey_image, [ list(polygon_points), ], cv.CV_RGB(255,255,255), 0, 0 )
                cv.PolyLine( display_image, [ polygon_points, ], 0, cv.CV_RGB(255,255,255), 1, 0, 0 )
                #cv.Rectangle( display_image, point1, point2, cv.CV_RGB(120,120,120), 1)
#        if Area > 3000:
#            cv2.drawContours(imgrgb,[cnt],0,(255,255,255),2)
#            print(Area)

                i=i+1
                contour = contour.h_next()




            # Find the average size of the bbox (targets), then
            # remove any tiny bboxes (which are prolly just noise).
            # "Tiny" is defined as any box with 1/10th the area of the average box.
            # This reduces false positives on tiny "sparkles" noise.
            box_areas = []
            for box in bounding_box_list:
                box_width = box[right][0] - box[left][0]
                box_height = box[bottom][0] - box[top][0]
                box_areas.append( box_width * box_height )


                #cv.Rectangle( display_image, box[0], box[1], cv.CV_RGB(255,0,0), 1)


            average_box_area = 0.0
            if len(box_areas): average_box_area = float( sum(box_areas) ) / len(box_areas)


            trimmed_box_list = []
            for box in bounding_box_list:
                box_width = box[right][0] - box[left][0]
                box_height = box[bottom][0] - box[top][0]


                # Only keep the box if it's not a tiny noise box:
                if (box_width * box_height) > average_box_area*0.1: trimmed_box_list.append( box )


            # Draw the trimmed box list:
            #for box in trimmed_box_list:
            #    cv.Rectangle( display_image, box[0], box[1], cv.CV_RGB(0,255,0), 2 )


            bounding_box_list = merge_collided_bboxes( trimmed_box_list )


            # Draw the merged box list:
            for box in bounding_box_list:
                cv.Rectangle( display_image, box[0], box[1], cv.CV_RGB(0,255,0), 1 )


            # Here are our estimate points to track, based on merged & trimmed boxes:
            estimated_target_count = len( bounding_box_list )


            # Don't allow target "jumps" from few to many or many to few.
            # Only change the number of targets up to one target per n seconds.
            # This fixes the "exploding number of targets" when something stops moving
            # and the motion erodes to disparate little puddles all over the place.


            if frame_t0 - last_target_change_t < .35:  # 1 change per 0.35 secs
                estimated_target_count = last_target_count
            else:
                if last_target_count - estimated_target_count > 1: estimated_target_count = last_target_count - 1
                if estimated_target_count - last_target_count > 1: estimated_target_count = last_target_count + 1
                last_target_change_t = frame_t0


            # Clip to the user-supplied maximum:
            estimated_target_count = min( estimated_target_count, max_targets )


            # The estimated_target_count at this point is the maximum number of targets
            # we want to look for.  If kmeans decides that one of our candidate
            # bboxes is not actually a target, we remove it from the target list below.


            # Using the numpy values directly (treating all pixels as points):
            points = non_black_coords_array
            center_points = []


            if len(points):


                # If we have all the "target_count" targets from last frame,
                # use the previously known targets (for greater accuracy).
                k_or_guess = max( estimated_target_count, 1 )  # Need at least one target to look for.
                if len(codebook) == estimated_target_count:
                    k_or_guess = codebook


                #points = vq.whiten(array( points ))  # Don't do this!  Ruins everything.
                codebook, distortion = vq.kmeans( array( points ), k_or_guess )


                # Convert to tuples (and draw it to screen)
                for center_point in codebook:
                    center_point = ( int(center_point[0]), int(center_point[1]) )
                    center_points.append( center_point )
                    #cv.Circle(display_image, center_point, 10, cv.CV_RGB(255, 0, 0), 2)
                    #cv.Circle(display_image, center_point, 5, cv.CV_RGB(255, 0, 0), 3)


            # Now we have targets that are NOT computed from bboxes -- just
            # movement weights (according to kmeans).  If any two targets are
            # within the same "bbox count", average them into a single target.
            #
            # (Any kmeans targets not within a bbox are also kept.)
            trimmed_center_points = []
            removed_center_points = []


            for box in bounding_box_list:
                # Find the centers within this box:
                center_points_in_box = []


                for center_point in center_points:
                    if    center_point[0] < box[right][0] and center_point[0] > box[left][0] and \
                        center_point[1] < box[bottom][1] and center_point[1] > box[top][1] :


                        # This point is within the box.
                        center_points_in_box.append( center_point )


                # Now see if there are more than one.  If so, merge them.
                if len( center_points_in_box ) > 1:
                    # Merge them:
                    x_list = y_list = []
                    for point in center_points_in_box:
                        x_list.append(point[0])
                        y_list.append(point[1])


                    average_x = int( float(sum( x_list )) / len( x_list ) )
                    average_y = int( float(sum( y_list )) / len( y_list ) )


                    trimmed_center_points.append( (average_x, average_y) )


                    # Record that they were removed:
                    removed_center_points += center_points_in_box


                if len( center_points_in_box ) == 1:
                    trimmed_center_points.append( center_points_in_box[0] ) # Just use it.


            # If there are any center_points not within a bbox, just use them.
            # (It's probably a cluster comprised of a bunch of small bboxes.)
            for center_point in center_points:
                if (not center_point in trimmed_center_points) and (not center_point in removed_center_points):
                    trimmed_center_points.append( center_point )


            # Draw what we found:
            #for center_point in trimmed_center_points:
            #    center_point = ( int(center_point[0]), int(center_point[1]) )
            #    cv.Circle(display_image, center_point, 20, cv.CV_RGB(255, 255,255), 1)
            #    cv.Circle(display_image, center_point, 15, cv.CV_RGB(100, 255, 255), 1)
            #    cv.Circle(display_image, center_point, 10, cv.CV_RGB(255, 255, 255), 2)
            #    cv.Circle(display_image, center_point, 5, cv.CV_RGB(100, 255, 255), 3)


            # Determine if there are any new (or lost) targets:
            actual_target_count = len( trimmed_center_points )
            last_target_count = actual_target_count


            # Now build the list of physical entities (objects)
            this_frame_entity_list = []


            # An entity is list: [ name, color, last_time_seen, last_known_coords ]


            for target in trimmed_center_points:


                # Is this a target near a prior entity (same physical entity)?
                entity_found = False
                entity_distance_dict = {}


                for entity in last_frame_entity_list:


                    entity_coords= entity[3]
                    delta_x = entity_coords[0] - target[0]
                    delta_y = entity_coords[1] - target[1]


                    distance = sqrt( pow(delta_x,2) + pow( delta_y,2) )
                    entity_distance_dict[ distance ] = entity


                # Did we find any non-claimed entities (nearest to furthest):
                distance_list = entity_distance_dict.keys()
                distance_list.sort()


                for distance in distance_list:


                    # Yes; see if we can claim the nearest one:
                    nearest_possible_entity = entity_distance_dict[ distance ]


                    # Don't consider entities that are already claimed:
                    if nearest_possible_entity in this_frame_entity_list:
                        #print "Target %s: Skipping the one iwth distance: %d at %s, C:%s" % (target, distance, nearest_possible_entity[3], nearest_possible_entity[1] ) #Commented Out 3/20/2016
                        continue


                    #print "Target %s pixel(b,g,r) : USING the one iwth distance: %d at %s, C:%s" % (target, distance, nearest_possible_entity[3] , nearest_possible_entity[1]) # Commented Out 3/20/2016
                    # Found the nearest entity to claim:
                    entity_found = True
                    nearest_possible_entity[2] = frame_t0  # Update last_time_seen
                    nearest_possible_entity[3] = target  # Update the new location
                    this_frame_entity_list.append( nearest_possible_entity )
                    #log_file.write( "%.3f MOVED %s %d %d\n" % ( frame_count, nearest_possible_entity[0], nearest_possible_entity[3][0], nearest_possible_entity[3][1]  ) )
                    break


                if entity_found == False:
                    # It's a new entity.
                    color = ( random.randint(0,255), random.randint(0,255), random.randint(0,255) )
                    name = hashlib.md5( str(frame_t0) + str(color) ).hexdigest()[:6]
                    last_time_seen = frame_t0
                    if imgthreshold_white[target[1],target[0]] == 0.0:
                        # It's a real detect (not a line marker)

                        new_entity = [ name, color, last_time_seen, target ]
                        this_frame_entity_list.append( new_entity )
                        log_file.write( "%.3f %.3f FOUND %s %d %d\n" % ( frame_count/fps, frame_count, new_entity[0], new_entity[3][0], new_entity[3][1]  ) )
                        filedrive = "C:/Users/525494/New_folder/000216/run_096/"
                        filename = "img"+str(name)
			#print "gfilter is: %.2f" + gfilter
                        cv.SaveImage("image-test%s-%3f.png"%(new_entity[0],gfilter), display_image)
                    elif imgthreshold_white[target[1],target[0]] == 255.0:
                        # It's a white line detect

                        new_entity = [ name, color, last_time_seen, target ]
                        this_frame_entity_list.append( new_entity )
                        log_file.write( "%.3f %.3f FOUND %s %d %d\n" % ( frame_count/fps, frame_count, new_entity[0], new_entity[3][0], new_entity[3][1]  ) )
                        filedrive = "C:/Users/525494/New_folder/000216/run_096/"
                        filename = "img"+str(name)
			#print "gfilter is: %.2f" + gfilter
                        cv.SaveImage("white-line-image-test%s-%3f.png"%(new_entity[0],gfilter), display_image)
                    elif imgthreshold_yellow[target[1],target[0]] == 255.0:
                        # It's a yellow line detect

                        new_entity = [ name, color, last_time_seen, target ]
                        this_frame_entity_list.append( new_entity )
                        log_file.write( "%.3f %.3f FOUND %s %d %d\n" % ( frame_count/fps, frame_count, new_entity[0], new_entity[3][0], new_entity[3][1]  ) )
                        filedrive = "C:/Users/525494/New_folder/000216/run_096/"
                        filename = "img"+str(name)
                        cv.SaveImage("yellow-line-image-test%s.png"%(new_entity[0]), camera_image)

            # Now "delete" any not-found entities which have expired:
            entity_ttl = 1.0  # 1 sec.


            for entity in last_frame_entity_list:
                last_time_seen = entity[2]
                if frame_t0 - last_time_seen > entity_ttl:
                    # It's gone.
                    #log_file.write( "%.3f STOPD %s %d %d\n" % ( frame_count, entity[0], entity[3][0], entity[3][1]  ) )
                    pass
                else:
                    # Save it for next time... not expired yet:
                    this_frame_entity_list.append( entity )


            # For next frame:
            last_frame_entity_list = this_frame_entity_list


            # Draw the found entities to screen:
            for entity in this_frame_entity_list:
                center_point = entity[3]
                c = entity[1]  # RGB color tuple
                cv.Circle(display_image, center_point, 20, cv.CV_RGB(c[0], c[1], c[2]), 1)
                cv.Circle(display_image, center_point, 15, cv.CV_RGB(c[0], c[1], c[2]), 1)
                cv.Circle(display_image, center_point, 10, cv.CV_RGB(c[0], c[1], c[2]), 2)
                cv.Circle(display_image, center_point,  5, cv.CV_RGB(c[0], c[1], c[2]), 3)




            #print "min_size is: " + str(min_size)
            # Listen for ESC or ENTER key
            c = cv.WaitKey(7) % 0x100
            if c == 27 or c == 10:
                break


            # Toggle which image to show
            if chr(c) == 'd':
                image_index = ( image_index + 1 ) % len( image_list )


            image_name = image_list[ image_index ]


            # Display frame to user
            if image_name == "camera":
                image = camera_image
                cv.PutText( image, "Camera (Normal)", text_coord, text_font, text_color )
            elif image_name == "shadow":
                image = fgmask
                cv.PutText( image, "No Shadow", text_coord, text_font, text_color )
            elif image_name == "white":
                #image = difference
                image = imgthreshold_white
                cv.PutText( image, "White Threshold", text_coord, text_font, text_color )
            elif image_name == "display":
                #image = display_image
                image = display_image
                cv.PutText( image, "Targets (w/AABBs and contours)", text_coord, text_font, text_color )
                cv.PutText( image, str(frame_t0), text_coord2, text_font, text_color )
                cv.PutText( image, str(frame_count), text_coord3, text_font, text_color )
            elif image_name == "threshold":
                # Convert the image to color.
                cv.CvtColor( grey_image, display_image, cv.CV_GRAY2RGB )
                image = display_image  # Re-use display image here
                cv.PutText( image, "Motion Mask", text_coord, text_font, text_color )
            elif image_name == "yellow":
                # Do face detection
                #detect_faces( camera_image, haar_cascade, mem_storage )
                image = imgthreshold_yellow  # Re-use camera image here
                cv.PutText( image, "Yellow Threshold", text_coord, text_font, text_color )


            #cv.ShowImage( "Target", image )		Commented out 3/19

#            self.writer.write( image )
#            out.write( image );
#            cv.WriteFrame( self.writer, image );
#            if self.writer:
#                cv.WriteFrame( self.writer, image );
#                video.write( image );

            log_file.flush()

            # If only using a camera, then there is no time.sleep() needed,
            # because the camera clips us to 15 fps.  But if reading from a file,
            # we need this to keep the time-based target clipping correct:
            frame_t1 = time.time()

            # If reading from a file, put in a forced delay:
#            if not self.writer:
#                delta_t = frame_t1 - frame_t0
#                if delta_t < ( 1.0 / 15.0 ): time.sleep( ( 1.0 / 15.0 ) - delta_t ):

            if frame_count == 155740:
                cv2.destroyWindow("Target")
#                    cv.ReleaseVideoWriter()
#                    self.writer.release()
#                    log_file.flush()
                break

        t1 = time.time()
        time_delta = t1 - t0
        processed_fps = float( frame_count ) / time_delta
        print "Got %d frames. %.1f s. %f fps." % ( frame_count, time_delta, processed_fps )
#        video.release()


if __name__=="__main__":
    t = Target() # Commented out 3/20/2016
#    import cProfile
#    cProfile.run( 't.run()' )
    t.run()
