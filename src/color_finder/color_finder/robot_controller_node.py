import rclpy

from rclpy.node import Node
from std_msgs.msg import Bool
from geometry_msgs.msg import Point, Twist


class RobotControllerNode(Node):
    def __init__(self):
        super().__init__('robot_controller_node')

        self.object_found = False
        self.object_position = None

        self.create_subscription(Bool, '/object_found', self.found_callback, 10)
        self.create_subscription(Point, '/object_position', self.position_callback, 10)

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)

        self.timer = self.create_timer(0.1, self.control_loop)

    def found_callback(self, msg):
        self.object_found = msg.data

    def position_callback(self, msg):
        self.object_position = msg

    def control_loop(self):
        cmd = Twist()

        if not self.object_found or self.object_position is None:
            cmd.angular.z = 0.4
            cmd.linear.x = 0.0
            self.cmd_vel_pub.publish(cmd)
            return

        x = self.object_position.x
        area = self.object_position.z

        error = x - 0.5

        cmd.angular.z = -1.0 * error

        if area < 5000:
            cmd.linear.x = 0.15
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        self.cmd_vel_pub.publish(cmd)


def main(args=None):
    rclpy.init(args=args)
    node = RobotControllerNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()