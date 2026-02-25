#!/bin/bash
# Kill SLAM + Navigation related processes and clean up
# Usage: ./stop_all.sh

SESSION="go2_slam"

echo "=== Stopping Go2 SLAM + Navigation System ==="
echo ""

# Kill tmux session if it exists
if tmux has-session -t $SESSION 2>/dev/null; then
    echo "Killing tmux session: $SESSION"
    tmux kill-session -t $SESSION
    echo "✓ Tmux session killed"
else
    echo "No tmux session found"
fi

echo ""
echo "Stopping services..."

# Stop user-level cmd_vel bridge service if it is running
if systemctl --user is-active --quiet go2-cmdvel-bridge.service 2>/dev/null; then
    systemctl --user stop go2-cmdvel-bridge.service && echo "✓ Stopped go2-cmdvel-bridge.service" || echo "  (failed to stop go2-cmdvel-bridge.service)"
fi

# Stop user-level odom TF service if it is running
if systemctl --user is-active --quiet go2-odom-to-tf.service 2>/dev/null; then
    systemctl --user stop go2-odom-to-tf.service && echo "✓ Stopped go2-odom-to-tf.service" || echo "  (failed to stop go2-odom-to-tf.service)"
fi

echo ""
echo "Killing SLAM-related processes..."

# Kill SLAM Toolbox
pkill -f "slam_toolbox" && echo "✓ Killed slam_toolbox" || echo "  (slam_toolbox not running)"

# Kill robot_state_publisher
pkill -f "robot_state_publisher" && echo "✓ Killed robot_state_publisher" || echo "  (robot_state_publisher not running)"

# Kill odom_to_tf
pkill -f "odom_to_tf.py" && echo "✓ Killed odom_to_tf" || echo "  (odom_to_tf not running)"

# Kill pc2_relay
pkill -f "pc2_relay_be.py" && echo "✓ Killed pc2_relay" || echo "  (pc2_relay not running)"

# Kill static TF publisher aliases
pkill -f "static_transform_publisher.*base_link.*base" && echo "✓ Killed static_transform_publisher (base)" || echo "  (static_transform_publisher base not running)"
pkill -f "static_transform_publisher.*base_link.*hesai_lidar" && echo "✓ Killed static_transform_publisher (hesai_lidar)" || echo "  (static_transform_publisher hesai_lidar not running)"

# Kill pointcloud_to_laserscan
pkill -f "pointcloud_to_laserscan" && echo "✓ Killed pointcloud_to_laserscan" || echo "  (pointcloud_to_laserscan not running)"

# Kill optional joint-state bridge script (manual run)
pkill -f "lowstate_to_joint_states.py" && echo "✓ Killed lowstate_to_joint_states.py" || echo "  (lowstate_to_joint_states.py not running)"

echo ""
echo "Killing Navigation-related processes..."

# Kill navigation launch and nodes
pkill -f "go2_navigation.launch.py" && echo "✓ Killed go2_navigation.launch.py" || echo "  (go2_navigation.launch.py not running)"
pkill -f "nav2_" && echo "✓ Killed nav2_* nodes" || echo "  (nav2_* nodes not running)"
pkill -f "amcl" && echo "✓ Killed amcl" || echo "  (amcl not running)"
pkill -f "map_server" && echo "✓ Killed map_server" || echo "  (map_server not running)"
pkill -f "planner_server" && echo "✓ Killed planner_server" || echo "  (planner_server not running)"
pkill -f "controller_server" && echo "✓ Killed controller_server" || echo "  (controller_server not running)"
pkill -f "recoveries_server" && echo "✓ Killed recoveries_server" || echo "  (recoveries_server not running)"
pkill -f "bt_navigator" && echo "✓ Killed bt_navigator" || echo "  (bt_navigator not running)"
pkill -f "waypoint_follower" && echo "✓ Killed waypoint_follower" || echo "  (waypoint_follower not running)"
pkill -f "lifecycle_manager" && echo "✓ Killed lifecycle_manager" || echo "  (lifecycle_manager not running)"
pkill -f "goal_pose_relay" && echo "✓ Killed goal_pose_relay" || echo "  (goal_pose_relay not running)"

# Kill bridge process if manually launched
pkill -f "go2_bridge.launch.py" && echo "✓ Killed go2_bridge.launch.py" || echo "  (go2_bridge.launch.py not running)"
pkill -f "cmd_vel_unitree_bridge" && echo "✓ Killed cmd_vel bridge process" || echo "  (cmd_vel bridge process not running)"

# Optional: stop lidar driver if running
pkill -f "hesai_ros_driver" && echo "✓ Killed hesai_ros_driver" || echo "  (hesai_ros_driver not running)"

# Clean up any zombie ros2 processes
pkill -9 -f "ros2" 2>/dev/null

echo ""
echo "Waiting 2 seconds for processes to terminate..."
sleep 2

# Check if anything is still running
REMAINING=$(ps aux | grep -E "slam_toolbox|odom_to_tf|pointcloud_to_laserscan|lowstate_to_joint_states.py|static_transform_publisher|robot_state_publisher|pc2_relay|go2_navigation.launch.py|nav2_|amcl|map_server|planner_server|controller_server|recoveries_server|bt_navigator|waypoint_follower|lifecycle_manager|goal_pose_relay|go2_bridge.launch.py|cmd_vel_unitree_bridge|hesai_ros_driver" | grep -v grep | wc -l)

if [ $REMAINING -eq 0 ]; then
    echo ""
    echo "✓ All SLAM + Navigation processes stopped successfully!"
    echo ""
    echo "You can now start fresh with: ./start_slam.sh or ./start_navigation.sh"
else
    echo ""
    echo "⚠ Warning: $REMAINING process(es) still running"
    echo "Run this command to force kill: pkill -9 -f ros2"
fi

# Clean up temp files if they exist
rm -rf /tmp/go2_slam_* /tmp/go2_nav_* 2>/dev/null

echo ""
echo "=== Cleanup Complete ==="
