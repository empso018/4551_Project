import cv2
import rclpy
import pytesseract
import time

from sensor_msgs.msg import Image
from rclpy.node import Node
from cv_bridge import CvBridge

class SubscriberNode(Node):
    def __init__(self):
        super().__init__('subscriber_node')

        self.bridgeObject = CvBridge()

        self.topicNameFrames='topic_camera_image'

        self.queueSize=20

        self.subscription = self.create_subscription(
            Image, 
            self.topicNameFrames, 
            self.listener_callbackFunction, 
            self.queueSize
        )

        self.ocr_interval = 1.0 / 5.0
        self.last_processed_time = 0.0

    def listener_callbackFunction(self, imageMessage):
        # self.get_logger().info('The image frame is recieved')

        now = time.time()

        openCVImage = self.bridgeObject.imgmsg_to_cv2(imageMessage)

        cv2.imshow("Camera video", openCVImage)
        cv2.waitKey(1)

        if (now - self.last_processed_time < self.ocr_interval):
            return

        self.last_processed_time = now

        img_rgb = cv2.cvtColor(openCVImage, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(img_rgb)
        self.get_logger().info(f'Text: {text}')

        

def main(args=None):
    rclpy.init(args=args)
    subscriberNode = SubscriberNode()
    rclpy.spin(subscriberNode)
    subscriberNode.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
