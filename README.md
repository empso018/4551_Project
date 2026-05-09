# 4551_Project   
Final project for 4551   
  
## --- Project Description ---   
* ROS2 system   
* Utilizes SLAM and Nav2 packages from ros   
* Uses camera and tesseract ocr to select target color  
* Implemented color finding logic as nodes   
* Robot looks for colored objects, and remembers their location as it searches for and pursues a currently targeted color. 
* When it has previously seen the currently targeted color, it attempts to return to that area to find it.   

## --- Other Requirements ---   
- Have flashcards/sheets of paper with the words "red", "yellow", "blue", and "green" on them (case insensitive) (not provided)  
- Follow the setup instructions below step-by-step. If you go out of order, you will have errors.  
  
## --- Setup Instructions ---  
  
### Step 0 (for non-lab computers only)  
This step is to set up the ROS2 libraries and dependencies that are already on the CSE lab computers,
such as for running this project on a home Ubuntu 24.04 computer. Sudo permissions are required.  
  
These commands will download the ROS2 setup script and run it:  
$ curl -fsSL -o bootstrap_system.sh https://raw.githubusercontent.com/empso018/4551_Project/main/bootstrap_system.sh  
$ hmod +x bootstrap_system.sh  
$ ./bootstrap_system.sh  
  
### Step 1 - Clone and create venv  
Note: while we use "~/4551_Project" as the workspace (WS) directory, this will work from any directory you clone into. "/4551_Project" should not exist already relative to your working directory, so delete this folder if it is present and you want to start fresh.   
#### a) Download the project files from github  
$ git clone https://github.com/empso018/4551_Project.git ~/4551_Project/  
#### b) Download m explore files from github  
$ cd ~/4551_Project/src  
$ git clone https://github.com/robo-friends/m-explore-ros2.git  
$ cd ..  
#### c) Create venv for python packages  
$ python3 -m venv --system-site-packages ~/ros2_venv  
$ source ~/ros2_venv/bin/activate  
$ pip install -r requirements.txt  
$ deactivate  
### Step 2 - Build Project  
$ ./build_ros.sh  
### Step 3 - Source the runtime env (do this for every new terminal)  
$ source setup_ros_env.sh  
Note: This sources ros2, the ws overlay, the venv, and exports TURTLEBOT3_MODEL=burger  
  
## --- How to Run ---   
$ ros2 launch color_finder nav2_explore.launch.py   
   
* Rebuild everytime you update the code   
* Do step 3 everytime you open a new terminal   
   

## --- User Instructions ---  
- Upon startup and when finding the target color, a new target color will be randomly selected  
- To change the target color manually, show the flashcard of the color you want to target to the camera  
- If the color doesn't change, make sure the flashcard is close to the camera and blocks out most of the background while still being readable on the video feed  
  
## --- Troubleshooting ---  
**If the Build fails with "em.TransientParseError: not enough data to read", "ModuleNotFoundError: No module named 'lark'", or "Could NOT find Python3 (missing: NumPy)"**  
Then the venv was likely run without "-system-site-packages" in Step 1c. Those packages are present in the system from ROS2, but that part of the command must be included so the venv can see/use them.  
  
