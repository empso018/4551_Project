import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    slam_toolbox_dir = get_package_share_directory('slam_toolbox')

    turtlebot3_house = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                turtlebot3_gazebo_dir,
                'launch',
                'turtlebot3_house.launch.py'
            )
        )
    )

    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                slam_toolbox_dir,
                'launch',
                'online_sync_launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': 'true'
        }.items()
    )

    target_color = Node(
        package='color_finder',
        executable='target_color',
        name='target_color_node'
    )

    color_detector = Node(
        package='color_finder',
        executable='color_detector',
        name='color_detector_node'
    )

    robot_controller = Node(
        package='color_finder',
        executable='robot_controller',
        name='robot_controller_node'
    )

    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger'),

        turtlebot3_house,
        slam_toolbox,

        target_color,
        color_detector,
        robot_controller,
    ])