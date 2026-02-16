# Go2 Robot SLAM & Mapping Package

ROS2 workspace for SLAM mapping and navigation on the Unitree Go2 robot.

## Overview

This package provides a complete SLAM solution for the Go2 robot, including:
- Odometry to TF broadcasting
- PointCloud to LaserScan conversion
- SLAM Toolbox integration
- Pre-configured parameters optimized for Go2

## Quick Start

### 1. Source the Workspace
```bash
cd ~/odom
source install/setup.bash
```

### 2. Launch Hesai Lidar (Terminal 1)
```bash
source /opt/ros/foxy/setup.bash
source ~/odom/xt16_ws/install/setup.bash
ros2 launch hesai_ros_driver start.py
```

### 3. Launch SLAM Mapping (Terminal 2)
```bash
source /opt/ros/foxy/setup.bash
source ~/odom/install/setup.bash
ros2 launch go2_mapping go2_mapping.launch.py
```

This starts all required nodes:
- Robot State Publisher (URDF)
- Odom to TF broadcaster
- PointCloud relay
- Static TF (base_link → hesai_lidar)
- PointCloud to LaserScan converter
- SLAM Toolbox (async mapping mode)

### 4. Visualize in RViz (On Local Computer)

First, set the package path so RViz can find the robot meshes:
```bash
export ROS_PACKAGE_PATH=~/GO2_URDF:$ROS_PACKAGE_PATH
```

Then launch RViz:
```bash
rviz2 -d ~/Desktop/rviz/go2_slam_visualization.rviz
```

Or if the file is in a different location:
```bash
rviz2 -d /path/to/go2_slam_visualization.rviz
```

**Note:** If you see mesh loading errors, make sure the GO2_URDF folder is copied to your local computer's home directory.

### 5. (Optional) Joint State Publisher for Robot Model Visualization
If you want to see the robot's 3D model with joint movements in RViz:
```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><NetworkInterfaceAddress>eth0</NetworkInterfaceAddress></General></Domain></CycloneDDS>'
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
/usr/bin/python3.8 ~/odom/lowstate_to_joint_states.py
```

### 6. Drive the Robot
```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel
```

**Controls:**
```
   u    i    o
   j    k    l
   m    ,    .

i/k = forward/backward
j/l = turn left/right
k = stop
q/z = increase/decrease speed
```

## Navigation with Saved Map

### 1. Launch Hesai Lidar (Terminal 1)
```bash
source /opt/ros/foxy/setup.bash
source ~/odom/xt16_ws/install/setup.bash
ros2 launch hesai_ros_driver start.py
```

### 2. Launch Navigation Stack (Terminal 2)
```bash
source /opt/ros/foxy/setup.bash
source ~/odom/install/setup.bash
ros2 launch go2_mapping go2_navigation.launch.py
```

This starts:
- Map server (loads `floor10_1.yaml` by default)
- AMCL localization
- Nav2 navigation stack
- Costmap generators
- Path planners

### 3. Visualize Navigation in RViz (On Local Computer)
```bash
export ROS_PACKAGE_PATH=~/GO2_URDF:$ROS_PACKAGE_PATH
rviz2 -d ~/Desktop/rviz/go2_navigation_visualization.rviz
```

Or use the launch file:
```bash
ros2 launch ~/Desktop/rviz/go2_navigation_visualization.launch.py
```

**In RViz:**
1. **Set Initial Pose**: Click "2D Pose Estimate" button, then click and drag on the map where the robot actually is
2. **Send Navigation Goal**: Click "Nav2 Goal" button, then click where you want the robot to go
3. The robot will autonomously navigate to the goal!

**Displays shown:**
- Map (loaded from file)
- Robot model with live joint states
- Global path (red line - overall route)
- Local path (green line - immediate trajectory)
- Global costmap (obstacles in planning space)
- Local costmap (immediate obstacles)
- Particle cloud (yellow points - AMCL localization estimates)
- Laser scan

### 4. (Optional) Use Different Map
To use a different map (e.g., `floor15_2.yaml`):
```bash
ros2 launch go2_mapping go2_navigation.launch.py map_yaml:=/home/unitree/odom/maps/floor15_2.yaml
```

## Package Structure

```
odom/
├── src/go2_mapping/              # Main ROS2 package
│   ├── go2_mapping/              # Python modules
│   │   ├── odom_to_tf.py        # Odometry to TF broadcaster
│   │   ├── odom_to_tf_planar.py # 2D-only TF broadcaster
│   │   ├── scan_stamp_fix.py    # LaserScan timestamp fixer
│   │   └── wifi_topic_relay.py  # WiFi topic relay
│   ├── config/                   # SLAM configuration files
│   │   ├── slam_params_go2.yaml # Go2 optimized parameters
│   │   └── pointcloud_to_laserscan.yaml
│   └── launch/                   # Launch files
│       ├── go2_slam_full.launch.py        # Complete SLAM launch
│       ├── go2_mapping.launch.py          # Basic mapping launch
│       └── pointcloud_to_laserscan.launch.py
├── maps/                         # Saved maps
│   ├── floor10_1.pgm
│   └── floor10_1.yaml
├── build/                        # Build artifacts
├── install/                      # Installed packages
└── stop_slam.sh                 # Emergency stop script
```

## SLAM Configuration

### Parameters (slam_params_go2.yaml)

Key settings optimized for Go2:
```yaml
use_sim_time: false              # Using real robot time
mode: mapping                     # Mapping mode (vs localization)
map_frame: map                    # Map coordinate frame
odom_frame: odom                  # Odometry frame
base_frame: base_link             # Robot base frame
scan_topic: /scan_raw             # LiDAR scan topic
use_scan_matching: true           # Enable scan matching
resolution: 0.05                  # 5cm map resolution
max_laser_range: 30.0            # 30m maximum range
```

## Individual Node Usage

### Odometry to TF
```bash
ros2 run go2_mapping odom_to_tf
```
- Converts `/utlidar/robot_odom` → TF transform
- Publishes: `odom → base_link` transform
- Updates at ~150 Hz

### PointCloud to LaserScan
```bash
ros2 launch go2_mapping pointcloud_to_laserscan.launch.py
```
- Converts `/utlidar/cloud_deskewed` (PointCloud2) → `/scan` (LaserScan)
- Extracts horizontal slice ±10cm height
- 360° coverage, 1° resolution

### SLAM Toolbox
```bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:=~/odom/src/go2_mapping/config/slam_params_go2.yaml
```
- Builds map while correcting odometry drift
- Publishes `/map` topic and `map → odom` transform

## Map Management

### Save Map
```bash
mkdir -p ~/odom/maps
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap \
  "{name: {data: '/home/unitree/odom/maps/my_map'}}"
```

Saves two files:
- `my_map.yaml` - Map metadata
- `my_map.pgm` - Map image (grayscale)

### Load Map
```bash
ros2 run nav2_map_server map_server --ros-args \
  -p yaml_filename:=/home/unitree/odom/maps/floor10_1.yaml \
  -p use_sim_time:=false
```

Activate the map server:
```bash
ros2 lifecycle set /map_server configure
ros2 lifecycle set /map_server activate
```

## TF Tree

Complete transform hierarchy:
```
map → odom → base_link → base_footprint
```

- **map**: Global fixed frame
- **odom**: Odometry frame (drifts over time)
- **base_link**: Robot center
- **base_footprint**: Robot ground projection

## Building the Workspace

### First Time Build
```bash
cd ~/odom
colcon build --symlink-install
source install/setup.bash
```

### Rebuild After Changes
```bash
cd ~/odom
colcon build --symlink-install --packages-select go2_mapping
source install/setup.bash
```

### Add to .bashrc (Auto-source)
```bash
echo "source ~/odom/install/setup.bash" >> ~/.bashrc
```

## Troubleshooting

### Can't See Topics from Remote Laptop

**Option 1 - Disable ROS daemon:**
```bash
export ROS2CLI_DISABLE_DAEMON=1
ros2 daemon stop 2>/dev/null || true
pkill -f _ros2_daemon 2>/dev/null || true
```

**Option 2 - Configure DDS:**
```bash
unset CYCLONEDDS_URI
unset RMW_IMPLEMENTATION
source ~/unitree_ros2/setup.sh
```

### SLAM Not Building Map

1. Check all nodes are running:
   ```bash
   ros2 node list
   ```

2. Verify TF tree:
   ```bash
   ros2 run tf2_tools view_frames
   evince frames.pdf
   ```

3. Check scan data:
   ```bash
   ros2 topic echo /scan --once
   ```

4. Verify odometry:
   ```bash
   ros2 topic echo /utlidar/robot_odom --once
   ```

### Emergency Stop
```bash
./stop_slam.sh
```
Kills all SLAM-related processes.

## Requirements

- ROS2 Foxy or later
- slam_toolbox
- pointcloud_to_laserscan
- nav2_map_server (for map loading)
- teleop_twist_keyboard (for manual control)

## Hardware

- Unitree Go2 robot
- LiDAR sensor (publishes to `/utlidar/cloud_deskewed`)
- Odometry source (publishes to `/utlidar/robot_odom`)

## Topics

### Subscribed
- `/utlidar/robot_odom` (nav_msgs/Odometry) - Robot odometry
- `/utlidar/cloud_deskewed` (sensor_msgs/PointCloud2) - 3D point cloud

### Published
- `/scan` (sensor_msgs/LaserScan) - 2D laser scan
- `/map` (nav_msgs/OccupancyGrid) - Occupancy grid map
- TF transforms: `map→odom`, `odom→base_link`, `base_link→base_footprint`

## License

This package is provided as-is for the Unitree Go2 robot.

## Support

For issues or questions, check:
- TF tree: `ros2 run tf2_tools view_frames`
- Node list: `ros2 node list`
- Topic list: `ros2 topic list`
- Node info: `ros2 node info <node_name>`
