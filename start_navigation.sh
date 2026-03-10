#!/bin/bash

# Go2 Robot Navigation Startup Script
# This script launches the complete navigation stack and prerequisites.

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}======================================${NC}"
echo -e "${GREEN}  Go2 Robot Navigation Stack${NC}"
echo -e "${GREEN}======================================${NC}"

# Resolve workspace root from this script location
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check if map file is provided
MAP_FILE="${1:-$ROOT_DIR/maps/floor10.yaml}"

if [ ! -f "$MAP_FILE" ]; then
    echo -e "${RED}Error: Map file not found: $MAP_FILE${NC}"
    echo -e "${YELLOW}Usage: $0 [map_file.yaml]${NC}"
    echo -e "${YELLOW}Example: $0 $ROOT_DIR/maps/floor10.yaml${NC}"
    exit 1
fi

echo -e "${GREEN}Using map: $MAP_FILE${NC}"

# Running SLAM Toolbox and AMCL/Nav2 together causes map->odom TF conflicts.
if pgrep -f "slam_toolbox" >/dev/null; then
    echo -e "${RED}Error: slam_toolbox is running.${NC}"
    echo -e "${YELLOW}Stop SLAM first (./stop_all.sh), then start navigation.${NC}"
    exit 1
fi

# Prevent duplicate odom->base_link TF publishers if user service is active.
if systemctl --user is-active --quiet go2-odom-to-tf.service 2>/dev/null; then
    echo -e "${YELLOW}go2-odom-to-tf.service is active; stopping it to avoid duplicate TF.${NC}"
    systemctl --user stop go2-odom-to-tf.service || {
        echo -e "${RED}Failed to stop go2-odom-to-tf.service${NC}"
        exit 1
    }
fi

# Disable pyenv contamination for ROS2 Python nodes.
export PYENV_VERSION=system
unset PYTHONHOME

# Source ROS2 workspace and optional overlays
source /opt/ros/foxy/setup.bash
source "$ROOT_DIR/install/setup.bash"
[[ -f ~/unitree_ros2/cyclonedds_ws/install/setup.bash ]] && source ~/unitree_ros2/cyclonedds_ws/install/setup.bash
[[ -f ~/go2_bringup_ws/install/setup.bash ]] && source ~/go2_bringup_ws/install/setup.bash
[[ -f "$ROOT_DIR/xt16_ws/install/setup.bash" ]] && source "$ROOT_DIR/xt16_ws/install/setup.bash"
[[ -f ~/go2_desc_ws/install/setup.bash ]] && source ~/go2_desc_ws/install/setup.bash

has_topic_publisher() {
    local topic="$1"
    local count
    count="$(timeout 3 ros2 topic info "$topic" 2>/dev/null | awk '/Publisher count:/ {print $3; exit}')"
    [[ -n "$count" && "$count" =~ ^[0-9]+$ && "$count" -gt 0 ]]
}

detect_model_mode() {
    local go2_prefix
    local robot_vlp_xacro
    go2_prefix="$(ros2 pkg prefix go2_description 2>/dev/null || true)"
    robot_vlp_xacro="$go2_prefix/share/go2_description/xacro/robot_VLP.xacro"
    if [[ -n "$go2_prefix" && -f "$robot_vlp_xacro" ]] && command -v xacro >/dev/null 2>&1; then
        echo "robot_vlp"
    else
        echo "legacy_go2_urdf"
    fi
}

# Force a valid CycloneDDS network interface on this host.
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
# Prefer eth0 on robot because Unitree lowstate/odom publishers are typically on eth0.
if ip -o link show eth0 >/dev/null 2>&1; then
    DDS_IFACE="eth0"
else
    DDS_IFACE="$(ip route 2>/dev/null | awk '/default/ {print $5; exit}')"
    if [[ -z "$DDS_IFACE" ]]; then
        DDS_IFACE="$(ip -o link show 2>/dev/null | awk -F': ' '$2 != "lo" {print $2; exit}')"
    fi
fi
if [[ -z "$DDS_IFACE" ]]; then
    DDS_IFACE="eth0"
fi
export CYCLONEDDS_URI="<CycloneDDS><Domain><General><Interfaces><NetworkInterface name=\"$DDS_IFACE\" priority=\"default\" multicast=\"default\" /></Interfaces></General></Domain></CycloneDDS>"
echo -e "${GREEN}Using CycloneDDS interface: $DDS_IFACE${NC}"

echo -e "${GREEN}Starting navigation prerequisites...${NC}"

MODEL_MODE="$(detect_model_mode)"
if [[ "$MODEL_MODE" == "robot_vlp" ]]; then
    LOWSTATE_SCRIPT="$ROOT_DIR/noneed/lowstate_to_joint_states.py"
    echo -e "${GREEN}[OK] Robot model mode: robot_VLP (rf/lf/rh/lh joints)${NC}"
else
    LOWSTATE_SCRIPT="$ROOT_DIR/noneed/lowstate_to_joint_states_nav.py"
    echo -e "${YELLOW}[WARN] Robot model mode: legacy GO2_URDF (FL/FR/RL/RR joints)${NC}"
    echo -e "${YELLOW}[WARN] go2_description/xacro not fully available; using legacy joint-state mapping.${NC}"
fi

# 0) Hesai XT16 driver
if ros2 pkg prefix hesai_ros_driver >/dev/null 2>&1; then
    if pgrep -f "hesai_ros_driver.*start.py|hesai_ros_driver_node" >/dev/null 2>&1; then
        echo -e "${YELLOW}[OK] Hesai driver already running${NC}"
    else
        ros2 launch hesai_ros_driver start.py >/tmp/start_nav_hesai.log 2>&1 &
        echo -e "${GREEN}[OK] Hesai driver started${NC}"
        sleep 2
    fi
else
    echo -e "${YELLOW}[WARN] hesai_ros_driver package not found (xt16_ws may not be built/sourced)${NC}"
fi

# 1) LowState -> JointStates (required for full leg TF tree)
if pgrep -f "lowstate_to_joint_states(_nav)?\.py" >/dev/null 2>&1; then
    echo -e "${YELLOW}[OK] LowState -> JointStates already running${NC}"
elif ros2 interface show unitree_go/msg/LowState >/dev/null 2>&1; then
    # Keep lowstate bridge on the same DDS interface as the rest of Nav2 stack.
    LOWSTATE_DDS_IFACE="$DDS_IFACE"
    LOWSTATE_PY="/usr/bin/python3.8"
    if [[ ! -x "$LOWSTATE_PY" ]]; then
        LOWSTATE_PY="/usr/bin/python3"
    fi

    bash -lc "export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp; \
export CYCLONEDDS_URI='<CycloneDDS><Domain><General><Interfaces><NetworkInterface name=\"$LOWSTATE_DDS_IFACE\"/></Interfaces></General></Domain></CycloneDDS>'; \
source /opt/ros/foxy/setup.bash; \
[[ -f ~/unitree_ros2/cyclonedds_ws/install/setup.bash ]] && source ~/unitree_ros2/cyclonedds_ws/install/setup.bash; \
exec $LOWSTATE_PY '$LOWSTATE_SCRIPT'" >/tmp/start_nav_lowstate.log 2>&1 &
    echo -e "${GREEN}[OK] LowState -> JointStates started${NC}"
else
    echo -e "${YELLOW}[WARN] unitree_go/msg/LowState not found; skipping lowstate_to_joint_states${NC}"
fi

for _ in {1..5}; do
    if has_topic_publisher "/joint_states"; then
        echo -e "${GREEN}[OK] /joint_states is being published${NC}"
        break
    fi
    sleep 1
done
if ! has_topic_publisher "/joint_states"; then
    echo -e "${YELLOW}[WARN] /joint_states has no publisher yet. Full leg TF may be missing.${NC}"
    echo -e "${YELLOW}[WARN] Check /tmp/start_nav_lowstate.log and DDS interface (expected: $DDS_IFACE).${NC}"
fi

# 2) cmd_vel bridge (if service is not already managing it)
if systemctl --user is-active --quiet go2-cmdvel-bridge.service 2>/dev/null; then
    echo -e "${YELLOW}[OK] go2-cmdvel-bridge.service is active (manual bridge not started)${NC}"
elif pgrep -f "cmd_vel_unitree_bridge|go2_bridge.launch.py" >/dev/null 2>&1; then
    echo -e "${YELLOW}[OK] cmd_vel bridge already running${NC}"
elif ros2 pkg prefix cmd_vel_unitree_bridge >/dev/null 2>&1; then
    ros2 launch go2_mapping go2_bridge.launch.py >/tmp/start_nav_bridge.log 2>&1 &
    echo -e "${GREEN}[OK] cmd_vel bridge started${NC}"
    sleep 1
else
    echo -e "${YELLOW}[WARN] cmd_vel_unitree_bridge package not found; navigation commands will not reach robot${NC}"
fi

echo -e "${GREEN}Launching navigation stack...${NC}"

# Launch navigation
ros2 launch go2_mapping go2_navigation.launch.py \
    map_yaml:=$MAP_FILE \
    use_sim_time:=false \
    params_file:=$ROOT_DIR/src/go2_mapping/config/go2_nav2_params.yaml \
    autostart:=true

echo -e "${YELLOW}Navigation stack stopped.${NC}"
