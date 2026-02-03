#!/usr/bin/env python3
import math

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy, QoSDurabilityPolicy

from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


# For odom/TF style streams, BEST_EFFORT is typically better than RELIABLE
QOS_ODOM = QoSProfile(
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=10,
    reliability=QoSReliabilityPolicy.BEST_EFFORT,
    durability=QoSDurabilityPolicy.VOLATILE,
)


def yaw_from_quat(x: float, y: float, z: float, w: float) -> float:
    """Extract yaw (rotation about Z) from a quaternion."""
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def quat_from_yaw(yaw: float):
    """Build a quaternion with roll=pitch=0 and only yaw rotation."""
    half = yaw * 0.5
    return 0.0, 0.0, math.sin(half), math.cos(half)


def stamp_to_ns(stamp) -> int:
    """Convert builtin_interfaces/msg/Time to integer nanoseconds."""
    return int(stamp.sec) * 1_000_000_000 + int(stamp.nanosec)


class OdomToTF(Node):
    def __init__(self):
        super().__init__('odom_to_tf_planar')

        self.br = TransformBroadcaster(self)
        self.count = 0
        self.last_stamp = None
        self.last_stamp_ns = None

        # 1 Hz log tick
        self.create_timer(1.0, self._tick)

        self.sub = self.create_subscription(
            Odometry,
            '/utlidar/robot_odom',
            self.cb,
            QOS_ODOM
        )

        self.get_logger().info("odom_to_tf_planar started (z=0, yaw-only, BEST_EFFORT sub)")

    def _tick(self):
        if self.last_stamp is None:
            self.get_logger().info("waiting for odom messages...")
        else:
            self.get_logger().info(
                f"rx odom msgs: {self.count}, last stamp: {self.last_stamp.sec}.{self.last_stamp.nanosec:09d}"
            )

    def cb(self, msg: Odometry):
        self.count += 1

        # Guard: ignore time going backwards (compare by integer ns)
        cur_ns = stamp_to_ns(msg.header.stamp)
        if self.last_stamp_ns is not None and cur_ns < self.last_stamp_ns:
            self.get_logger().warn(
                f"Odometry time went backwards: "
                f"{msg.header.stamp.sec}.{msg.header.stamp.nanosec:09d} < "
                f"{self.last_stamp.sec}.{self.last_stamp.nanosec:09d}. Ignoring."
            )
            return

        self.last_stamp = msg.header.stamp
        self.last_stamp_ns = cur_ns

        # Extract yaw-only from odom orientation
        q = msg.pose.pose.orientation
        yaw = yaw_from_quat(q.x, q.y, q.z, q.w)
        qx, qy, qz, qw = quat_from_yaw(yaw)

        # Build TF: odom -> base_link (PLANAR)
        t = TransformStamped()
        t.header.stamp = msg.header.stamp
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'

        t.transform.translation.x = float(msg.pose.pose.position.x)
        t.transform.translation.y = float(msg.pose.pose.position.y)
        t.transform.translation.z = 0.0

        t.transform.rotation.x = qx
        t.transform.rotation.y = qy
        t.transform.rotation.z = qz
        t.transform.rotation.w = qw

        self.br.sendTransform(t)


def main():
    rclpy.init()
    node = OdomToTF()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
