import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'color_finder'


def package_files(directory):
    paths = []
    for path, _, filenames in os.walk(directory):
        files = [os.path.join(path, filename) for filename in filenames]
        if files:
            paths.append((os.path.join('share', package_name, path), files))

    return paths


setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),

        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'),
            glob('launch/*.launch.py')),

        (os.path.join('share', package_name, 'worlds'),
            glob('worlds/*')),

        (os.path.join('share', package_name, 'urdf'),
            glob('urdf/*')),

        (os.path.join('share', package_name, 'config'),
            glob('config/*')),
    ] + package_files('models'),
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='empso018',
    maintainer_email='empso018@umn.edu',
    description='Color-finding TurtleBot3 ROS2 project',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'target_color = color_finder.target_color_node:main',
            'color_detector = color_finder.color_detector_node:main',
            'robot_controller = color_finder.robot_controller_node:main',
            'waypoint_search = color_finder.waypoint_search_node:main',
            'color_approach = color_finder.color_approach_node:main',
            'cube_locator = color_finder.cube_locator_node:main',
            'camera = color_finder.camera_node:main',
            'ocr = color_finder.ocr_node:main'
        ],
    },
)
