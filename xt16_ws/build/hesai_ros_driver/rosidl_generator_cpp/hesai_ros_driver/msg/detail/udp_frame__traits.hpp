// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hesai_ros_driver:msg/UdpFrame.idl
// generated code does not contain a copyright notice

#ifndef HESAI_ROS_DRIVER__MSG__DETAIL__UDP_FRAME__TRAITS_HPP_
#define HESAI_ROS_DRIVER__MSG__DETAIL__UDP_FRAME__TRAITS_HPP_

#include "hesai_ros_driver/msg/detail/udp_frame__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__traits.hpp"

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<hesai_ros_driver::msg::UdpFrame>()
{
  return "hesai_ros_driver::msg::UdpFrame";
}

template<>
inline const char * name<hesai_ros_driver::msg::UdpFrame>()
{
  return "hesai_ros_driver/msg/UdpFrame";
}

template<>
struct has_fixed_size<hesai_ros_driver::msg::UdpFrame>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<hesai_ros_driver::msg::UdpFrame>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<hesai_ros_driver::msg::UdpFrame>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HESAI_ROS_DRIVER__MSG__DETAIL__UDP_FRAME__TRAITS_HPP_
