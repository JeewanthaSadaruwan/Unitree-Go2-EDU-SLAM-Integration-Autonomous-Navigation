#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARAM_FILE="${1:-${ROOT_DIR}/config/rosbridge_nav.yaml}"

if [[ ! -f "${PARAM_FILE}" ]]; then
  echo "rosbridge param file not found: ${PARAM_FILE}" >&2
  exit 1
fi

pkill -f rosbridge_websocket || true
pkill -f run_voice_agent_py311.sh || true

set +u
source /opt/ros/foxy/setup.bash
set -u
export PYENV_VERSION=system
unset PYTHONHOME
hash -r

echo "[rosbridge] mode=nav params=${PARAM_FILE}" >&2
exec ros2 run rosbridge_server rosbridge_websocket --ros-args --params-file "${PARAM_FILE}"
