#!/usr/bin/env python
import rospy
import numpy as np
from ar_track_alvar_msgs.msg import AlvarMarkers
from visualization_msgs.msg import Marker

# Flag used to ensure home goal is only sent once
packageOneFlag = False
packageTwoFlag = False
Q = [0,0,0,0]
boxInfo = [5,5,5,5]
#boxReference = {'ids': 0,1,2,3, 'width': 10,5,10,5, 'height': 5,5,5,5, 'depth': 5,10,5,10}


def quaternion_rotation_matrix(Q):
    """
    Covert a quaternion into a full three-dimensional rotation matrix.
 
    Input
    :param Q: A 4 element array representing the quaternion (q0,q1,q2,q3) 
 
    Output
    :return: A 3x3 element matrix representing the full 3D rotation matrix. 
             This rotation matrix converts a point in the local reference 
             frame to a point in the global reference frame.
    """
    # Extract the values from Q
    q0 = Q[0]
    q1 = Q[1]
    q2 = Q[2]
    q3 = Q[3]
     
    # First row of the rotation matrix
    r00 = 2 * (q0 * q0 + q1 * q1) - 1
    r01 = 2 * (q1 * q2 - q0 * q3)
    r02 = 2 * (q1 * q3 + q0 * q2)
     
    # Second row of the rotation matrix
    r10 = 2 * (q1 * q2 + q0 * q3)
    r11 = 2 * (q0 * q0 + q2 * q2) - 1
    r12 = 2 * (q2 * q3 - q0 * q1)
     
    # Third row of the rotation matrix
    r20 = 2 * (q1 * q3 - q0 * q2)
    r21 = 2 * (q2 * q3 + q0 * q1)
    r22 = 2 * (q0 * q0 + q3 * q3) - 1
     
    # 3x3 rotation matrix
    rot_matrix = np.array([[r00, r01, r02],
                           [r10, r11, r12],
                           [r20, r21, r22]])
                            
    return rot_matrix


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

def box_locator():

    """
    Function to create ROS nodes to utilize AlvarMarkers to check and parse the aruco markers' pose with respect to the camera

    Output
    :return: returns nothing
    """
	
    # Initialize ROS node called box_locator
    rospy.init_node('box_locator', anonymous=True)
    
	# Initialize subscriber to ar_pose_marker topic and call the callback function when data arrives
	rospy.Subscriber('ar_pose_marker', AlvarMarkers, callback)
    
	# Initialize ROS publisher to publish pose of markers 
    pub1 = rospy.Publisher('visualization_marker_1', Marker, queue_size=100)
    pub2 = rospy.Publisher('visualization_marker_2', Marker, queue_size=100)
    
	rate = rospy.Rate(20)
    
	# Loop to keep the nodes going until crtl-c is pressed
    while not rospy.is_shutdown():
		global boxInfo
		# Check if the 0 or 1 marker ID (corresponding to 1st package) is detected 
		if (boxInfo[0]==0 or boxInfo[0]==1):

			global packageOneFlag
			
			# Set the packageOneFlag to True to ensure detection only happens once 
			if (packageOneFlag==False):
				packageOneFlag = True

				# Obtain rotation matrix 
				rotM = quaternion_rotation_matrix(Q)
				
				# Identify position of box centre wrt to top and side face marker
				boxGeo0 = np.array([[0.022], [0], [-0.05]])
				boxGeo1 = np.array([[0],[0],[-0.1]])
				
				# Declare a new Marker object
				marker1=Marker()
				marker1.header.stamp=rospy.get_rostime()

				# Ensure that the marker is plotted wrt to map frame
				marker1.header.frame_id='map'

				# Calculate correct position by taking aruco pose and translating it to box centre units
				if (boxInfo[0]==0):
					marker1.pose.position.x = boxInfo[1]+np.dot(rotM[0,:],boxGeo0)
					marker1.pose.position.y = boxInfo[2]+np.dot(rotM[1,:],boxGeo0)
					marker1.pose.position.z = boxInfo[3]+np.dot(rotM[2,:],boxGeo0)
				if (boxInfo[0]==1):
					marker1.pose.position.x = boxInfo[1]+np.dot(rotM[0,:],boxGeo1)
					marker1.pose.position.y = boxInfo[2]+np.dot(rotM[1,:],boxGeo1)
					marker1.pose.position.z = boxInfo[3]+np.dot(rotM[2,:],boxGeo1)
				
				marker1.pose.orientation.x=Q[0]
				marker1.pose.orientation.y=Q[1]
				marker1.pose.orientation.z=Q[2]
				marker1.pose.orientation.w=Q[3]

				# Set colour and transparency
				marker1.color.g=0
				marker1.color.r=0
				marker1.color.b=255
				marker1.color.a=1
				marker1.scale.x=0.05
				marker1.scale.y=0.05
				marker1.scale.z=0.05
				pub1.publish(marker1)
				
		# Check if the 2 or 3 marker ID (corresponding to 2nd package) is detected 		
		elif (boxInfo[0]==2 or boxInfo[0]==3):
			
			global packageTwoFLag

			# Set the packageTwoFlag to True to ensure detection only happens once 
			if (packageTwoFlag==False):
				packageTwoFlag = True
				
				# Obtain rotation matrix 
				rotM = quaternion_rotation_matrix(Q)

				# Identify position of box centre wrt to top and side face marker
				boxGeo2 = np.array([[0.022], [0], [-0.05]])
				boxGeo3 = np.array([[0],[0],[-0.1]])
				
				# Declare a new Marker object
				marker2=Marker()
				marker2.header.stamp=rospy.get_rostime()

				# Ensure that the marker is plotted wrt to map frame
				marker2.header.frame_id='map'
				
				# Calculate correct position by taking aruco pose and translating it to box centre units
				if (boxInfo[0]==2):
					marker2.pose.position.x = boxInfo[1]+np.dot(rotM[0,:],boxGeo2)
					marker2.pose.position.y = boxInfo[2]+np.dot(rotM[1,:],boxGeo2)
					marker2.pose.position.z = boxInfo[3]+np.dot(rotM[2,:],boxGeo2)
				if (boxInfo[0]==3):
					marker2.pose.position.x = boxInfo[1]+np.dot(rotM[0,:],boxGeo3)
					marker2.pose.position.y = boxInfo[2]+np.dot(rotM[1,:],boxGeo3)
					marker2.pose.position.z = boxInfo[3]+np.dot(rotM[2,:],boxGeo3)
				
				marker2.pose.orientation.x=Q[0]
				marker2.pose.orientation.y=Q[1]
				marker2.pose.orientation.z=Q[2]
				marker2.pose.orientation.w=Q[3]
				marker2.color.g=0
				marker2.color.r=255
				marker2.color.b=0
				marker2.color.a=1
				marker2.scale.x=0.05
				marker2.scale.y=0.05
				marker2.scale.z=0.05
				pub2.publish(marker2)
		
		rate.sleep()

if __name__ == '__main__':
    try:
        box_locator()
    except rospy.ROSInterruptException:
        pass
