#!/usr/bin/env bash
# This is an optional Step 0 for computers that are not yet set up with ROS2 Jazzy like the CSE lab computers are
# This requires Ubuntu 24.04 and sudo permissions.
# Official Installation instructions are here for if something goes wrong or changes drastically upstream:
# https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

# Helps with errors/issues
set -euo pipefail

# Make sure we have pre-requisites before getting ROS2
sudo apt update
sudo apt install -y software-properties-common curl ca-certificates jq
sudo add-apt-repository -y universe

# Gets the official ROS2 files needed for the next step
ROS_APT_VER="$(curl -fsSL https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | jq -r .tag_name)"
CODENAME="$(. /etc/os-release && echo "$VERSION_CODENAME")"
curl -fsSL -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_VER}/ros2-apt-source_${ROS_APT_VER}.${CODENAME}_all.deb"
sudo apt install -y /tmp/ros2-apt-source.deb
sudo apt update

# Installs ROS2 Jazzy and other project dependencies to match the CSE Lab environment setup
sudo apt install -y ros-jazzy-desktop-full ros-jazzy-nav2-bringup ros-jazzy-slam-toolbox \
                    ros-jazzy-turtlebot3 ros-jazzy-turtlebot3-gazebo ros-jazzy-turtlebot3-simulations \
                    python3-colcon-common-extensions python3-venv python3-pip tesseract-ocr \
                    tesseract-ocr-eng git

echo "ROS2 Jazzy Environment Setup complete. Please check README for Step 1 instructions."








