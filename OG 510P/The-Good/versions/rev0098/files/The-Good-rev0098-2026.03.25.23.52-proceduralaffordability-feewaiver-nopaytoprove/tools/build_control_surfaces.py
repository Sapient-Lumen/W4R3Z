#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import CONTROL_SURFACES, ROOT, current_revision


def main() -> None:
    out = {'revision': current_revision(), 'surfaces': CONTROL_SURFACES}
    (ROOT / 'CONTROL_SURFACES.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
