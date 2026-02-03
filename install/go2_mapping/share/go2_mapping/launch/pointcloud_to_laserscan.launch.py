#!/usr/bin/env python3
"""
Launch file for PointCloud2 to LaserScan conversion

Converts 3D LiDAR point cloud to 2D laser scan for SLAM
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    
    # Path to config file
    config_file = PathJoinSubstitution([
        FindPackageShare('go2_mapping'),
        'config',
        'pointcloud_to_laserscan.yaml'
    ])

    # PointCloud to LaserScan node
    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[config_file],
        remappings=[
            ('cloud_in', '/utlidar/cloud_deskewed'),
            ('scan', '/scan'),
        ]
    )

    return LaunchDescription([
        pointcloud_to_laserscan_node,
    ])
