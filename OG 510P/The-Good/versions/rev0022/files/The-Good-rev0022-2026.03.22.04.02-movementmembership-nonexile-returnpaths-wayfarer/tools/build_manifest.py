#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from archive_meta import CODENAME, ROOT, TIMESTAMP, current_revision


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    files = []
    for path in sorted(p for p in ROOT.rglob('*') if p.is_file() and p.name != 'MANIFEST.json'):
        rel = path.relative_to(ROOT)
        if '__pycache__' in rel.parts or path.suffix == '.pyc':
            continue
        files.append({'file': str(rel), 'sha256': sha256(path), 'bytes': path.stat().st_size})
    out = {
        'archive': 'The Good',
        'revision': current_revision(),
        'timestamp': TIMESTAMP,
        'codename': CODENAME,
        'file_count': len(files),
        'files': files,
    }
    (ROOT / 'MANIFEST.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
