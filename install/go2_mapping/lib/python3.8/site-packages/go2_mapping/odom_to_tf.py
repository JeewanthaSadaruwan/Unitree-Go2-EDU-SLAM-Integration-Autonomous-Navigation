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
        self.create_timer(1.0, self._tick)

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

    def cb(self, msg: Odometry):
        self.count += 1
        self.last_odom_stamp = msg.header.stamp

        t = TransformStamped()
        # IMPORTANT: stamp TF with host time to match Hesai-derived LaserScan stamps
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation = msg.pose.pose.orientation
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
