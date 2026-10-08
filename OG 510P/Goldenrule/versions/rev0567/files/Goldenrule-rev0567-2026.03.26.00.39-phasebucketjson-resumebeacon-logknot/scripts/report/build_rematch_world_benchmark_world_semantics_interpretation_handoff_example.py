#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_world_semantics_interpretation_handoff.json'
TOOL = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_world_semantics_interpretation_handoff.py'


def _load_module(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    tool = _load_module('build_rematch_world_benchmark_world_semantics_interpretation_handoff', TOOL)
    handoff = tool.build_handoff(
        tool.load_json(tool.PUBLICATION_PATH),
        tool.ROLE_NOTE_PATH.read_text(encoding='utf-8'),
        tool.INHERITOR_BRIEF_PATH.read_text(encoding='utf-8'),
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(handoff, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(OUT.relative_to(ROOT).as_posix())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
