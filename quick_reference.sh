#!/bin/bash
# Quick Reference for Go2 Robot Commands

cat << 'EOF'
╔════════════════════════════════════════════════════════════════════╗
║                    GO2 ROBOT QUICK REFERENCE                       ║
╠════════════════════════════════════════════════════════════════════╣
║  MAPPING (SLAM)                                                    ║
╠════════════════════════════════════════════════════════════════════╣
║  Start SLAM:          ./start_slam.sh                              ║
║  Stop SLAM:           ./stop_slam.sh                               ║
║  Diagnose SLAM:       ./diagnose_slam.sh                           ║
║  Save Map:            ./save_current_map.sh [map_name]             ║
╠════════════════════════════════════════════════════════════════════╣
║  NAVIGATION                                                        ║
╠════════════════════════════════════════════════════════════════════╣
║  Start Bridge:        ./start_bridge.sh                            ║
║  Start Navigation:    ./start_navigation.sh [map.yaml]             ║
╠════════════════════════════════════════════════════════════════════╣
║  WORKFLOW                                                          ║
╠════════════════════════════════════════════════════════════════════╣
║  1. Create Map:                                                    ║
║     Terminal 1: ./start_slam.sh                                    ║
║     - Drive robot around                                           ║
║     Terminal 2: ./save_current_map.sh office_floor1                ║
║     Terminal 1: Ctrl+C or ./stop_slam.sh                           ║
║                                                                    ║
║  2. Navigate with Map:                                             ║
║     Terminal 1: ./start_bridge.sh                                  ║
║     Terminal 2: ./start_navigation.sh                              ║
║     - Set initial pose in RViz                                     ║
║     - Send navigation goals                                        ║
╠════════════════════════════════════════════════════════════════════╣
║  USEFUL COMMANDS                                                   ║
╠════════════════════════════════════════════════════════════════════╣
║  List maps:           ls -lh ~/odom/maps/                          ║
║  Check topics:        ros2 topic list                              ║
║  View transforms:     ros2 run tf2_tools view_frames               ║
║  Check nodes:         ros2 node list                               ║
║  Lifecycle status:    ros2 lifecycle nodes                         ║
║  Echo scan:           ros2 topic echo /scan_raw                    ║
║  Echo odom:           ros2 topic echo /odom                        ║
╠════════════════════════════════════════════════════════════════════╣
║  DOCUMENTATION                                                     ║
╠════════════════════════════════════════════════════════════════════╣
║  Main README:         cat README.md                                ║
║  Navigation Guide:    cat NAVIGATION.md                            ║
║  Workflow Comparison: cat NAVIGATION_WORKFLOW.md                   ║
╠════════════════════════════════════════════════════════════════════╣
║  TROUBLESHOOTING                                                   ║
╠════════════════════════════════════════════════════════════════════╣
║  No scan data:        Check LiDAR connection                       ║
║  No odometry:         Check robot connection & bridge              ║
║  TF errors:           Run ./diagnose_slam.sh                       ║
║  Can't save map:      Ensure SLAM is running                       ║
║  Nav won't start:     Check map file exists                        ║
╚════════════════════════════════════════════════════════════════════╝

EOF
