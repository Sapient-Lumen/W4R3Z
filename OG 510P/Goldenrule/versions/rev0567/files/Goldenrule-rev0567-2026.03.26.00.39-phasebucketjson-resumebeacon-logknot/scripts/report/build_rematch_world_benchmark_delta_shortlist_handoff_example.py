#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_delta_shortlist_handoff.json'
TOOL = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_delta_shortlist_handoff.py'


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    tool = _load_module('build_rematch_world_benchmark_delta_shortlist_handoff', TOOL)
    publishability = tool.load_json(tool.PUBLISHABILITY_PATH)
    decision = tool.load_json(tool.DECISION_CONTRACT_PATH)
    handoff = tool.build_handoff(publishability, decision)
    OUT.write_text(json.dumps(handoff, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(f'rematch-world-benchmark-delta-shortlist-handoff-example: wrote {OUT.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
