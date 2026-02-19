#!/usr/bin/env python3
"""
RViz launch file for Go2 navigation visualization.

Usage (absolute path launch):
  ros2 launch /home/unitree/odom/rviz/go2_navigation_visualization.launch.py

Usage (custom config):
  ros2 launch /home/unitree/odom/rviz/go2_navigation_visualization.launch.py \
    rviz_config:=/path/to/custom.rviz
"""

from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch import LaunchDescription
from launch_ros.actions import Node
import os


def generate_launch_description():
    default_rviz_config = os.path.join(
        os.path.dirname(__file__), 'go2_navigation_visualization.rviz'
    )

    rviz_config_arg = DeclareLaunchArgument(
        'rviz_config',
        default_value=default_rviz_config,
        description='Absolute path to RViz config file'
    )

    rviz_config = LaunchConfiguration('rviz_config')

    # RViz Node
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )
    
    return LaunchDescription([rviz_config_arg, rviz_node])
