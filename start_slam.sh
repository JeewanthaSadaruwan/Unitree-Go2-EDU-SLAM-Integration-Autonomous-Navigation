#!/bin/bash
# Wrapper script to handle ROS2 selection and run SLAM
# This automatically selects option 1 (Foxy) if menu appears

echo "=== Go2 SLAM Startup ==="
echo ""

# Check if we're already in a ROS2 environment
if [ -z "$ROS_DISTRO" ]; then
    echo "Sourcing ROS2 Foxy..."
    source /opt/ros/foxy/setup.bash
    
    if [ $? -eq 0 ]; then
        echo "✓ ROS2 Foxy sourced successfully"
    else
        echo "✗ Failed to source ROS2 Foxy"
        exit 1
    fi
else
    echo "✓ Already in ROS2 environment: $ROS_DISTRO"
fi

echo ""
echo "Starting SLAM system with tmux..."
echo ""

# Run the improved tmux script
cd ~/odom
./go2_slam_improved.sh
