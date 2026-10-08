#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import CODENAME, RELEASE_HIGHLIGHTS, ROOT, TIMESTAMP, current_revision


def main() -> None:
    out = {
        'archive': 'The Good',
        'current_revision': current_revision(),
        'releases': [
            {
                'revision': current_revision(),
                'timestamp': TIMESTAMP,
                'codename': CODENAME,
                'highlights': RELEASE_HIGHLIGHTS,
            }
        ],
    }
    (ROOT / 'RELEASES.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
