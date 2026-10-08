#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from native_message_budget_lib import budget_report_for_path


def iter_targets(paths: list[str]) -> list[Path]:
    items: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            items.extend(sorted(path.rglob('*.json')))
        else:
            items.append(path)
    return items



def main() -> None:
    parser = argparse.ArgumentParser(description='Estimate Chrome native-messaging budget usage for GlassTTY fixture JSON artifacts')
    parser.add_argument('path', nargs='+', help='JSON file or directory of JSON files')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    reports = [budget_report_for_path(path) for path in iter_targets(args.path)]
    payload = {'count': len(reports), 'reports': reports}
    print(json.dumps(payload, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == '__main__':
    main()
