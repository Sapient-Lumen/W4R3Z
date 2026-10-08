#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

from fixture_plan_lib import interaction_plan, load_fixture


def main() -> None:
    parser = argparse.ArgumentParser(description='Generate a user-facing interaction plan from a saved GlassTTY fixture JSON file')
    parser.add_argument('fixture')
    parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()
    path = Path(args.fixture)
    plan = interaction_plan(load_fixture(path), path=str(path))
    print(json.dumps(plan, indent=2 if args.pretty else None, ensure_ascii=False))


if __name__ == '__main__':
    main()
