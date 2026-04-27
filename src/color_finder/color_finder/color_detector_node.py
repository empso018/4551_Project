import cv2
import rclpy
import numpy as np

from rclpy.node import Node
from std_msgs.msg import String, Bool
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point
from cv_bridge import CvBridge


class ColorDetectorNode(Node):
    def __init__(self):
        super().__init__('color_detector_node')

        self.bridge = CvBridge()
        self.target_color = 'red'
        self.last_logged_color = None

        self.create_subscription(String, '/target_color', self.color_callback, 10)
        self.create_subscription(Image, '/camera/image_raw', self.image_callback, 10)

        self.object_found_pub = self.create_publisher(Bool, '/object_found', 10)
        self.object_position_pub = self.create_publisher(Point, '/object_position', 10)

    def color_callback(self, msg):
        new_color = msg.data.lower()
        self.target_color = new_color

        if new_color == self.last_logged_color:
            return

        self.last_logged_color = new_color
        self.get_logger().info(f'Now searching for: {self.target_color}')

    def image_callback(self, msg):
        frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = self.get_color_mask(hsv, self.target_color)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        found_msg = Bool()
        position_msg = Point()

        if contours:
            largest = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(largest)

            if area > 500:
                x, y, w, h = cv2.boundingRect(largest)

                center_x = x + w / 2
                center_y = y + h / 2

                image_height, image_width = frame.shape[:2]

                position_msg.x = float(center_x / image_width)
                position_msg.y = float(center_y / image_height)
                position_msg.z = float(area)

                found_msg.data = True

                self.object_position_pub.publish(position_msg)
                self.object_found_pub.publish(found_msg)
                return

        found_msg.data = False
        self.object_found_pub.publish(found_msg)

    def get_color_mask(self, hsv, color):
        if color == 'red':
            lower1 = np.array([0, 100, 100])
            upper1 = np.array([10, 255, 255])
            lower2 = np.array([160, 100, 100])
            upper2 = np.array([179, 255, 255])
            return cv2.inRange(hsv, lower1, upper1) | cv2.inRange(hsv, lower2, upper2)

        if color == 'blue':
            lower = np.array([100, 100, 100])
            upper = np.array([130, 255, 255])
            return cv2.inRange(hsv, lower, upper)

        if color == 'green':
            lower = np.array([40, 80, 80])
            upper = np.array([80, 255, 255])
            return cv2.inRange(hsv, lower, upper)

        if color == 'yellow':
            lower = np.array([20, 100, 100])
            upper = np.array([35, 255, 255])
            return cv2.inRange(hsv, lower, upper)

        return np.zeros(hsv.shape[:2], dtype=np.uint8)


def main(args=None):
    rclpy.init(args=args)
    node = ColorDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
