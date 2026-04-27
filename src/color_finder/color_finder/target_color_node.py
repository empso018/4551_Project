import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Bool
import random


class TargetColorNode(Node):
    def __init__(self):
        super().__init__('target_color_node')

        self.colors = ['red', 'blue', 'green', 'yellow']
        self.current_color = random.choice(self.colors)

        self.publisher = self.create_publisher(String, '/target_color', 10)
        self.create_subscription(Bool, '/object_found', self.object_found_callback, 10)
        self.timer = self.create_timer(1.0, self.publish_color)

        self.switch_cooldown_seconds = 3.0
        self.last_switch_time = self.get_clock().now()

    def publish_color(self):
        msg = String()
        msg.data = self.current_color
        self.publisher.publish(msg)
        self.get_logger().info(f'Looking for: {msg.data}')

    def object_found_callback(self, msg):
        if not msg.data:
            return

        now = self.get_clock().now()
        elapsed = (now - self.last_switch_time).nanoseconds / 1e9

        if elapsed < self.switch_cooldown_seconds:
            return

        self.get_logger().info(f'Found {self.current_color}! Picking new color...')

        new_color = self.current_color
        while new_color == self.current_color:
            new_color = random.choice(self.colors)

        self.current_color = new_color
        self.last_switch_time = now


def main(args=None):
    rclpy.init(args=args)
    node = TargetColorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()