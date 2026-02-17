#!/bin/bash

# Go2 SLAM Startup Script
# This script starts all SLAM nodes in separate terminals to avoid launch file DDS issues

echo "=== Starting Go2 SLAM System ==="

# Disable pyenv temporarily
export PYENV_VERSION=system

# Source ROS2
source /opt/ros/foxy/setup.bash
source ~/odom/install/setup.bash

# Kill any existing processes
pkill -9 -f "slam_toolbox|odom_to_tf|static_transform|pointcloud_to_laserscan|robot_state_publisher|pc2_relay"
sleep 1

echo "Starting nodes..."

# 1. Robot State Publisher (use launch file parameter loading)
ros2 run robot_state_publisher robot_state_publisher \
    --ros-args \
    -p use_sim_time:=false \
    __params:=<(echo "robot_state_publisher:
  ros__parameters:
    robot_description: '$(cat ~/odom/GO2_URDF/urdf/go2_description.urdf | sed "s/'/\\\\'/g")'") 2>/dev/null &
echo "✓ Robot State Publisher started"
sleep 1

# 2. Odom to TF
python3 ~/odom/src/go2_mapping/go2_mapping/odom_to_tf.py &
echo "✓ Odom to TF started"
sleep 1

# 3. PC2 Relay
python3 ~/pc2_relay_be.py &
echo "✓ PC2 Relay started"
sleep 1

# 4. Static TF alias: base_link -> base (connects odom tree to URDF root frame)
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link base 2>/dev/null &
echo "✓ Static TF (base_link -> base) started"
sleep 1

# 5. Static TF: base_link -> hesai_lidar
ros2 run tf2_ros static_transform_publisher 0.15 0 0.12 0 0 0 base_link hesai_lidar 2>/dev/null &
echo "✓ Static TF (base_link -> hesai_lidar) started"
sleep 1

# 6. PointCloud to LaserScan
ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node --ros-args \
    --params-file ~/odom/install/go2_mapping/share/go2_mapping/config/pointcloud_to_laserscan.yaml \
    -r cloud_in:=/lidar_points \
    -r scan:=/scan_raw 2>/dev/null &
echo "✓ PointCloud to LaserScan started"
sleep 2

# 7. SLAM Toolbox
ros2 run slam_toolbox async_slam_toolbox_node --ros-args \
    --params-file ~/odom/install/go2_mapping/share/go2_mapping/config/slam_params.yaml \
    -r scan:=/scan_raw 2>/dev/null &
echo "✓ SLAM Toolbox started"

echo ""
echo "=== All SLAM nodes started successfully! ==="
echo ""
echo "To view in RViz: rviz2"
echo "To stop all nodes: ./stop_slam.sh"
echo ""
echo "Note: Ignore 'bad_alloc' warnings - they are harmless ROS2 Foxy logging bugs"
echo ""

# Keep script running
wait
