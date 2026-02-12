// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hesai_ros_driver:msg/Ptp.idl
// generated code does not contain a copyright notice

#ifndef HESAI_ROS_DRIVER__MSG__DETAIL__PTP__TRAITS_HPP_
#define HESAI_ROS_DRIVER__MSG__DETAIL__PTP__TRAITS_HPP_

#include "hesai_ros_driver/msg/detail/ptp__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<hesai_ros_driver::msg::Ptp>()
{
  return "hesai_ros_driver::msg::Ptp";
}

template<>
inline const char * name<hesai_ros_driver::msg::Ptp>()
{
  return "hesai_ros_driver/msg/Ptp";
}

template<>
struct has_fixed_size<hesai_ros_driver::msg::Ptp>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<hesai_ros_driver::msg::Ptp>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<hesai_ros_driver::msg::Ptp>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HESAI_ROS_DRIVER__MSG__DETAIL__PTP__TRAITS_HPP_
