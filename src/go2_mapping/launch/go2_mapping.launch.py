#!/usr/bin/env python3
"""
Go2 Mapping Bringup Launch File

This launch file starts all necessary nodes for Go2 robot SLAM:
- Robot State Publisher (URDF visualization)
- Odom to TF broadcaster
- Static TF: base_link -> hesai_lidar
- PointCloud to LaserScan conversion
- SLAM Toolbox

Usage:
    ros2 launch go2_mapping go2_mapping.launch.py
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, SetEnvironmentVariable, TimerAction, RegisterEventHandler
from launch.event_handlers import OnProcessStart
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
import os


def generate_launch_description():
    
    # Path to robot URDF
    urdf_file = os.path.expanduser('~/odom/GO2_URDF/urdf/go2_description.urdf')
    
    # Read URDF file
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    
    # Declare arguments
    slam_params_file = LaunchConfiguration('slam_params_file', 
        default=PathJoinSubstitution([
            FindPackageShare('go2_mapping'),
            'config',
            'slam_params.yaml'
        ])
    )
    
    pointcloud_params_file = PathJoinSubstitution([
        FindPackageShare('go2_mapping'),
        'config',
        'pointcloud_to_laserscan.yaml'
    ])

    # 1. Robot State Publisher (publishes URDF for RViz visualization)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': False
        }]
    )

    # 2. Odom to TF broadcaster (Python script directly)
    odom_to_tf_node = ExecuteProcess(
        cmd=['/usr/bin/python3', 
             os.path.expanduser('~/odom/src/go2_mapping/go2_mapping/odom_to_tf.py')],
        output='screen',
        name='odom_to_tf'
    )

    # 3. PointCloud relay script for Hesai lidar
    pc2_relay_node = ExecuteProcess(
        cmd=['/usr/bin/python3', os.path.expanduser('~/pc2_relay_be.py')],
        output='screen',
        name='pc2_relay'
    )

    # 4. Static TF: base_link -> hesai_lidar
    # Typical Hesai XT32 mounting: 15cm forward, centered, 12cm above base_link
    static_tf_node = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='base_link_to_hesai_lidar',
        arguments=['0.15', '0', '0.12', '0', '0', '0', 'base_link', 'hesai_lidar'],
        output='screen'
    )

    # 5. PointCloud to LaserScan converter (Hesai lidar)
    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[pointcloud_params_file],
        remappings=[
            ('cloud_in', '/lidar_points'),
            ('scan', '/scan_raw'),
        ]
    )

    # 6. SLAM Toolbox
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        parameters=[slam_params_file],
        output='screen',
        remappings=[
            ('scan', '/scan_raw'),
        ]
    )

    # Launch nodes with delays to prevent resource contention
    return LaunchDescription([
        robot_state_publisher_node,
        TimerAction(
            period=0.5,
            actions=[odom_to_tf_node]
        ),
        TimerAction(
            period=1.0,
            actions=[pc2_relay_node]
        ),
        TimerAction(
            period=1.0,
            actions=[static_tf_node]
        ),
        TimerAction(
            period=3.0,
            actions=[pointcloud_to_laserscan_node]
        ),
        TimerAction(
            period=4.0,
            actions=[slam_toolbox_node]
        ),
    ])
