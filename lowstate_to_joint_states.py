#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from unitree_go.msg import LowState

# IMPORTANT: verify motor order for your SDK.
# Common Unitree order is: FR, FL, RR, RL (hip, thigh, calfkk
JOINT_NAMES = [
    "rf_hip_joint", "rf_upper_leg_joint", "rf_lower_leg_joint",
    "lf_hip_joint", "lf_upper_leg_joint", "lf_lower_leg_joint",
    "rh_hip_joint", "rh_upper_leg_joint", "rh_lower_leg_joint",
    "lh_hip_joint", "lh_upper_leg_joint", "lh_lower_leg_joint",
]


MOTOR_INDEX = list(range(12))

class LowStateToJointState(Node):
    def __init__(self):
        super().__init__("lowstate_to_joint_states")
        self.sub = self.create_subscription(LowState, "/lowstate", self.cb, 10)
        self.pub = self.create_publisher(JointState, "/joint_states", 10)

    def cb(self, msg: LowState):
        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = JOINT_NAMES
        js.position = [msg.motor_state[i].q for i in MOTOR_INDEX]
        js.velocity = [msg.motor_state[i].dq for i in MOTOR_INDEX]
        js.effort   = [msg.motor_state[i].tau_est for i in MOTOR_INDEX]
        self.pub.publish(js)

def main():
    rclpy.init()
    node = LowStateToJointState()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
