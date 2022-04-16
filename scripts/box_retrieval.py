#!/usr/bin/env python
import rospy
from geometry_msgs.msg import PoseStamped
from std_msgs.msg import Float32, Int32
from ar_track_alvar_msgs.msg import AlvarMarkers
from actionlib_msgs.msg import GoalStatusArray, GoalID
from time import sleep

#flag used to ensure home goal is only sent once
status_goal = 10
counterFlag = False
collectionFlag = True
flag = True
counter = 0
Q = [0,0,0,0]
boxInfo = [5,5,5,5]
explorationFlag = False

def mappingCallback(data):
	"""
	Sets explorationFlag to True when exploration is terminated

    Input
    :param data: message on move_base/cancel 
 
    Output
    :return: returns nothing
    """

	if (data.id==''):
		global explorationFlag
		explorationFlag = True	

def counterback(data):
	"""
	Sets counterFlag to True when 2 boxes have been detected

    Input
    :param data: message on box_counter 
 
    Output
    :return: returns nothing
	"""
	
	if (data.data>=2):
		global counterFlag
		counterFlag = True

def callback(data):
	"""
    Callback function to check and parse the aruco markers' pose with respect to the camera
 
    Input
    :param data: data of the message received on a topic that is of hierarchial structure
 
    Output
    :return: 
    """

	if(data.markers[0].id!=''):
		global boxInfo
		boxInfo[0] = data.markers[0].id
		boxInfo[1] = data.markers[0].pose.pose.position.x
		boxInfo[2] = data.markers[0].pose.pose.position.y
		boxInfo[3] = data.markers[0].pose.pose.position.z
		global Q
		Q[0] = data.markers[0].pose.pose.orientation.x
		Q[1] = data.markers[0].pose.pose.orientation.y
		Q[2] = data.markers[0].pose.pose.orientation.z
		Q[3] = data.markers[0].pose.pose.orientation.w

def status_callback(data):
	"""
    Callback function to save the status of goals sent to move_base
 
    Input
    :param data: data of the message received on topic move_base/status
 
    Output
    :return: 
    """
	if (data!=None):
		global status_goal
		status_goal = data.status_list[len(data.status_list)-1].status

def return_home():
	"""
    Function to create ROS node that sends the robot to the last detected package, then to start pose.
	This happens when mapping and box exploration are complete

    Output
    :return: returns nothing
    """
    # Initialize ros node
	rospy.init_node('box_retrieval', anonymous=True)
    
	# Create a subscribers to move_base/cancel (mapping), box_counter, ar_pose_marker, and move_base/status
	rospy.Subscriber('move_base/cancel', GoalID, mappingCallback)
	rospy.Subscriber('box_counter', Int32, counterback)
	rospy.Subscriber('ar_pose_marker', AlvarMarkers, callback)
	rospy.Subscriber('move_base/status', GoalStatusArray, status_callback)

    
	# Initialize ROS publisher to servo_angle and move_base_simple/goal
	pubServo = rospy.Publisher('servo_angle', Float32, queue_size=20)
	pub = rospy.Publisher('move_base_simple/goal', PoseStamped, queue_size=20)
    
	# Set node publish rate
	rate = rospy.Rate(20)
    
	# Loop to keep the nodes going
	while not rospy.is_shutdown():

		global flag, counterFlag, counter, collectionFlag, explorationFlag
	# Check is mapping and box exploration are complete
		if (counterFlag==True and collectionFlag==True and flag==True and explorationFlag==True):
		# If everything is complete, publish package goal
			goal = PoseStamped()
			goal.header.stamp=rospy.get_rostime()
			goal.header.frame_id='map'
			goal.pose.position.x=boxInfo[1]
			goal.pose.position.y=boxInfo[2]
			goal.pose.orientation.w=1.0
			rospy.loginfo(goal)
			pub.publish(goal)
			
			# Counter to publish goal 20 times to ensure it overrides the path planning algorithm
			counter+=1
			if(counter>=20):
				flag = False

		#Checks if goal has been reached. If it has, then lift package retrieval system
		if (status_goal==3 and collectionFlag==True and flag==False and explorationFlag==True):
			collectionFlag  = False
			flag = True
			pubServo.publish(-0.2) #where servo angle is mapped from -1 to 1
			counter = 0
		
		# If package has been retieved, publish home goal
		if (counterFlag==True and collectionFlag==False and flag==True and explorationFlag==True):
			goal = PoseStamped()
			goal.header.stamp=rospy.get_rostime()
			goal.header.frame_id='map'
			goal.pose.position.x=0
			goal.pose.position.y=0
			goal.pose.position.z=0
			goal.pose.orientation.w=1.0
			rospy.loginfo(goal)
			pub.publish(goal)
			
			# Counter to publish goal 20 times to ensure it overrides the path planning algorithm
			counter+=1
			if(counter>=20):
				flag = False
				
		# If home goal has been reached, lower package retrieval system
		if (status_goal==3 and collectionFlag==False and flag==False and explorationFlag==True):
			pubServo.publish(0.2)
				
		rate.sleep()

if __name__ == '__main__':
    try:
        return_home()
    except rospy.ROSInterruptException:
        pass
