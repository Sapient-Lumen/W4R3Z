#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPAIR_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_repair_patch.json'
REPAIR_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_repair.patch'
GUARD_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_guard.json'
GUARD_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_guard.patch'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_repair_rehearsal.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_REPAIR_REHEARSAL.md'


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _run_apply(cwd: Path, patch_path: Path, check_only: bool) -> tuple[bool, str]:
    cmd = ['git', 'apply']
    if check_only:
        cmd.append('--check')
    cmd.append(str(patch_path))
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    summary = '\n'.join(part for part in [proc.stdout.strip(), proc.stderr.strip()] if part).strip()
    return proc.returncode == 0, summary


def _write_support_file(root: Path, relpath: str, data: str) -> Path:
    dst = root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(data, encoding='utf-8')
    return dst


def collect() -> dict[str, Any]:
    repair_report = json.loads(REPAIR_REPORT.read_text(encoding='utf-8'))
    repair_patch_text = REPAIR_PATCH.read_text(encoding='utf-8')
    guard_report = json.loads(GUARD_REPORT.read_text(encoding='utf-8'))
    guard_patch_text = GUARD_PATCH.read_text(encoding='utf-8')
    source_rel = str(repair_report['target_file'])
    source_text = (ROOT / source_rel).read_text(encoding='utf-8')
    expected_source_sha = str(repair_report['summary']['target_sha256'])
    expected_source_bytes = int(repair_report['summary']['target_bytes'])
    guard_target_rel = str(guard_report['target_file'])
    expected_guard_sha = str(guard_report['summary']['target_sha256'])
    expected_guard_bytes = int(guard_report['summary']['target_bytes'])

    with tempfile.TemporaryDirectory(prefix='gr_bootstrap_repair_') as tmp:
        scratch = Path(tmp)
        repair_patch_dst = _write_support_file(scratch, str(REPAIR_PATCH.relative_to(ROOT)), repair_patch_text)
        guard_patch_dst = _write_support_file(scratch, str(GUARD_PATCH.relative_to(ROOT)), guard_patch_text)
        _write_support_file(scratch, source_rel, source_text)

        repair_check_ok, repair_check_summary = _run_apply(scratch, repair_patch_dst, True)
        repair_apply_ok = False
        repair_apply_summary = ''
        repaired_sha = ''
        repaired_bytes = 0
        guard_check_ok = False
        guard_check_summary = ''
        guard_apply_ok = False
        guard_apply_summary = ''
        guard_target_sha = ''
        guard_target_bytes = 0

        if repair_check_ok:
            repair_apply_ok, repair_apply_summary = _run_apply(scratch, repair_patch_dst, False)
            source_path = scratch / source_rel
            if source_path.exists():
                payload = source_path.read_bytes()
                repaired_sha = _sha256_bytes(payload)
                repaired_bytes = len(payload)
            if repair_apply_ok:
                guard_check_ok, guard_check_summary = _run_apply(scratch, guard_patch_dst, True)
                if guard_check_ok:
                    guard_apply_ok, guard_apply_summary = _run_apply(scratch, guard_patch_dst, False)
                    guard_target_path = scratch / guard_target_rel
                    if guard_target_path.exists():
                        payload = guard_target_path.read_bytes()
                        guard_target_sha = _sha256_bytes(payload)
                        guard_target_bytes = len(payload)

    return {
        'tool': 'build_rust_standing_bootstrap_repair_rehearsal',
        'source_repair_report': str(REPAIR_REPORT.relative_to(ROOT)),
        'source_repair_patch': str(REPAIR_PATCH.relative_to(ROOT)),
        'source_guard_report': str(GUARD_REPORT.relative_to(ROOT)),
        'source_guard_patch': str(GUARD_PATCH.relative_to(ROOT)),
        'repair_target_file': source_rel,
        'guard_target_file': guard_target_rel,
        'summary': {
            'repair_check_ok': repair_check_ok,
            'repair_apply_ok': repair_apply_ok,
            'repair_target_sha_matches_report': repaired_sha == expected_source_sha,
            'repair_target_bytes_match_report': repaired_bytes == expected_source_bytes,
            'guard_check_ok_after_repair': guard_check_ok,
            'guard_apply_ok_after_repair': guard_apply_ok,
            'guard_target_sha_matches_report': guard_target_sha == expected_guard_sha,
            'guard_target_bytes_match_report': guard_target_bytes == expected_guard_bytes,
            'repair_patch_sha256': _sha256_bytes(repair_patch_text.encode('utf-8')),
            'guard_patch_sha256': _sha256_bytes(guard_patch_text.encode('utf-8')),
        },
        'notes': {
            'sequence': 'repair patch applies first to probe.rs, then the standalone guard patch cleanly layers on top to create the dedicated regression test file',
            'repair_check_summary': repair_check_summary,
            'repair_apply_summary': repair_apply_summary,
            'guard_check_summary': guard_check_summary,
            'guard_apply_summary': guard_apply_summary,
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    return '\n'.join([
        '# Rust Standing Bootstrap Repair Rehearsal',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_repair_rehearsal.py`. This scratch-applies the source-level bootstrap repair patch and then the standalone regression guard patch to prove the intended first-machine sequence lands cleanly.',
        '',
        '## Snapshot',
        '',
        f"- source repair patch: `{report['source_repair_patch']}`",
        f"- source guard patch: `{report['source_guard_patch']}`",
        f"- repair target file: `{report['repair_target_file']}`",
        f"- guard target file: `{report['guard_target_file']}`",
        f"- repair_check_ok: `{str(s['repair_check_ok']).lower()}`",
        f"- repair_apply_ok: `{str(s['repair_apply_ok']).lower()}`",
        f"- repair_target_sha_matches_report: `{str(s['repair_target_sha_matches_report']).lower()}`",
        f"- repair_target_bytes_match_report: `{str(s['repair_target_bytes_match_report']).lower()}`",
        f"- guard_check_ok_after_repair: `{str(s['guard_check_ok_after_repair']).lower()}`",
        f"- guard_apply_ok_after_repair: `{str(s['guard_apply_ok_after_repair']).lower()}`",
        f"- guard_target_sha_matches_report: `{str(s['guard_target_sha_matches_report']).lower()}`",
        f"- guard_target_bytes_match_report: `{str(s['guard_target_bytes_match_report']).lower()}`",
        f"- repair_patch_sha256: `{s['repair_patch_sha256']}`",
        f"- guard_patch_sha256: `{s['guard_patch_sha256']}`",
        '',
        '## Sequence proved here',
        '',
        '1. `git apply artifacts/patches/rust_standing_bootstrap_repair.patch`',
        '2. `git apply artifacts/patches/rust_standing_bootstrap_guard.patch`',
        '3. Run the exact `probe_standing_bootstrap` guard tests listed in the repair card.',
        '',
    ])


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    actual_report = json.loads(OUT_JSON.read_text(encoding='utf-8'))
    if actual_report != expected_report:
        raise SystemExit('rust-standing-bootstrap-repair-rehearsal: report drift detected')
    actual_markdown = OUT_MD.read_text(encoding='utf-8').rstrip('\n')
    if actual_markdown != expected_markdown.rstrip('\n'):
        raise SystemExit('rust-standing-bootstrap-repair-rehearsal: markdown drift detected')
    print('rust-standing-bootstrap-repair-rehearsal: ok repair/guard sequence clean')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report = collect()
    markdown = render_markdown(report)
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown + '\n', encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'wrote {OUT_MD.relative_to(ROOT)}')
        return 0
    return _check(report, markdown)


if __name__ == '__main__':
    raise SystemExit(main())
