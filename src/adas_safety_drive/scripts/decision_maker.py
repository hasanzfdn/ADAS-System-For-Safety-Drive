#!/usr/bin/env python3

import rospy
from std_msgs.msg import Bool
from std_msgs.msg import String
import message_filters



face_alert = False
lane_alert = False
sleep_publisher = rospy.Publisher('sleep_warning', String, queue_size = 1)
drive_publisher = rospy.Publisher('drive_warning', String, queue_size = 1)
health_warning_pub = rospy.Publisher('health_situation', Bool, queue_size = 1)
health_warning = False
face_cnt = 0
lane_cnt = 0

def face(data):
    global face_cnt, face_alert
    # 10 sn'de bir uyku verisi geliyor.
    # 20 sn' içerisinde üst üste iki veri de uykulu olursa uyarı ver.

    if (data == False):
        face_cnt = 0

    else:
        face_cnt = face_cnt + 1
        print('dvsdfgvsfdbsrgdsfdgjhdf')
        if (face_cnt == 1):

            sleep_publisher.publish('PLEASE TAKE A COFFEE BREAK FOR YOUR HEALTH')

        if (face_cnt == 2):
            face_alert = True
            face_cnt = 0

    return face_alert



def lane(data):
    global lane_cnt, lane_alert
    # 10 sn'de bir lane verisi geliyor.
    # 20 sn' içerisinde üst üste iki veri de sıkıntılı olursa uyarı ver.

    if (data == False):
        lane_cnt = 0

    else:
        lane_cnt = lane_cnt + 1

        if (lane_cnt == 1):
            drive_publisher.publish('PLEASE KEEP YOUR VEHICLE WITHIN THE LANES FOR YOUR HEALTH')

        if (lane_cnt == 2):
            lane_alert = True
            lane_cnt = 0

    return lane_alert

def callback(face_sub, lane_sub):
    global health_warning
    flag1 = face(face_sub.data)
    flag2 = lane(lane_sub.data)

    if flag1 == True and flag2 == True:
        health_warning = True
        health_warning_pub.publish(health_warning)

    else:
        health_warning_pub.publish(health_warning)



def decision_publisher():

    rospy.init_node('decision_sub_pub', anonymous=False)

    face_sub = message_filters.Subscriber('/face_alert', Bool)
    lane_sub = message_filters.Subscriber('/lane_alert', Bool)

    ts = message_filters.ApproximateTimeSynchronizer([face_sub, lane_sub], 10, 0.2, allow_headerless=True)
    ts.registerCallback(callback)

    rospy.spin()


if __name__ == '__main__':
    decision_publisher()

