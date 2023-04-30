import cv2
import numpy as np
import findwaypoints
import matplotlib.pyplot as plt


cap = cv2.VideoCapture("2019pist.mp4")
frame_width = int(cap.get(3))
frame_height = int(cap.get(4))
size = (frame_width, frame_height)

if (cap.isOpened()== False): 
  print("Error opening video stream or file")
cnt = 0
while cap.isOpened()and cnt<10000 :
    ret, frame = cap.read()
    #cv2.imshow('das',frame)
    #cv2.waitKey(1)
    if ret:
        new_img , a = findwaypoints.polyfit(frame)
        #cv2.imshow('image',new_img)
        #cv2.waitKey(42)
        plt.imshow(new_img)
        plt.show()
        print(a)

    else:
        break

    cnt += 1
cap.release()
