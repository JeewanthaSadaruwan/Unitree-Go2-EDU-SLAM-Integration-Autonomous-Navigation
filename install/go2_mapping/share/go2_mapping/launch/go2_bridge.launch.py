#!/usr/bin/env python3

"""
Launch file for the cmd_vel bridge that connects ROS2 Nav2 to Unitree Go2
This bridges navigation commands to the robot's control interface
"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )

    # Get launch configurations
    use_sim_time = LaunchConfiguration('use_sim_time')

    # Bridge node
    bridge_node = Node(
        package='cmd_vel_unitree_bridge',
        executable='cmd_vel_unitree_bridge_node',
        name='cmd_vel_bridge',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time
        }]
    )

    return LaunchDescription([
        use_sim_time_arg,
        bridge_node,
    ])
