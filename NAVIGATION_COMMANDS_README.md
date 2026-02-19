# Navigation Commands (Quick Run)

## Cleanup (robot)
Purpose: stop old SLAM/navigation processes before starting a fresh run.

```bash
cd ~/odom
source /opt/ros/foxy/setup.bash
source ~/odom/install/setup.bash
./stop_slam.sh
pkill -f "go2_navigation.launch.py|nav2_|amcl|map_server|pointcloud_to_laserscan|odom_to_tf" || true
```

## Terminal 1 (robot): Hesai LiDAR
Purpose: start LiDAR driver and publish point cloud.

```bash
source /opt/ros/foxy/setup.bash
source ~/odom/xt16_ws/install/setup.bash
ros2 launch hesai_ros_driver start.py
```

## Terminal 2 (robot): cmd_vel bridge
Purpose: bridge ROS2 `/cmd_vel` commands to the robot controller.

```bash
source /opt/ros/foxy/setup.bash
source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
source ~/go2_bringup_ws/install/setup.bash
ros2 run cmd_vel_unitree_bridge cmd_vel_unitree_bridge_node
```

## Terminal 3 (robot): Navigation stack
Purpose: start map server, localization, and Nav2.

```bash
cd ~/odom
source /opt/ros/foxy/setup.bash
source ~/odom/install/setup.bash
ros2 launch go2_mapping go2_navigation.launch.py map_yaml:=/home/unitree/odom/maps/floor10.yaml cloud_topic:=/lidar_points
```
