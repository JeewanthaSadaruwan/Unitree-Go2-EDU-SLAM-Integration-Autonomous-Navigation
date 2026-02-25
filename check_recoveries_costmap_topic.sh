#!/bin/bash
set -eo pipefail

source /opt/ros/foxy/setup.bash
set -u

TOPICS=""
if command -v ros2 >/dev/null 2>&1; then
  # ros2 topic list can intermittently fail on this host (Foxy bad_alloc).
  TOPICS="$(timeout 5 ros2 topic list 2>/dev/null || true)"
fi

if echo "$TOPICS" | grep -qx '/local_costmap/costmap_raw'; then
  echo '/local_costmap/costmap_raw'
  echo 'Reason: detected /local_costmap/costmap_raw in live topic list.' >&2
elif echo "$TOPICS" | grep -qx '/local_costmap/costmap'; then
  echo '/local_costmap/costmap'
  echo 'Reason: detected /local_costmap/costmap in live topic list (costmap_raw not found).' >&2
else
  echo '/local_costmap/costmap_raw'
  echo 'Reason: no local_costmap topic detected; defaulting to Foxy/Nav2 convention /local_costmap/costmap_raw.' >&2
fi
