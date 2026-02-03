#!/usr/bin/env python3
"""
Go2 Mapping Bringup Launch File

This launch file starts all necessary nodes for Go2 robot SLAM:
- Odom to TF broadcaster
- Scan timestamp fix (if needed)
- SLAM Toolbox

Usage:
    ros2 launch go2_mapping go2_mapping.launch.py
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # Declare arguments
    use_planar_odom = DeclareLaunchArgument(
        'use_planar_odom',
        default_value='false',
        description='Use planar (2D) odom_to_tf node instead of full 3D'
    )
    
    slam_params_file = LaunchConfiguration('slam_params_file', 
        default=PathJoinSubstitution([
            FindPackageShare('go2_mapping'),
            'config',
            'slam_params_go2.yaml'
        ])
    )

    # Odom to TF broadcaster (3D version)
    odom_to_tf_node = Node(
        package='go2_mapping',
        executable='odom_to_tf',
        name='odom_to_tf',
        output='screen',
        condition=launch.conditions.UnlessCondition(LaunchConfiguration('use_planar_odom'))
    )

    # Odom to TF broadcaster (Planar 2D version)
    odom_to_tf_planar_node = Node(
        package='go2_mapping',
        executable='odom_to_tf_planar',
        name='odom_to_tf_planar',
        output='screen',
        condition=launch.conditions.IfCondition(LaunchConfiguration('use_planar_odom'))
    )

    # SLAM Toolbox
    slam_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=[slam_params_file],
        output='screen'
    )

    return LaunchDescription([
        use_planar_odom,
        odom_to_tf_node,
        odom_to_tf_planar_node,
        slam_node,
    ])
