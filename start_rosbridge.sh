#!/bin/bash

# Standalone rosbridge startup for laptop visualization relay.
# Usage:
#   ./start_rosbridge.sh
#   ./start_rosbridge.sh /path/to/params.yaml

set -eo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARAM_FILE="${1:-$ROOT_DIR/rosbridge_safe.yaml}"

if [[ ! -f "$PARAM_FILE" ]]; then
    echo "Error: params file not found: $PARAM_FILE"
    exit 1
fi

pkill -f rosbridge_websocket || true
source /opt/ros/foxy/setup.bash
export PYENV_VERSION=system
unset PYTHONHOME
hash -r

echo "Starting rosbridge with params: $PARAM_FILE"
echo "WebSocket endpoint: ws://<robot_ip>:9090"
exec ros2 run rosbridge_server rosbridge_websocket --ros-args --params-file "$PARAM_FILE"
