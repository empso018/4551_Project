# 4551_Project   
Final project for 4551   

---Project Description---   
* ROS2 system   
* Utilizes SLAM and Nav2 packages from ros   
* Uses camera and tesseract ocr to select target color
* Implemented color finding logic as nodes   
* Robot looks for colored objects, and remembers their location as it searches for and pursues a currently targeted color. 
* When it has previously seen the currently targeted color, it attempts to return to that area to find it.   

--- Setup Requirements ---   
- Have flashcards/sheets of paper with the words "red", "yellow", "blue", and "green" on them (case insensitive) (not provided)
- Must have the tesseract package installed (may have different name depending on OS)
- After cloning this repo, you also need to clone   
- https://github.com/robo-friends/m-explore-ros2   
- into the /color-finder-ros2/src/ folder alongside /color_finder/   

## Setup Instructions
Inside the 4551_Project folder, run the following commands
### Download m explore
$ cd <your_ros2_ws>/src  
$ git clone https://github.com/robo-friends/m-explore-ros2.git  
$ cd ..
### Create venv for python packages  
$ python3 -m venv ~/ros2_venv  
$ source ~/ros2_venv/bin/activate  
$ pip install -r requirements.txt  
$ deactivate
### Build and setup project
$ source build_ros.sh  
$ source setup_ros_env.sh  
Note: setup_ros_env assumes your workspace is named '4551_Project'

---How to Run---   
$ ros2 launch color_finder nav2_explore.launch.py   
   
* Rebuild everytime you update the code   
* Source bash everytime you open a new terminal   
   
~/.bashrc file   
* Make sure that file has TURTLEBOT3_MODEL=burger   


## User Instructions
- Upon startup and when finding the target color, a new target color will be randomly selected
- To change the target color manually, show the flashcard of the color you want to target to the camera
- If the color doesn't change, make sure the flashcard is close to the camera and blocks out most of the background while still being readable on the video feed
