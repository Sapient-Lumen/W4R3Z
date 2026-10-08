#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description='Append a structured GlassTTY worklog entry')
    parser.add_argument('summary')
    parser.add_argument('--status', default='done')
    parser.add_argument('--note', action='append', default=[])
    args = parser.parse_args()

    root = Path(__file__).resolve().parent.parent
    worklog = root / '.llm' / 'WORKLOG.jsonl'
    worklog.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'status': args.status,
        'summary': args.summary,
        'notes': args.note,
    }
    with worklog.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(worklog)


if __name__ == '__main__':
    main()
