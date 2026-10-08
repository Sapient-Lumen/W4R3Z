#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORT_PATH = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_checkpoints.json'
VERIFIER_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_checkpoint_verifier.json'
VERIFIER_DOC = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_CHECKPOINT_VERIFIER.md'
TOOL_PATH = ROOT / 'scripts' / 'tools' / 'verify_rust_standing_bootstrap_checkpoint.py'
PATCH_ROOT = ROOT / 'artifacts' / 'patches'
TARGET_FILES = [
    'crates/gr_engine/src/probe.rs',
    'crates/gr_engine/tests/metamorphic_suite.rs',
    'crates/gr_engine/tests/probe_run.rs',
    'crates/gr_engine/tests/probe_standing_bootstrap.rs',
]
PATCH_MAP = {
    'repair': PATCH_ROOT / 'rust_standing_bootstrap_repair.patch',
    'guard': PATCH_ROOT / 'rust_standing_bootstrap_guard.patch',
    'patchset': PATCH_ROOT / 'rust_external_test_patchset.patch',
    'bundle': PATCH_ROOT / 'rust_standing_bootstrap_comeback_bundle.patch',
    'post_patchset_bundle': PATCH_ROOT / 'rust_standing_bootstrap_post_patchset_bundle.patch',
}


def _materialize(sequence: list[str], drift: bool = False) -> tuple[Path, tempfile.TemporaryDirectory[str]]:
    tmp = tempfile.TemporaryDirectory(prefix='gr_bootstrap_checkpoint_verifier_tool_')
    scratch = Path(tmp.name)
    for rel in TARGET_FILES:
        src = ROOT / rel
        if src.exists():
            dst = scratch / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    for patch in PATCH_MAP.values():
        dst = scratch / patch.relative_to(ROOT)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(patch, dst)
    for step in sequence:
        proc = subprocess.run(
            ['git', 'apply', str(PATCH_MAP[step].relative_to(ROOT))],
            cwd=scratch,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise SystemExit('checkpoint-verifier-tool-check: failed to materialize scratch state\n' + proc.stderr)
    if drift:
        path = scratch / 'crates/gr_engine/src/probe.rs'
        path.write_text(path.read_text(encoding='utf-8') + '\n// drifted in checkpoint verifier tool check\n', encoding='utf-8')
    return scratch, tmp


def _run(target_root: Path, *args: str) -> tuple[int, dict[str, Any] | None]:
    proc = subprocess.run(
        ['python3', str(TOOL_PATH), '--report', str(REPORT_PATH), '--target-root', str(target_root), '--json', *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    payload = json.loads(proc.stdout) if proc.stdout.strip() else None
    return proc.returncode, payload


def main() -> int:
    missing = [path for path in [REPORT_PATH, VERIFIER_REPORT, VERIFIER_DOC, TOOL_PATH] if not path.exists()]
    if missing:
        for path in missing:
            print(f'checkpoint-verifier-tool-check: missing {path.relative_to(ROOT)}', file=sys.stderr)
        return 1

    checkpoints = json.loads(REPORT_PATH.read_text(encoding='utf-8'))
    by_state = {state['state_id']: state for state in checkpoints['state_checkpoints']}

    rc, payload = _run(ROOT, '--expect-state-id', 'clean_head', '--expect-combined-hash', by_state['clean_head']['observed_combined_hash'])
    if rc != 0 or payload is None or not payload['verified'] or payload['matched_state_id'] != 'clean_head':
        print('checkpoint-verifier-tool-check: live clean_head verification failed', file=sys.stderr)
        return 1

    scratch, tmp = _materialize(['repair'])
    try:
        rc, payload = _run(
            scratch,
            '--expect-state-id', 'repair_only',
            '--expect-combined-hash', by_state['repair_only']['observed_combined_hash'],
        )
        if rc != 0 or payload is None or not payload['verified'] or payload['matched_state_id'] != 'repair_only':
            print('checkpoint-verifier-tool-check: direct repair_only verification failed', file=sys.stderr)
            return 1
        cp = by_state['repair_only']['checkpoints'][0]
        apply_proc = subprocess.run(cp['apply_command'].split(), cwd=scratch, capture_output=True, text=True, check=False)
        if apply_proc.returncode != 0:
            print('checkpoint-verifier-tool-check: failed to apply guard checkpoint in scratch', file=sys.stderr)
            return 1
        rc, payload = _run(scratch, '--from-state-id', 'repair_only', '--step-index', '1')
        if (
            rc != 0 or payload is None or not payload['verified']
            or payload['matched_state_id'] != cp['expected_state_id']
            or payload['observed_combined_hash'] != cp['expected_combined_hash']
        ):
            print('checkpoint-verifier-tool-check: route-step verification from repair_only step 1 failed', file=sys.stderr)
            return 1
    finally:
        tmp.cleanup()

    scratch, tmp = _materialize(['repair'], drift=True)
    try:
        rc, payload = _run(scratch, '--expect-state-id', 'repair_only')
        if rc == 0 or payload is None or payload['verified'] or payload['recognized']:
            print('checkpoint-verifier-tool-check: drifted scratch state did not fail closed', file=sys.stderr)
            return 1
    finally:
        tmp.cleanup()

    print('checkpoint-verifier-tool-check: ok live clean_head, direct repair_only, route-step repair_only->repair_guard, and drift failure all hold')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
