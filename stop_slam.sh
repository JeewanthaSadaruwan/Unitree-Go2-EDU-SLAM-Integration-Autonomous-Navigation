#!/bin/bash
# Kill all SLAM-related processes and clean up
# Usage: ./stop_slam.sh

SESSION="go2_slam"

echo "=== Stopping Go2 SLAM System ==="
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
echo "Killing SLAM-related processes..."

# Kill SLAM Toolbox
pkill -f "slam_toolbox" && echo "✓ Killed slam_toolbox" || echo "  (slam_toolbox not running)"

# Kill robot_state_publisher
pkill -f "robot_state_publisher" && echo "✓ Killed robot_state_publisher" || echo "  (robot_state_publisher not running)"

# Kill odom_to_tf
pkill -f "odom_to_tf.py" && echo "✓ Killed odom_to_tf" || echo "  (odom_to_tf not running)"

# Kill pc2_relay
pkill -f "pc2_relay_be.py" && echo "✓ Killed pc2_relay" || echo "  (pc2_relay not running)"

# Kill static TF publisher (both versions)
pkill -f "static_transform_publisher.*base_link.*base_footprint" && echo "✓ Killed static_transform_publisher (base_footprint)" || echo "  (static_transform_publisher base_footprint not running)"
pkill -f "static_transform_publisher.*base_link.*hesai_lidar" && echo "✓ Killed static_transform_publisher (hesai_lidar)" || echo "  (static_transform_publisher hesai_lidar not running)"

# Kill pointcloud_to_laserscan
pkill -f "pointcloud_to_laserscan" && echo "✓ Killed pointcloud_to_laserscan" || echo "  (pointcloud_to_laserscan not running)"

# Kill any ros2 launch processes
pkill -f "ros2 launch" && echo "✓ Killed ros2 launch processes" || echo "  (no ros2 launch processes)"

# Clean up any zombie ros2 processes
pkill -9 -f "ros2" 2>/dev/null

echo ""
echo "Waiting 2 seconds for processes to terminate..."
sleep 2

# Check if anything is still running
REMAINING=$(ps aux | grep -E "slam_toolbox|odom_to_tf|pointcloud_to_laserscan|static_transform_publisher|robot_state_publisher|pc2_relay" | grep -v grep | wc -l)

if [ $REMAINING -eq 0 ]; then
    echo ""
    echo "✓ All SLAM processes stopped successfully!"
    echo ""
    echo "You can now start fresh with: ./start_slam.sh"
else
    echo ""
    echo "⚠ Warning: $REMAINING process(es) still running"
    echo "Run this command to force kill: pkill -9 -f slam"
fi

# Clean up temp files if they exist
rm -rf /tmp/go2_slam_* 2>/dev/null

echo ""
echo "=== Cleanup Complete ==="
