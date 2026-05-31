#!/usr/bin/env bash
# Resolve the Python runtime used by ai-news harness scripts.
# Prefer Python 3.11 because the local Homebrew python3 may point at an
# experimental interpreter that can hang before user code executes.

set -euo pipefail

resolve_python() {
  if [ -n "${PYTHON:-}" ] && command -v "$PYTHON" >/dev/null 2>&1; then
    printf '%s\n' "$PYTHON"
    return 0
  fi

  for candidate in python3.11 python3; do
    if command -v "$candidate" >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

if [ "${1:-}" = "--print" ]; then
  resolve_python
  exit $?
fi

PYTHON_BIN="$(resolve_python)" || {
  printf 'ERROR: Python 3.11+ or python3 is required for ai-news harness scripts.\n' >&2
  exit 127
}

exec "$PYTHON_BIN" "$@"
