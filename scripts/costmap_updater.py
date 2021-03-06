#!/usr/bin/env python
from operator import truediv
import rospy, math
from visualization_msgs.msg import Marker
from ar_track_alvar_msgs.msg import AlvarMarkers
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Int32
from actionlib_msgs.msg import GoalID

# Initialize boxes and time variables for creating fake laserscans
# Note: the boxes are initialized at non-zero values in order to appear outside the map such that costmap cannot prematurely process the boxes
box1=[0,19,6]
time1=[0.0,0.0]
box2=[0,19,6]
time2=[0.0,0.0]
counterFlag = True
explorationFlag = True

def mappingCallback(data):
	"""
	Sets explorationFlag to False when exploration is terminated

    Input
    :param data: message on move_base/cancel 
 
    Output
    :return: returns nothing
    """

	if (data.id==''):
		global explorationFlag
		explorationFlag = False	

def counterback(data):
	"""
	Sets counterFlag to False when 2 boxes have been detected

    Input
    :param data: message on box_counter 
 
    Output
    :return: returns nothing
	"""
	
	if (data.data>=2):
		global counterFlag
		counterFlag = False

def callback(data):
	""" Callback function that processes AlvarMarkers messages to compute box dimensions

	Args:
	data (AlvarMarker): Message of AlvarMarker  
	"""
	global box1, time1, box2, time2

	# compute the positions of the boxes with respect to the base_scan coordinate system
	# Marker id 0 and 1 is associated with first box, marker id 2 and 3 is associated with the second box
	if (data.markers[0].id==0 or data.markers[0].id==1):
		box1[0]=math.atan2(data.markers[0].pose.pose.position.y,data.markers[0].pose.pose.position.x)
		box1[1]=math.sqrt(data.markers[0].pose.pose.position.x*data.markers[0].pose.pose.position.x+data.markers[0].pose.pose.position.y*data.markers[0].pose.pose.position.y)
		box1[2]=data.markers[0].id
	if (data.markers[0].id==2 or data.markers[0].id==3):
		box2[0]=math.atan2(data.markers[0].pose.pose.position.y,data.markers[0].pose.pose.position.x)
		box2[1]=math.sqrt(data.markers[0].pose.pose.position.x*data.markers[0].pose.pose.position.x+data.markers[0].pose.pose.position.y*data.markers[0].pose.pose.position.y)
		box2[2]=data.markers[0].id

# Function to update costmap regularly 
def costmap_updater():
	"""
    Function to create ROS node that publishes fake laser scans of the packages.
	This happens until mapping and box exploration are complete

    Output
    :return: returns nothing
    """

    # Initialize a node to update costmap
	rospy.init_node('costmap_updater', anonymous=True)
	
	# Initialize subscriber to move_base/cancel (mapping), box_counter, and box_local (ar_track) topics
	rospy.Subscriber('move_base/cancel', GoalID, mappingCallback)
	rospy.Subscriber('box_counter', Int32, counterback)
	rospy.Subscriber('box_local', AlvarMarkers, callback)

    # Initialize publisher to scan_1 and scan_2 topics
	pub1 = rospy.Publisher('scan_1', LaserScan, queue_size = 10)
	pub2 = rospy.Publisher('scan_2', LaserScan, queue_size = 10)
	
	# Set node rate
	rate = rospy.Rate(1)
    
	while not rospy.is_shutdown():
		global box1, time1, box2, time2, counterFlag

		# Only publish scans during exploration (until two boxes have been found and mapping complete)
		# Stopping the scan publishers allows them to be cleared from costmap
		# This allows the robot to retrieve the package
		if (counterFlag or explorationFlag):
			# Create a LaserScan message and publish to box1_scan topic
			box1_scan=LaserScan()
			box1_scan.header.stamp=rospy.get_rostime()
			box1_scan.header.frame_id='base_scan'
			box1_scan.angle_min=box1[0]
			box1_scan.angle_max=box1[0]+0.0001
			box1_scan.range_min=0
			box1_scan.range_max=20
			box1_scan.angle_increment=0.0001
			box1_scan.time_increment=0.0001
			box1_scan.ranges=[box1[1]+0.025,box1[1]+0.025]
			pub1.publish(box1_scan)

			box2_scan=LaserScan()
			box2_scan.header.stamp=rospy.get_rostime()
			box2_scan.header.frame_id='base_scan'
			box2_scan.angle_min=box2[0]
			box2_scan.angle_max=box2[0]+0.0001
			box2_scan.range_min=0
			box2_scan.range_max=20
			box2_scan.angle_increment=0.0001
			box2_scan.time_increment=0.0001
			box2_scan.ranges=[box2[1]+0.025,box2[1]+0.025]
			pub2.publish(box2_scan)
	rate.sleep()

if __name__ == '__main__':
    try:
        costmap_updater()
    except rospy.ROSInterruptException:
        pass
