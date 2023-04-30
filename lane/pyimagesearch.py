# import the necessary packages
from imutils import contours
from skimage import measure
import numpy as np
import argparse
import imutils
import cv2
import line_detection_with_opencv

# load the image, convert it to grayscale, and blur it
#gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
#blurred = cv2.GaussianBlur(gray, (11, 11), 0)

#thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)[1]




#thresh = cv2.erode(thresh, None, iterations=2)
#thresh = cv2.dilate(thresh, None, iterations=4)


def conturs(thresh):

    # perform a connected component analysis on the thresholded
    # image, then initialize a mask to store only the "large"
    # components
    labels = measure.label(thresh, connectivity=1, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")

    # loop over the unique components
    for label in np.unique(labels):
        # if this is the background label, ignore it
        if label == 0:
            continue
        # otherwise, construct the label mask and count the
        # number of pixels 
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)
        # if the number of pixels in the component is sufficiently
        # large, then add it to our mask of "large blobs"
        if numPixels > 70:
           mask = cv2.add(mask, labelMask)

    # find the contours in the mask, then sort them from left to
    # right
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    try:
        cnts = imutils.grab_contours(cnts)
        cnts = contours.sort_contours(cnts)[0]
    except:
        pass

    # loop over the contours
    for (i, c) in enumerate(cnts):
       # draw the bright spot on the image
        (x, y, w, h) = cv2.boundingRect(c)
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        cv2.circle(thresh, (int(cX), int(cY)), int(radius),
           (255, 255, 255), 3)
        cv2.putText(thresh, "#{}".format(i + 1), (x, y - 15),
           cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 2)
    # show the output image
 

    return thresh



def waypoints(yol_fotosu):

    canny=line_detection_with_opencv.canny(yol_fotosu)
    zeros = np.copy(canny) * 0

    for katsayi in range(9, 2, -1):

        canny=line_detection_with_opencv.canny(yol_fotosu)
        height, width = canny.shape


        top = (height//10)*katsayi
        bottom = (height//10)*(katsayi+1)

        canny[:top,:] = 0
        canny[bottom:,:] = 0

        waypoint_area = conturs(canny)

        zeros = cv2.addWeighted(zeros, 1, waypoint_area, 1, 0)
    
    return zeros


path = r'/home/hasan/Desktop/bitirme/lane/1.png'
yol_fotosu = cv2.imread(path)
zeros = waypoints(yol_fotosu)


