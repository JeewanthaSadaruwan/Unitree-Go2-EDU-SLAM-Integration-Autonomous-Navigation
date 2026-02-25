#!/usr/bin/env python3

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose


class GoalPoseRelay(Node):
    """
    Relay PoseStamped goals from /goal_pose to Nav2 NavigateToPose action.

    This helps when RViz goal tools publish PoseStamped but action transport
    from a remote machine is unreliable.
    """

    def __init__(self):
        super().__init__('goal_pose_relay')

        self.declare_parameter('goal_topic', '/goal_pose')
        self.declare_parameter('duplicate_window_sec', 0.75)

        self._goal_topic = self.get_parameter('goal_topic').value
        duplicate_window_sec = float(self.get_parameter('duplicate_window_sec').value)
        self._duplicate_window_ns = int(max(0.0, duplicate_window_sec) * 1e9)

        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self._sub = self.create_subscription(PoseStamped, self._goal_topic, self._on_goal, 10)
        self._last_goal_handle = None
        self._last_goal_signature = None
        self._last_goal_time_ns = None

        self.get_logger().info(
            f'goal_pose_relay started, listening on {self._goal_topic}'
        )

    @staticmethod
    def _goal_signature(msg: PoseStamped):
        p = msg.pose.position
        q = msg.pose.orientation
        return (
            msg.header.frame_id,
            round(p.x, 3),
            round(p.y, 3),
            round(p.z, 3),
            round(q.x, 4),
            round(q.y, 4),
            round(q.z, 4),
            round(q.w, 4),
        )

    def _on_goal(self, msg: PoseStamped) -> None:
        if msg.header.frame_id == '':
            self.get_logger().warn(f'Ignoring {self._goal_topic} without frame_id')
            return

        goal_signature = self._goal_signature(msg)
        now_ns = self.get_clock().now().nanoseconds
        if (
            self._last_goal_signature == goal_signature
            and self._last_goal_time_ns is not None
            and (now_ns - self._last_goal_time_ns) < self._duplicate_window_ns
        ):
            self.get_logger().warn('Ignoring duplicate goal inside duplicate_window_sec')
            return

        self._last_goal_signature = goal_signature
        self._last_goal_time_ns = now_ns

        if not self._action_client.wait_for_server(timeout_sec=1.0):
            self.get_logger().warn('navigate_to_pose action server not available yet')
            return

        goal = NavigateToPose.Goal()
        goal.pose = msg

        # Use robot clock stamp to avoid cross-machine clock skew issues.
        goal.pose.header.stamp = self.get_clock().now().to_msg()

        self.get_logger().info(
            f"Forwarding goal: frame={goal.pose.header.frame_id}, "
            f"x={goal.pose.pose.position.x:.2f}, y={goal.pose.pose.position.y:.2f}"
        )

        send_future = self._action_client.send_goal_async(goal)
        send_future.add_done_callback(self._goal_response_cb)

    def _goal_response_cb(self, future):
        try:
            goal_handle = future.result()
        except Exception as exc:
            self.get_logger().error(f'Failed to send goal: {exc}')
            return

        if not goal_handle.accepted:
            self.get_logger().warn('Goal rejected by NavigateToPose server')
            return

        self._last_goal_handle = goal_handle
        self.get_logger().info('Goal accepted by NavigateToPose server')


def main():
    rclpy.init()
    node = GoalPoseRelay()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
