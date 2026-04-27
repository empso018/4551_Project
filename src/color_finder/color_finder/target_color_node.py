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
        self.create_subscription(Bool, '/object_reached', self.object_reached_callback, 10)
        self.timer = self.create_timer(1.0, self.publish_color)

    def publish_color(self):
        msg = String()
        msg.data = self.current_color
        self.publisher.publish(msg)
        self.get_logger().info(f'Looking for: {msg.data}')

    def object_reached_callback(self, msg):
        if not msg.data:
            return

        self.get_logger().info(f'Reached {self.current_color}! Picking new color...')

        new_color = self.current_color
        while new_color == self.current_color:
            new_color = random.choice(self.colors)

        self.current_color = new_color


def main(args=None):
    rclpy.init(args=args)
    node = TargetColorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
