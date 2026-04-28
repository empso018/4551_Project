import math

import rclpy
import tf2_ros
import tf2_geometry_msgs  # noqa: F401  (registers PointStamped transform)

from rclpy.action import ActionClient
from rclpy.duration import Duration
from rclpy.node import Node

from geometry_msgs.msg import PointStamped, PoseStamped
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool, ColorRGBA, String
from visualization_msgs.msg import Marker, MarkerArray
from nav2_msgs.action import NavigateToPose


COLORS = ('red', 'blue', 'green', 'yellow')

COLOR_RGBA = {
    'red':    ColorRGBA(r=1.0, g=0.0, b=0.0, a=1.0),
    'blue':   ColorRGBA(r=0.0, g=0.3, b=1.0, a=1.0),
    'green':  ColorRGBA(r=0.0, g=1.0, b=0.0, a=1.0),
    'yellow': ColorRGBA(r=1.0, g=1.0, b=0.0, a=1.0),
}

CAMERA_H_FOV = math.radians(62.0)

# This maintains records of the colored cube positions, so the robot can return to them when
# they become the target color.
# Three responsibilities:
# 1. Build memory: convert /cube_sightings/<color> + /scan into map-frame positions.
# 2. Visualize: publish /cube_locations MarkerArray for Foxglove.
# 3. Pursue: when /target_color changes to a color in memory, pause explore_lite and send Nav2 directly to the remembered position. 
#    color_approach_node takes over for the final approach when the cube enters camera frame.
class CubeLocatorNode(Node):

    def __init__(self):
        super().__init__('cube_locator_node')

        self.cube_positions = {}
        self.latest_scan = None
        self.current_target = None
        self.pursuit_goal_handle = None
        # True between /object_found True and /object_reached or sight lost.
        # When sight is lost mid-approach, we re-issue the pursuit goal rather
        # than resuming exploration; this prevents explore_lite from preempting
        # us back to a frontier when the robot was almost at the remembered cube.
        self.target_in_view = False

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)
        for color in COLORS:
            self.create_subscription(
                PointStamped,
                f'/cube_sightings/{color}',
                lambda msg, c=color: self.sighting_callback(msg, c),
                10,
            )

        self.create_subscription(String, '/target_color', self.target_callback, 10)
        self.create_subscription(Bool, '/object_found', self.object_found_callback, 10)
        self.create_subscription(Bool, '/object_reached', self.object_reached_callback, 10)

        self.markers_pub = self.create_publisher(MarkerArray, '/cube_locations', 10)
        self.explore_resume_pub = self.create_publisher(Bool, '/explore/resume', 10)
        self.nav_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

        self.create_timer(1.0, self.publish_markers)

    def scan_callback(self, msg: LaserScan):
        self.latest_scan = msg

    def sighting_callback(self, msg: PointStamped, color: str):
        if self.latest_scan is None:
            return

        scan = self.latest_scan

        normalized_x = msg.point.x
        bearing = -(normalized_x - 0.5) * CAMERA_H_FOV

        wrapped = bearing
        if wrapped < scan.angle_min:
            wrapped += 2.0 * math.pi
        if wrapped > scan.angle_max:
            wrapped -= 2.0 * math.pi

        index = int((wrapped - scan.angle_min) / scan.angle_increment)
        if index < 0 or index >= len(scan.ranges):
            return

        distance = scan.ranges[index]
        if not math.isfinite(distance):
            return
        if distance < scan.range_min or distance > scan.range_max:
            return

        local = PointStamped()
        local.header.frame_id = scan.header.frame_id
        local.header.stamp = scan.header.stamp
        local.point.x = distance * math.cos(bearing)
        local.point.y = distance * math.sin(bearing)
        local.point.z = 0.0

        try:
            map_point = self.tf_buffer.transform(
                local,
                'map',
                timeout=Duration(seconds=0.5),
            )
        except (
            tf2_ros.LookupException,
            tf2_ros.ConnectivityException,
            tf2_ros.ExtrapolationException,
        ):
            return

        first_sighting = color not in self.cube_positions
        self.cube_positions[color] = map_point

        if first_sighting:
            self.get_logger().info(
                f'Located {color} cube at '
                f'({map_point.point.x:.2f}, {map_point.point.y:.2f}) in map frame.'
            )
            if color == self.current_target and self.pursuit_goal_handle is None:
                self.start_pursuit(color)

    def target_callback(self, msg: String):
        new_target = msg.data.lower()
        if new_target == self.current_target:
            return

        self.current_target = new_target
        self.cancel_pursuit()

        if new_target in self.cube_positions:
            self.start_pursuit(new_target)
        else:
            # No memory for the new target; let explore_lite drive again.
            self.set_explore_resume(True)

    def object_found_callback(self, msg: Bool):
        was_in_view = self.target_in_view
        self.target_in_view = msg.data

        if msg.data:
            # Camera has acquired a target cube; color_approach is taking over
            # via /cmd_vel. Cancel pursuit so Nav2 doesn't fight, and ensure
            # explore stays paused.
            self.cancel_pursuit()
            self.set_explore_resume(False)
            return

        if was_in_view:
            # Just lost sight without reaching. Don't resume exploration —
            # we still want this cube. Re-issue pursuit so Nav2 drives us
            # back toward the remembered position.
            if (
                self.current_target in self.cube_positions
                and self.pursuit_goal_handle is None
            ):
                self.start_pursuit(self.current_target)

    def object_reached_callback(self, msg: Bool):
        if msg.data:
            self.target_in_view = False
            self.pursuit_goal_handle = None
            # Cube physically reached. Resume exploration so explore_lite can
            # find the next color (if not in memory) or so we're moving when
            # cube_locator decides to pursue the next target.
            self.set_explore_resume(True)

    def start_pursuit(self, color: str):
        if not self.nav_client.wait_for_server(timeout_sec=2.0):
            self.get_logger().warn(f'Nav2 not ready; cannot pursue {color}.')
            self.set_explore_resume(True)
            return

        pos = self.cube_positions[color]
        self.get_logger().info(
            f'Pursuing remembered {color} cube at '
            f'({pos.point.x:.2f}, {pos.point.y:.2f}).'
        )

        self.set_explore_resume(False)

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = pos.point.x
        goal.pose.pose.position.y = pos.point.y
        goal.pose.pose.orientation.w = 1.0

        future = self.nav_client.send_goal_async(goal)
        future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().warn('Pursuit goal rejected by Nav2.')
            self.set_explore_resume(True)
            return

        self.pursuit_goal_handle = goal_handle
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.goal_result_callback)

    def goal_result_callback(self, future):
        self.pursuit_goal_handle = None

    def cancel_pursuit(self):
        if self.pursuit_goal_handle is None:
            return
        self.pursuit_goal_handle.cancel_goal_async()
        self.pursuit_goal_handle = None

    def set_explore_resume(self, value: bool):
        msg = Bool()
        msg.data = value
        self.explore_resume_pub.publish(msg)

    def publish_markers(self):
        if not self.cube_positions:
            return

        array = MarkerArray()
        now = self.get_clock().now().to_msg()

        for i, color in enumerate(COLORS):
            if color not in self.cube_positions:
                continue

            pos = self.cube_positions[color]

            marker = Marker()
            marker.header.frame_id = 'map'
            marker.header.stamp = now
            marker.ns = 'cubes'
            marker.id = i
            marker.type = Marker.SPHERE
            marker.action = Marker.ADD
            marker.pose.position.x = pos.point.x
            marker.pose.position.y = pos.point.y
            marker.pose.position.z = 0.15
            marker.pose.orientation.w = 1.0
            marker.scale.x = 0.25
            marker.scale.y = 0.25
            marker.scale.z = 0.25
            marker.color = COLOR_RGBA[color]
            array.markers.append(marker)

            label = Marker()
            label.header.frame_id = 'map'
            label.header.stamp = now
            label.ns = 'cube_labels'
            label.id = i
            label.type = Marker.TEXT_VIEW_FACING
            label.action = Marker.ADD
            label.pose.position.x = pos.point.x
            label.pose.position.y = pos.point.y
            label.pose.position.z = 0.45
            label.pose.orientation.w = 1.0
            label.scale.z = 0.15
            label.color = ColorRGBA(r=1.0, g=1.0, b=1.0, a=1.0)
            label.text = color
            array.markers.append(label)

        self.markers_pub.publish(array)


def main(args=None):
    rclpy.init(args=args)
    node = CubeLocatorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
