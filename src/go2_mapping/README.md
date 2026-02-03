# Go2 Mapping Package

ROS2 package for Go2 robot SLAM and mapping operations.

## Package Structure

```
go2_mapping/
├── go2_mapping/          # Python nodes
│   ├── odom_to_tf.py              # Full 3D odom → TF broadcaster
│   ├── odom_to_tf_planar.py       # Planar 2D odom → TF broadcaster
│   ├── scan_stamp_fix.py          # LaserScan timestamp fixer
│   └── wifi_topic_relay.py        # Topic relay for WiFi visualization
├── config/               # Configuration files
│   ├── slam_params_go2.yaml
│   └── slam_params.yaml
├── launch/               # Launch files
│   └── go2_mapping.launch.py
├── package.xml
└── setup.py
```

## Installation

### 1. Build the workspace

```bash
cd /home/unitree/odom
colcon build --symlink-install
```

### 2. Source the workspace

```bash
source /home/unitree/odom/install/setup.bash
```

Add to your `~/.bashrc` for automatic sourcing:
```bash
echo "source /home/unitree/odom/install/setup.bash" >> ~/.bashrc
```

## Nodes

### odom_to_tf
Converts odometry messages to TF transforms (odom → base_link).

**Subscribes:**
- `/utlidar/robot_odom` (nav_msgs/Odometry) - RELIABLE QoS

**Publishes:**
- TF transform: `odom` → `base_link`
- Logs message count every second

**Run (RECOMMENDED):**
```bash
/usr/bin/python3 ~/odom/odom_to_tf.py
```

**What it does:**
1. Subscribes to robot odometry from LiDAR
2. Extracts position (x, y, z) and orientation (quaternion)
3. Broadcasts as TF transform with original timestamp
4. Critical for SLAM - without this, SLAM can't locate the robot

**Expected output:**
```
[INFO] [odom_to_tf]: odom_to_tf started (RELIABLE sub)
[INFO] [odom_to_tf]: rx odom msgs: 151, last stamp: ...
```

### odom_to_tf_planar
Planar (2D) version - extracts only yaw rotation, sets z=0, guards against time reversals.

**Run:**
```bash
/usr/bin/python3 ~/odom/odom_to_tf_now.py
```

**Use this if:**
- You want strict 2D mapping
- You see height drift issues
- Your robot operates on flat ground only

### scan_stamp_fix
Republishes laser scans with current timestamps.

**Run:**
```bash
ros2 run go2_mapping scan_stamp_fix
```

### wifi_topic_relay
Relays topics over WiFi with proper QoS settings.

**Run:**
```bash
ros2 run go2_mapping wifi_topic_relay --prefix /wifi --scan
```

## Usage

### ⚠️ RECOMMENDED: Direct Python Execution

Due to Python version conflicts between system Python and ROS2, use direct execution:

### Terminal 1 - Odom to TF (KEEP RUNNING)
```bash
/usr/bin/python3 ~/odom/odom_to_tf.py
```

**What you should see:**
```
[INFO] [odom_to_tf]: odom_to_tf started (RELIABLE sub)
[INFO] [odom_to_tf]: rx odom msgs: 151, last stamp: 1770007266.881025314
[INFO] [odom_to_tf]: rx odom msgs: 298, last stamp: 1770007267.877771854
```

**What this means:**
- ✅ Node is running
- ✅ Receiving odometry messages (~150 Hz)
- ✅ Broadcasting TF transforms (odom → base_link)
- ✅ Timestamps are valid

### Terminal 2 - SLAM Toolbox
```bash
source /opt/ros/foxy/setup.bash
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:=/home/unitree/odom/src/go2_mapping/config/slam_params_go2.yaml
```

## Configuration

Edit SLAM parameters in `config/slam_params_go2.yaml`:

- `resolution`: Map resolution (default: 0.05m)
- `max_laser_range`: Maximum laser range (default: 30m)
- `scan_topic`: LaserScan topic (default: /scan)
- `base_frame`: Robot base frame (default: base_link)
- `odom_frame`: Odometry frame (default: odom)
- `map_frame`: Map frame (default: map)

## Verification Commands

### 1. Check if odom messages are coming
```bash
source /opt/ros/foxy/setup.bash
ros2 topic echo /utlidar/robot_odom --once
```

**Expected:** Shows position, orientation, velocities (see example below)

### 2. Check if odom_to_tf is running
Look for this in Terminal 1:
```
[INFO] [odom_to_tf]: rx odom msgs: 151, last stamp: ...
```
- Message count should be **increasing** (typically ~150/sec)
- If stuck at "waiting for odom messages..." → Check LiDAR is running

### 3. Check TF transform values (BEST VERIFICATION)
```bash
source /opt/ros/foxy/setup.bash
ros2 run tf2_ros tf2_echo odom base_link
```

### Problem: "waiting for odom messages..." doesn't stop
**Cause:** LiDAR node not publishing odometry

**Solution:**
```bash
# Check if topic exists
source /opt/ros/foxy/setup.bash
ros2 topic list | grep odom

# Check publishing rate
ros2 topic hz /utlidar/robot_odom
```
If no output → Start your LiDAR node first

### Problem: "ros2: command not found"
**Solution:** Source ROS2 first:
```bash
source /opt/ros/foxy/setup.bash
```

### Problem: "ModuleNotFoundError: No module named 'rclpy._rclpy'"
**Cause:** Python version mismatch (pyenv vs system Python)

**Solution:** Use system Python directly:
```bash
/usr/bin/python3 ~/odom/odom_to_tf.py
```
**NOT:** `python3` or `ros2 run`

### Problem: "bad_alloc caught: std::bad_alloc"
**Cause:** Memory allocation error with `ros2 run` launcher

**Solution:** Use direct Python execution instead:
```bash
/usr/bin/python3 ~/odom/odom_to_tf.py
```

### Problem: Exit Code 137
**Cause:** Process killed by system (out of memory)

**Solution:** 
- Close other applications
- Check memory: `free -h`
- Reboot if necessary

### Problem: TF transform not updating
**Check:**
1. Is odom_to_tf showing increasing message count?
2. Run: `ros2 topic hz /tf` - should show ~150 Hz
3. Check timestamps aren't frozen in the logs

### SLAM not creating map
**Prerequisites checklist:**
1. ✅ odom_to_tf running and receiving messages
2. ✅ LiDAR publishing to /scan: `ros2 topic hz /scan`
3. ✅ Frame names match in slam_params.yaml
4. ✅ TF transform exists: `ros2 run tf2_ros tf2_echo odom base_link`
```bash
source /opt/ros/foxy/setup.bash
ros2 topic hz /tf
```
Should show ~150 Hz (matches odom rate)

### 5. Visualize TF tree structure
```bash
source /opt/ros/foxy/setup.bash
ros2 run tf2_tools view_frames
```
Creates `frames.pdf` showing: `odom → base_link`

## Troubleshooting

**No odom messages:**
- Check if LiDAR is publishing: `ros2 topic hz /utlidar/robot_odom`

**TF not broadcasting:**
- Verify odom_to_tf node is running: `ros2 node list | grep odom`
- Check logs: Look for "odom_to_tf started" message

**SLAM not working:**
- Ensure odom→base_link transform exists
- Verify scan topic: `ros2 topic hz /scan`
- Check SLAM params match your frame names
