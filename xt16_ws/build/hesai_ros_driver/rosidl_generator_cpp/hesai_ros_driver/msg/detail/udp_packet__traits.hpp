// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hesai_ros_driver:msg/UdpPacket.idl
// generated code does not contain a copyright notice

#ifndef HESAI_ROS_DRIVER__MSG__DETAIL__UDP_PACKET__TRAITS_HPP_
#define HESAI_ROS_DRIVER__MSG__DETAIL__UDP_PACKET__TRAITS_HPP_

#include "hesai_ros_driver/msg/detail/udp_packet__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'stamp'
#include "builtin_interfaces/msg/detail/time__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<hesai_ros_driver::msg::UdpPacket>()
{
  return "hesai_ros_driver::msg::UdpPacket";
}

template<>
inline const char * name<hesai_ros_driver::msg::UdpPacket>()
{
  return "hesai_ros_driver/msg/UdpPacket";
}

template<>
struct has_fixed_size<hesai_ros_driver::msg::UdpPacket>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hesai_ros_driver::msg::UdpPacket>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hesai_ros_driver::msg::UdpPacket>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HESAI_ROS_DRIVER__MSG__DETAIL__UDP_PACKET__TRAITS_HPP_
