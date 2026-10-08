#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / 'scripts' / 'tools' / 'build_rematch_world_benchmark_publication_chain_receipt.py'
OUT = ROOT / 'examples' / 'snapshots' / 'rematch_world_benchmark_publication_chain_receipt.json'
def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f'could not load module {name} from {path}')
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module

def main() -> int:
    tool = _load_module('build_rematch_world_benchmark_publication_chain_receipt', TOOL)
    receipt = tool.build_receipt(tool.load_json(tool.DEFAULT_FROZEN_AUDIT), tool.DEFAULT_FROZEN_AUDIT, tool.load_json(tool.DEFAULT_COPY_FORWARD_AUDIT), tool.DEFAULT_COPY_FORWARD_AUDIT, tool.load_json(tool.DEFAULT_PUBLICATION_SPINE_AUDIT), tool.DEFAULT_PUBLICATION_SPINE_AUDIT, tool.load_json(tool.DEFAULT_POST_PRUNE_AUDIT), tool.DEFAULT_POST_PRUNE_AUDIT)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(receipt, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    print(OUT.relative_to(ROOT).as_posix()); return 0
if __name__ == '__main__':
    raise SystemExit(main())
