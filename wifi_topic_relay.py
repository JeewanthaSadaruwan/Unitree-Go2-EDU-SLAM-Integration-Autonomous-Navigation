#!/usr/bin/env python3
import argparse

import rclpy
from rclpy.node import Node
from rclpy.qos import (
    QoSProfile,
    QoSHistoryPolicy,
    QoSReliabilityPolicy,
    QoSDurabilityPolicy,
)

from tf2_msgs.msg import TFMessage
from nav_msgs.msg import OccupancyGrid, MapMetaData
from sensor_msgs.msg import LaserScan


def qos_volatile(depth: int = 50, reliable: bool = True) -> QoSProfile:
    return QoSProfile(
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=depth,
        reliability=QoSReliabilityPolicy.RELIABLE if reliable else QoSReliabilityPolicy.BEST_EFFORT,
        durability=QoSDurabilityPolicy.VOLATILE,
    )


def qos_transient_local(depth: int = 1, reliable: bool = True) -> QoSProfile:
    return QoSProfile(
        history=QoSHistoryPolicy.KEEP_LAST,
        depth=depth,
        reliability=QoSReliabilityPolicy.RELIABLE if reliable else QoSReliabilityPolicy.BEST_EFFORT,
        durability=QoSDurabilityPolicy.TRANSIENT_LOCAL,
    )


class TopicRelay(Node):
    def __init__(self, prefix: str, enable_scan: bool):
        super().__init__("wifi_topic_relay")
        self.prefix = prefix.rstrip("/")

        # ---- TF ----
        self.pub_tf = self.create_publisher(
            TFMessage, f"{self.prefix}/tf", qos_volatile(depth=200, reliable=True)
        )
        self.sub_tf = self.create_subscription(
            TFMessage, "/tf", self._cb_tf, qos_volatile(depth=200, reliable=True)
        )

        # /tf_static must be transient_local (latched)
        self.pub_tf_static = self.create_publisher(
            TFMessage, f"{self.prefix}/tf_static", qos_transient_local(depth=50, reliable=True)
        )
        self.sub_tf_static = self.create_subscription(
            TFMessage, "/tf_static", self._cb_tf_static, qos_transient_local(depth=50, reliable=True)
        )

        # ---- MAP ----
        # slam_toolbox typically uses transient_local for /map + /map_metadata
        self.pub_map = self.create_publisher(
            OccupancyGrid, f"{self.prefix}/map", qos_transient_local(depth=1, reliable=True)
        )
        self.sub_map = self.create_subscription(
            OccupancyGrid, "/map", self._cb_map, qos_transient_local(depth=1, reliable=True)
        )

        self.pub_map_md = self.create_publisher(
            MapMetaData, f"{self.prefix}/map_metadata", qos_transient_local(depth=1, reliable=True)
        )
        self.sub_map_md = self.create_subscription(
            MapMetaData, "/map_metadata", self._cb_map_md, qos_transient_local(depth=1, reliable=True)
        )

        # ---- SCAN (optional) ----
        # Your /scan publisher is BEST_EFFORT -> relay MUST subscribe BEST_EFFORT to match.
        self.enable_scan = enable_scan
        if enable_scan:
            self.pub_scan = self.create_publisher(
                LaserScan, f"{self.prefix}/scan", qos_volatile(depth=50, reliable=False)
            )
            self.sub_scan = self.create_subscription(
                LaserScan, "/scan", self._cb_scan, qos_volatile(depth=50, reliable=False)
            )

        self.get_logger().info(f"Relaying to prefix: {self.prefix}")
        self.get_logger().info(
            "Relaying: /tf, /tf_static, /map, /map_metadata" + (", /scan" if enable_scan else "")
        )

    def _cb_tf(self, msg: TFMessage):
        self.pub_tf.publish(msg)

    def _cb_tf_static(self, msg: TFMessage):
        self.pub_tf_static.publish(msg)

    def _cb_map(self, msg: OccupancyGrid):
        self.pub_map.publish(msg)

    def _cb_map_md(self, msg: MapMetaData):
        self.pub_map_md.publish(msg)

    def _cb_scan(self, msg: LaserScan):
        self.pub_scan.publish(msg)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prefix", default="/wifi", help="Prefix for republished topics (default: /wifi)")
    parser.add_argument("--scan", action="store_true", help="Also relay /scan")
    args = parser.parse_args()

    rclpy.init()
    node = TopicRelay(prefix=args.prefix, enable_scan=args.scan)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()
