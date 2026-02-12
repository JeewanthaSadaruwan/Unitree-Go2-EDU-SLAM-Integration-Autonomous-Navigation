// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from hesai_ros_driver:msg/Firetime.idl
// generated code does not contain a copyright notice
#include "hesai_ros_driver/msg/detail/firetime__rosidl_typesupport_fastrtps_cpp.hpp"
#include "hesai_ros_driver/msg/detail/firetime__struct.hpp"

#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions

namespace hesai_ros_driver
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_hesai_ros_driver
cdr_serialize(
  const hesai_ros_driver::msg::Firetime & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: data
  {
    cdr << ros_message.data;
  }
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_hesai_ros_driver
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  hesai_ros_driver::msg::Firetime & ros_message)
{
  // Member: data
  {
    cdr >> ros_message.data;
  }

  return true;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_hesai_ros_driver
get_serialized_size(
  const hesai_ros_driver::msg::Firetime & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: data
  {
    size_t array_size = 512;
    size_t item_size = sizeof(ros_message.data[0]);
    current_alignment += array_size * item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_hesai_ros_driver
max_serialized_size_Firetime(
  bool & full_bounded,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;
  (void)full_bounded;


  // Member: data
  {
    size_t array_size = 512;

    current_alignment += array_size * sizeof(uint64_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint64_t));
  }

  return current_alignment - initial_alignment;
}

static bool _Firetime__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const hesai_ros_driver::msg::Firetime *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _Firetime__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<hesai_ros_driver::msg::Firetime *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _Firetime__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const hesai_ros_driver::msg::Firetime *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _Firetime__max_serialized_size(bool & full_bounded)
{
  return max_serialized_size_Firetime(full_bounded, 0);
}

static message_type_support_callbacks_t _Firetime__callbacks = {
  "hesai_ros_driver::msg",
  "Firetime",
  _Firetime__cdr_serialize,
  _Firetime__cdr_deserialize,
  _Firetime__get_serialized_size,
  _Firetime__max_serialized_size
};

static rosidl_message_type_support_t _Firetime__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_Firetime__callbacks,
  get_message_typesupport_handle_function,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace hesai_ros_driver

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_hesai_ros_driver
const rosidl_message_type_support_t *
get_message_type_support_handle<hesai_ros_driver::msg::Firetime>()
{
  return &hesai_ros_driver::msg::typesupport_fastrtps_cpp::_Firetime__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, hesai_ros_driver, msg, Firetime)() {
  return &hesai_ros_driver::msg::typesupport_fastrtps_cpp::_Firetime__handle;
}

#ifdef __cplusplus
}
#endif
