#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

_script = Path(__file__).with_name('e2e_fixturelab_capture.py')
_spec = importlib.util.spec_from_file_location('glasstty_e2e_fixturelab_capture_module', _script)
_module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_module)

if __name__ == '__main__':
    _module.cli()
