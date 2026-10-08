#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import ROOT, THREADS, current_revision


def main() -> None:
    out = {
        'revision': current_revision(),
        'thread_count': len(THREADS),
        'threads': [
            {
                'id': t['id'],
                'title': t['title'],
                'note_count': len(t['notes']),
                'description': t['description'],
            }
            for t in THREADS
        ],
    }
    (ROOT / 'THREAD_SUMMARY.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
