from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='color_finder',
            executable='target_color',
            name='target_color_node',
            parameters=[
                {'target_color': 'red'}
            ]
        ),

        Node(
            package='color_finder',
            executable='color_detector',
            name='color_detector_node'
        ),

        Node(
            package='color_finder',
            executable='robot_controller',
            name='robot_controller_node'
        ),
    ])