import rclpy

from rclpy.node import Node
from std_msgs.msg import Bool
from geometry_msgs.msg import Point, Twist

# This drives the robot directly to the colored cube when it's seen by the camera
# Responsibilities are deliberately narrow:
# Subscribes to /object_found and /object_position from the color_detector_node
# Publishes velocity commands to /cmd_vel until the cube is large enough to indicate we reached it.
# Then it publishes /object_reached is True.
# cube_locator_node owns the /explore/resume coordination and color_approach does not.
# This helps us avoid the different nodes messing up navigation with conflicting commands.
class ColorApproachNode(Node):

    def __init__(self):
        super().__init__('color_approach_node')

        self.object_found = False
        self.object_position = None
        self.object_reached = False

        self.approach_area_threshold = 8000.0

        self.create_subscription(Bool, '/object_found', self.object_found_callback, 10)
        self.create_subscription(Point, '/object_position', self.object_position_callback, 10)

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.object_reached_pub = self.create_publisher(Bool, '/object_reached', 10)

        self.timer = self.create_timer(0.1, self.control_loop)

    def object_found_callback(self, msg):
        if msg.data and not self.object_found:
            self.get_logger().info('Target object in frame.')
            self.object_reached = False

        self.object_found = msg.data
        if not self.object_found:
            self.object_position = None

    def object_position_callback(self, msg):
        self.object_position = msg

    def control_loop(self):
        if not self.object_found:
            return
        self.approach_object()

    def approach_object(self):
        cmd = Twist()

        if self.object_position is None:
            cmd.angular.z = 0.3
            self.cmd_vel_pub.publish(cmd)
            return

        x = self.object_position.x
        area = self.object_position.z

        error = x - 0.5
        cmd.angular.z = -1.2 * error

        if area < self.approach_area_threshold:
            cmd.linear.x = 0.12
            self.cmd_vel_pub.publish(cmd)
            return

        cmd.linear.x = 0.0
        cmd.angular.z = 0.0
        self.cmd_vel_pub.publish(cmd)

        if not self.object_reached:
            self.object_reached = True
            reached_msg = Bool()
            reached_msg.data = True
            self.object_reached_pub.publish(reached_msg)
            self.get_logger().info('Reached target object.')


def main(args=None):
    rclpy.init(args=args)
    node = ColorApproachNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
