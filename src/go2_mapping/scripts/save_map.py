#!/usr/bin/env python3

"""
Script to save SLAM Toolbox map
Usage: ros2 run go2_mapping save_map.py [map_name]
"""

import sys
import rclpy
from rclpy.node import Node
from slam_toolbox.srv import SaveMap


class MapSaver(Node):
    def __init__(self):
        super().__init__('map_saver')
        self.client = self.create_client(SaveMap, '/slam_toolbox/save_map')
        
        while not self.client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /slam_toolbox/save_map service...')
        
    def save_map(self, map_path):
        request = SaveMap.Request()
        request.name.data = map_path
        
        self.get_logger().info(f'Saving map to: {map_path}')
        future = self.client.call_async(request)
        rclpy.spin_until_future_complete(self, future)
        
        if future.result() is not None:
            self.get_logger().info(f'Map saved successfully!')
            return True
        else:
            self.get_logger().error('Failed to save map')
            return False


def main(args=None):
    rclpy.init(args=args)
    
    # Get map name from command line or use default
    if len(sys.argv) > 1:
        map_name = sys.argv[1]
    else:
        import os
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        map_name = os.path.expanduser(f'~/SLAM/maps/map_{timestamp}')
    
    # Ensure maps directory exists
    import os
    os.makedirs(os.path.dirname(map_name), exist_ok=True)
    
    saver = MapSaver()
    success = saver.save_map(map_name)
    
    saver.destroy_node()
    rclpy.shutdown()
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
