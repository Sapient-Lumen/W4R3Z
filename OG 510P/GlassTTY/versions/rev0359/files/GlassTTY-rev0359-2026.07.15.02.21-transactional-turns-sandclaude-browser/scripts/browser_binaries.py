from __future__ import annotations

import os
import signal
import shutil
import subprocess
from pathlib import Path
from typing import Any


def _version(path: str) -> str | None:
    if os.environ.get('GLASSTTY_PROBE_BROWSER_VERSION') != '1':
        return None
    try:
        proc = subprocess.Popen(
            [path, '--version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            start_new_session=True,
        )
        try:
            stdout, stderr = proc.communicate(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except Exception:
                proc.kill()
            try:
                stdout, stderr = proc.communicate(timeout=0.5)
            except Exception:
                return None
    except Exception:
        return None
    text = (stdout or stderr or '').strip()
    return text or None


def augment_browser_choice(choice: dict[str, Any]) -> dict[str, Any]:
    path = str(choice.get('path') or '')
    source = str(choice.get('source') or '')
    targets: list[str]
    lowered = path.lower()
    if 'chrome-for-testing' in source or 'chrome-for-testing' in lowered:
        targets = ['chrome-for-testing'] if '146.' in str(choice.get('version') or path) else ['chrome']
    elif 'google-chrome' in source or 'google-chrome' in lowered or lowered.endswith('/chrome'):
        targets = ['chrome']
    else:
        targets = ['chromium']
    payload = dict(choice)
    payload.setdefault('exists', bool(path and Path(path).exists()))
    payload['native_messaging_targets'] = targets
    return payload


def discover_browser_executable() -> dict[str, Any]:
    explicit = os.environ.get('GLASSTTY_BROWSER_BIN')
    if explicit:
        return augment_browser_choice({'source': 'env:GLASSTTY_BROWSER_BIN', 'path': explicit, 'exists': Path(explicit).expanduser().exists(), 'version': explicit})

    candidates = [
        ('chromium', 'chromium'),
        ('google-chrome', 'google-chrome'),
        ('chrome', 'chrome'),
    ]
    for source, executable in candidates:
        found = shutil.which(executable)
        if found:
            return augment_browser_choice({'source': source, 'path': found, 'exists': True, 'version': _version(found)})
    fallback = os.environ.get('BROWSER') or 'chromium'
    return augment_browser_choice({'source': 'fallback', 'path': fallback, 'exists': Path(fallback).exists(), 'version': None})
