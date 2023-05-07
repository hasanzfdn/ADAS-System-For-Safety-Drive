"""
@author E-mail = hasan.ozfidan@std.yildiz.edu.tr

"""
# Note: Comment lines added for debugging.

import cv2
import numpy as np
import matplotlib.pyplot as plt
import psutil


def warp(img):
    img_size = (img.shape[1], img.shape[0])
    
    width = img.shape[1]
    height = img.shape[0]
       
    sag_ust_src_x = int(width * 0.68)
    sag_ust_src_y = int(height * 0.52)

    sag_alt_src_X = int(width * 0.791)
    sag_alt_src_y = int(height * 1)

    sol_alt_src_x = int(width * 0.208)
    sol_alt_src_y = int(height * 1)

    sol_ust_src_x = int(width * 0.319)
    sol_ust_src_y = int(height * 0.52)


    sag_ust_dst_x = int(width * 0.74)
    sag_ust_dst_y = int(height * 0.4)

    sag_alt_dst_x = int(width * 0.74)
    sag_alt_dst_y = int(height * 1)

    sol_alt_dst_x = int(width * 0.259)
    sol_alt_dst_y = int(height * 1)

    sol_ust_dst_x = int(width * 0.259)
    sol_ust_dst_y = int(height * 0.4)


    src = np.float32(
        [[sag_ust_src_x, sag_ust_src_y],       #sag_ust
         [sag_alt_src_X, sag_alt_src_y],       #sag_alt
         [sol_alt_src_x, sol_alt_src_y],       #sol_alt
         [sol_ust_src_x, sol_ust_src_y]])      #sol_ust
    dst = np.float32(
        [[sag_ust_dst_x, sag_ust_dst_y],
         [sag_alt_dst_x, sag_alt_dst_y],
         [sol_alt_dst_x, sol_alt_dst_y],
         [sol_ust_dst_x, sol_ust_dst_y]])
    M = cv2.getPerspectiveTransform(src, dst)
    Minv = cv2.getPerspectiveTransform(dst, src)
    warped = cv2.warpPerspective(img, M, img_size, flags=cv2.INTER_LINEAR)


    return warped


def preprocess_img(img):

    cropped_image = np.copy(img)

    height = cropped_image.shape[0]
    width = cropped_image.shape[1]

    min_x = 0
    max_x = width     
    min_y = 0    
    max_y = int(height * 0.54)  #0.54
    car_top_y = int(height * 1) #0.87
    car_bottom_y = height

    cropped_image[ min_y :max_y, min_x:max_x]=0
    cropped_image[car_top_y:car_bottom_y, min_x:max_x]=0

    return cropped_image

def increase_brightness(img, value=30):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)

    lim = 255 - value
    v[v > lim] = 255
    v[v <= lim] += value

    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)

    #cv2.imshow('image',img)
    #cv2.waitKey(42)
    return img


def firstzonecut(img, mercedes_dif=0):
    height, width = img.shape
    polygons = np.array(
        [
            [
                 [width // 6 + mercedes_dif, height],
                 [5 * (width // 6) + mercedes_dif, height],
                 [5 * (width // 6)-50  + mercedes_dif, (height // 11) * 10],
                 [(width // 6)+50 + mercedes_dif, (height // 11) * 10]  #sol_ust
            ]
        ], dtype=np.int32
    )

    mask = np.zeros_like(img)
    cv2.fillPoly(mask, polygons, 255)
    masked_image = cv2.bitwise_and(img, mask)
    return masked_image


def blur(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    kernel_sizex = 9
    kernel_sizey = 9
    blur_gray = cv2.GaussianBlur(gray, (kernel_sizex, kernel_sizey), 0)
    return blur_gray


def regional_canny(blur_gray):


    height = blur_gray.shape[0]
    width = blur_gray.shape[1]

    min_x = 0
    max_x = width     
    min_y = 0    
    max_y = int(height * 0.55)  
    car_top_y = int(height * 0.87)
    car_bottom_y = height

    zero_img = np.copy(blur_gray) * 0
    top_line = max_y+1         #(height // 4) * 3   #plus 1 is offset(actually not necessery to understand) 
    mid_line = ((car_top_y - top_line) // 2) + top_line    #((height - top_line) // 2) + top_line
    sigma1 = 1.33 # 1.33	#5	#5	#6	#7	#7
    sigma2 = 0.77 # 0.77	#2	#3	#5	#5	#6
    katsayi = 1  # 2		#1	#1	#1	#1

    for x in range(2):
        for a in range(1, 7):
            left = int(width * (a - 1) * (1.0 / 6))
            right = int(width * a * (1.0 / 6))
            box = blur_gray[top_line: mid_line, left: right]

            average = np.mean(box)
            upper = int(max(0, (sigma1) * average)) * katsayi
            lower = int(min(255, (sigma2) * average)) * katsayi
            little_canny_area = cv2.Canny(box, upper, lower)
            zero_img[top_line: mid_line, left: right] = little_canny_area
        top_line = mid_line
        mid_line = (car_top_y - 3) #minus 3 is offset(actually not necessery to understand)
    little_canny_area = zero_img
    little_canny_area = little_canny_area[max_y:car_top_y, min_x:max_x]

    return little_canny_area


def hough1(edges):		#implement to the full_image
    rho = 2
    theta = np.pi / 180
    threshold = 15
    min_line_length = 25
    max_line_gap = 5
    line_image = np.copy(edges) * 0
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)
    try:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), 10)
    except:
        pass
    hough = cv2.addWeighted(edges, 1, line_image, 1, 0)
    return hough


def hough2(edges):		#implement to the first zone only
    rho = 2
    theta = np.pi / 180
    threshold = 15
    min_line_length = 25
    max_line_gap = 7
    line_image = np.copy(edges) * 0
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)
    try:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), 17)
    except:
        pass
    hough = cv2.addWeighted(edges, 1, line_image, 1, 0)
    return hough


def finishzonecut(img):
    height, width = img.shape
    zero_img = np.copy(img) * 0
    img = img[10 * (height // 13): 11 * (height // 13), 533: 1367]
    zero_img[10 * (height // 13): 11 * (height // 13), 533: 1367] = img
    img = zero_img
    # cv2.imshow('fsf' , img)
    # cv2.waitKey(0)
    return img


def draw_line(img,mercedes_dif):
     height, width = img.shape
#    mercedes_dif= -170
     pts = np.array(
         [
             [
                 [width // 6 + mercedes_dif, height],   #bottom_left
                 [5 * (width // 6) + mercedes_dif, height], #bottom_right
                 [5 * (width // 6)-50  + mercedes_dif, (height // 11) * 10],  #top_right
                 [(width // 6)+50 + mercedes_dif, (height // 11) * 10]      #top_left
             ]
         ], np.int32
      )
     cv2.polylines(img, [pts], True, (255, 255, 255),5)
     return img

def canny(image, mercedes_dif=0):
    org_mercedes = mercedes_dif
    mercedes_dif *= 1
    cut_image = preprocess_img(image)
   # cut_image = increase_brightness(cut_image, value=90)            #if the image is very dark you can use this line for bright image
    blur_gray = blur(cut_image)
    edges = regional_canny(blur_gray)
    firstzone = firstzonecut(edges, mercedes_dif)
    Hough2 = hough2(firstzone)
    Hough1 = hough1(edges)
    final = cv2.addWeighted(Hough2, 1, Hough1, 1, 0)
    #final = draw_line(final ,mercedes_dif)
    resim = cv2.resize(final, (1080 , 720))
    warped_final = warp(resim)

    
    #cv2.imshow("Image", resim)
    #cv2.waitKey(0)


 
    # Calling psutil.cpu_precent() for 4 seconds
    print('RAM memory % used:', psutil.virtual_memory()[2])
   

    return warped_final

#path = r'/home/hasan/Desktop/bitirme/lane/1.png'
#image = cv2.imread(path)
#canny(image, mercedes_dif=0)