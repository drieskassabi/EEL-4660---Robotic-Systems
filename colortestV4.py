# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import numpy as np
import RPi.GPIO as GPIO

# set up GPIO for motor control and send signal
GPIO.setmode(GPIO.BCM)
GPIO.setup(22, GPIO.OUT) #clockwise rotation for vertical down servo
GPIO.setup(23, GPIO.OUT) #counter-clockwise rotation for vertical up servo
GPIO.setup(24, GPIO.OUT) #clockwise rotation for horizontal right servo
GPIO.setup(25, GPIO.OUT) #counter-clockwise rotation for horizontal left servo

 
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.2)
 
# initializ the variable that changes which color is detected
# colorKey guide: 0= Red, 1=Green, 2=Blue, 3=Yellow, 4=Orange
colorKey = 0

# save captured video to a file
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#out = cv2.VideoWriter('output3.avi', fourcc, 5, (640, 480))

# default color detected is red
print "detecting red"
# capture frames from the camera
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
	 # grab the raw NumPy array representing the image, then initialize the timestamp
	 # and occupied/unoccupied text
	 frame = frame.array
 
	 hsv =cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

         #Threshold for color
	 # Green: lower_color = [75,80,50] , upper_color = [95,255,255]
	 # Red: lower_color = [160,90,70] , upper_color = [180,255,255]
	 # Blue: lower_color = [110,85,75] , upper_color = [130,255,255]
	 # Yellow: lower_color = [20,125,75] , upper_color = [29,255,255]
	 # Orange: lower_color = [11,180,130] , upper_color = [17,255,255]
         
         if colorKey == 0: # Detecting Red
             lower_color = np.array([160, 90, 70])
             upper_color = np.array([180, 255, 255])
             
         elif colorKey == 1: # Detecting Green
             lower_color = np.array([75, 80, 50])
             upper_color = np.array([95, 255, 255])
             
         elif colorKey == 2: # Detecting Blue
             lower_color = np.array([110, 85, 75])
             upper_color = np.array([130, 255, 255])
             
         elif colorKey == 3: # Detecting Yellow
             lower_color = np.array([20, 125, 75])
             upper_color = np.array([29, 255, 255])
             
         elif colorKey == 4: # Detecting Orange
             lower_color = np.array([11, 180, 130])
             upper_color = np.array([17, 255, 255])
                      
             
         #Extract green with mask
         mask = cv2.inRange(hsv, lower_color, upper_color)
         res = cv2.bitwise_and(frame, frame, mask = mask)

         # filtering the mask in two ways
         kernelOpen = np.ones((5,5))
         kernelClose = np.ones((20,20))

         maskOpen = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernelOpen)
         maskClose = cv2.morphologyEx(maskOpen, cv2.MORPH_CLOSE, kernelClose)


         # Mask Contours
         maskFinal = maskClose
         _, conts, h = cv2.findContours(maskFinal.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
         
	 # draw exact contours on all possible objects! use for testing best_contour
	 cv2.drawContours(frame, conts, -1, (255, 255, 255), 3)

         # finding contour with maximum area and store it as best_cnt
	 max_area = 0
	 best_cnt = 1
	 for cnt in conts:
	     area = cv2.contourArea(cnt)
	     if area > max_area:
	          max_area = area
	          best_cnt = cnt
	 
	 # finding centroids of best_cnt and draw a circle there
	 M = cv2.moments(best_cnt)
	 cX, cY = int(M['m10'] / M['m00']), int(M['m01'] / M['m00'])
	 
	 # if there is nothing detected, set the "detected center" to the camera's centerpoint
	 # this will avoid the problem where the "detected center" started in the top left corner
	 # of the frame when nothing was detected
	 if cX == 0 and cY == 0:
             cX, cY = 320, 240
	 
	 # draw the centerpoint of the detected object
         cv2.circle(frame, (cX, cY), 10, (0, 255, 0), -1)    #BGR
	 
	 # to find the centerpoint of detection, print coordinates 
	 #print cX,cY #remove the # to see where the circle coordinate is
	 
	 # Centering box
	 bound_upper_x = 360
	 bound_lower_x = 280

 	 bound_upper_y = 280
	 bound_lower_y = 200
	
	 # for testing: shows center bounds we want to reach
	 cv2.rectangle(frame, (bound_lower_x, bound_upper_y), (bound_upper_x, bound_lower_y), (0, 255, 0), 3)
	 
	 # differnce in vertical and horizontal directions,
	 # up and right being positive displacement from center
	 # left and down beign negative displacement from center
	 #vertical_difference = cY - 240
	 #horizontal_difference = cX - 320
	 
	 # move up/down
	 if cY > bound_upper_y:
             move_down = bound_upper_y - cY
	     #print "move down", move_down
	     # for servo control
	     # rotate counter-clockwise
	     GPIO.output(23, GPIO.HIGH)
             GPIO.output(22, GPIO.LOW)
	 elif cY < bound_lower_y:
             move_up = bound_lower_y - cY
	     #print "move up", move_up
             # for servo control
             # rotate clockwise
             GPIO.output(22, GPIO.HIGH)
             GPIO.output(23, GPIO.LOW)
         else:
             GPIO.output(22, GPIO.LOW)
             GPIO.output(23, GPIO.LOW)
             
	  # move left/right
	 if cX <  bound_lower_x:
             move_left = cX - bound_lower_x
	     #print "move left", move_left
	     # for servo control
	     # rotate counter-clockwise
	     GPIO.output(25, GPIO.HIGH)
             GPIO.output(24, GPIO.LOW)
	 elif cX > bound_upper_x:
             move_right = cX - bound_upper_x
             #print "move right", move_right
             # for servo control
	     # rotate clockwise
	     GPIO.output(24, GPIO.HIGH)
             GPIO.output(25, GPIO.LOW)
         else:
             GPIO.output(24, GPIO.LOW)
             GPIO.output(25, GPIO.LOW)
        
    ##############################################################


	 # show the frame
	 cv2.imshow("Frame", frame)
	 key = cv2.waitKey(1) & 0xFF
         # save the frame
         #out.write(frame)
         
 	 # if the 'q' key was pressed, break from the loop
	 if key == ord("q"):
             break
	 
	 # if the 'r' key is pressed, change color detection to red
	 if key == ord("r"):
             colorKey = 0
             print "detecting red"
         # if the 'g' key is pressed, change color detection to green
	 if key == ord("g"):
             colorKey = 1
             print "detecting green"
         # if the 'b' key is pressed, change color detection to blue
	 if key == ord("b"):
             colorKey = 2
             print "detecting blue"
         # if the 'y' key is pressed, change color detection to yellow
	 if key == ord("y"):
             colorKey = 3
             print "detecting yellow"
         # if the 'o' key is pressed, change color detection to orange
	 if key == ord("o"):
             colorKey = 4
             print "detecting orange"
             
	 # clear the stream in preparation for the next frame
	 rawCapture.truncate(0)
 
#out.release()

	  


