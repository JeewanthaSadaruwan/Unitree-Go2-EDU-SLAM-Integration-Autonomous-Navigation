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

# Resolve workspace root from this script location
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if map file is provided
MAP_FILE="${1:-$ROOT_DIR/maps/floor10.yaml}"

if [ ! -f "$MAP_FILE" ]; then
    echo -e "${RED}Error: Map file not found: $MAP_FILE${NC}"
    echo -e "${YELLOW}Usage: $0 [map_file.yaml]${NC}"
    echo -e "${YELLOW}Example: $0 $ROOT_DIR/maps/floor10.yaml${NC}"
    exit 1
fi

echo -e "${GREEN}Using map: $MAP_FILE${NC}"

# Running SLAM Toolbox and AMCL/Nav2 together causes map->odom TF conflicts.
if pgrep -f "slam_toolbox" >/dev/null; then
    echo -e "${RED}Error: slam_toolbox is running.${NC}"
    echo -e "${YELLOW}Stop SLAM first (./stop_all.sh), then start navigation.${NC}"
    exit 1
fi

# Prevent duplicate odom->base_link TF publishers if user service is active.
if systemctl --user is-active --quiet go2-odom-to-tf.service 2>/dev/null; then
    echo -e "${YELLOW}go2-odom-to-tf.service is active; stopping it to avoid duplicate TF.${NC}"
    systemctl --user stop go2-odom-to-tf.service || {
        echo -e "${RED}Failed to stop go2-odom-to-tf.service${NC}"
        exit 1
    }
fi

# Source ROS2 workspace
source /opt/ros/foxy/setup.bash
source "$ROOT_DIR/install/setup.bash"

echo -e "${GREEN}Launching navigation stack...${NC}"

# Launch navigation
ros2 launch go2_mapping go2_navigation.launch.py \
    map_yaml:=$MAP_FILE \
    use_sim_time:=false \
    params_file:=$ROOT_DIR/src/go2_mapping/config/go2_nav2_params.yaml \
    autostart:=true

echo -e "${YELLOW}Navigation stack stopped.${NC}"
