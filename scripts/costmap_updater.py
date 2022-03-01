#!/usr/bin/env python
import rospy
from std_msgs.msg import String, Int32
from geometry_msgs.msg import PoseStamped
from actionlib_msgs.msg import GoalID
from move_base_msgs.msg import MoveBaseActionGoal
from multiprocessing import Process, Pipe
import thread, time

#flag used to ensure home goal is only sent once
flag = False

#ros return_home subscriber callback function
#Checks if data has been published to move_base/cancel topic and changes flag
def callback(data):
        if (data.id==''):
		global flag
		flag = True	

#function to send the robot the origin as a goal when exploration is complete
def return_home():
    #initialize ros subscriber to move_base/cancel
    rospy.init_node('return_home', anonymous=True)
    rospy.Subscriber('move_base/cancel', GoalID, callback)
    #initialize ros publisher to move_base_simple/goal
    pub = rospy.Publisher('move_base_simple/goal', PoseStamped, queue_size=100)
    rate = rospy.Rate(20)
    #loop to keep the nodes going
    while not rospy.is_shutdown():
    #check is mapping is complete (flag)
	if (flag==True):
		#if mapping is complete, let user know and then return to home
		print("EXPLORATION STOPPED")
		goal = PoseStamped()
		goal.header.stamp=rospy.get_rostime()
		goal.header.frame_id='map'
		goal.pose.position.x=0
		goal.pose.position.y=0
		goal.pose.position.z=0
		goal.pose.orientation.w=1.0
		rospy.loginfo(goal)
		pub.publish(goal)
		global flag
		flag = False   	
	rate.sleep()

if __name__ == '__main__':
    try:
        return_home()
    except rospy.ROSInterruptException:
        pass