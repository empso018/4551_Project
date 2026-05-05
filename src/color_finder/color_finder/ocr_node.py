import cv2
import rclpy
import pytesseract
import time
import re

from sensor_msgs.msg import Image
from rclpy.node import Node
from cv_bridge import CvBridge
from std_msgs.msg import String

class SubscriberNode(Node):
    def __init__(self):
        super().__init__('ocr_node')

        self.bridgeObject = CvBridge()

        self.topicNameFrames='/camera_image'

        self.queueSize=20

        self.subscription = self.create_subscription(
            Image, 
            self.topicNameFrames, 
            self.listener_callbackFunction, 
            self.queueSize
        )

        self.topicNameText = '/ocr_text'

        self.publisher = self.create_publisher(
            String,
            self.topicNameText,
            self.queueSize
        )

        self.ocr_interval = 1.0 / 5.0
        self.last_processed_time = 0.0

    def listener_callbackFunction(self, imageMessage):
        # self.get_logger().info('The image frame is recieved')

        openCVImage = self.bridgeObject.imgmsg_to_cv2(imageMessage)

        cv2.imshow("Camera video", openCVImage)
        cv2.waitKey(1)

        now = time.time()

        if (now - self.last_processed_time < self.ocr_interval):
            return

        self.last_processed_time = now

        img_rgb = cv2.cvtColor(openCVImage, cv2.COLOR_BGR2RGB)
        text = pytesseract.image_to_string(img_rgb)

        cleaned_text = text.strip()
        # Remove extra whitespace such as newlines
        cleaned_text = re.sub(r'\s', ' ', cleaned_text)
        # Remove non alphabetical characters
        cleaned_text = re.sub(r'[^a-zA-Z]', '', cleaned_text)

        msg = String()
        msg.data = cleaned_text

        self.publisher.publish(msg)
        # self.get_logger().info(f'Text: {cleaned_text}')

        

def main(args=None):
    rclpy.init(args=args)
    subscriberNode = SubscriberNode()
    rclpy.spin(subscriberNode)
    subscriberNode.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
