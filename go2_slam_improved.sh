#!/bin/bash
# Go2 SLAM Bringup with tmux - IMPROVED VERSION
# Usage: ./go2_slam_improved.sh

SESSION="go2_slam"

echo "Starting Go2 SLAM with tmux..."
echo "Session name: $SESSION"

# Kill existing session if it exists
tmux kill-session -t $SESSION 2>/dev/null

# Create new session with first window, using bash without bashrc to skip menu
tmux new-session -d -s $SESSION -n "SLAM"

# ==================================================
# Pane 0 (top-left): odom_to_tf
# ==================================================
tmux send-keys -t $SESSION:0.0 'export BASH_ENV="" && /usr/bin/python3 ~/odom/odom_to_tf.py' C-m

# ==================================================
# Pane 1 (top-right): static TF
# ==================================================
tmux split-window -h -t $SESSION:0
tmux send-keys -t $SESSION:0.1 'source /opt/ros/foxy/setup.bash && ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link base_footprint' C-m

# ==================================================
# Pane 2 (middle-left): pointcloud to laserscan
# ==================================================
tmux select-pane -t $SESSION:0.0
tmux split-window -v -t $SESSION:0.0
tmux send-keys -t $SESSION:0.2 'source /opt/ros/foxy/setup.bash && source ~/odom/install/setup.bash && ros2 launch go2_mapping pointcloud_to_laserscan.launch.py' C-m

# ==================================================
# Pane 3 (middle-right): SLAM Toolbox
# ==================================================
tmux select-pane -t $SESSION:0.1
tmux split-window -v -t $SESSION:0.1
tmux send-keys -t $SESSION:0.3 '1' C-m
sleep 1
tmux send-keys -t $SESSION:0.3 'echo "=== Starting SLAM Toolbox ==="' C-m
tmux send-keys -t $SESSION:0.3 'echo "Waiting 3 seconds for other nodes..."' C-m
tmux send-keys -t $SESSION:0.3 'sleep 3 && source /opt/ros/foxy/setup.bash && ====================
tmux select-pane -t $SESSION:0.2
tmux split-window -v -t $SESSION:0.2
tmux send-keys -t $SESSION:0.4 '1' C-m
sleep 1
tmux send-keys -t $SESSION:0.4 'echo "=== Monitoring & Commands ==="' C-m
tmux send-keys -t $SESSION:0.4 'echo "Waiting 10 seconds for SLAM to start..."' C-m
tmux send-keys -t $SESSION:0.4 'sleep 10' C-m
tmux send-keys -t $SESSION:0.4 'sleep 10 && source /opt/ros/foxy/setup.bash && ros2 param set /slam_toolbox use_sim_time false && ros2 param set /slam_toolbox base_frame base_link && echo "=== SLAM Ready ==="= SLAM System Ready! ==="' C-m
tmux send-keys -t $SESSION:0.4 'echo ""' C-m
tmux send-keys -t $SESSION:0.4 'echo "Useful commands:"' C-m
tmux send-keys -t $SESSION:0.4 'echo "  ros2 topic hz /scan     - Check scan rate"' C-m
tmux send-keys -t $SESSION:0.4 'echo "  ros2 topic hz /map      - Check map updates"' C-m
tmux send-keys -t $SESSION:0.4 'echo "  ros2 node list          - List all nodes"' C-m
tmux send-keys -t $SESSION:0.4 'echo ""' C-m
tmux send-keys -t $SESSION:0.4 'echo "To save map:"' C-m
tmux send-keys -t $SESSION:0.4 'echo "  mkdir -p ~/maps"' C-m
tmux send-keys -t $SESSION:0.4 'echo "  ros2 service call /slam_toolbox/save_map slam_toolbox/srv/SaveMap"' C-m

# Layout: tile all panes evenly
tmux select-layout -t $SESSION:0 tiled

# Select the first pane
tmux select-pane -t $SESSION:0.0

# Attach to session
echo ""
echo "Attaching to tmux session..."
echo "Use Ctrl+B then arrow keys to switch between panes"
echo "Use Ctrl+B then D to detach (keeps running)"
echo "Use Ctrl+C in each pane to stop"
tmux attach-session -t $SESSION
