#!/usr/bin/env python3
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPAIR_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_repair_patch.json'
REPAIR_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_repair.patch'
GUARD_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_guard.json'
GUARD_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_guard.patch'
PATCH_REHEARSAL_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_rehearsal.json'
PATCHSET_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_external_test_patchset.patch'
INTEGRATION_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_integration_rehearsal.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_post_patchset_bundle.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_POST_PATCHSET_BUNDLE.md'
PATCH_PATH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_post_patchset_bundle.patch'


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


def _copy_if_exists(root: Path, relpath: str) -> None:
    src = ROOT / relpath
    if not src.exists():
        return
    dst = root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def _write_support_file(root: Path, relpath: str, data: bytes) -> Path:
    dst = root / relpath
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(data)
    return dst


def _snapshot_bytes(root: Path, relpaths: list[str]) -> dict[str, bytes | None]:
    out: dict[str, bytes | None] = {}
    for rel in relpaths:
        path = root / rel
        out[rel] = path.read_bytes() if path.exists() else None
    return out


def _snapshot_hashes_from_bytes(payloads: dict[str, bytes | None]) -> dict[str, str]:
    return {rel: (_sha256_bytes(data) if data is not None else 'MISSING') for rel, data in payloads.items()}


def _combined_hash(snapshot: dict[str, str]) -> str:
    payload = '\n'.join(f'{rel}:{digest}' for rel, digest in sorted(snapshot.items()))
    return _sha256_bytes(payload.encode('utf-8'))


def _render_patch(baseline: dict[str, bytes | None], final: dict[str, bytes | None], relpaths: list[str]) -> str:
    chunks: list[str] = []
    for rel in relpaths:
        before = baseline[rel]
        after = final[rel]
        if before == after:
            continue
        if before is None:
            fromfile = '/dev/null'
            before_lines: list[str] = []
        else:
            fromfile = f'a/{rel}'
            before_lines = before.decode('utf-8').splitlines(keepends=True)
        if after is None:
            tofile = '/dev/null'
            after_lines: list[str] = []
        else:
            tofile = f'b/{rel}'
            after_lines = after.decode('utf-8').splitlines(keepends=True)
        diff_lines = difflib.unified_diff(before_lines, after_lines, fromfile=fromfile, tofile=tofile, lineterm='')
        chunks.append(''.join(line if line.endswith('\n') else line + '\n' for line in diff_lines))
    return ''.join(chunks)


def collect() -> tuple[dict[str, Any], str, str]:
    repair_report = json.loads(REPAIR_REPORT.read_text(encoding='utf-8'))
    guard_report = json.loads(GUARD_REPORT.read_text(encoding='utf-8'))
    patch_rehearsal = json.loads(PATCH_REHEARSAL_REPORT.read_text(encoding='utf-8'))
    integration_report = json.loads(INTEGRATION_REPORT.read_text(encoding='utf-8'))

    target_files = sorted({
        str(repair_report['target_file']),
        str(guard_report['target_file']),
        *[str(path) for path in patch_rehearsal['targets']['files']],
    })

    with tempfile.TemporaryDirectory(prefix='gr_bootstrap_post_patchset_bundle_') as tmp:
        scratch = Path(tmp)
        for rel in target_files:
            _copy_if_exists(scratch, rel)
        patchset_dst = _write_support_file(scratch, str(PATCHSET_PATCH.relative_to(ROOT)), PATCHSET_PATCH.read_bytes())
        repair_patch_dst = _write_support_file(scratch, str(REPAIR_PATCH.relative_to(ROOT)), REPAIR_PATCH.read_bytes())
        guard_patch_dst = _write_support_file(scratch, str(GUARD_PATCH.relative_to(ROOT)), GUARD_PATCH.read_bytes())

        patchset_check_ok, patchset_check_summary = _run_apply(scratch, patchset_dst, True)
        if not patchset_check_ok:
            raise SystemExit('rust-standing-bootstrap-post-patchset-bundle: patchset precondition failed check')
        patchset_apply_ok, patchset_apply_summary = _run_apply(scratch, patchset_dst, False)
        if not patchset_apply_ok:
            raise SystemExit('rust-standing-bootstrap-post-patchset-bundle: patchset baseline failed apply')
        patchset_baseline = _snapshot_bytes(scratch, target_files)

        steps: list[dict[str, Any]] = []
        for step_id, patch_path in [('repair', repair_patch_dst), ('guard', guard_patch_dst)]:
            check_ok, check_summary = _run_apply(scratch, patch_path, True)
            apply_ok = False
            apply_summary = ''
            if check_ok:
                apply_ok, apply_summary = _run_apply(scratch, patch_path, False)
            steps.append({
                'step_id': step_id,
                'check_ok': check_ok,
                'apply_ok': apply_ok,
                'check_summary': check_summary,
                'apply_summary': apply_summary,
            })
            if not (check_ok and apply_ok):
                raise SystemExit(f'rust-standing-bootstrap-post-patchset-bundle: failed scratch sequence at {step_id}')

        final = _snapshot_bytes(scratch, target_files)

    patch_text = _render_patch(patchset_baseline, final, target_files)
    final_hashes = _snapshot_hashes_from_bytes(final)
    sequence = integration_report['sequences']['monolithic_then_bootstrap']
    changed_files = sorted(rel for rel in target_files if patchset_baseline[rel] != final[rel])
    patch_lines = patch_text.splitlines()
    lines_added = sum(1 for line in patch_lines if line.startswith('+') and not line.startswith('+++'))
    lines_removed = sum(1 for line in patch_lines if line.startswith('-') and not line.startswith('---'))
    patch_bytes = patch_text.encode('utf-8')

    report = {
        'tool': 'build_rust_standing_bootstrap_post_patchset_bundle',
        'source_reports': [
            str(REPAIR_REPORT.relative_to(ROOT)),
            str(GUARD_REPORT.relative_to(ROOT)),
            str(PATCH_REHEARSAL_REPORT.relative_to(ROOT)),
            str(INTEGRATION_REPORT.relative_to(ROOT)),
        ],
        'source_patches': {
            'patchset': str(PATCHSET_PATCH.relative_to(ROOT)),
            'repair': str(REPAIR_PATCH.relative_to(ROOT)),
            'guard': str(GUARD_PATCH.relative_to(ROOT)),
        },
        'patch_path': str(PATCH_PATH.relative_to(ROOT)),
        'target_files': target_files,
        'changed_files': changed_files,
        'final_hashes': final_hashes,
        'summary': {
            'target_file_count': len(target_files),
            'changed_file_count': len(changed_files),
            'patch_sha256': _sha256_bytes(patch_bytes),
            'patch_bytes': len(patch_bytes),
            'lines_added': lines_added,
            'lines_removed': lines_removed,
            'apply_hint': f'git apply {PATCH_PATH.relative_to(ROOT).as_posix()}',
            'combined_final_hash': _combined_hash(final_hashes),
            'matches_monolithic_then_bootstrap_sequence': _combined_hash(final_hashes) == sequence['final_combined_hash'],
            'file_hashes_match_integration_sequence': final_hashes == sequence['final_hashes'],
            'scope': 'patchset-landed convenience bundle for the narrow probe-local bootstrap repair plus standalone guard',
        },
        'scratch_precondition': {
            'baseline_sequence': 'patchset',
            'patchset_check_ok': patchset_check_ok,
            'patchset_apply_ok': patchset_apply_ok,
            'patchset_check_summary': patchset_check_summary,
            'patchset_apply_summary': patchset_apply_summary,
        },
        'scratch_sequence': steps,
        'notes': {
            'first_machine_use': 'use this bundle only when the monolithic comeback patchset is already landed and you want the probe-local bootstrap repair plus standalone guard in one additional apply step',
            'clean_head_alternative': 'on a clean head, prefer the full comeback bundle instead of pre-landing the patchset',
            'equivalent_sequence': 'patchset -> repair -> guard',
        },
    }
    markdown = render_markdown(report)
    return report, markdown, patch_text


def render_markdown(report: dict[str, Any]) -> str:
    s = report['summary']
    lines = [
        '# Rust Standing Bootstrap Post-Patchset Bundle',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_post_patchset_bundle.py`. This emits a one-step Rust patch for the branch state where the monolithic comeback patchset has already landed, compressing the narrow bootstrap repair plus standalone guard into a single follow-on apply.',
        '',
        '## Snapshot',
        '',
        f"- target_file_count: `{s['target_file_count']}`",
        f"- changed_file_count: `{s['changed_file_count']}`",
        f"- patch artifact: `{report['patch_path']}`",
        f"- apply hint: `{s['apply_hint']}`",
        f"- patch_sha256: `{s['patch_sha256']}`",
        f"- patch_bytes: `{s['patch_bytes']}`",
        f"- lines_added: `{s['lines_added']}`",
        f"- lines_removed: `{s['lines_removed']}`",
        f"- combined_final_hash: `{s['combined_final_hash']}`",
        f"- matches_monolithic_then_bootstrap_sequence: `{str(s['matches_monolithic_then_bootstrap_sequence']).lower()}`",
        f"- file_hashes_match_integration_sequence: `{str(s['file_hashes_match_integration_sequence']).lower()}`",
        '',
        '## What this buys the inheritor',
        '',
        '- This closes the last ergonomic gap in the comeback lane: the patchset-already-landed case now has its own one-step convenience patch instead of requiring two extra manual applies.',
        '- The patch is exact, not hand-curated: it is generated from the patchset-landed baseline followed by the same `repair -> guard` sequence already proven in the integration rehearsal.',
        '- The footprint stays intentionally narrow even in this convenience form: only the probe bootstrap source seam and its dedicated guard test differ from the patchset-landed baseline.',
        '',
        '## Changed files',
        '',
    ]
    for rel in report['changed_files']:
        lines.append(f'- `{rel}`')
    lines.extend([
        '',
        '## Practical use',
        '',
        '1. Land the monolithic comeback patchset first, or confirm your branch already matches that patchset baseline.',
        f"2. `{s['apply_hint']}`",
        '3. Run the exact `probe_standing_bootstrap` guards first; they are the only newly introduced test surface in this follow-on bundle.',
        '4. On a clean head, prefer `docs/RUST_STANDING_BOOTSTRAP_COMEBACK_BUNDLE.md` instead of forcing this post-patchset bundle.',
        '',
    ])
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str, expected_patch: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists() or not PATCH_PATH.exists():
        print('rust-standing-bootstrap-post-patchset-bundle: missing report/doc/patch', file=sys.stderr)
        return 1
    if json.loads(OUT_JSON.read_text(encoding='utf-8')) != expected_report:
        print('rust-standing-bootstrap-post-patchset-bundle: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-post-patchset-bundle: markdown drift detected', file=sys.stderr)
        return 1
    if PATCH_PATH.read_text(encoding='utf-8') != expected_patch:
        print('rust-standing-bootstrap-post-patchset-bundle: patch drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-post-patchset-bundle: ok patchset->repair->guard convenience bundle matches integration sequence')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report, markdown, patch_text = collect()
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        PATCH_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown + '\n', encoding='utf-8')
        PATCH_PATH.write_text(patch_text, encoding='utf-8')
        print(f'wrote {OUT_JSON.relative_to(ROOT)}')
        print(f'wrote {OUT_MD.relative_to(ROOT)}')
        print(f'wrote {PATCH_PATH.relative_to(ROOT)}')
        return 0
    return _check(report, markdown, patch_text)


if __name__ == '__main__':
    raise SystemExit(main())
