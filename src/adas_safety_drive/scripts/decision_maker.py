#!/usr/bin/env python3

import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String
import message_filters
import send_e_mail
from sensor_msgs.msg import Image
import cv2


sleep_publisher = rospy.Publisher('sleep_warning', String, queue_size = 1)
drive_publisher = rospy.Publisher('drive_warning', String, queue_size = 1)
health_warning_pub = rospy.Publisher('health_situation', Bool, queue_size = 1)
face_cnt = 0
lane_cnt = 0
msg_lane = String()
msg_lane.data = 'PLEASE KEEP YOUR VEHICLE WITHIN THE LANES FOR YOUR HEALTH'


msg = String()
msg.data = 'PLEASE TAKE A COFFEE BREAK FOR YOUR HEALTH'

def face(data):
    global face_alert
    face_alert = False

    # 10 sn'de bir uyku verisi geliyor.
    # 20 sn' içerisinde üst üste iki veri de uykulu olursa uyarı ver.
    """
    if (data == False):
        face_cnt = 0

    else:
        face_cnt = face_cnt + 1
        if (face_cnt == 1):
            sleep_publisher.publish(msg)

        if (face_cnt == 2):
            face_alert = True
            face_cnt = 0
    """
    if (data == True):
        face_alert = True
    else:
        face_alert = False

    return face_alert



def lane(data):
#    global lane_cnt, lane_alert
    global lane_alert
    lane_alert = False

    # 10 sn'de bir lane verisi geliyor.
    # 20 sn' içerisinde üst üste iki veri de sıkıntılı olursa uyarı ver.

    '''
    if (data == False):
        lane_cnt = 0

    else:
        lane_cnt = lane_cnt + 1

        if (lane_cnt == 1):
            drive_publisher.publish(msg_lane)

        if (lane_cnt == 2):
            lane_alert = True
            lane_cnt = 0
    '''

    if (data == True):
        lane_alert = True
    else:
        lane_alert = False


    return lane_alert

def callback(face_sub, lane_sub):
    global health_warning
    health_warning = False
    flag1 = face(face_sub.data)
    flag2 = lane(lane_sub.data)
    print("callback")

    cap = cv2.VideoCapture("/dev/video0")
    success, img= cap.read()
    cv2.imshow("Result of detector", img)
    cv2.waitKey(1)
    if flag1 == True:
        if flag2 == True:
            health_warning = True
            print("first if")
            health_warning_pub.publish(health_warning)
            send_e_mail.send_mail()


        else:
            print("first false")

            health_warning_pub.publish(health_warning)
    else:
        health_warning_pub.publish(health_warning)

    if flag2 == True:
        if flag1 == True:
            print("second if")
            health_warning = True
            health_warning_pub.publish(health_warning)
            send_e_mail.send_mail()

        else:
            print("second false")
            health_warning_pub.publish(health_warning)

    else:
        health_warning_pub.publish(health_warning)



def decision_publisher():

    rospy.init_node('decision_sub_pub', anonymous=False)

    face_sub = message_filters.Subscriber('/face_alert', Bool)
    lane_sub = message_filters.Subscriber('/lane_alert', Bool)

    ts = message_filters.ApproximateTimeSynchronizer([face_sub, lane_sub], 10, 1, allow_headerless=True)
    ts.registerCallback(callback)


    rospy.spin()


if __name__ == '__main__':
    decision_publisher()

