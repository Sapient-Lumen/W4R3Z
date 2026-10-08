#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import LIFECYCLE_GATES, ROOT, current_revision


def main() -> None:
    out = {'revision': current_revision(), 'gates': LIFECYCLE_GATES}
    (ROOT / 'LIFECYCLE_GATES.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
