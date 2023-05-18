#!/usr/bin/env python3

import rospy
from std_msgs.msg import Bool
from std_msgs.msg import string


face_alert = False
lane_alert = False
sleep_publisher = rospy.Publisher('sleep_warning', string, queue_size = 1)
drive_publisher= rospy.Publisher('drive_warning', string, queue_size = 1)

global face_cnt = 0
global line_cnt = 0

def face(data):
    # 10 sn'de bir uyku verisi geliyor.
    # 20 sn' içerisinde üst üste iki veri de uykulu olursa uyarı ver.

    if (data == False):
        face_cnt = 0

    else:
        face_cnt = face_cnt + 1

        if (face_cnt == 1):
            sleep_publisher.publish('BİR KAHVE MOLASI VERİNİZ')

        if (face_cnt == 2):
            face_alert = True
            face_cnt = 0

        return face_alert



def lane(data):

    if (data == False):
        out_lane =+ 1

    else:
        in_lane =+ 1



    if (out_lane//in_lane == 0.4):
        drive_publisher.publish('DİKKATLİ SÜRÜNÜZ')
        line_cnt =+ 1

    return lane_alert
'''
import message_filters
 from sensor_msgs.msg import Image, CameraInfo

 def callback(image, camera_info):
    5   # Solve all of perception here...

 image_sub = message_filters.Subscriber('image', Image)
 info_sub = message_filters.Subscriber('camera_info', CameraInfo)

 ts = message_filters.TimeSynchronizer([image_sub, info_sub], 10)
 ts.registerCallback(callback)
 rospy.spin()
 '''
def decision_publisher():

    rospy.init_node('decision_sub_pub', anonymous=False)

    rospy.Subscriber('/face_alert', Bool, face)
    rospy.Subscriber('/lane_alert', Bool, lane)



    rospy.spin()


if __name__ == '__main__':
    decision_publisher()

