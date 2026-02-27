#!/usr/bin/env python3

import math

import rclpy
from geometry_msgs.msg import PointStamped, PoseStamped
from rclpy.node import Node


def quaternion_to_yaw(x: float, y: float, z: float, w: float) -> float:
    """Convert quaternion to yaw (radians)."""
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


class RvizClickLogger(Node):
    """Log clicked points and goal poses from RViz."""

    def __init__(self) -> None:
        super().__init__('rviz_click_logger')

        self.declare_parameter('clicked_point_topic', '/clicked_point')
        self.declare_parameter('goal_pose_topic', '/goal_pose')

        clicked_topic = str(self.get_parameter('clicked_point_topic').value)
        goal_topic = str(self.get_parameter('goal_pose_topic').value)

        self.create_subscription(PointStamped, clicked_topic, self._on_clicked_point, 10)
        self.create_subscription(PoseStamped, goal_topic, self._on_goal_pose, 10)

        self.get_logger().info(
            f'Listening on {clicked_topic} (xyz) and {goal_topic} (xyz+yaw)'
        )

    def _on_clicked_point(self, msg: PointStamped) -> None:
        p = msg.point
        self.get_logger().info(
            f'[clicked_point] frame={msg.header.frame_id} '
            f'x={p.x:.3f}, y={p.y:.3f}, z={p.z:.3f}'
        )

    def _on_goal_pose(self, msg: PoseStamped) -> None:
        p = msg.pose.position
        q = msg.pose.orientation
        yaw_rad = quaternion_to_yaw(q.x, q.y, q.z, q.w)
        yaw_deg = math.degrees(yaw_rad)
        self.get_logger().info(
            f'[goal_pose] frame={msg.header.frame_id} '
            f'x={p.x:.3f}, y={p.y:.3f}, z={p.z:.3f}, '
            f'yaw={yaw_rad:.3f} rad ({yaw_deg:.1f} deg)'
        )


def main() -> None:
    rclpy.init()
    node = RvizClickLogger()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
