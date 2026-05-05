# 4551_Project   
Final project for 4551   

---Project Description---   
* ROS2 system   
* Utilizes SLAM and Nav2 packages from ros   
* Implemented color finding logic as nodes   
* Robot looks for colored objects, and remembers their location as it searches for and   
* pursues a currently targeted color. When it has previously seen the currently targeted   
* color, it attempts to return to that area to find it.   

--- Setup Requirements ---   
- After cloning this repo, you also need to clone   
- https://github.com/robo-friends/m-explore-ros2   
- into the /color-finder-ros2/src/ folder alongside /color_finder/   

Extra setup commands:   
$ cd <your_ros2_ws>/src   
$ git clone https://github.com/robo-friends/m-explore-ros2.git   

To initialize workspace:   
$ colcon build   
$ source install/setup.bash   

---How to Run---   
$ ros2 launch color_finder nav2_explore.launch.py   
   
* Rebuild everytime you update the code   
* Source bash everytime you open a new terminal   
   
~/.bashrc file   
* Make sure that file has TURTLEBOT3_MODEL=burger   
   


## Testing Notes (Remove Later)
To test camera use the following commands in different terminals
- ros2 run ros2_opencv publisher_node
- ros2 run ros2_opencv subscriber_node


## Setup Instructions
Inside the 4551_Project folder, run the following commands
### Create venv for python packages
- python3 -m venv ~/ros2_venv
- source ~/ros2_venv/bin/activate
- pip install -r requirements.txt
- deactivate
### Build and setup Project
- source build_ros.sh
- source setup_ros_env.sh
