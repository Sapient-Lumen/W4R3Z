from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DAEMON_SRC = ROOT / 'daemon' / 'src'
SCRIPTS = ROOT / 'scripts'

# Tests import many root scripts with importlib.util.spec_from_file_location().
# Those spec-loaded modules still use normal imports for their dependencies.
# Keep the scripts directory on sys.path before test-module collection so
# dependency imports are resolved once by Python's import cache instead of each
# module's fallback loader recursively spec-loading dependency cycles.
for path in (DAEMON_SRC, SCRIPTS):
    path_str = str(path)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)
