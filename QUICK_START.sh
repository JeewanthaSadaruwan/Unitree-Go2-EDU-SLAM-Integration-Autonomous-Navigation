#!/bin/bash
# Go2 SLAM Quick Start Guide
# This script helps you understand and run the SLAM setup

cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║          Go2 Robot SLAM - Quick Reference Guide                  ║
╚══════════════════════════════════════════════════════════════════╝

📦 WORKSPACE SETUP
─────────────────────────────────────────────────────────────────
Location: /home/unitree/odom/
Package:  go2_mapping

First time setup:
  cd /home/unitree/odom
  colcon build --symlink-install
  source install/setup.bash

Add to ~/.bashrc (recommended):
  echo "source /home/unitree/odom/install/setup.bash" >> ~/.bashrc


🚀 4-TERMINAL SLAM STARTUP
─────────────────────────────────────────────────────────────────

Terminal 1 - Odom → TF Broadcaster (KEEP RUNNING):
  ros2 run go2_mapping odom_to_tf
  
  Purpose: Converts /utlidar/robot_odom to TF transforms
           Publishes: odom → base_link transform
           Critical for localization!

Terminal 2 - SLAM Toolbox:
  ros2 launch slam_toolbox online_async_launch.py \
    slam_params_file:=$HOME/odom/src/go2_mapping/config/slam_params_go2.yaml
  
  Purpose: Performs 2D SLAM mapping
           Creates: /map topic and map → odom transform

Terminal 3 - RViz (Visualization):
  rviz2
  
  Add displays:
    - Map (/map)
    - LaserScan (/scan)
    - TF
    - RobotModel

Terminal 4 - Monitoring/Commands:
  # Check topics
  ros2 topic list
  
  # Monitor odom
  ros2 topic echo /utlidar/robot_odom --once
  
  # Check TF
  ros2 run tf2_ros tf2_echo odom base_link


📊 VERIFICATION COMMANDS
─────────────────────────────────────────────────────────────────
Check if odom is publishing:
  ros2 topic hz /utlidar/robot_odom

View TF tree:
  ros2 run tf2_tools view_frames
  # Creates frames.pdf showing the transform tree

Monitor all TF broadcasts:
  ros2 run tf2_tools tf2_monitor

List all nodes:
  ros2 node list

Check specific transform:
  ros2 run tf2_ros tf2_echo odom base_link


🔍 WHAT EACH NODE DOES
─────────────────────────────────────────────────────────────────

1. odom_to_tf:
   - Subscribes: /utlidar/robot_odom (Odometry message)
   - Publishes: TF transform (odom → base_link)
   - Why: SLAM needs TF tree to know robot location
   - QoS: RELIABLE (ensures no data loss)

2. odom_to_tf_planar (alternative):
   - Same as above but enforces 2D (z=0, yaw-only)
   - Better for ground robots
   - QoS: BEST_EFFORT (lower latency)

3. slam_toolbox:
   - Subscribes: /scan (LaserScan), TF tree
   - Publishes: /map (OccupancyGrid), map→odom TF
   - Creates 2D map from laser scans

4. scan_stamp_fix (if needed):
   - Fixes timestamp issues in laser scans
   - Use if you see TF extrapolation errors


⚙️  CONFIGURATION FILES
─────────────────────────────────────────────────────────────────
SLAM params: src/go2_mapping/config/slam_params_go2.yaml

Key parameters:
  - resolution: 0.05        # 5cm per grid cell
  - max_laser_range: 30.0   # 30 meters
  - scan_topic: /scan
  - base_frame: base_link
  - odom_frame: odom
  - map_frame: map


🎯 UNDERSTANDING THE TF TREE
─────────────────────────────────────────────────────────────────
      map
       ↓ (published by SLAM)
      odom
       ↓ (published by odom_to_tf)
   base_link (robot)
       ↓ (usually static)
     lidar

- map: Global reference frame (fixed)
- odom: Odometry frame (drifts over time)
- base_link: Robot center
- SLAM corrects odom drift by adjusting map→odom


📝 SAVED FILES
─────────────────────────────────────────────────────────────────
After building, you can run nodes via:
  ros2 run go2_mapping <node_name>

Available nodes:
  - odom_to_tf
  - odom_to_tf_planar
  - scan_stamp_fix
  - wifi_topic_relay

Or use launch file (starts multiple nodes):
  ros2 launch go2_mapping go2_mapping.launch.py


🐛 TROUBLESHOOTING
─────────────────────────────────────────────────────────────────
Problem: "No odom messages"
  → Check: ros2 topic hz /utlidar/robot_odom
  → Ensure LiDAR node is running

Problem: "No TF transform"
  → Check: ros2 node list | grep odom
  → Verify odom_to_tf is running
  → Check: ros2 topic echo /tf

Problem: "SLAM not creating map"
  → Ensure odom_to_tf is running first
  → Check scan data: ros2 topic hz /scan
  → Verify frame names match in config

Problem: "TF extrapolation errors"
  → Timestamps might be wrong
  → Try: ros2 run go2_mapping scan_stamp_fix


📚 MORE INFO
─────────────────────────────────────────────────────────────────
Package README: /home/unitree/odom/src/go2_mapping/README.md
Source code:    /home/unitree/odom/src/go2_mapping/go2_mapping/

EOF
