#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from unitree_go.msg import LowState

# IMPORTANT: verify motor order for your SDK.
# Common Unitree order is: FR, FL, RR, RL (hip, thigh, calf)
# Joint names must match the URDF (FL=Front Left, FR=Front Right, RL=Rear Left, RR=Rear Right)
JOINT_NAMES = [
    "FR_hip_joint", "FR_thigh_joint", "FR_calf_joint",
    "FL_hip_joint", "FL_thigh_joint", "FL_calf_joint",
    "RR_hip_joint", "RR_thigh_joint", "RR_calf_joint",
    "RL_hip_joint", "RL_thigh_joint", "RL_calf_joint",
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