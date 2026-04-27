import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import AppendEnvironmentVariable, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
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
    turtlebot3_model = 'burger_cam'
    os.environ['TURTLEBOT3_MODEL'] = turtlebot3_model

    turtlebot3_gazebo_dir = get_package_share_directory('turtlebot3_gazebo')
    ros_gz_sim_dir = get_package_share_directory('ros_gz_sim')
    slam_toolbox_dir = get_package_share_directory('slam_toolbox')
    nav2_bringup_dir = get_package_share_directory('nav2_bringup')
    color_finder_dir = get_package_share_directory('color_finder')

    world = os.path.join(
        turtlebot3_gazebo_dir,
        'worlds',
        'turtlebot3_house.world'
    )

    gzserver = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                ros_gz_sim_dir,
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': ['-r -s -v2 ', world],
            'on_exit_shutdown': 'true'
        }.items()
    )

    gzclient = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                ros_gz_sim_dir,
                'launch',
                'gz_sim.launch.py'
            )
        ),
        launch_arguments={
            'gz_args': '-g -v2 ',
            'on_exit_shutdown': 'true'
        }.items()
    )

    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                turtlebot3_gazebo_dir,
                'launch',
                'robot_state_publisher.launch.py'
            )
        ),
        launch_arguments={
            'use_sim_time': 'true'
        }.items()
    )

    spawn_turtlebot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', turtlebot3_model,
            '-file', os.path.join(
                turtlebot3_gazebo_dir,
                'models',
                'turtlebot3_' + turtlebot3_model,
                'model.sdf'
            ),
            '-x', '-6.0',
            '-y', '3.0',
            '-z', '0.01',
        ],
        output='screen'
    )

    image_bridge = Node(
        package='ros_gz_image',
        executable='image_bridge',
        arguments=['/camera/image_raw'],
        output='screen'
    )

    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '--ros-args',
            '-p',
            'config_file:=' + os.path.join(
                color_finder_dir,
                'config',
                'turtlebot3_burger_bridge_twist.yaml'
            ),
        ],
        output='screen'
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
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    color_detector = Node(
        package='color_finder',
        executable='color_detector',
        name='color_detector_node',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    waypoint_search = Node(
        package='color_finder',
        executable='waypoint_search',
        name='waypoint_search_node',
        output='screen',
        parameters=[{'use_sim_time': True}]
    )

    colored_cubes = TimerAction(
        period=5.0,
        actions=[
            spawn_colored_cube('red', -1.5, 4.0),
            spawn_colored_cube('blue', 4.7, 1.0),
            spawn_colored_cube('green', 6.0, -1.0),
            spawn_colored_cube('yellow', 1.6, -0.2),
        ]
    )

    return LaunchDescription([
        SetEnvironmentVariable('TURTLEBOT3_MODEL', turtlebot3_model),
        AppendEnvironmentVariable(
            'GZ_SIM_RESOURCE_PATH',
            os.path.join(turtlebot3_gazebo_dir, 'models')
        ),

        gzserver,
        gzclient,
        spawn_turtlebot,
        robot_state_publisher,
        bridge,
        image_bridge,

        colored_cubes,

        slam,
        nav2,

        target_color,
        color_detector,
        TimerAction(period=8.0, actions=[waypoint_search]),
    ])
