# Go2 Robot Navigation Guide

This guide explains how to use the navigation stack for the Unitree Go2 robot.

## Overview

The navigation system consists of:
- **Map Server**: Provides the saved map to the navigation stack
- **AMCL**: Adaptive Monte Carlo Localization for robot localization
- **Nav2**: Complete navigation stack including path planning and obstacle avoidance
- **Bridge**: Connects Nav2 cmd_vel commands to the Unitree Go2 robot

## Prerequisites

Before starting navigation, ensure you have:
1. A saved map (see "Creating a Map" section)
2. The Nav2 parameters file at `/home/unitree/nav2/go2_nav2_params_foxy.yaml`
3. All required ROS2 packages installed

## Quick Start

### 1. Save a Map (First Time Only)

After running SLAM and creating a good map:

```bash
./save_current_map.sh floor10_1
```

Or to auto-generate a timestamped name:
```bash
./save_current_map.sh
```

This creates two files in `~/odom/maps/`:
- `map_name.pgm` - The map image
- `map_name.yaml` - The map metadata

### 2. Launch Navigation Stack

**On the robot/Jetson**, run these in separate terminals:

#### Terminal 1: Start the bridge
```bash
./start_bridge.sh
```

#### Terminal 2: Start navigation
```bash
./start_navigation.sh /home/unitree/odom/maps/floor10_1.yaml
```

Or use the default map:
```bash
./start_navigation.sh
```

That's it! The navigation stack will automatically:
- Load the map
- Start AMCL for localization
- Configure and activate all Nav2 nodes
- Ready to receive navigation goals

## Using Navigation

### From RViz

1. Launch RViz on your development machine
2. Add the Nav2 plugin
3. Set the initial pose using "2D Pose Estimate"
4. Send navigation goals using "2D Nav Goal"

### From Command Line

Send a navigation goal:
```bash
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: 'map'}, pose: {position: {x: 2.0, y: 1.0, z: 0.0}, orientation: {w: 1.0}}}}"
```

### From Python

```python
import rclpy
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose

# ... create node and action client ...
goal_msg = NavigateToPose.Goal()
goal_msg.pose.header.frame_id = 'map'
goal_msg.pose.pose.position.x = 2.0
goal_msg.pose.pose.position.y = 1.0
# ... send goal ...
```

## Launch File Details

### Navigation Launch File

**File**: `src/go2_mapping/launch/go2_navigation.launch.py`

**Parameters**:
- `map_yaml`: Path to the map YAML file (default: `/home/unitree/odom/maps/floor10_1.yaml`)
- `use_sim_time`: Use simulation time (default: `false`)
- `params_file`: Nav2 parameters file (default: `/home/unitree/nav2/go2_nav2_params_foxy.yaml`)
- `autostart`: Auto-start lifecycle nodes (default: `true`)
- `base_frame_id`: Robot base frame (default: `base_link`)
- `odom_frame_id`: Odometry frame (default: `odom`)
- `global_frame_id`: Global/map frame (default: `map`)
- `scan_topic`: Laser scan topic (default: `scan_raw`)

**Launch with custom parameters**:
```bash
ros2 launch go2_mapping go2_navigation.launch.py \
    map_yaml:=/path/to/your/map.yaml \
    base_frame_id:=base_footprint
```

### Bridge Launch File

**File**: `src/go2_mapping/launch/go2_bridge.launch.py`

Launches the cmd_vel bridge that translates Nav2 velocity commands to Unitree Go2 robot commands.

**Launch directly**:
```bash
ros2 launch go2_mapping go2_bridge.launch.py
```

## Map Management

### Save Current Map

Use the provided script:
```bash
ros2 run go2_mapping save_map.py /home/unitree/odom/maps/my_map
```

Or use the wrapper script:
```bash
./save_current_map.sh my_map
```

### List Available Maps

```bash
ls -lh ~/odom/maps/
```

### Switch Maps

Stop navigation and restart with a different map:
```bash
./start_navigation.sh /home/unitree/odom/maps/different_map.yaml
```

## Troubleshooting

### Map Server Won't Start
- Verify the map YAML file exists and path is correct
- Check that both .pgm and .yaml files are present

### AMCL Not Localizing
- Ensure you've set an initial pose in RViz
- Check that the scan topic is publishing: `ros2 topic echo /scan_raw`
- Verify the base_link → odom → map transform chain

### Navigation Goals Failing
- Check that all lifecycle nodes are active:
  ```bash
  ros2 lifecycle list
  ```
- Verify the Nav2 parameters file exists
- Check costmap topics for obstacles

### Bridge Not Working
- Ensure the Unitree workspaces are sourced:
  ```bash
  source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
  source ~/go2_bringup_ws/install/setup.bash
  ```
- Verify cmd_vel commands are being published: `ros2 topic echo /cmd_vel`

## System Architecture

```
┌─────────────────┐
│   RViz/Client   │
└────────┬────────┘
         │ Nav Goals
         ▼
┌─────────────────┐
│   Nav2 Stack    │ ← Map Server + AMCL
│  (Planner, etc) │
└────────┬────────┘
         │ /cmd_vel
         ▼
┌─────────────────┐
│  Unitree Bridge │
└────────┬────────┘
         │ Unitree SDK
         ▼
┌─────────────────┐
│   Go2 Robot     │
└─────────────────┘
```

## Advanced Usage

### Manual Lifecycle Management

If you set `autostart:=false`, you'll need to manually activate nodes:

```bash
# Configure nodes
ros2 lifecycle set /controller_server configure
ros2 lifecycle set /planner_server configure
ros2 lifecycle set /recoveries_server configure
ros2 lifecycle set /bt_navigator configure
ros2 lifecycle set /waypoint_follower configure

# Activate nodes
ros2 lifecycle set /controller_server activate
ros2 lifecycle set /planner_server activate
ros2 lifecycle set /recoveries_server activate
ros2 lifecycle set /bt_navigator activate
ros2 lifecycle set /waypoint_follower activate
```

### Checking Node Status

```bash
# List all lifecycle nodes
ros2 lifecycle nodes

# Get state of a specific node
ros2 lifecycle get /map_server
ros2 lifecycle get /amcl
```

## Next Steps

- Configure Nav2 parameters for your specific environment
- Tune AMCL parameters for better localization
- Set up waypoint following for patrol routes
- Integrate with higher-level mission planning
