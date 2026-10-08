#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import ASSURANCE_ARTIFACTS, ROOT, current_revision


def main() -> None:
    out = {'revision': current_revision(), 'artifacts': ASSURANCE_ARTIFACTS}
    (ROOT / 'ASSURANCE_ARTIFACTS.json').write_text(json.dumps(out, indent=2) + '\n')


if __name__ == '__main__':
    main()
