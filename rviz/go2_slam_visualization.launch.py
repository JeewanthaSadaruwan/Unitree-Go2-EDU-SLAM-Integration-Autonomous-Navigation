#!/usr/bin/env python3
"""
RViz Launch File for Go2 SLAM Visualization

This launches RViz on your LOCAL COMPUTER with all displays configured:
- RobotModel (Go2 3D mesh)
- TF (all frames)
- Map (SLAM map)
- LaserScan (/scan_raw)
- Odometry (/odom)
- Hesai PointCloud (optional)

Usage on your laptop:
    ros2 launch go2_slam_visualization.launch.py
    
Or simply:
    rviz2 -d ~/Desktop/go2_slam_visualization.rviz
"""

from launch import LaunchDescription
from launch_ros.actions import Node
import os


def generate_launch_description():
    
    # Path to RViz config file (in same directory as this launch file)
    rviz_config = os.path.join(os.path.dirname(__file__), 'go2_slam_visualization.rviz')
    
    # RViz Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )
    
    return LaunchDescription([
        rviz_node,
    ])
