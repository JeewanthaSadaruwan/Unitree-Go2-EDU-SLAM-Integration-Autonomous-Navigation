#!/bin/bash

# Go2 Robot Navigation Startup Script
# This script launches the complete navigation stack

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Go2 Robot Navigation Stack${NC}"
echo -e "${GREEN}======================================${NC}"

# Check if map file is provided
MAP_FILE="${1:-/home/unitree/odom/maps/floor10_1.yaml}"

if [ ! -f "$MAP_FILE" ]; then
    echo -e "${RED}Error: Map file not found: $MAP_FILE${NC}"
    echo -e "${YELLOW}Usage: $0 [map_file.yaml]${NC}"
    echo -e "${YELLOW}Example: $0 /home/unitree/odom/maps/floor10_1.yaml${NC}"
    exit 1
fi

echo -e "${GREEN}Using map: $MAP_FILE${NC}"

# Source ROS2 workspace
source /opt/ros/humble/setup.bash
source /home/unitree/odom/install/setup.bash

echo -e "${GREEN}Launching navigation stack...${NC}"

# Launch navigation
ros2 launch go2_mapping go2_navigation.launch.py \
    map_yaml:=$MAP_FILE \
    use_sim_time:=false \
    params_file:=/home/unitree/odom/src/go2_mapping/config/go2_nav2_params.yaml \
    autostart:=true

echo -e "${YELLOW}Navigation stack stopped.${NC}"
