#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class ScanStampFix(Node):
    def __init__(self):
        super().__init__('scan_stamp_fix')
        self.pub = self.create_publisher(LaserScan, '/scan_fixed', 10)
        self.sub = self.create_subscription(LaserScan, '/scan', self.cb, 10)
        self.get_logger().info("scan_stamp_fix started: /scan -> /scan_fixed")

    def cb(self, msg: LaserScan):
        msg.header.stamp = self.get_clock().now().to_msg()
        self.pub.publish(msg)


def main():
    rclpy.init()
    node = ScanStampFix()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
