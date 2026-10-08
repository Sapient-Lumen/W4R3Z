#!/usr/bin/env bash
set -euo pipefail

# Keep Micromax's tiny test suite insulated from whatever pytest plugins the
# host Python happens to have installed.  Callers can opt back into plugin
# autoloading by setting PYTEST_DISABLE_PLUGIN_AUTOLOAD=0 explicitly.
export PYTEST_DISABLE_PLUGIN_AUTOLOAD="${PYTEST_DISABLE_PLUGIN_AUTOLOAD:-1}"
export PYTHONDONTWRITEBYTECODE="${PYTHONDONTWRITEBYTECODE:-1}"
python -m pytest -q "$@"
