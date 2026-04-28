import cv2
import rclpy
import numpy as np

from rclpy.node import Node
from std_msgs.msg import String, Bool, Header
from sensor_msgs.msg import Image
from geometry_msgs.msg import Point, PointStamped
from cv_bridge import CvBridge


COLORS = ('red', 'blue', 'green', 'yellow')

MIN_AREA = 500.0


# This detects colored cubes inside the camera frame.
# There are 2 output paths:
# /object_found, /object_position fires only for the currently targeted color. This is used by color_approach_node
# /cube_sightings/[COLOR] fires when any color is seen, and lets cube_locator_node remember previously seen cubes
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

        self.sighting_pubs = {
            color: self.create_publisher(PointStamped, f'/cube_sightings/{color}', 10)
            for color in COLORS
        }

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

        image_height, image_width = frame.shape[:2]

        target_detection = None

        for color in COLORS:
            detection = self._detect(hsv, color, image_width, image_height)
            if detection is None:
                continue

            self._publish_sighting(msg.header, color, detection)

            if color == self.target_color:
                target_detection = detection

        self._publish_target_status(target_detection)

    def _detect(self, hsv, color, image_width, image_height):
        mask = self.get_color_mask(hsv, color)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return None

        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        if area <= MIN_AREA:
            return None

        x, y, w, h = cv2.boundingRect(largest)
        center_x = x + w / 2.0
        center_y = y + h / 2.0

        return {
            'norm_x': float(center_x / image_width),
            'norm_y': float(center_y / image_height),
            'area': float(area),
        }

    def _publish_sighting(self, image_header, color, detection):
        msg = PointStamped()
        msg.header = Header()
        msg.header.stamp = image_header.stamp
        msg.header.frame_id = image_header.frame_id
        msg.point.x = detection['norm_x']
        msg.point.y = detection['norm_y']
        msg.point.z = detection['area']
        self.sighting_pubs[color].publish(msg)

    def _publish_target_status(self, target_detection):
        found_msg = Bool()
        if target_detection is None:
            found_msg.data = False
            self.object_found_pub.publish(found_msg)
            return

        position_msg = Point()
        position_msg.x = target_detection['norm_x']
        position_msg.y = target_detection['norm_y']
        position_msg.z = target_detection['area']

        found_msg.data = True
        self.object_position_pub.publish(position_msg)
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
