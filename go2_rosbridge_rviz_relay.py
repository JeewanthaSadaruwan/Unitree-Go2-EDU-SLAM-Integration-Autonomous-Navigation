#!/usr/bin/env python3
"""Relay selected rosbridge topics into local ROS2 topics for RViz2.

Use this when DDS discovery is blocked on Wi-Fi/hotspot but rosbridge is reachable.
"""

from __future__ import annotations

import argparse
import asyncio
import base64
import importlib
import json
import logging
import math
import re
import signal
import sys
import uuid
from dataclasses import dataclass
from typing import Any

import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.node import Node
from rclpy.qos import (
    DurabilityPolicy,
    HistoryPolicy,
    QoSProfile,
    ReliabilityPolicy,
)
from rosidl_runtime_py.convert import message_to_ordereddict
from rosidl_runtime_py import set_message_fields
import websockets

PRIMITIVE_TYPES = {
    "bool",
    "boolean",
    "byte",
    "char",
    "float32",
    "float64",
    "int8",
    "uint8",
    "int16",
    "uint16",
    "int32",
    "uint32",
    "int64",
    "uint64",
    "string",
    "wstring",
}

DEFAULT_TOPICS = [
    "/utlidar/grid_map",
    "/utlidar/robot_odom",
    "/utlidar/robot_pose",
    "/tf",
    "/tf_static",
]

DEFAULT_TOPIC_TYPES = {
    "/utlidar/grid_map": "nav_msgs/OccupancyGrid",
    "/utlidar/robot_odom": "nav_msgs/Odometry",
    "/utlidar/robot_pose": "geometry_msgs/PoseStamped",
    "/tf": "tf2_msgs/TFMessage",
    "/tf_static": "tf2_msgs/TFMessage",
}

NAV_MINIMAL_TOPICS = [
    "/tf",
    "/tf_static",
    "/map",
    "/scan",
    "/robot_description",
    "/joint_states",
    "/utlidar/robot_odom",
    "/plan",
    "/local_plan",
    "/global_costmap/costmap",
    "/global_costmap/costmap_updates",
    "/global_costmap/costmap_raw",
    "/local_costmap/costmap",
    "/local_costmap/costmap_updates",
    "/local_costmap/costmap_raw",
    "/particlecloud",
    "/map_updates",
    "/lidar_points",
]

NAV_MINIMAL_TOPIC_TYPES = {
    "/tf": "tf2_msgs/TFMessage",
    "/tf_static": "tf2_msgs/TFMessage",
    "/map": "nav_msgs/OccupancyGrid",
    "/scan": "sensor_msgs/LaserScan",
    "/robot_description": "std_msgs/String",
    "/joint_states": "sensor_msgs/JointState",
    "/utlidar/robot_odom": "nav_msgs/Odometry",
    "/plan": "nav_msgs/Path",
    "/local_plan": "nav_msgs/Path",
    "/global_costmap/costmap": "nav_msgs/OccupancyGrid",
    "/global_costmap/costmap_updates": "map_msgs/OccupancyGridUpdate",
    "/global_costmap/costmap_raw": "nav2_msgs/Costmap",
    "/local_costmap/costmap": "nav_msgs/OccupancyGrid",
    "/local_costmap/costmap_updates": "map_msgs/OccupancyGridUpdate",
    "/local_costmap/costmap_raw": "nav2_msgs/Costmap",
    "/particlecloud": "geometry_msgs/PoseArray",
    "/map_updates": "map_msgs/OccupancyGridUpdate",
    "/lidar_points": "sensor_msgs/PointCloud2",
}

NAV_UPLINK_TOPIC_TYPES = {
    "/initialpose": "geometry_msgs/PoseWithCovarianceStamped",
    "/goal_pose": "geometry_msgs/PoseStamped",
}

UNSTABLE_BINARY_TOPICS = {
    "/lidar_points",
    "/utlidar/cloud",
    "/global_costmap/costmap_raw",
    "/local_costmap/costmap_raw",
}


@dataclass
class TopicRelay:
    in_topic: str
    out_topic: str
    ros_type: str
    msg_cls: type
    publisher: Any


def normalize_ros_type(type_name: str) -> str:
    return type_name.strip().replace("/msg/", "/")


def normalize_topic(topic: str) -> str:
    if not topic:
        return "/"
    return topic if topic.startswith("/") else f"/{topic}"


def output_topic(prefix: str, topic: str) -> str:
    topic = normalize_topic(topic)
    if topic in {"/tf", "/tf_static"}:
        return topic
    prefix = prefix.strip()
    if not prefix:
        return topic
    prefix = normalize_topic(prefix)
    if prefix == "/":
        return topic
    if topic == "/":
        return prefix
    return f"{prefix}{topic}"


def import_message_class(type_name: str, cache: dict[str, type]) -> type:
    norm = normalize_ros_type(type_name)
    if norm in cache:
        return cache[norm]
    parts = norm.split("/")
    if len(parts) != 2:
        raise ValueError(f"Unsupported ROS message type format: {type_name}")
    package, msg_name = parts
    module = importlib.import_module(f"{package}.msg")
    cls = getattr(module, msg_name)
    cache[norm] = cls
    return cls


def parse_sequence_type(type_str: str) -> str | None:
    m = re.fullmatch(r"sequence<([^,>]+)(?:,\s*\d+)?>", type_str.strip())
    return m.group(1).strip() if m else None


def parse_fixed_array_type(type_str: str) -> str | None:
    m = re.fullmatch(r"(.+)\[\d+\]", type_str.strip())
    return m.group(1).strip() if m else None


def is_message_type(type_str: str) -> bool:
    return "/" in type_str and type_str not in PRIMITIVE_TYPES


def decode_byte_sequence(value: Any, signed: bool) -> Any:
    if isinstance(value, str):
        raw = base64.b64decode(value)
        data = list(raw)
        if signed:
            return [b - 256 if b > 127 else b for b in data]
        return data
    return value


def _to_float(v: Any, default: float = 0.0) -> float:
    if v is None:
        return default
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("inf", "+inf", "infinity", "+infinity"):
            return float("inf")
        if s in ("-inf", "-infinity"):
            return float("-inf")
        if s == "nan":
            return float("nan")
    try:
        return float(v)
    except Exception:
        return default


def _sanitize_float_array(arr: Any, none_as_inf: bool = False) -> list[float]:
    out: list[float] = []
    default = float("inf") if none_as_inf else 0.0
    for x in (arr or []):
        if x is None:
            out.append(default)
        else:
            out.append(_to_float(x, default=default))
    return out


def preprocess_fields(
    msg_cls: type,
    payload: Any,
    class_cache: dict[str, type],
) -> Any:
    if not isinstance(payload, dict):
        return payload

    fields = msg_cls.get_fields_and_field_types()
    out = dict(payload)

    for name, type_str in fields.items():
        if name not in out:
            continue
        value = out[name]
        if value is None:
            continue

        # ROS1-style stamp fallback (secs/nsecs) to ROS2 (sec/nanosec).
        if type_str in {"builtin_interfaces/Time", "builtin_interfaces/Duration"}:
            if isinstance(value, dict):
                if "secs" in value and "sec" not in value:
                    value["sec"] = value.pop("secs")
                if "nsecs" in value and "nanosec" not in value:
                    value["nanosec"] = value.pop("nsecs")
            nested_cls = import_message_class(type_str, class_cache)
            out[name] = preprocess_fields(nested_cls, value, class_cache)
            continue

        seq_inner = parse_sequence_type(type_str)
        if seq_inner is not None:
            if seq_inner == "uint8":
                out[name] = decode_byte_sequence(value, signed=False)
                continue
            if seq_inner == "int8":
                out[name] = decode_byte_sequence(value, signed=True)
                continue
            if is_message_type(seq_inner) and isinstance(value, list):
                nested_cls = import_message_class(seq_inner, class_cache)
                out[name] = [
                    preprocess_fields(nested_cls, item, class_cache) for item in value
                ]
                continue
            continue

        fixed_inner = parse_fixed_array_type(type_str)
        if fixed_inner is not None:
            if fixed_inner == "uint8":
                out[name] = decode_byte_sequence(value, signed=False)
                continue
            if fixed_inner == "int8":
                out[name] = decode_byte_sequence(value, signed=True)
                continue
            if is_message_type(fixed_inner) and isinstance(value, list):
                nested_cls = import_message_class(fixed_inner, class_cache)
                out[name] = [
                    preprocess_fields(nested_cls, item, class_cache) for item in value
                ]
                continue
            continue

        if is_message_type(type_str) and isinstance(value, dict):
            nested_cls = import_message_class(type_str, class_cache)
            out[name] = preprocess_fields(nested_cls, value, class_cache)

    return out


def choose_qos(topic_name: str) -> QoSProfile:
    if topic_name == "/tf_static":
        return QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
    if topic_name in {"/map", "/global_costmap/costmap", "/local_costmap/costmap"}:
        # RViz map displays commonly request TRANSIENT_LOCAL durability.
        return QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=1,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
        )
    if topic_name in {"/tf", "/utlidar/cloud", "/lidar_points", "/scan", "/scan_raw"}:
        return QoSProfile(
            history=HistoryPolicy.KEEP_LAST,
            depth=20,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE,
        )
    return QoSProfile(
        history=HistoryPolicy.KEEP_LAST,
        depth=20,
        reliability=ReliabilityPolicy.RELIABLE,
        durability=DurabilityPolicy.VOLATILE,
    )


class RosbridgeRvizRelay(Node):
    def __init__(
        self,
        node_name: str,
        rosbridge_url: str,
        prefix: str,
        topics: list[str],
        topic_types: dict[str, str],
        prefer_rosapi: bool,
        subscribe_throttle_ms: int,
        allow_binary_topics: bool,
        enable_uplink: bool,
        enable_nav2_action_proxy: bool,
    ):
        super().__init__(node_name)
        self.rosbridge_url = rosbridge_url
        self.prefix = prefix
        self.topics = [normalize_topic(t) for t in topics]
        self.topic_types = {
            normalize_topic(k): normalize_ros_type(v) for k, v in topic_types.items()
        }
        self.prefer_rosapi = bool(prefer_rosapi)
        self.subscribe_throttle_ms = max(0, int(subscribe_throttle_ms))
        self.allow_binary_topics = bool(allow_binary_topics)
        self.enable_uplink = bool(enable_uplink)
        self.enable_nav2_action_proxy = bool(enable_nav2_action_proxy)
        self.topic_relays: dict[str, TopicRelay] = {}
        self.type_cache: dict[str, type] = {}
        self._stop = asyncio.Event()
        self._req_futures: dict[str, asyncio.Future] = {}
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._loop: asyncio.AbstractEventLoop | None = None
        self._uplink_subs: list[Any] = []
        self._nav_action_server: ActionServer | None = None
        self._nav_action_type: Any = None

        if self.enable_uplink:
            uplink_qos = QoSProfile(
                history=HistoryPolicy.KEEP_LAST,
                depth=10,
                reliability=ReliabilityPolicy.RELIABLE,
                durability=DurabilityPolicy.VOLATILE,
            )
            for topic_name, topic_type in NAV_UPLINK_TOPIC_TYPES.items():
                msg_cls = import_message_class(topic_type, self.type_cache)
                sub = self.create_subscription(
                    msg_cls,
                    topic_name,
                    lambda msg, topic=topic_name: self._on_uplink(topic, msg),
                    uplink_qos,
                )
                self._uplink_subs.append(sub)
            self.get_logger().info(
                "Uplink enabled for topics: "
                + ", ".join(sorted(NAV_UPLINK_TOPIC_TYPES.keys()))
            )
        if self.enable_nav2_action_proxy:
            self._setup_nav2_action_proxy()

    def _setup_nav2_action_proxy(self) -> None:
        try:
            from nav2_msgs.action import NavigateToPose
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(
                "Nav2 action proxy disabled: nav2_msgs is unavailable "
                f"({type(exc).__name__}: {exc})"
            )
            return

        self._nav_action_type = NavigateToPose
        self._nav_action_server = ActionServer(
            self,
            NavigateToPose,
            "navigate_to_pose",
            execute_callback=self._execute_nav_goal,
            goal_callback=self._goal_nav_cb,
            cancel_callback=self._cancel_nav_cb,
        )
        self.get_logger().info(
            "Local action proxy enabled: /navigate_to_pose -> rosbridge /goal_pose"
        )

    def _goal_nav_cb(self, goal_request: Any) -> GoalResponse:
        _ = goal_request
        if self._ws is None or self._loop is None:
            self.get_logger().warn(
                "Rejecting /navigate_to_pose goal: rosbridge not connected."
            )
            return GoalResponse.REJECT
        return GoalResponse.ACCEPT

    def _cancel_nav_cb(self, goal_handle: Any) -> CancelResponse:
        _ = goal_handle
        self.get_logger().warn(
            "Cancel accepted locally; remote NavigateToPose cancel is not proxied."
        )
        return CancelResponse.ACCEPT

    def _publish_wire_topic(self, topic: str, payload: dict[str, Any]) -> bool:
        if self._ws is None or self._loop is None:
            return False
        try:
            wire = {"op": "publish", "topic": topic, "msg": payload}
            fut = asyncio.run_coroutine_threadsafe(
                self._ws.send(json.dumps(wire)),
                self._loop,
            )
            fut.result(timeout=2.0)
            return True
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f"Failed wire publish on {topic}: {exc}")
            return False

    async def _call_service(
        self,
        ws: websockets.WebSocketClientProtocol,
        service: str,
        args: dict[str, Any] | None = None,
        timeout_s: float = 5.0,
    ) -> dict[str, Any]:
        req_id = f"svc-{uuid.uuid4().hex}"
        fut: asyncio.Future = asyncio.get_running_loop().create_future()
        self._req_futures[req_id] = fut
        await ws.send(
            json.dumps(
                {
                    "op": "call_service",
                    "id": req_id,
                    "service": service,
                    "args": args or {},
                }
            )
        )
        try:
            return await asyncio.wait_for(fut, timeout=timeout_s)
        finally:
            self._req_futures.pop(req_id, None)

    async def _resolve_topic_type(
        self,
        ws: websockets.WebSocketClientProtocol,
        topic: str,
    ) -> str:
        topic = normalize_topic(topic)
        if not self.prefer_rosapi and topic in self.topic_types:
            return self.topic_types[topic]

        if self.prefer_rosapi:
            try:
                response = await self._call_service(
                    ws,
                    "/rosapi/topic_type",
                    {"topic": topic},
                    timeout_s=5.0,
                )
                values = response.get("values", {})
                ros_type = normalize_ros_type(values.get("type", ""))
                if ros_type:
                    return ros_type
            except Exception as exc:  # noqa: BLE001
                self.get_logger().warn(
                    f"rosapi topic_type failed for {topic}, falling back to static map: {exc}"
                )

        mapped = self.topic_types.get(topic)
        if mapped:
            return mapped
        raise RuntimeError(
            f"Could not resolve type for topic {topic}. "
            "Provide --topic-types mapping or enable rosapi."
        )

    async def _create_relays(self, ws: websockets.WebSocketClientProtocol) -> None:
        created = 0
        for topic in self.topics:
            if (not self.allow_binary_topics) and topic in UNSTABLE_BINARY_TOPICS:
                self.get_logger().warn(
                    f"Skipping unstable binary topic by default: {topic}. "
                    "Use --allow-binary-topics to force-enable."
                )
                continue
            try:
                ros_type = await self._resolve_topic_type(ws, topic)
                msg_cls = import_message_class(ros_type, self.type_cache)
                out = output_topic(self.prefix, topic)
                qos = choose_qos(topic)
                pub = self.create_publisher(msg_cls, out, qos)
                self.topic_relays[topic] = TopicRelay(
                    in_topic=topic,
                    out_topic=out,
                    ros_type=ros_type,
                    msg_cls=msg_cls,
                    publisher=pub,
                )
                created += 1
                self.get_logger().info(
                    f"Relay ready: {topic} ({ros_type}) -> {out}"
                )
            except Exception as exc:  # noqa: BLE001
                self.get_logger().warn(f"Skipping topic {topic}: {exc}")
        if created == 0:
            raise RuntimeError("No topics could be created for relay.")

    async def _subscribe_all(self, ws: websockets.WebSocketClientProtocol) -> None:
        for topic, relay in self.topic_relays.items():
            sub_msg = {
                "op": "subscribe",
                "id": f"sub-{topic}",
                "topic": topic,
            }
            if self.subscribe_throttle_ms > 0:
                sub_msg["throttle_rate"] = self.subscribe_throttle_ms
            await ws.send(json.dumps(sub_msg))
            self.get_logger().info(f"Subscribed: {topic}")

    def _on_uplink(self, topic: str, msg: Any) -> None:
        try:
            payload = message_to_ordereddict(msg)
            self._publish_wire_topic(topic, payload)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f"Failed uplink publish on {topic}: {exc}")

    def _execute_nav_goal(self, goal_handle: Any) -> Any:
        nav_type = self._nav_action_type
        if nav_type is None:
            return None

        result = nav_type.Result()
        try:
            payload = message_to_ordereddict(goal_handle.request.pose)
            ok = self._publish_wire_topic("/goal_pose", payload)
            if not ok:
                if hasattr(result, "error_code"):
                    result.error_code = 1
                goal_handle.abort()
                return result

            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                return result

            if hasattr(result, "error_code"):
                result.error_code = 0
            goal_handle.succeed()
            return result
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(f"NavigateToPose proxy failed: {exc}")
            if hasattr(result, "error_code"):
                result.error_code = 1
            goal_handle.abort()
            return result

    def _publish_topic(self, topic: str, payload: dict[str, Any]) -> None:
        relay = self.topic_relays.get(topic)
        if relay is None:
            return
        try:
            cleaned = preprocess_fields(relay.msg_cls, payload, self.type_cache)
            if relay.ros_type == "sensor_msgs/LaserScan":
                d = cleaned if isinstance(cleaned, dict) else {}
                msg = relay.msg_cls()

                header = d.get("header")
                if isinstance(header, dict):
                    set_message_fields(msg.header, header)

                msg.range_min = _to_float(d.get("range_min"), 0.0)
                msg.range_max = _to_float(d.get("range_max"), 0.0)
                msg.angle_min = _to_float(d.get("angle_min"), -math.pi)
                msg.angle_max = _to_float(d.get("angle_max"), math.pi)
                msg.angle_increment = _to_float(d.get("angle_increment"), 0.0)
                msg.time_increment = _to_float(d.get("time_increment"), 0.0)
                msg.scan_time = _to_float(d.get("scan_time"), 0.0)
                msg.ranges = _sanitize_float_array(d.get("ranges"), none_as_inf=True)
                msg.intensities = _sanitize_float_array(
                    d.get("intensities"), none_as_inf=False
                )
                relay.publisher.publish(msg)
                return

            msg = relay.msg_cls()
            set_message_fields(msg, cleaned)
            relay.publisher.publish(msg)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().warn(
                f"Failed to republish {topic} -> {relay.out_topic}: {exc}"
            )

    async def run_forever(self) -> None:
        while not self._stop.is_set():
            try:
                self.get_logger().info(f"Connecting to {self.rosbridge_url}")
                async with websockets.connect(
                    self.rosbridge_url,
                    open_timeout=5.0,
                    close_timeout=2.0,
                    ping_interval=20.0,
                    ping_timeout=20.0,
                    max_size=2**24,
                ) as ws:
                    self._loop = asyncio.get_running_loop()
                    self._ws = ws
                    self._req_futures.clear()
                    self.topic_relays.clear()

                    await self._create_relays(ws)
                    await self._subscribe_all(ws)
                    self.get_logger().info("Relay running.")

                    while not self._stop.is_set():
                        raw = await ws.recv()
                        data = json.loads(raw)
                        msg_id = data.get("id")
                        if msg_id in self._req_futures:
                            fut = self._req_futures[msg_id]
                            if not fut.done():
                                fut.set_result(data)
                            continue

                        if data.get("op") == "publish":
                            topic = normalize_topic(data.get("topic", ""))
                            payload = data.get("msg")
                            if isinstance(payload, dict):
                                self._publish_topic(topic, payload)
                        rclpy.spin_once(self, timeout_sec=0.0)
                    self._ws = None
                    self._loop = None
            except asyncio.CancelledError:
                break
            except Exception as exc:  # noqa: BLE001
                self._ws = None
                self._loop = None
                self.get_logger().error(f"Relay disconnected/error: {exc}")
                await asyncio.sleep(2.0)

    def stop(self) -> None:
        self._stop.set()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Relay rosbridge topics to local ROS2 for RViz2.",
    )
    parser.add_argument(
        "--rosbridge-url",
        default="ws://10.77.248.104:9090",
        help="Robot rosbridge websocket URL.",
    )
    parser.add_argument(
        "--prefix",
        default="/relay",
        help="Prefix for republished local topics. Use '' for same topic names.",
    )
    parser.add_argument(
        "--topics",
        default=",".join(DEFAULT_TOPICS),
        help="Comma-separated input topics to relay.",
    )
    parser.add_argument(
        "--topic-types",
        default=",".join([f"{k}={v}" for k, v in DEFAULT_TOPIC_TYPES.items()]),
        help=(
            "Comma-separated topic=type mappings, e.g. "
            "/utlidar/cloud=sensor_msgs/PointCloud2."
        ),
    )
    parser.add_argument(
        "--prefer-rosapi",
        action="store_true",
        help="Resolve topic types from /rosapi/topic_type first, then fall back.",
    )
    parser.add_argument(
        "--subscribe-throttle-ms",
        type=int,
        default=100,
        help="rosbridge subscribe throttle rate in milliseconds (0 = disabled).",
    )
    parser.add_argument(
        "--allow-binary-topics",
        action="store_true",
        help=(
            "Enable binary-heavy topics such as point clouds/costmap_raw. "
            "Disabled by default because rosbridge on Foxy often throws "
            "serialization errors on these."
        ),
    )
    parser.add_argument(
        "--nav-minimal",
        action="store_true",
        help="Use navigation-minimal relay set: /tf, /tf_static, /map, /scan.",
    )
    parser.add_argument(
        "--disable-uplink",
        action="store_true",
        help="Disable uplink forwarding of /initialpose and /goal_pose to robot.",
    )
    parser.add_argument(
        "--enable-nav2-action-proxy",
        action="store_true",
        help=(
            "Expose local /navigate_to_pose action server and proxy goals to "
            "robot /goal_pose over rosbridge."
        ),
    )
    parser.add_argument(
        "--node-name",
        default="go2_rosbridge_rviz_relay",
        help="ROS2 node name.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Python log level.",
    )
    return parser.parse_args(argv)


async def async_main(args: argparse.Namespace) -> int:
    logging.basicConfig(level=getattr(logging, args.log_level, logging.INFO))
    if args.nav_minimal:
        topics = list(NAV_MINIMAL_TOPICS)
        topic_types = dict(NAV_MINIMAL_TOPIC_TYPES)
    else:
        topics = [t.strip() for t in args.topics.split(",") if t.strip()]
        if not topics:
            print("No topics provided.", file=sys.stderr)
            return 2
        topic_types: dict[str, str] = {}
        for item in [x.strip() for x in args.topic_types.split(",") if x.strip()]:
            if "=" not in item:
                print(f"Invalid --topic-types entry: {item}", file=sys.stderr)
                return 2
            topic, ros_type = item.split("=", 1)
            topic_types[normalize_topic(topic.strip())] = normalize_ros_type(
                ros_type.strip()
            )

    rclpy.init()
    relay = RosbridgeRvizRelay(
        node_name=args.node_name,
        rosbridge_url=args.rosbridge_url,
        prefix=args.prefix,
        topics=topics,
        topic_types=topic_types,
        prefer_rosapi=args.prefer_rosapi,
        subscribe_throttle_ms=args.subscribe_throttle_ms,
        allow_binary_topics=args.allow_binary_topics,
        enable_uplink=not args.disable_uplink,
        enable_nav2_action_proxy=args.enable_nav2_action_proxy,
    )

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, relay.stop)
        except NotImplementedError:
            pass

    try:
        await relay.run_forever()
    finally:
        relay.destroy_node()
        rclpy.shutdown()
    return 0


def main() -> int:
    args = parse_args(sys.argv[1:])
    try:
        return asyncio.run(async_main(args))
    except KeyboardInterrupt:
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
