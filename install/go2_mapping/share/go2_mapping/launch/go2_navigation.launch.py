#!/usr/bin/env python3

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, EmitEvent, RegisterEventHandler
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution, Command
from launch.events import matches_action
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node, LifecycleNode
from launch_ros.event_handlers import OnStateTransition
from launch_ros.events.lifecycle import ChangeState
from lifecycle_msgs.msg import Transition
from ament_index_python.packages import get_package_share_directory


def generate_launch_description():
    # Path to URDF file
    urdf_file = '/home/unitree/odom/GO2_URDF/urdf/go2_description.urdf'
    
    # Read URDF file
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    # Declare launch arguments
    map_yaml_arg = DeclareLaunchArgument(
        'map_yaml',
        default_value='/home/unitree/odom/maps/floor10_1.yaml',
        description='Full path to map yaml file'
    )
    
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation time'
    )
    
    params_file_arg = DeclareLaunchArgument(
        'params_file',
        default_value='/home/unitree/odom/src/go2_mapping/config/go2_nav2_params.yaml',
        description='Full path to Nav2 params file'
    )
    
    autostart_arg = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack'
    )
    
    base_frame_arg = DeclareLaunchArgument(
        'base_frame_id',
        default_value='base_link',
        description='Base frame ID'
    )
    
    odom_frame_arg = DeclareLaunchArgument(
        'odom_frame_id',
        default_value='odom',
        description='Odom frame ID'
    )
    
    global_frame_arg = DeclareLaunchArgument(
        'global_frame_id',
        default_value='map',
        description='Global frame ID'
    )
    
    scan_topic_arg = DeclareLaunchArgument(
        'scan_topic',
        default_value='scan_raw',
        description='Scan topic name'
    )

    # Get launch configurations
    map_yaml = LaunchConfiguration('map_yaml')
    use_sim_time = LaunchConfiguration('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')
    base_frame_id = LaunchConfiguration('base_frame_id')
    odom_frame_id = LaunchConfiguration('odom_frame_id')
    global_frame_id = LaunchConfiguration('global_frame_id')
    scan_topic = LaunchConfiguration('scan_topic')

    # ========== BASE NODES (TF & SENSORS) ==========
    
    # Robot State Publisher (publishes robot URDF and TF tree)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description,
            'use_sim_time': use_sim_time
        }]
    )
    
    # Odom to TF broadcaster (publishes odom->base_link transform)
    odom_to_tf_node = Node(
        package='go2_mapping',
        executable='odom_to_tf',
        name='odom_to_tf',
        output='screen',
        parameters=[{'use_sim_time': use_sim_time}]
    )
    
    # Static TF: base_link -> hesai_lidar
    static_tf_hesai = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_tf_base_to_hesai',
        arguments=['0.15', '0', '0.12', '0', '0', '0', 'base_link', 'hesai_lidar'],
        output='screen'
    )
    
    # PointCloud to LaserScan converter
    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        remappings=[
            ('cloud_in', '/utlidar/cloud_deskewed'),
            ('scan', '/scan_raw')
        ],
        parameters=['/home/unitree/odom/src/go2_mapping/config/pointcloud_to_laserscan.yaml']
    )

    # Map Server Lifecycle Node
    map_server_node = LifecycleNode(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'yaml_filename': map_yaml,
            'use_sim_time': use_sim_time
        }]
    )

    # AMCL Lifecycle Node
    amcl_node = LifecycleNode(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[{
            'use_sim_time': use_sim_time,
            'base_frame_id': base_frame_id,
            'odom_frame_id': odom_frame_id,
            'global_frame_id': global_frame_id,
            'scan_topic': scan_topic
        }]
    )

    # Map Server Lifecycle Management
    map_server_configure = EmitEvent(
        event=ChangeState(
            lifecycle_node_matcher=matches_action(map_server_node),
            transition_id=Transition.TRANSITION_CONFIGURE,
        )
    )

    map_server_activate = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=map_server_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(map_server_node),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    )
                ),
            ],
        )
    )

    # AMCL Lifecycle Management
    amcl_configure = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=map_server_node,
            start_state='activating',
            goal_state='active',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(amcl_node),
                        transition_id=Transition.TRANSITION_CONFIGURE,
                    )
                ),
            ],
        )
    )

    amcl_activate = RegisterEventHandler(
        OnStateTransition(
            target_lifecycle_node=amcl_node,
            start_state='configuring',
            goal_state='inactive',
            entities=[
                EmitEvent(
                    event=ChangeState(
                        lifecycle_node_matcher=matches_action(amcl_node),
                        transition_id=Transition.TRANSITION_ACTIVATE,
                    )
                ),
            ],
        )
    )

    # Nav2 Bringup Launch
    nav2_bringup_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                get_package_share_directory('nav2_bringup'),
                'launch',
                'navigation_launch.py'
            ])
        ]),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'params_file': params_file,
            'autostart': autostart,
            'map_subscribe_transient_local': 'true'
        }.items()
    )

    return LaunchDescription([
        # Declare arguments
        map_yaml_arg,
        use_sim_time_arg,
        params_file_arg,
        autostart_arg,
        base_frame_arg,
        odom_frame_arg,
        global_frame_arg,
        scan_topic_arg,
        
        # Base nodes (TF & Sensors)
        robot_state_publisher_node,
        odom_to_tf_node,
        static_tf_hesai,
        pointcloud_to_laserscan_node,
        
        # Navigation nodes
        map_server_node,
        amcl_node,
        
        # Lifecycle management
        map_server_configure,
        map_server_activate,
        amcl_configure,
        amcl_activate,
        
        # Nav2
        nav2_bringup_launch,
    ])
