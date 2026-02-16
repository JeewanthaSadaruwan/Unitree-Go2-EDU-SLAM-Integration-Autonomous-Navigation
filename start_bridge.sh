#!/bin/bash

# Go2 Robot Bridge Startup Script
# This script launches the cmd_vel bridge for navigation

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Go2 Robot Navigation Bridge${NC}"
echo -e "${GREEN}======================================${NC}"

# Source ROS2 workspaces
source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
source ~/go2_bringup_ws/install/setup.bash

echo -e "${GREEN}Launching cmd_vel bridge...${NC}"

# Launch bridge
ros2 launch go2_mapping go2_bridge.launch.py

echo -e "${YELLOW}Bridge stopped.${NC}"
