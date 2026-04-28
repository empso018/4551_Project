import math
import time
import rclpy

from rclpy.node import Node
from rclpy.action import ActionClient

from std_msgs.msg import Bool
from geometry_msgs.msg import PoseStamped, Point, Twist
from nav2_msgs.action import NavigateToPose


class WaypointSearchNode(Node):
    def __init__(self):
        super().__init__('waypoint_search_node')

        self.object_found = False
        self.object_position = None
        self.object_reached = False

        self.current_goal_index = 0
        self.goal_in_progress = False
        self.current_goal_handle = None
        self.next_goal_time = 0.0
        self.last_log_times = {}

        self.approach_area_threshold = 8000.0

        self.waypoints = [
            (1.0, 0.0, 0.0),
            (1.0, 1.0, 1.57),
            (0.0, 1.0, 3.14),
            (-1.0, 1.0, 3.14),
            (-1.0, 0.0, -1.57),
            (0.0, -1.0, 0.0),
        ]

        self.create_subscription(Bool, '/object_found', self.object_found_callback, 10)
        self.create_subscription(Point, '/object_position', self.object_position_callback, 10)

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.object_reached_pub = self.create_publisher(Bool, '/object_reached', 10)

        self.nav_client = ActionClient(
            self,
            NavigateToPose,
            'navigate_to_pose'
        )

        self.timer = self.create_timer(0.2, self.control_loop)

    def object_found_callback(self, msg):
        if msg.data and not self.object_found:
            self.get_logger().info('Target object found. Canceling Nav2 waypoint search.')
            self.object_reached = False
            self.cancel_current_goal()

        self.object_found = msg.data
        if not self.object_found:
            self.object_position = None

    def object_position_callback(self, msg):
        self.object_position = msg

    def control_loop(self):
        if self.object_found:
            self.approach_object()
            return

        if self.goal_in_progress:
            return

        if time.monotonic() < self.next_goal_time:
            return

        if not self.nav_client.wait_for_server(timeout_sec=1.0):
            self.log_throttled('warn', 'nav_wait', 'Waiting for Nav2 action server...', 5.0)
            return

        waypoint = self.waypoints[self.current_goal_index]
        self.send_goal(*waypoint)

    def send_goal(self, x, y, yaw):
        goal_msg = NavigateToPose.Goal()

        goal_msg.pose = PoseStamped()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()

        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.position.z = 0.0

        qz, qw = self.yaw_to_quaternion(yaw)
        goal_msg.pose.pose.orientation.z = qz
        goal_msg.pose.pose.orientation.w = qw

        self.get_logger().info(f'Sending waypoint goal: x={x}, y={y}, yaw={yaw}')

        self.goal_in_progress = True

        future = self.nav_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )

        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.log_throttled('warn', 'goal_rejected', 'Waypoint goal rejected by Nav2.', 5.0)
            self.goal_in_progress = False
            self.next_goal_time = time.monotonic() + 2.0
            return

        self.current_goal_handle = goal_handle
        self.get_logger().info('Waypoint goal accepted.')
        self.current_goal_index = (self.current_goal_index + 1) % len(self.waypoints)

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_callback)

    def goal_result_callback(self, future):
        self.get_logger().info('Waypoint finished.')
        self.goal_in_progress = False
        self.current_goal_handle = None
        self.next_goal_time = time.monotonic() + 1.0

    def cancel_current_goal(self):
        if self.current_goal_handle is not None:
            self.current_goal_handle.cancel_goal_async()
            self.goal_in_progress = False
            self.current_goal_handle = None
            self.next_goal_time = time.monotonic() + 1.0

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
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0
            if not self.object_reached:
                self.object_reached = True
                reached_msg = Bool()
                reached_msg.data = True
                self.object_reached_pub.publish(reached_msg)
                self.get_logger().info('Reached target object.')

        self.cmd_vel_pub.publish(cmd)

    def feedback_callback(self, feedback_msg):
        distance = feedback_msg.feedback.distance_remaining
        self.log_throttled('info', 'distance', f'Distance remaining: {distance:.2f} m', 2.0)

    def yaw_to_quaternion(self, yaw):
        qz = math.sin(yaw / 2.0)
        qw = math.cos(yaw / 2.0)
        return qz, qw

    def log_throttled(self, level, key, message, period):
        now = time.monotonic()
        last_time = self.last_log_times.get(key, 0.0)
        if now - last_time < period:
            return

        self.last_log_times[key] = now

        # Updated this to avoid rclpy severity error present in some package versions (like mine)
        logger = self.get_logger()
        if level == 'info':
            logger.info(message)
        elif level == 'warn':
            logger.warn(message)
        elif level == 'error':
            logger.error(message)
        elif level == 'debug':
            logger.debug(message)


def main(args=None):
    rclpy.init(args=args)
    node = WaypointSearchNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
