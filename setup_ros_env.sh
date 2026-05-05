# Source system ROS
source /opt/ros/jazzy/setup.bash

# Source workspace
source ~/4551_Project/install/setup.bash

# Add virtualenv packages
export PYTHONPATH=~/ros2_venv/lib/python3.12/site-packages:$PYTHONPATH
