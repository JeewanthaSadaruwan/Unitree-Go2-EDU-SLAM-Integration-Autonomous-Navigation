#!/bin/bash
# Go2 SLAM Bringup with tmux - Working WITH robot's .bashrc menu
# Usage: ./go2_slam_tmux.sh

SESSION="go2_slam"

echo "Starting Go2 SLAM with tmux..."
echo "Session name: $SESSION"

# Kill existing session if it exists
tmux kill-session -t $SESSION 2>/dev/null

# Create new session (will load .bashrc normally)
tmux new-session -d -s $SESSION

# ==================================================
# Pane 0 (top-left): odom_to_tf
# ==================================================
# Send "1" to select ROS Foxy from the menu
tmux send-keys -t $SESSION:0.0 '1' C-m
sleep 1
tmux send-keys -t $SESSION:0.0 'echo "=== Starting odom_to_tf ==="' C-m
tmux send-keys -t $SESSION:0.0 '/usr/bin/python3 ~/odom/odom_to_tf.py' C-m

# ==================================================
# Pane 1 (top-right): static TF
# ==================================================
tmux split-window -h -t $SESSION:0
tmux send-keys -t $SESSION:0.1 '1' C-m
sleep 1
tmux send-keys -t $SESSION:0.1 'echo "=== Starting static TF publisher ==="' C-m
tmux send-keys -t $SESSION:0.1 'ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link base_footprint' C-m

# ==================================================
# Pane 2 (bottom-left): pointcloud to laserscan
# ==================================================
tmux select-pane -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.0
tmux send-keys -t $SESSION:0.2 '1' C-m
sleep 1
tmux send-keys -t $SESSION:0.2 'echo "=== Starting pointcloud_to_laserscan ==="' C-m
tmux send-keys -t $SESSION:0.2 'source ~/odom/install/setup.bash' C-m
tmux send-keys -t $SESSION:0.2 'ros2 launch go2_mapping pointcloud_to_laserscan.launch.py' C-m

# ==================================================
# Pane 3 (bottom-right): SLAM Toolbox
# ==================================================
tmux select-pane -t $SESSION:0.1
tmux split-window -v -t $SESSION:0.1
tmux send-keys -t $SESSION:0.3 '1' C-m
sleep 1
tmux send-keys -t $SESSION:0.3 'echo "=== Starting SLAM Toolbox ==="' C-m
tmux send-keys -t $SESSION:0.3 'echo "Waiting 5 seconds for other nodes..."' C-m
tmux send-keys -t $SESSION:0.3 'sleep 5' C-m
tmux send-keys -t $SESSION:0.3 'ros2 launch slam_toolbox online_async_launch.py slam_params_file:=/home/unitree/odom/slam_params_go2.yaml use_sim_time:=false' C-m

# Layout: tile all panes evenly
sleep 2
tmux select-layout -t $SESSION:0 tiled

# Select the first pane
tmux select-pane -t $SESSION:0.0

# Attach to session
echo ""
echo "=== Starting SLAM in 2 seconds ==="
sleep 2
echo ""
echo "Tmux Controls:"
echo "  Ctrl+B then arrow keys - Switch between panes"
echo "  Ctrl+B then D - Detach (keeps running in background)"
echo "  Ctrl+C in each pane - Stop that node"
echo ""
echo "To reattach later: tmux attach -t go2_slam"
echo "To stop everything: ./stop_slam.sh"
echo ""
tmux attach-session -t $SESSION
