#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
python_cmd=python3
if ! command -v "$python_cmd" >/dev/null 2>&1; then
    python_cmd=python
fi
exec "$python_cmd" "$script_dir/verify.py" "$@"
