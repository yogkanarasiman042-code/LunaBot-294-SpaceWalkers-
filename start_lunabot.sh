#!/bin/bash

echo "========================================"
echo "   🌙 LUNABOT MISSION SYSTEM STARTING"
echo "========================================"

source /opt/ros/lyrical/setup.bash
source "$HOME/nav2_ws/install/setup.bash"
source "$HOME/lunabot_ws/install/setup.bash"

echo "ROS 2 environment loaded."
echo "Starting Lunar Habitat Simulation..."
echo

ros2 launch lunabot_core lunabot_demo.launch.py
