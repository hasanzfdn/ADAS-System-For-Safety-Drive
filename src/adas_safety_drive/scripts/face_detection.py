#!/usr/bin/env python3

"""
Created on Thu Mar 30 18:41:57 2023

@author: elifs
"""

# Importing OpenCV Library for basic image processing functions
import cv2
# Numpy for array related functions
import numpy as np
# Dlib for deep learning based Modules and face landmark detection
import dlib
# face_utils for basic operations of conversion
from imutils import face_utils
import time
from cv_bridge import CvBridge
from sensor_msgs.msg import Image
import rospy
from std_msgs.msg import Bool




def compute(ptA, ptB):
    dist = np.linalg.norm(ptA - ptB)
    return dist

def blinkedleft(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    # Checking if it is blinked
    if (ratio > 0.18):
        return 2
    #elif (ratio > 0.21 and ratio <= 0.25):
    #   return 1
    else:
        return 0
def blinkedright(a, b, c, d, e, f):
    up = compute(b, d) + compute(c, e)
    down = compute(a, f)
    ratio = up / (2.0 * down)

    # Checking if it is blinked
    if (ratio > 0.18):
        return 2
    #elif (ratio > 0.21 and ratio <= 0.25):
    #   return 1
    else:
        return 0





# time variables
start_time = time.time()
prev_time = start_time
# Initializing the face detector and landmark detector
detector = dlib.get_frontal_face_detector()
# GIVE PATH YOUR WEIGHTS
predictor = dlib.shape_predictor("/home/hasan/Desktop/bitirme/ADAS-System-For-Safety-Drive/src/adas_safety_drive/weights/shape_predictor_68_face_landmarks.dat")


# loop until 1 minute
frame_count = 0
active = 0

# status marking for current state
sleep = 0
drowsy = 0
status = ""
color = (0, 0, 0)
face_alert  = False

sleep_status_publisher = rospy.Publisher('face_alert', Bool, queue_size = 1)
face_pub = rospy.Publisher('face_image', Image, queue_size = 10)
def detect_face(data):
    global start_time , active ,sleep , drowsy, prev_time, frame_count , face_alert

    bridge = CvBridge()
    cv_image = bridge.imgmsg_to_cv2(data, desired_encoding='passthrough')



    frame = cv_image
    ret = True
    if ret == True:


        frame_count += 1
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = detector(gray)
        # detected face in faces array
        for face in faces:
            x1 = face.left()
            y1 = face.top()
            x2 = face.right()
            y2 = face.bottom()

            face_frame = frame.copy()
            cv2.rectangle(face_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            landmarks = predictor(gray, face)
            landmarks = face_utils.shape_to_np(landmarks)

            # The numbers are actually the landmarks which will show eye
            left_blink = blinkedleft(landmarks[36], landmarks[37],
                                     landmarks[38], landmarks[41], landmarks[40], landmarks[39])
            right_blink = blinkedright(landmarks[42], landmarks[43],
                                       landmarks[44], landmarks[47], landmarks[46], landmarks[45])

            # Now judge what to do for the eye blinks
            if (left_blink == 0 and right_blink == 0):
                sleep += 1
            elif (left_blink == 2 and right_blink == 0):
                drowsy += 1
            elif (right_blink == 0 and left_blink == 2):
                drowsy += 1
            elif (left_blink == 2 and right_blink == 2):
                active += 1

            # print status every 2 seconds
            if time.time() - prev_time >= 2:
                prev_time = time.time()
                sleep_count = sleep
                drowsy_count = drowsy
                active_count = active
                total_count = sleep_count + drowsy_count + active_count
                Rate = sleep_count/total_count

                print("Sleep:", sleep_count )
                print("Drowsy:", drowsy_count)
                print("Active:", active)
                print("Total:", total_count)
                if (Rate >= 0.25 ):
                    print("Rate of Sleepy:",Rate)
                    face_alert = True
                else :
                    face_alert = False

                cv2.putText(frame, status, (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

                for n in range(0, 68):
                    (x, y) = landmarks[n]
                    cv2.circle(frame, (x, y), 1, (255, 255, 255), -1)
            else:
                break

    #        cv2.imshow("Result of detector", frame)
    #       cv2.waitKey(1)
    image_message = bridge.cv2_to_imgmsg(frame, encoding="passthrough")
    face_pub.publish(image_message)

    if time.time() - start_time > 2:
        frame_count = 0
        active = 0

        # status marking for current state
        sleep = 0
        drowsy = 0

        sleep_status_publisher.publish(face_alert)
        start_time = time.time()

def FaceCameraListener():

    rospy.init_node('image_subscriber', anonymous=False)

    rospy.loginfo('Waiting for face camera topic %s to be published..','/usb_cam/image_raw')
    rospy.wait_for_message('/usb_cam_webcam/image_raw', Image)
    rospy.loginfo('%s  topic is now available for face camera!','/usb_cam/image_raw')

    rospy.Subscriber('/usb_cam_webcam/image_raw', Image, detect_face)


    rospy.spin()


if __name__ == '__main__':
    FaceCameraListener()


