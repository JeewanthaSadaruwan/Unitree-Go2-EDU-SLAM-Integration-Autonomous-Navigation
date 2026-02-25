# SLAM

## Robot
```bash
cd ~/odom
source /opt/ros/foxy/setup.bash
source ~/odom/install/setup.bash
./stop_all.sh
```

```bash
source /opt/ros/foxy/setup.bash
source ~/odom/xt16_ws/install/setup.bash
ros2 launch hesai_ros_driver start.py
```

```bash
cd ~/odom
./start_slam.sh
```

```bash
# Joint states (run in another terminal)
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces><NetworkInterface name="eth0"/></Interfaces></General></Domain></CycloneDDS>'
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
/usr/bin/python3.8 ~/odom/noneed/lowstate_to_joint_states.py
```

## Personal Computer
```bash
source /opt/ros/foxy/setup.bash
rviz2
```

# Map Saving

## Robot
```bash
cd ~/odom
./save_current_map.sh floor15_2
```

```bash
cd ~/odom
./save_current_map.sh
```

```bash
source /opt/ros/foxy/setup.bash
source ~/odom/install/setup.bash
ros2 run go2_mapping save_map.py /home/unitree/odom/maps/floor15_2
```

# Navigation

## Robot
```bash
cd ~/odom
source /opt/ros/foxy/setup.bash
source ~/odom/install/setup.bash
./stop_all.sh
```

```bash
source /opt/ros/foxy/setup.bash
source ~/odom/xt16_ws/install/setup.bash
ros2 launch hesai_ros_driver start.py
```

```bash
systemctl --user status go2-cmdvel-bridge.service
```

```bash
cd ~/odom
# If service is active (running), do NOT run ./start_bridge.sh
# If service is inactive, run bridge manually:
./start_bridge.sh
```

```bash
# Optional: stop service first, then run bridge manually
systemctl --user stop go2-cmdvel-bridge.service
cd ~/odom
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
source ~/go2_bringup_ws/install/setup.bash
source ~/odom/install/setup.bash
ros2 launch go2_mapping go2_bridge.launch.py

```

```bash
cd ~/odom
./start_navigation.sh /home/unitree/odom/maps/floor10.yaml
```

```bash
# Joint states (run in another terminal)
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces><NetworkInterface name="eth0"/></Interfaces></General></Domain></CycloneDDS>'
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
/usr/bin/python3.8 ~/odom/noneed/lowstate_to_joint_states.py
```

## Personal Computer
```bash
source /opt/ros/foxy/setup.bash
rviz2 -d /opt/ros/foxy/share/nav2_bringup/rviz/nav2_default_view.rviz
```

## Nav2 Runtime Sanity Checks
```bash
cd ~/odom
source /opt/ros/foxy/setup.bash

# Detect which recoveries costmap topic is currently published
./check_recoveries_costmap_topic.sh

ros2 topic list | grep -E "local_costmap|global_costmap|scan"
ros2 topic hz /scan
ros2 topic hz /local_costmap/costmap_updates
ros2 run tf2_ros tf2_echo odom base_link
ros2 topic echo /scan --once
# Replace <scan_frame> with header.frame_id from /scan
ros2 run tf2_ros tf2_echo base_link <scan_frame>
```

If `/local_costmap/costmap_updates` is near 0 Hz while `/scan` is alive, local obstacle marking is not working (usually missing TF from `base_link` to the scan frame).
