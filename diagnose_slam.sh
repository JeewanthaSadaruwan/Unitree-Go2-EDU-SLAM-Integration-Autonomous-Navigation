#!/bin/bash

echo "=== SLAM Diagnostics ==="
echo ""

source /opt/ros/foxy/setup.bash

echo "1. Checking active nodes:"
ros2 node list 2>/dev/null | grep -E "slam|odom|pointcloud|robot_state" || echo "No SLAM nodes found!"
echo ""

echo "2. Checking critical topics:"
echo "  /lidar_points: $(ros2 topic info /lidar_points 2>/dev/null | grep -c 'Publisher' || echo '0') publishers"
echo "  /scan_raw: $(ros2 topic info /scan_raw 2>/dev/null | grep -c 'Publisher' || echo '0') publishers"
echo "  /odom: $(ros2 topic info /odom 2>/dev/null | grep -c 'Publisher' || echo '0') publishers"
echo "  /map: $(ros2 topic info /map 2>/dev/null | grep -c 'Publisher' || echo '0') publishers"
echo ""

echo "3. Checking TF frames:"
ros2 topic echo /tf --once 2>/dev/null | grep "frame_id" | head -5 || echo "No TF data"
echo ""

echo "4. Checking if SLAM is receiving scans:"
timeout 1 ros2 topic echo /scan_raw --once 2>/dev/null > /dev/null && echo "✓ Laser scan data is available" || echo "✗ No laser scan data!"
echo ""

echo "5. Checking slam_toolbox subscriptions:"
ros2 node info /slam_toolbox 2>/dev/null | grep -A 20 "Subscribers:" | head -25 || echo "slam_toolbox node not found!"
echo ""

echo "=== Diagnostics Complete ==="
