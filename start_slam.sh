#!/bin/bash

# Go2 SLAM Startup Script
# This script starts all SLAM nodes in separate terminals to avoid launch file DDS issues

echo "=== Starting Go2 SLAM System ==="

# Disable pyenv temporarily
export PYENV_VERSION=system
unset PYTHONHOME

# Resolve workspace root from this script location
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source ROS2 and workspace
source /opt/ros/foxy/setup.bash
source "$ROOT_DIR/install/setup.bash"

# Source CycloneDDS overlay if present
[[ -f ~/unitree_ros2/cyclonedds_ws/install/setup.bash ]] && source ~/unitree_ros2/cyclonedds_ws/install/setup.bash

# Force a valid CycloneDDS network interface on this host.
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
DDS_IFACE="$(ip route 2>/dev/null | awk '/default/ {print $5; exit}')"
if [[ -z "$DDS_IFACE" ]]; then
    DDS_IFACE="$(ip -o link show 2>/dev/null | awk -F': ' '$2 != "lo" {print $2; exit}')"
fi
if [[ -z "$DDS_IFACE" ]]; then
    DDS_IFACE="eth0"
fi
export CYCLONEDDS_URI="<CycloneDDS><Domain><General><Interfaces><NetworkInterface name=\"$DDS_IFACE\" priority=\"default\" multicast=\"default\" /></Interfaces></General></Domain></CycloneDDS>"
echo "Using CycloneDDS interface: $DDS_IFACE"

# Source optional overlays if present
[[ -f ~/go2_bringup_ws/install/setup.bash ]] && source ~/go2_bringup_ws/install/setup.bash
[[ -f "$ROOT_DIR/xt16_ws/install/setup.bash" ]] && source "$ROOT_DIR/xt16_ws/install/setup.bash"

HAS_GO2_DESC=0
if [[ -f ~/go2_desc_ws/install/setup.bash ]]; then
    source ~/go2_desc_ws/install/setup.bash
    HAS_GO2_DESC=1
fi

has_topic_publisher() {
    local topic="$1"
    local count
    count="$(ros2 topic info "$topic" 2>/dev/null | awk '/Publisher count:/ {print $3; exit}')"
    [[ -n "$count" && "$count" =~ ^[0-9]+$ && "$count" -gt 0 ]]
}

# Kill any existing processes
pkill -9 -f "slam_toolbox|odom_to_tf|static_transform|pointcloud_to_laserscan|robot_state_publisher|pc2_relay|lowstate_to_joint_states.py"
sleep 1

echo "Starting nodes..."

# 0. Hesai XT16 driver
if ros2 pkg prefix hesai_ros_driver >/dev/null 2>&1; then
    if pgrep -f "hesai_ros_driver_node" >/dev/null 2>&1; then
        echo "✓ Hesai driver already running"
    else
        ros2 launch hesai_ros_driver start.py >/tmp/start_slam_hesai.log 2>&1 &
        echo "✓ Hesai driver started"
        sleep 2
    fi
else
    echo "⚠ hesai_ros_driver package not found (xt16_ws may not be built/sourced)"
fi

# Detect active odometry topic for odom_to_tf
ODOM_TOPIC="/utlidar/robot_odom"
for _ in {1..8}; do
    if has_topic_publisher "/utlidar/robot_odom"; then
        ODOM_TOPIC="/utlidar/robot_odom"
        break
    fi
    if has_topic_publisher "/lio_sam_ros2/mapping/odometry"; then
        ODOM_TOPIC="/lio_sam_ros2/mapping/odometry"
        break
    fi
    sleep 1
done
if [[ "$ODOM_TOPIC" != "/utlidar/robot_odom" ]]; then
    echo "✓ Using odometry topic: $ODOM_TOPIC"
elif ! has_topic_publisher "/utlidar/robot_odom"; then
    echo "⚠ No publisher for /utlidar/robot_odom (odom_to_tf will wait)"
fi

# 1. Robot State Publisher
if [[ "$HAS_GO2_DESC" -eq 1 ]] && command -v xacro >/dev/null 2>&1; then
    ros2 run robot_state_publisher robot_state_publisher --ros-args \
        -p robot_description:="$(xacro "$(ros2 pkg prefix go2_description)/share/go2_description/xacro/robot_VLP.xacro")" \
        -p use_sim_time:=false 2>/dev/null &
    echo "✓ Robot State Publisher started (robot_VLP.xacro)"
else
    ros2 run robot_state_publisher robot_state_publisher \
        --ros-args \
        -p use_sim_time:=false \
        __params:=<(echo "robot_state_publisher:
  ros__parameters:
    robot_description: '$(cat "$ROOT_DIR/GO2_URDF/urdf/go2_description.urdf" | sed "s/'/\\\\'/g")'") 2>/dev/null &
    echo "✓ Robot State Publisher started (GO2_URDF fallback)"
fi
sleep 1

# 2. LowState -> JointStates (required for full leg TF tree in RViz)
if ros2 interface show unitree_go/msg/LowState >/dev/null 2>&1; then
    /usr/bin/python3 "$ROOT_DIR/noneed/lowstate_to_joint_states.py" &
    echo "✓ LowState -> JointStates started"
else
    echo "⚠ unitree_go/msg/LowState not found; skipping lowstate_to_joint_states"
fi
sleep 1

# 3. Odom to TF
/usr/bin/python3 "$ROOT_DIR/src/go2_mapping/go2_mapping/odom_to_tf.py" \
    --ros-args -r /utlidar/robot_odom:="$ODOM_TOPIC" &
echo "✓ Odom to TF started"
sleep 1

# 4. PC2 Relay
/usr/bin/python3 ~/pc2_relay_be.py &
echo "✓ PC2 Relay started"
sleep 1

# 5. Static TF for Hesai alignment
if [[ "$HAS_GO2_DESC" -eq 1 ]]; then
    # robot_VLP includes base_link -> velodyne in URDF
    ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 velodyne hesai_lidar 2>/dev/null &
    echo "✓ Static TF (velodyne -> hesai_lidar) started"
else
    ros2 run tf2_ros static_transform_publisher 0.15 0 0.12 0 0 0 base_link hesai_lidar 2>/dev/null &
    echo "✓ Static TF (base_link -> hesai_lidar) started"
    # GO2_URDF root alignment: odom->base_link and URDF rooted at 'base'
    ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link base 2>/dev/null &
    echo "✓ Static TF (base_link -> base) started"
fi
sleep 1

# 6. PointCloud to LaserScan
ros2 run pointcloud_to_laserscan pointcloud_to_laserscan_node --ros-args \
    --params-file "$ROOT_DIR/src/go2_mapping/config/pointcloud_to_laserscan.yaml" \
    -r cloud_in:=/lidar_points \
    -r scan:=/scan_raw 2>/dev/null &
echo "✓ PointCloud to LaserScan started"
sleep 2

# 7. SLAM Toolbox
ros2 run slam_toolbox async_slam_toolbox_node --ros-args \
    --params-file "$ROOT_DIR/src/go2_mapping/config/slam_params.yaml" \
    -r scan:=/scan_raw 2>/dev/null &
echo "✓ SLAM Toolbox started"

echo ""
echo "=== All SLAM nodes started successfully! ==="
echo ""
echo "To view in RViz: rviz2"
echo "To stop all nodes: ./stop_all.sh"
echo ""
echo "Note: Ignore 'bad_alloc' warnings - they are harmless ROS2 Foxy logging bugs"
echo ""

# Keep script running
wait