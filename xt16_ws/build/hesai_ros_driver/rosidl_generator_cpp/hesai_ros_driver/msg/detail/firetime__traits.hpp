// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from hesai_ros_driver:msg/Firetime.idl
// generated code does not contain a copyright notice

#ifndef HESAI_ROS_DRIVER__MSG__DETAIL__FIRETIME__TRAITS_HPP_
#define HESAI_ROS_DRIVER__MSG__DETAIL__FIRETIME__TRAITS_HPP_

#include "hesai_ros_driver/msg/detail/firetime__struct.hpp"
#include <rosidl_runtime_cpp/traits.hpp>
#include <stdint.h>
#include <type_traits>

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<hesai_ros_driver::msg::Firetime>()
{
  return "hesai_ros_driver::msg::Firetime";
}

template<>
inline const char * name<hesai_ros_driver::msg::Firetime>()
{
  return "hesai_ros_driver/msg/Firetime";
}

template<>
struct has_fixed_size<hesai_ros_driver::msg::Firetime>
  : std::integral_constant<bool, true> {};

template<>
struct has_bounded_size<hesai_ros_driver::msg::Firetime>
  : std::integral_constant<bool, true> {};

template<>
struct is_message<hesai_ros_driver::msg::Firetime>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // HESAI_ROS_DRIVER__MSG__DETAIL__FIRETIME__TRAITS_HPP_
