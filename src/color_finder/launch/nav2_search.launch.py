import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def spawn_colored_cube(color, x, y, z=0.2):
    return Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', f'{color}_cube',
            '-file', os.path.join(
                get_package_share_directory('color_finder'),
                'models',
                f'{color}_cube',
                'model.sdf'
            ),
            '-x', str(x),
            '-y', str(y),
            '-z', str(z),
        ],
        output='screen'
    )


def generate_launch_description():
    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    slam_toolbox_dir = get_package_share_directory('slam_toolbox')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')

    turtlebot3_house = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                turtlebot3_gazebo_dir,
                'launch',
                'turtlebot3_house.launch.py'
            )
        )
    )

    slam = IncludeLaunchDescription(
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

    nav2 = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                nav2_bringup_dir,
                'launch',
                'navigation_launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': 'true'
        }.items()
    )

    target_color = Node(
        package='color_finder',
        executable='target_color',
        name='target_color_node',
        output='screen'
    )

    color_detector = Node(
        package='color_finder',
        executable='color_detector',
        name='color_detector_node',
        output='screen'
    )

    waypoint_search = Node(
        package='color_finder',
        executable='waypoint_search',
        name='waypoint_search_node',
        output='screen'
    )

    colored_cubes = TimerAction(
        period=5.0,
        actions=[
            spawn_colored_cube('red', 1.5, 0.5),
            spawn_colored_cube('blue', -1.0, 1.5),
            spawn_colored_cube('green', 0.0, -1.5),
            spawn_colored_cube('yellow', 2.0, -1.0),
        ]
    )

    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', 'burger'),

        turtlebot3_house,

        colored_cubes,

        slam,
        nav2,

        target_color,
        color_detector,
        waypoint_search,
    ])
