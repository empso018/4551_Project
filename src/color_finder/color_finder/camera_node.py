import cv2
import rclpy

from sensor_msgs.msg import Image
from rclpy.node import Node
from cv_bridge import CvBridge

class CameraNode(Node):
    def __init__(self):
        super().__init__('camera_node')

        self.cameraDeviceNumber=0
        self.camera = cv2.VideoCapture(self.cameraDeviceNumber)

        self.bridgeObject = CvBridge()

        self.topicNameFrames='/camera_image'

        self.queueSize=20

        self.publisher = self.create_publisher(Image, self.topicNameFrames, self.queueSize)

        self.periodCommunication = 0.02

        # calls timer_callbackFunction every periodCommunication seconds
        self.timer = self.create_timer(self.periodCommunication, self.timer_callbackFunction)

        # number of images published
        # self.i = 0

    def timer_callbackFunction(self):

        success, frame = self.camera.read()
        frame = cv2.resize(frame, (820,640), interpolation=cv2.INTER_CUBIC)

        if success == True:
            Ros2ImageMessage = self.bridgeObject.cv2_to_imgmsg(frame)
            self.publisher.publish(Ros2ImageMessage)

        # self.get_logger().info('Publishing image number %d' % self.i)
        # self.i += 1

def main(args=None):
    rclpy.init(args=args)
    publisherObject = CameraNode()
    rclpy.spin(publisherObject)
    publisherObject.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
