#!/usr/bin/env python3

import rospy
from std_msgs.msg import Bool




def face(data):


def lane(data);




def decision_publisher():

    rospy.init_node('decision_sub_pub', anonymous=False)


    rospy.Subscriber('/face_alert', Bool, face)
    rospy.Subscriber('/lane_alert', Bool, lane)

    rospy.spin()


if __name__ == '__main__':
    decision_publisher()

