#!/usr/bin/env python3

import line_detection_with_opencv
import cv2
import numpy as np
import matplotlib.pyplot as plt
from sensor_msgs.msg import Image
import rospy
from cv_bridge import CvBridge
from std_msgs.msg import Bool
import matplotlib.image as mpimg



def find_lane_pixels(binary_warped):
    # Take a histogram of the bottom half of the image
    histogram = np.sum(binary_warped[binary_warped.shape[0]//2:, :], axis=0)
    # Create an output image to draw on and visualize the result
    out_img = np.dstack((binary_warped, binary_warped, binary_warped))
    # Find the peak of the left and right halves of the histogram
    # These will be the starting point for the left and right lines
    midpoint = np.int64(histogram.shape[0]//2)
    leftx_base = np.argmax(histogram[:midpoint])
    rightx_base = np.argmax(histogram[midpoint:]) + midpoint

    # HYPERPARAMETERS
    # Choose the number of sliding windows
    nwindows = 12
    # Set the width of the windows +/- margin
    margin = 120
    # Set minimum number of pixels found to recenter window
    minpix = 50

    # Set height of windows - based on nwindows above and image shape
    window_height = np.int64(binary_warped.shape[0]//nwindows)
    # Identify the x and y positions of all nonzero pixels in the image
    nonzero = binary_warped.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    # Current positions to be updated later for each window in nwindows
    leftx_current = leftx_base
    rightx_current = rightx_base

    # Create empty lists to receive left and right lane pixel indices
    left_lane_inds = []
    right_lane_inds = []

    # Step through the windows one by one
    for window in range(nwindows-1):
        # Identify window boundaries in x and y (and right and left)
        win_y_low = binary_warped.shape[0] - (window+1)*window_height
        win_y_high = binary_warped.shape[0] - window*window_height
        win_xleft_low = leftx_current - margin
        win_xleft_high = leftx_current + margin
        win_xright_low = rightx_current - margin
        win_xright_high = rightx_current + margin

        # Draw the windows on the visualization image
        cv2.rectangle(out_img,(win_xleft_low,win_y_low),
        (win_xleft_high,win_y_high),(0,255,0), 2)
        cv2.rectangle(out_img,(win_xright_low,win_y_low),
        (win_xright_high,win_y_high),(0,255,0), 2)

        # Identify the nonzero pixels in x and y within the window #
        good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
        (nonzerox >= win_xleft_low) &  (nonzerox < win_xleft_high)).nonzero()[0]
        good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) &
        (nonzerox >= win_xright_low) &  (nonzerox < win_xright_high)).nonzero()[0]

        # Append these indices to the lists
        left_lane_inds.append(good_left_inds)
        right_lane_inds.append(good_right_inds)

        # If you found > minpix pixels, recenter next window on their mean position
        if len(good_left_inds) > minpix:
            leftx_current = np.int64(np.mean(nonzerox[good_left_inds]))
        if len(good_right_inds) > minpix:
            rightx_current = np.int64(np.mean(nonzerox[good_right_inds]))

    # Concatenate the arrays of indices (previously was a list of lists of pixels)
    try:
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
    except ValueError:
        # Avoids an error if the above is not implemented fully
        pass

    # Extract left and right line pixel positions
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds]
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds]

    return leftx, lefty, rightx, righty, out_img


def fit_polynomial(binary_warped):
    # Find our lane pixels first
    leftx, lefty, rightx, righty, out_img = find_lane_pixels(binary_warped)

    # Fit a second order polynomial to each using `np.polyfit`
    try:

        left_fit = np.polyfit(lefty, leftx, 2)
        right_fit = np.polyfit(righty, rightx, 2)

    # Generate x and y values for plotting
        ploty = np.linspace(0, binary_warped.shape[0]-1, binary_warped.shape[0] )
        try:
            left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
            right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]
        except TypeError:
        # Avoids an error if `left` and `right_fit` are still none or incorrect
            print('The function failed to fit a line!')
            left_fitx = 1*ploty**2 + 1*ploty
            right_fitx = 1*ploty**2 + 1*ploty


    ## Visualization ##
    # Colors in the left and right lane regions
        out_img[lefty, leftx] = [255, 0, 0]
        out_img[righty, rightx] = [0, 0, 255]

    # Plots the left and right polynomials on the lane lines
        plt.plot(left_fitx, ploty, color='cyan')
        plt.plot(right_fitx, ploty, color='yellow')



        mid_left = (binary_warped.shape[1] // 2.0) - (binary_warped.shape[1]*0.04)
        mid_right = (binary_warped.shape[1] // 2.0) + (binary_warped.shape[1]*0.04)

        lane_alert = False


        if all(x > mid_left for x in leftx):

            print("misses the road in the left lane")
            lane_alert = True

        if all(x < mid_right for x in rightx):

            print("misses the road in the right lane")
            lane_alert = True

    except:
        lane_alert = False



    return lane_alert

def polyfit(data,image_pub):

    bridge = CvBridge()
    cv_image = bridge.imgmsg_to_cv2(data, desired_encoding='passthrough')
    binary_image = line_detection_with_opencv.canny(cv_image)

    lane_alert_publisher = rospy.Publisher('lane_alert', Bool, queue_size = 1)
    lane_alert = fit_polynomial(binary_image)
    lane_alert_publisher.publish(lane_alert)

    image_message = bridge.cv2_to_imgmsg(binary_image, encoding="passthrough")
    image_pub.publish(image_message)

def cameraInfoListener():

    rospy.init_node('image_subscriber', anonymous=False)
    rospy.loginfo('Waiting for topic %s to be published..','/simulator/camera_node/image/compressed')
    rospy.wait_for_message('/simulator/middle_camera',Image)
    rospy.loginfo('%s topic is now available!','/simulator/camera_node/image/compressed')


    image_publisher = rospy.Publisher('image_topic', Image, queue_size = 10)
    rospy.Subscriber('/simulator/middle_camera', Image, polyfit, image_publisher)
    rospy.spin()



if __name__ == '__main__':
    cameraInfoListener()




#path = r'/home/hasan/Desktop/bitirme/lane/83777900_124440222390010_1534250390730571776_n.jpg'
#image = cv2.imread(path)

#out_img, a = polyfit(image)
#cv2.imshow('image',out_img)
#cv2.waitKey(0)