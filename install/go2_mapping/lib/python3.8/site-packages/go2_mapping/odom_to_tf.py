# #!/usr/bin/env python3
# import rclpy
# from rclpy.node import Node
# from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy, QoSDurabilityPolicy
# from nav_msgs.msg import Odometry
# from geometry_msgs.msg import TransformStamped
# from tf2_ros import TransformBroadcaster


# QOS_RELIABLE = QoSProfile(
#     history=QoSHistoryPolicy.KEEP_LAST,
#     depth=50,
#     reliability=QoSReliabilityPolicy.RELIABLE,
#     durability=QoSDurabilityPolicy.VOLATILE,
# )


# class OdomToTF(Node):
#     def __init__(self):
#         super().__init__('odom_to_tf')
#         self.br = TransformBroadcaster(self)
#         self.count = 0
#         self.last_stamp = None
#         self.create_timer(1.0, self._tick)

#         self.sub = self.create_subscription(
#             Odometry,
#             '/utlidar/robot_odom',
#             self.cb,
#             QOS_RELIABLE
#         )

#         self.get_logger().info("odom_to_tf started (RELIABLE sub)")

#     def _tick(self):
#         if self.last_stamp is None:
#             self.get_logger().info("waiting for odom messages...")
#         else:
#             self.get_logger().info(
#                 f"rx odom msgs: {self.count}, last stamp: {self.last_stamp.sec}.{self.last_stamp.nanosec:09d}"
#             )

#     def cb(self, msg: Odometry):
#         self.count += 1
#         self.last_stamp = msg.header.stamp

#         t = TransformStamped()
#         t.header.stamp = msg.header.stamp  # must match sensor timestamps
#         t.header.frame_id = 'odom'
#         t.child_frame_id = 'base_link'
#         t.transform.translation.x = msg.pose.pose.position.x
#         t.transform.translation.y = msg.pose.pose.position.y
#         t.transform.translation.z = msg.pose.pose.position.z
#         t.transform.rotation = msg.pose.pose.orientation
#         self.br.sendTransform(t)


# def main():
#     rclpy.init()
#     node = OdomToTF()
#     try:
#         rclpy.spin(node)
#     except KeyboardInterrupt:
#         pass
#     node.destroy_node()
#     rclpy.shutdown()


# if __name__ == '__main__':
#     main()
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, QoSHistoryPolicy, QoSReliabilityPolicy, QoSDurabilityPolicy
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

QOS_RELIABLE = QoSProfile(
    history=QoSHistoryPolicy.KEEP_LAST,
    depth=50,
    reliability=QoSReliabilityPolicy.RELIABLE,
    durability=QoSDurabilityPolicy.VOLATILE,
)

class OdomToTF(Node):
    def __init__(self):
        super().__init__('odom_to_tf')
        self.br = TransformBroadcaster(self)
        self.count = 0
        self.last_odom_stamp = None
        self.last_translation = None
        self.last_rotation = None
        self.publish_rate_hz = float(
            self.declare_parameter('publish_rate_hz', 20.0).value
        )
        if self.publish_rate_hz <= 0.0:
            self.publish_rate_hz = 20.0
        self.publish_timer = self.create_timer(1.0 / self.publish_rate_hz, self._publish_tf)
        self.log_timer = self.create_timer(1.0, self._tick)

        self.sub = self.create_subscription(
            Odometry,
            '/utlidar/robot_odom',
            self.cb,
            QOS_RELIABLE
        )

        self.get_logger().info("odom_to_tf started (RELIABLE sub)")

    def _tick(self):
        if self.last_odom_stamp is None:
            self.get_logger().info("waiting for odom messages...")
        else:
            now = self.get_clock().now().to_msg()
            self.get_logger().info(
                f"rx odom msgs: {self.count}, "
                f"odom stamp: {self.last_odom_stamp.sec}.{self.last_odom_stamp.nanosec:09d}, "
                f"tf stamp(now): {now.sec}.{now.nanosec:09d}"
            )

    def _publish_tf(self):
        if self.last_translation is None or self.last_rotation is None:
            return
        t = TransformStamped()
        # Stamp TF with host time to match sensor timestamps and avoid TF timeouts
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = self.last_translation[0]
        t.transform.translation.y = self.last_translation[1]
        t.transform.translation.z = self.last_translation[2]
        t.transform.rotation.x = self.last_rotation[0]
        t.transform.rotation.y = self.last_rotation[1]
        t.transform.rotation.z = self.last_rotation[2]
        t.transform.rotation.w = self.last_rotation[3]
        self.br.sendTransform(t)

    def cb(self, msg: Odometry):
        self.count += 1
        self.last_odom_stamp = msg.header.stamp
        self.last_translation = (
            msg.pose.pose.position.x,
            msg.pose.pose.position.y,
            msg.pose.pose.position.z,
        )
        self.last_rotation = (
            msg.pose.pose.orientation.x,
            msg.pose.pose.orientation.y,
            msg.pose.pose.orientation.z,
            msg.pose.pose.orientation.w,
        )

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
