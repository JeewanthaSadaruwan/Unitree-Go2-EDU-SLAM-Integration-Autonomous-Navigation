#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
from sensor_msgs.msg import LaserScan

class ScanReliableRepublisher(Node):
    def __init__(self):
        super().__init__('scan_reliable_republisher')

        # Subscribe with BEST_EFFORT (matches pointcloud_to_laserscan SensorDataQoS style)
        sub_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        # Publish with RELIABLE (so slam_toolbox / others requesting RELIABLE can connect)
        pub_qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE,
        )

        self.pub = self.create_publisher(LaserScan, '/scan', pub_qos)
        self.sub = self.create_subscription(LaserScan, '/scan_raw', self.cb, sub_qos)

        self.get_logger().info("Republishing /scan_raw (best_effort) -> /scan (reliable)")

    def cb(self, msg: LaserScan):
        self.pub.publish(msg)

def main():
    rclpy.init()
    node = ScanReliableRepublisher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
