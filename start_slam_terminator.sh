#!/bin/bash
# Go2 SLAM using Terminator (split terminals)
# Usage: ./start_slam_terminator.sh
# Requires: Terminator installed (sudo apt install terminator)

# Check if terminator is installed
if ! command -v terminator &> /dev/null; then
    echo "Terminator is not installed!"
    echo "Install it with: sudo apt install terminator"
    exit 1
fi

# Create temporary directory for command scripts
TMPDIR="/tmp/go2_slam_$$"
mkdir -p $TMPDIR

# Create script for each pane
cat > $TMPDIR/pane1.sh << 'EOF'
#!/bin/bash
echo "=== Terminal 1: Odom to TF ==="
/usr/bin/python3 ~/odom/odom_to_tf.py
exec bash
EOF

cat > $TMPDIR/pane2.sh << 'EOF'
#!/bin/bash
echo "=== Terminal 2: Static TF Publisher ==="
source /opt/ros/foxy/setup.bash
ros2 run tf2_ros static_transform_publisher 0 0 0 0 0 0 base_link base_footprint
exec bash
EOF

cat > $TMPDIR/pane3.sh << 'EOF'
#!/bin/bash
echo "=== Terminal 3: PointCloud to LaserScan ==="
source /opt/ros/foxy/setup.bash
source ~/odom/install/setup.bash
ros2 launch go2_mapping pointcloud_to_laserscan.launch.py
exec bash
EOF

cat > $TMPDIR/pane4.sh << 'EOF'
#!/bin/bash
echo "=== Terminal 4: SLAM Toolbox ==="
source /opt/ros/foxy/setup.bash
echo "Waiting 5 seconds for other nodes to start..."
sleep 5
ros2 launch slam_toolbox online_async_launch.py \
  slam_params_file:=/home/unitree/odom/src/go2_mapping/config/slam_params_go2.yaml
exec bash
EOF

# Make scripts executable
chmod +x $TMPDIR/*.sh

# Launch Terminator with 4 split panes
terminator \
  --layout=custom \
  -e "bash $TMPDIR/pane1.sh" \
  --new-tab \
  -e "bash $TMPDIR/pane2.sh" \
  --new-tab \
  -e "bash $TMPDIR/pane3.sh" \
  --new-tab \
  -e "bash $TMPDIR/pane4.sh" &

echo "Terminator launched with 4 tabs for SLAM!"
echo "Clean up temp files with: rm -rf $TMPDIR"
