#!/usr/bin/env python3

import rospy
from std_msgs.msg import Bool


face_alert = False
lane_alert = False
cnt = 0

def face(data):
    # 10 sn'de bir uyku verisi geliyor.
    # 20 sn' içerisinde üst üste iki veri de uykulu olursa uyarı ver.

    if (data == False):
        cnt = 0

    else:
        cnt = cnt + 1

        if (cnt == 2):
            face_alert = True
            cnt = 0




def lane(data):

    if (data == False):
        cnt = 0

    else:
        cnt = cnt + 1

        if (cnt == 2):
            lane_alert = True
            cnt = 0






def decision_publisher():

    rospy.init_node('decision_sub_pub', anonymous=False)

    rospy.Subscriber('/face_alert', Bool, face)
    rospy.Subscriber('/lane_alert', Bool, lane)



    rospy.spin()


if __name__ == '__main__':
    decision_publisher()

