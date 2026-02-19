#!/bin/bash

# Go2 Robot Map Saving Script
# This script saves the current SLAM map

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Go2 Robot Map Saver${NC}"
echo -e "${GREEN}======================================${NC}"

# Create maps directory if it doesn't exist
mkdir -p ~/odom/maps

# Get map name from argument or use default
if [ -z "$1" ]; then
    TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
    MAP_NAME="map_${TIMESTAMP}"
    echo -e "${YELLOW}No map name provided, using: $MAP_NAME${NC}"
else
    MAP_NAME="$1"
    echo -e "${GREEN}Using map name: $MAP_NAME${NC}"
fi

MAP_PATH="/home/unitree/odom/maps/${MAP_NAME}"

# Source ROS2 workspace
source /opt/ros/humble/setup.bash
source /home/unitree/odom/install/setup.bash

echo -e "${GREEN}Saving map to: ${MAP_PATH}${NC}"

# Save the map using the Python script
ros2 run go2_mapping save_map.py "$MAP_PATH"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Map saved successfully!${NC}"
    echo -e "${GREEN}Files created:${NC}"
    ls -lh "${MAP_PATH}."*
else
    echo -e "${RED}Failed to save map${NC}"
    exit 1
fi
