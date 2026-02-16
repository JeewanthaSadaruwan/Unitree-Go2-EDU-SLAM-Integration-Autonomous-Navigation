# Navigation Workflow - Before and After

## ❌ BEFORE (Manual Commands - Error Prone & Tedious)

### Step 1: Save the map
```bash
mkdir -p ~/maps
ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap \
"{name: {data: '/home/unitree/odom/maps/floor10_1'}}"
```

### Step 2: Start map server
```bash
ros2 run nav2_map_server map_server --ros-args \
-p yaml_filename:=/home/unitree/odom/maps/floor10_1.yaml \
-p use_sim_time:=false
```

### Step 3: Activate map server (in different terminal)
```bash
ros2 lifecycle get /map_server
ros2 lifecycle set /map_server configure
ros2 lifecycle set /map_server activate
```

### Step 4: Start AMCL
```bash
ros2 run nav2_amcl amcl --ros-args \
-p use_sim_time:=false \
-p base_frame_id:=base_link \
-p odom_frame_id:=odom \
-p global_frame_id:=map \
-p scan_topic:=scan_raw
```

### Step 5: Activate AMCL (in different terminal)
```bash
ros2 lifecycle set /amcl configure
ros2 lifecycle set /amcl activate
```

### Step 6: Start the bridge (in different terminal)
```bash
source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
source ~/go2_bringup_ws/install/setup.bash
ros2 run cmd_vel_unitree_bridge cmd_vel_unitree_bridge_node
```

### Step 7: Start Nav2
```bash
ros2 launch nav2_bringup navigation_launch.py \
use_sim_time:=false \
params_file:=/home/unitree/nav2/go2_nav2_params_foxy.yaml \
map_subscribe_transient_local:=true \
autostart:=false
```

### Step 8: Configure all Nav2 nodes (in different terminal)
```bash
ros2 lifecycle set /controller_server configure
ros2 lifecycle set /planner_server configure
ros2 lifecycle set /recoveries_server configure
ros2 lifecycle set /bt_navigator configure
ros2 lifecycle set /waypoint_follower configure
```

### Step 9: Activate all Nav2 nodes
```bash
ros2 lifecycle set /controller_server activate
ros2 lifecycle set /planner_server activate
ros2 lifecycle set /recoveries_server activate
ros2 lifecycle set /bt_navigator activate
ros2 lifecycle set /waypoint_follower activate
```

**Total:** 9 steps, multiple terminals, ~20+ commands to type! 😫

---

## ✅ AFTER (Automated Launch Files - Clean & Simple)

### To Save a Map:
```bash
./save_current_map.sh floor10_1
```

### To Start Navigation:

**Terminal 1: Bridge**
```bash
./start_bridge.sh
```

**Terminal 2: Navigation**
```bash
./start_navigation.sh
```

**Total:** 2 terminals, 2 simple commands! 🎉

---

## What Changed?

### New Files Created:

1. **Launch Files:**
   - `src/go2_mapping/launch/go2_navigation.launch.py` - Complete navigation stack with automatic lifecycle management
   - `src/go2_mapping/launch/go2_bridge.launch.py` - Bridge launcher

2. **Scripts:**
   - `src/go2_mapping/scripts/save_map.py` - Python script for saving maps
   - `save_current_map.sh` - Convenient map saving wrapper
   - `start_navigation.sh` - Navigation stack launcher
   - `start_bridge.sh` - Bridge launcher

3. **Documentation:**
   - `NAVIGATION.md` - Complete navigation guide

### Key Features:

✅ **Automatic lifecycle management** - No manual configure/activate needed
✅ **Single command startup** - Everything launches together  
✅ **Error checking** - Scripts validate map files exist
✅ **Sensible defaults** - Works out of the box
✅ **Configurable** - Easy to customize via launch arguments
✅ **Documented** - Full guide in NAVIGATION.md

### Usage Examples:

```bash
# Save a map with custom name
./save_current_map.sh my_office_map

# Save a map with auto-generated timestamp
./save_current_map.sh

# Start navigation with specific map
./start_navigation.sh /home/unitree/odom/maps/floor15_2.yaml

# Start navigation with default map
./start_navigation.sh

# Launch programmatically with custom params
ros2 launch go2_mapping go2_navigation.launch.py \
    map_yaml:=/path/to/map.yaml \
    base_frame_id:=base_footprint \
    scan_topic:=/scan
```

## Benefits:

1. **Faster startup** - 2 commands vs 20+
2. **Less error-prone** - No forgetting steps
3. **Consistent** - Same process every time
4. **Maintainable** - Changes in one place
5. **Professional** - Industry standard practice
6. **Shareable** - Easy for others to use
7. **Documented** - Clear usage instructions

---

## Migration Notes:

Your old workflow still works! But now you have better options:

- Old way: Manual commands (still available if needed)
- New way: Launch files (recommended for normal use)

All the same ROS2 nodes and parameters are being used, just orchestrated automatically instead of manually.
