#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'scripts' / 'tools' / 'audit_rematch_world_benchmark_copy_forward.py'
OUT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_copy_forward_audit_receipt.json'


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    tool = _load_module('audit_rematch_world_benchmark_copy_forward', TOOL)
    receipt = tool.build_receipt(
        artifact=tool.load_json(tool.DEFAULT_ARTIFACT),
        artifact_path=tool.DEFAULT_ARTIFACT,
        seed=tool.load_json(tool.DEFAULT_SEED),
        seed_path=tool.DEFAULT_SEED,
        seed_audit=tool.load_json(tool.DEFAULT_SEED_AUDIT),
        seed_audit_path=tool.DEFAULT_SEED_AUDIT,
        decision_contract=tool.load_json(tool.DEFAULT_DECISION_CONTRACT),
        decision_contract_path=tool.DEFAULT_DECISION_CONTRACT,
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(OUT.relative_to(ROOT).as_posix())
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
