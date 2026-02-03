# Go2 Robot Complete SLAM & Navigation Guide

## Overview

This guide covers the complete workflow for SLAM mapping and navigation on the Go2 robot.

---

## 🚀 SLAM Mapping Workflow (4 Terminals)

### Terminal 1 — Odom → TF Broadcaster (KEEP RUNNING)

```bash
/usr/bin/python3 ~/odom/odom_to_tf.py
```

**What it does:**
- Converts `/utlidar/robot_odom` to TF transform
- Publishes: `odom → base_link` transform
- Updates ~150 Hz
- **Critical:** SLAM needs this to know robot position

**Expected output:**
```
[INFO] [odom_to_tf]: odom_to_tf started (RELIABLE sub)
[INFO] [odom_to_tf]: rx odom msgs: 151, last stamp: ...
```

---

### Terminal 2 — Static TF: base_link → base_footprint (KEEP RUNNING)

```bash
source /opt/ros/foxy/setup.bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link base_footprint
```

**What it does:**
- Creates static transform: `base_link → base_footprint`
- `base_footprint` = robot's projection on ground (z=0)
- Parameters: x y z roll pitch yaw parent child
- All zeros = footprint is directly below base_link

**Why needed:**
- Many navigation algorithms expect `base_footprint`
- Represents robot's 2D position on ground
- Used for collision checking and path planning

**TF Tree becomes:**
```
odom → base_link → base_footprint
```

---

### Terminal 3 — SLAM Toolbox (KEEP RUNNING)

```bash
source /opt/ros/foxy/setup.bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:=/home/unitree/odom/slam_params_go2.yaml
```

**What it does:**
- Performs 2D SLAM (Simultaneous Localization and Mapping)
- Subscribes: `/scan` (laser scans), TF tree
- Publishes: `/map` (OccupancyGrid), `map → odom` transform
- Builds map while correcting odometry drift

**Expected output:**
```
[INFO] [slam_toolbox]: Message Filter subscribing to topics...
[INFO] [slam_toolbox]: Registering sensor...
```

**Map TF Tree becomes:**
```
map → odom → base_link → base_footprint
```

---

### Terminal 4 — PointCloud2 → LaserScan Conversion (KEEP RUNNING)

```bash
source /opt/ros/foxy/setup.bash
ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node \
  --ros-args \
  -r cloud_in:=/utlidar/cloud_deskewed \
  -r scan:=/scan \
  -p target_frame:=base_link \
  -p min_height:=-0.1 \
  -p max_height:=0.1 \
  -p angle_min:=-3.14159 \
  -p angle_max:=3.14159 \
  -p angle_increment:=0.0174533 \
  -p range_min:=0.2 \
  -p range_max:=30.0 \
  -p use_inf:=true
```

**What it does:**
- Converts 3D point cloud to 2D laser scan
- Input: `/utlidar/cloud_deskewed` (PointCloud2)
- Output: `/scan` (LaserScan)
- Extracts horizontal slice between -10cm and +10cm height

**Parameters explained:**
- `min_height: -0.1` = Include points 10cm below robot
- `max_height: 0.1` = Include points 10cm above robot
- `angle_min/max: ±π` = Full 360° scan
- `angle_increment: 0.0174533` = 1° resolution (π/180)
- `range_min: 0.2` = Ignore points closer than 20cm
- `range_max: 30.0` = Ignore points farther than 30m
- `use_inf: true` = Use infinity for no returns

**Why needed:**
- Your LiDAR produces 3D point clouds
- SLAM Toolbox expects 2D laser scans
- This converts 3D → 2D for compatibility

---

### Terminal 4b — Force SLAM Settings (RUN ONCE after Terminal 3 is up)

```bash
source /opt/ros/foxy/setup.bash
ros2 param set /slam_toolbox use_sim_time false
ros2 param set /slam_toolbox base_frame base_link
```

**What it does:**
- Ensures SLAM uses real hardware time (not simulation)
- Confirms base frame name is `base_link`

**When to run:**
- Wait 5-10 seconds after starting SLAM Toolbox
- Run once to override any config issues
- Optional if your YAML config is correct

---

## 🎮 Robot Control

### Keyboard Teleop (Drive the Robot)

```bash
source /opt/ros/foxy/setup.bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard \
  --ros-args -r cmd_vel:=/cmd_vel
```

**Controls:**
```
   u    i    o
   j    k    l
   m    ,    .

i/k = forward/backward
j/l = turn left/right
u/o/m/. = diagonal movements
k = stop
q/z = increase/decrease speed
```

**Purpose:** Drive robot to explore environment while SLAM builds map

---

### Command Velocity Bridge (On Robot/Jetson)

```bash
source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
source ~/go2_bringup_ws/install/setup.bash
ros2 run cmd_vel_unitree_bridge cmd_vel_unitree_bridge_node
```

**What it does:**
- Bridges ROS2 `/cmd_vel` commands to Unitree SDK
- Translates velocity commands to robot motor controls
- Must run on robot hardware (Jetson)

---

## 💾 Map Management

### Save the Map

```bash
# Create maps directory
mkdir -p ~/maps

# Save map
source /opt/ros/foxy/setup.bash
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap \
  "{name: {data: '/home/unitree/maps/floor15_1'}}"
```

**Saves two files:**
- `floor15_1.yaml` - Map metadata
- `floor15_1.pgm` - Map image (grayscale)

**Map format:**
- White = free space
- Black = obstacles
- Gray = unknown

---

### Load/Publish Saved Map

```bash
source /opt/ros/foxy/setup.bash

# Start map server
ros2 run nav2_map_server map_server --ros-args \
  -p yaml_filename:=/home/unitree/maps/floor15_1.yaml \
  -p use_sim_time:=false
```

**Then activate (in another terminal):**

```bash
source /opt/ros/foxy/setup.bash

# Check state
ros2 lifecycle get /map_server

# Configure
ros2 lifecycle set /map_server configure

# Activate
ros2 lifecycle set /map_server activate
```

**Lifecycle states:**
1. **unconfigured** → Initial state
2. **inactive** → After configure (loaded but not publishing)
3. **active** → Publishing map on `/map` topic

---

## 📍 Localization (AMCL)

### Start AMCL (Adaptive Monte Carlo Localization)

```bash
source /opt/ros/foxy/setup.bash
ros2 run nav2_amcl amcl --ros-args \
  -p use_sim_time:=false \
  -p base_frame_id:=base_link \
  -p odom_frame_id:=odom \
  -p global_frame_id:=map \
  -p scan_topic:=scan
```

**What it does:**
- Localizes robot on pre-made map
- Uses particle filter to estimate position
- Publishes: `map → odom` transform
- Used for navigation (not mapping)

**Activate AMCL:**

```bash
source /opt/ros/foxy/setup.bash
ros2 lifecycle set /amcl configure
ros2 lifecycle set /amcl activate
```

**Difference from SLAM:**
- **SLAM**: Builds map + localizes simultaneously
- **AMCL**: Localizes on existing map only

---

## 🔧 Troubleshooting

### Can't See Topics from Laptop

**Problem:** Remote laptop can't see robot's ROS2 topics

**Solution 1 - Disable daemon:**
```bash
export ROS2CLI_DISABLE_DAEMON=1
ros2 daemon stop 2>/dev/null || true
pkill -f _ros2_daemon 2>/dev/null || true
```

**Solution 2 - Configure DDS:**
```bash
unset CYCLONEDDS_URI
unset RMW_IMPLEMENTATION
source ~/unitree_ros2/setup.sh
```

**Or use both:**
```bash
source ~/unitree_ros2/setup.sh
export ROS2CLI_DISABLE_DAEMON=1
```

---

## 📊 Verification Commands

### Check All Topics
```bash
source /opt/ros/foxy/setup.bash
ros2 topic list
```

**Expected topics:**
- `/utlidar/robot_odom` - Odometry
- `/utlidar/cloud_deskewed` - Point cloud
- `/scan` - Laser scan (after conversion)
- `/map` - Map from SLAM
- `/tf` - Transforms
- `/cmd_vel` - Velocity commands

### Check TF Tree
```bash
source /opt/ros/foxy/setup.bash
ros2 run tf2_ros tf2_echo map base_link
```

**Expected chain:**
```
map → odom → base_link → base_footprint
```

### Check SLAM Status
```bash
source /opt/ros/foxy/setup.bash
ros2 node info /slam_toolbox
```

### Monitor Topic Rates
```bash
source /opt/ros/foxy/setup.bash
ros2 topic hz /scan
ros2 topic hz /map
ros2 topic hz /tf
```

---

## 🎯 Complete Startup Sequence

### For SLAM Mapping (4 terminals):

**Terminal 1:**
```bash
/usr/bin/python3 ~/odom/odom_to_tf.py
```

**Terminal 2:**
```bash
source /opt/ros/foxy/setup.bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link base_footprint
```

**Terminal 3:**
```bash
source /opt/ros/foxy/setup.bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:=/home/unitree/odom/slam_params_go2.yaml
```

**Terminal 4:**
```bash
source /opt/ros/foxy/setup.bash
ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node \
  --ros-args \
  -r cloud_in:=/utlidar/cloud_deskewed \
  -r scan:=/scan \
  -p target_frame:=base_link \
  -p min_height:=-0.1 \
  -p max_height:=0.1 \
  -p angle_min:=-3.14159 \
  -p angle_max:=3.14159 \
  -p angle_increment:=0.0174533 \
  -p range_min:=0.2 \
  -p range_max:=30.0 \
  -p use_inf:=true
```

**Wait 10 seconds, then run once:**
```bash
source /opt/ros/foxy/setup.bash
ros2 param set /slam_toolbox use_sim_time false
ros2 param set /slam_toolbox base_frame base_link
```

---

## 📝 Summary of Components

| Component | Purpose | Keeps Running? |
|-----------|---------|----------------|
| odom_to_tf | Convert odom to TF | ✅ Yes |
| static_transform_publisher | base_link → base_footprint | ✅ Yes |
| pointcloud_to_laserscan | 3D → 2D scan conversion | ✅ Yes |
| slam_toolbox | Build map + localize | ✅ Yes |
| teleop_twist_keyboard | Drive robot | ✅ While exploring |
| cmd_vel_bridge | Control robot motors | ✅ Yes (on robot) |
| save_map | Save completed map | ❌ Run once |
| map_server | Publish saved map | ✅ For navigation |
| amcl | Localize on saved map | ✅ For navigation |

---

## 🔄 Workflows

### Mapping Mode (Creating New Map):
1. Start odom_to_tf
2. Start static TF publisher
3. Start pointcloud_to_laserscan
4. Start SLAM Toolbox
5. Drive with teleop
6. Save map when done

### Navigation Mode (Using Saved Map):
1. Start odom_to_tf
2. Start static TF publisher  
3. Start pointcloud_to_laserscan
4. Start map_server + activate
5. Start AMCL + activate
6. Use navigation stack (Nav2)

---

## 🎓 Understanding the Data Flow

```
Hardware (Go2 Robot)
  ↓
Unitree LiDAR SDK
  ↓
/utlidar/cloud_deskewed (PointCloud2)
  ↓
pointcloud_to_laserscan_node
  ↓
/scan (LaserScan)
  ↓
SLAM Toolbox → /map (builds map)
  ↑
TF Tree (knows robot position)
  ↑
odom_to_tf (converts odom to TF)
  ↑
/utlidar/robot_odom (odometry)
```

---

## 📚 Additional Resources

- **SLAM Toolbox docs:** https://github.com/SteveMacenski/slam_toolbox
- **Nav2 docs:** https://navigation.ros.org/
- **TF2 tutorials:** https://docs.ros.org/en/foxy/Tutorials/Intermediate/Tf2/Tf2-Main.html

---

**Created for Go2 Robot SLAM Mapping**
