#!/usr/bin/env python3
"""
Complete Go2 SLAM Launch File

Starts all necessary nodes for SLAM mapping:
- odom_to_tf (Python node from package)
- static TF: base_link -> base_footprint
- pointcloud_to_laserscan
- SLAM Toolbox

Usage:
    ros2 launch go2_mapping go2_slam_full.launch.py
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    
    # Declare arguments
    slam_params_file = LaunchConfiguration('slam_params_file', 
        default=PathJoinSubstitution([
            FindPackageShare('go2_mapping'),
            'config',
            'slam_params_go2.yaml'
        ])
    )
    
    pointcloud_params_file = PathJoinSubstitution([
        FindPackageShare('go2_mapping'),
        'config',
        'pointcloud_to_laserscan.yaml'
    ])

    # 1. Odom to TF broadcaster (Python script directly)
    odom_to_tf_node = ExecuteProcess(
        cmd=['/usr/bin/python3', 
             os.path.expanduser('~/odom/src/go2_mapping/go2_mapping/odom_to_tf.py')],
        output='screen',
        name='odom_to_tf'
    )

    # 2. Static TF: base_link -> base_footprint
    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_base_footprint',
        arguments=['0', '0', '0', '0', '0', '0', 'base_link', 'base_footprint'],
        output='screen'
    )

    # 3. PointCloud to LaserScan converter
    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[pointcloud_params_file],
        remappings=[
            ('cloud_in', '/lidar_points'),
            ('scan', '/scan'),
        ]
    )

    # 4. SLAM Toolbox
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=[slam_params_file],
        output='screen'
    )

    return LaunchDescription([
        odom_to_tf_node,
        static_tf_node,
        pointcloud_to_laserscan_node,
        slam_toolbox_node,
    ])
