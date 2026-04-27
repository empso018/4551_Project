import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'color_finder'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='empso018',
    maintainer_email='empso018@umn.edu',
    description='TODO: Package description',
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
        ],
    },
)
