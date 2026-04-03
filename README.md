# SLAM

## Robot
```bash
cd ~/SLAM
source /opt/ros/foxy/setup.bash
source ~/SLAM/install/setup.bash
./stop_all.sh
```

```bash
cd ~/SLAM
./start_slam.sh
```

```bash
# Optional: run rosbridge in a separate terminal (for laptop relay)
cd ~/SLAM
./start_rosbridge.sh
```
## Personal Computer

Laptop relay should connect to robot's IP:
[note : use the file go2_rosbridge_rvirelay.py]
```bash
source /opt/ros/foxy/setup.bash
export PYENV_VERSION=system
unset PYTHONHOME
unset CYCLONEDDS_URI FASTRTPS_DEFAULT_PROFILES_FILE
export ROS_DOMAIN_ID=0
export RMW_IMPLEMENTATION=rmw_fastrtps_cpp
export ROS_LOCALHOST_ONLY=0
echo "A: $ROS_DOMAIN_ID $RMW_IMPLEMENTATION $ROS_LOCALHOST_ONLY"
/usr/bin/python3 /home/sahas/Documents/github/RAI_examples/go2_rosbridge_rviz_relay.py \
  --rosbridge-url ws://10.224.44.104:9090 \
  --prefix '' \
  --subscribe-throttle-ms 100 \
  --topics /tf,/tf_static,/map,/scan_raw,/utlidar/robot_odom \
  --topic-types /tf=tf2_msgs/TFMessage,/tf_static=tf2_msgs/TFMessage,/map=nav_msgs/OccupancyGrid,/scan_raw=sensor_msgs/LaserScan,/utlidar/robot_odom=nav_msgs/Odometry
```
Then rviz2 need to be started ( save "rviz/go2_slam_visualization.rviz" and launch )
```bash
source /opt/ros/foxy/setup.bash
rviz2 -d <path_to_the_saved_file>/rviz/go2_slam_visualization.rviz

#eg: rviz2 -d /home/wso2-robotics/Desktop/rviz/go2_slam_visualization.rviz
```

# Map Saving

## Robot
```bash
cd ~/SLAM
./save_current_map.sh floor15_3
```

```bash
cd ~/SLAM
./save_current_map.sh
```

```bash
source /opt/ros/foxy/setup.bash
source ~/SLAM/install/setup.bash
ros2 run go2_mapping save_map.py /home/unitree/SLAM/maps/floor15_2
```

# Navigation

## Robot
```bash
cd ~/SLAM
source /opt/ros/foxy/setup.bash
source ~/SLAM/install/setup.bash
./stop_all.sh
```

```bash
cd ~/SLAM
./start_navigation.sh /home/unitree/SLAM/maps/floor15_3.yaml
```

`start_navigation.sh` now auto-starts:
- Hesai driver (if `hesai_ros_driver` is available)
- `lowstate_to_joint_states.py` for full leg TF tree
- cmd_vel bridge (unless `go2-cmdvel-bridge.service` is already active)
- Nav2 launch stack

So you do not need to run `./start_bridge.sh` separately for normal navigation startup.

If you need laptop relay / voice navigation via rosbridge, run this in another terminal:
```bash
cd ~/SLAM
./start_rosbridge.sh
```

Optional check:
```bash
systemctl --user status go2-cmdvel-bridge.service
```

## Personal Computer

Terminal A --> Run rosbridge with nav2 configuration
```bash
source /opt/ros/foxy/setup.bash
python3 /home/sahas/Documents/github/RAI_examples/go2_rosbridge_rviz_relay.py \
  --rosbridge-url ws://10.224.44.104:9090 \
  --prefix '' \
  --nav-minimal \
  --enable-nav2-action-proxy
```
Terminal B --> run rviz2 in nav2 default configuration

```bash
source /opt/ros/foxy/setup.bash
rviz2 -d /opt/ros/foxy/share/nav2_bringup/rviz/nav2_default_view.rviz
```


## Read XYZ and Yaw from RViz Clicks
```bash
cd ~/SLAM
source /opt/ros/foxy/setup.bash
source ~/SLAM/install/setup.bash
ros2 run go2_mapping rviz_click_logger
```

- RViz tool `Publish Point` publishes `/clicked_point` (`x, y, z`).
- RViz tool `2D Nav Goal` publishes `/goal_pose` (`x, y, z, yaw`).
- The logger prints yaw in both radians and degrees.


## Nav2 Runtime Sanity Checks
```bash
cd ~/SLAM
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
