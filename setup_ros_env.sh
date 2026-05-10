# Workspace directory, assuming that Step 0 (Lab setup/ros2 apt), 
# Step 1 (Clone/Venv), and Step 2 (Build) are complete.
WS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source system ROS
source /opt/ros/jazzy/setup.bash

# Source workspace
source "$WS_DIR/install/setup.bash"

# Add virtualenv packages
export PYTHONPATH=$HOME/ros2_venv/lib/python3.12/site-packages:$PYTHONPATH

# Need the burger bot
export TURTLEBOT3_MODEL=burger
