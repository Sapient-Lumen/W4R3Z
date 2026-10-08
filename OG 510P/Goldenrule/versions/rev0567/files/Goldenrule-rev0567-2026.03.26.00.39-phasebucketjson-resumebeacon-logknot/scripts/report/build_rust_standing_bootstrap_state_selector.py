#!/usr/bin/env python3
from __future__ import annotations

import argparse
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
GUARD_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_guard.json'
PATCH_REHEARSAL_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_external_test_patch_rehearsal.json'
PATCHSET_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_external_test_patchset.patch'
REPAIR_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_repair.patch'
GUARD_PATCH = ROOT / 'artifacts' / 'patches' / 'rust_standing_bootstrap_guard.patch'
COMEBACK_BUNDLE_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_comeback_bundle.json'
POST_PATCHSET_BUNDLE_REPORT = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_post_patchset_bundle.json'
OUT_JSON = ROOT / 'artifacts' / 'reports' / 'rust_standing_bootstrap_state_selector.json'
OUT_MD = ROOT / 'docs' / 'RUST_STANDING_BOOTSTRAP_STATE_SELECTOR.md'


SEQUENCES: dict[str, list[str]] = {
    'clean_head': [],
    'repair_only': ['repair'],
    'guard_only': ['guard'],
    'repair_guard': ['repair', 'guard'],
    'patchset_only': ['patchset'],
    'patchset_repair': ['patchset', 'repair'],
    'patchset_guard': ['patchset', 'guard'],
    'final_full': ['patchset', 'repair', 'guard'],
}


STATE_METADATA: dict[str, dict[str, Any]] = {
    'clean_head': {
        'label': 'clean head',
        'summary': 'Exact baseline state for the four bootstrap/comeback target files.',
        'recommendation': {
            'action_kind': 'apply_convenience_bundle',
            'summary': 'Use the clean-head comeback bundle; it is the shortest correct landing from an untouched branch.',
            'primary_apply_hint': 'git apply artifacts/patches/rust_standing_bootstrap_comeback_bundle.patch',
            'next_commands': [
                'git apply artifacts/patches/rust_standing_bootstrap_comeback_bundle.patch',
                'cargo test -p gr_engine --test probe_standing_bootstrap -- --exact',
                'cargo test -p gr_engine --test probe_run',
            ],
        },
        'notes': [
            'This is the only state where the full clean-head convenience bundle is the right one-step choice.',
            'Do not pre-land the monolithic patchset just to use the post-patchset bundle; the clean-head bundle already captures the proven layered sequence.',
        ],
    },
    'repair_only': {
        'label': 'repair only',
        'summary': 'The probe bootstrap source seam is repaired, but neither the guard file nor the comeback patchset has landed yet.',
        'recommendation': {
            'action_kind': 'continue_layered_sequence',
            'summary': 'Continue explicitly: add the guard, then land the monolithic comeback patchset or shard series.',
            'primary_apply_hint': 'git apply artifacts/patches/rust_standing_bootstrap_guard.patch',
            'next_commands': [
                'git apply artifacts/patches/rust_standing_bootstrap_guard.patch',
                'git apply artifacts/patches/rust_external_test_patchset.patch',
                'cargo test -p gr_engine --test probe_standing_bootstrap -- --exact',
            ],
        },
        'notes': [
            'Neither convenience bundle is exact for this partial state because the repair layer is already present.',
            'The safe continuation is still tiny: add the dedicated guard, then land the comeback test patchset.',
        ],
    },
    'guard_only': {
        'label': 'guard only',
        'summary': 'The dedicated bootstrap test file exists, but the source seam and the comeback patchset are still at baseline.',
        'recommendation': {
            'action_kind': 'continue_layered_sequence',
            'summary': 'Repair the source seam next, then land the comeback patchset.',
            'primary_apply_hint': 'git apply artifacts/patches/rust_standing_bootstrap_repair.patch',
            'next_commands': [
                'git apply artifacts/patches/rust_standing_bootstrap_repair.patch',
                'git apply artifacts/patches/rust_external_test_patchset.patch',
                'cargo test -p gr_engine --test probe_standing_bootstrap -- --exact',
            ],
        },
        'notes': [
            'The guard patch can exist before the repair because it only creates the test file.',
            'That state is still useful to recognize, because the clean-head bundle would now collide on the already-created test file.',
        ],
    },
    'repair_guard': {
        'label': 'repair + guard',
        'summary': 'The narrow bootstrap seam repair and its standalone guard are both present, but the broader comeback patchset has not landed.',
        'recommendation': {
            'action_kind': 'land_remaining_patchset',
            'summary': 'Only the comeback patchset remains; land it directly or via the shard series.',
            'primary_apply_hint': 'git apply artifacts/patches/rust_external_test_patchset.patch',
            'next_commands': [
                'git apply artifacts/patches/rust_external_test_patchset.patch',
                'cargo test -p gr_engine --test probe_standing_bootstrap -- --exact',
                'cargo test -p gr_engine --test probe_run',
            ],
        },
        'notes': [
            'This state is what the earlier blocked-session plan called the safest first-machine landing path before the convenience bundles were generated.',
            'At this point the dedicated bootstrap guards should be the first exact witness you run on a Rust-capable machine.',
        ],
    },
    'patchset_only': {
        'label': 'patchset only',
        'summary': 'The monolithic comeback patchset is landed, but the narrow bootstrap repair and guard are still absent.',
        'recommendation': {
            'action_kind': 'apply_convenience_bundle',
            'summary': 'Use the post-patchset convenience bundle; it is the shortest correct follow-on from this branch state.',
            'primary_apply_hint': 'git apply artifacts/patches/rust_standing_bootstrap_post_patchset_bundle.patch',
            'next_commands': [
                'git apply artifacts/patches/rust_standing_bootstrap_post_patchset_bundle.patch',
                'cargo test -p gr_engine --test probe_standing_bootstrap -- --exact',
                'cargo test -p gr_engine --test probe_run',
            ],
        },
        'notes': [
            'This is the only state where the post-patchset convenience bundle is the right one-step choice.',
            'The full clean-head bundle is no longer exact here because the patchset part is already present.',
        ],
    },
    'patchset_repair': {
        'label': 'patchset + repair',
        'summary': 'The broader comeback patchset and the source repair are present, but the standalone guard file has not landed yet.',
        'recommendation': {
            'action_kind': 'land_remaining_guard',
            'summary': 'Only the dedicated bootstrap guard patch remains.',
            'primary_apply_hint': 'git apply artifacts/patches/rust_standing_bootstrap_guard.patch',
            'next_commands': [
                'git apply artifacts/patches/rust_standing_bootstrap_guard.patch',
                'cargo test -p gr_engine --test probe_standing_bootstrap -- --exact',
                'cargo test -p gr_engine --test probe_run',
            ],
        },
        'notes': [
            'This state often appears if someone repaired the source seam manually after landing the existing comeback patchset.',
            'The post-patchset bundle is no longer exact here because it also reintroduces the already-landed repair layer.',
        ],
    },
    'patchset_guard': {
        'label': 'patchset + guard',
        'summary': 'The broader comeback patchset and the standalone guard file are present, but the source repair has not landed yet.',
        'recommendation': {
            'action_kind': 'land_remaining_repair',
            'summary': 'Only the source seam repair remains.',
            'primary_apply_hint': 'git apply artifacts/patches/rust_standing_bootstrap_repair.patch',
            'next_commands': [
                'git apply artifacts/patches/rust_standing_bootstrap_repair.patch',
                'cargo test -p gr_engine --test probe_standing_bootstrap -- --exact',
                'cargo test -p gr_engine --test probe_run',
            ],
        },
        'notes': [
            'This state is structurally valid because the guard patch only adds the test file and does not depend on the repair patch to apply.',
            'Running the dedicated guard tests here should still fail until the repair lands, which is why the selector routes this state to the repair patch rather than a convenience bundle.',
        ],
    },
    'final_full': {
        'label': 'final full state',
        'summary': 'The source repair, standalone guard, and comeback patchset are all already present.',
        'recommendation': {
            'action_kind': 'no_patch_needed',
            'summary': 'Do not apply another bundle; just run the exact witnesses and broader Rust lane checks.',
            'primary_apply_hint': None,
            'next_commands': [
                'cargo test -p gr_engine --test probe_standing_bootstrap -- --exact',
                'cargo test -p gr_engine --test probe_run',
            ],
        },
        'notes': [
            'All known bootstrap/comeback layers are already landed on these target files.',
            'Any further patch application should be treated as drift investigation, not as the normal comeback landing path.',
        ],
    },
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _combined_hash(snapshot: dict[str, str]) -> str:
    payload = '\n'.join(f'{rel}:{digest}' for rel, digest in sorted(snapshot.items()))
    return _sha256_bytes(payload.encode('utf-8'))


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
    return {rel: ((root / rel).read_bytes() if (root / rel).exists() else None) for rel in relpaths}


def _snapshot_hashes(payloads: dict[str, bytes | None]) -> dict[str, str]:
    return {rel: (_sha256_bytes(data) if data is not None else 'MISSING') for rel, data in payloads.items()}


def _materialize_state(target_files: list[str], patch_map: dict[str, Path], sequence: list[str]) -> tuple[dict[str, str], list[dict[str, Any]]]:
    with tempfile.TemporaryDirectory(prefix='gr_bootstrap_state_selector_') as tmp:
        scratch = Path(tmp)
        for rel in target_files:
            _copy_if_exists(scratch, rel)
        local_patch_map = {
            patch_id: _write_support_file(scratch, str(path.relative_to(ROOT)), path.read_bytes())
            for patch_id, path in patch_map.items()
        }
        steps: list[dict[str, Any]] = []
        for step_id in sequence:
            patch_path = local_patch_map[step_id]
            check_ok, check_summary = _run_apply(scratch, patch_path, True)
            apply_ok = False
            apply_summary = ''
            if check_ok:
                apply_ok, apply_summary = _run_apply(scratch, patch_path, False)
            steps.append(
                {
                    'step_id': step_id,
                    'check_ok': check_ok,
                    'apply_ok': apply_ok,
                    'check_summary': check_summary,
                    'apply_summary': apply_summary,
                }
            )
            if not (check_ok and apply_ok):
                raise SystemExit(f'rust-standing-bootstrap-state-selector: failed scratch sequence at {step_id}')
        final_hashes = _snapshot_hashes(_snapshot_bytes(scratch, target_files))
    return final_hashes, steps


def collect() -> tuple[dict[str, Any], str]:
    repair_report = json.loads(REPAIR_REPORT.read_text(encoding='utf-8'))
    guard_report = json.loads(GUARD_REPORT.read_text(encoding='utf-8'))
    patch_rehearsal = json.loads(PATCH_REHEARSAL_REPORT.read_text(encoding='utf-8'))
    comeback_bundle_report = json.loads(COMEBACK_BUNDLE_REPORT.read_text(encoding='utf-8'))
    post_patchset_bundle_report = json.loads(POST_PATCHSET_BUNDLE_REPORT.read_text(encoding='utf-8'))

    target_files = sorted({
        str(repair_report['target_file']),
        str(guard_report['target_file']),
        *[str(path) for path in patch_rehearsal['targets']['files']],
    })
    patch_map = {
        'repair': REPAIR_PATCH,
        'guard': GUARD_PATCH,
        'patchset': PATCHSET_PATCH,
    }

    states: list[dict[str, Any]] = []
    for state_id, sequence in SEQUENCES.items():
        file_hashes, steps = _materialize_state(target_files, patch_map, sequence)
        metadata = STATE_METADATA[state_id]
        states.append(
            {
                'state_id': state_id,
                'label': metadata['label'],
                'sequence': sequence,
                'file_hashes': file_hashes,
                'combined_hash': _combined_hash(file_hashes),
                'summary': metadata['summary'],
                'recommendation': metadata['recommendation'],
                'notes': metadata['notes'],
                'scratch_sequence': steps,
            }
        )

    report = {
        'tool': 'build_rust_standing_bootstrap_state_selector',
        'source_reports': [
            str(REPAIR_REPORT.relative_to(ROOT)),
            str(GUARD_REPORT.relative_to(ROOT)),
            str(PATCH_REHEARSAL_REPORT.relative_to(ROOT)),
            str(COMEBACK_BUNDLE_REPORT.relative_to(ROOT)),
            str(POST_PATCHSET_BUNDLE_REPORT.relative_to(ROOT)),
        ],
        'source_patches': {
            'repair': str(REPAIR_PATCH.relative_to(ROOT)),
            'guard': str(GUARD_PATCH.relative_to(ROOT)),
            'patchset': str(PATCHSET_PATCH.relative_to(ROOT)),
        },
        'tool_hint': 'python3 scripts/tools/choose_rust_standing_bootstrap_path.py --target-root . --json',
        'target_files': target_files,
        'states': states,
        'summary': {
            'state_count': len(states),
            'target_file_count': len(target_files),
            'clean_head_combined_hash': next(state['combined_hash'] for state in states if state['state_id'] == 'clean_head'),
            'patchset_only_combined_hash': next(state['combined_hash'] for state in states if state['state_id'] == 'patchset_only'),
            'final_full_combined_hash': next(state['combined_hash'] for state in states if state['state_id'] == 'final_full'),
            'clean_head_bundle_apply_hint': comeback_bundle_report['summary']['apply_hint'],
            'patchset_only_bundle_apply_hint': post_patchset_bundle_report['summary']['apply_hint'],
        },
        'unknown_policy': {
            'state_id': 'unrecognized_or_drifted_state',
            'recommendation': {
                'action_kind': 'manual_investigation',
                'summary': 'Do not force a convenience bundle onto a mixed or drifted state; inspect the target-file diffs first and continue explicitly.',
                'primary_apply_hint': None,
                'next_commands': [
                    'python3 scripts/tools/choose_rust_standing_bootstrap_path.py --target-root . --json',
                    'git diff -- crates/gr_engine/src/probe.rs crates/gr_engine/tests/metamorphic_suite.rs crates/gr_engine/tests/probe_run.rs crates/gr_engine/tests/probe_standing_bootstrap.rs',
                ],
            },
            'notes': [
                'Recognition is intentionally exact and only covers the four bootstrap/comeback target files.',
                'If your branch has hand edits or drift on those files, finish the landing explicitly instead of replaying a convenience bundle blind.',
            ],
        },
    }
    return report, render_markdown(report)


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        '# Rust Standing Bootstrap State Selector',
        '',
        'Generated by `scripts/report/build_rust_standing_bootstrap_state_selector.py`. This records the exact 4-file branch states that matter for the standing-bootstrap comeback lane and pairs each with the smallest safe next move for the first Rust-capable inheritor.',
        '',
        '## Snapshot',
        '',
        f"- state_count: `{report['summary']['state_count']}`",
        f"- target_file_count: `{report['summary']['target_file_count']}`",
        f"- clean_head_combined_hash: `{report['summary']['clean_head_combined_hash']}`",
        f"- patchset_only_combined_hash: `{report['summary']['patchset_only_combined_hash']}`",
        f"- final_full_combined_hash: `{report['summary']['final_full_combined_hash']}`",
        f"- selector tool: `{report['tool_hint']}`",
        '',
        '## What this buys the inheritor',
        '',
        '- The archive no longer leaves bundle choice to memory or manual reasoning: the selector recognizes the exact clean-head, patchset-only, partial-layer, and already-final states across the four files that actually matter here.',
        '- The convenience bundles now have a hard boundary. They are only recommended when the branch is in the exact state they were built for; otherwise the selector routes the inheritor to the smallest remaining explicit patch sequence.',
        '- Mixed or drifted states fail closed: the selector reports the best partial match, but it refuses to pretend an unknown combination is safe for one-shot replay.',
        '',
        '## Recognition scope',
        '',
        '- `crates/gr_engine/src/probe.rs`',
        '- `crates/gr_engine/tests/metamorphic_suite.rs`',
        '- `crates/gr_engine/tests/probe_run.rs`',
        '- `crates/gr_engine/tests/probe_standing_bootstrap.rs`',
        '',
        '## Known exact states',
        '',
        '| state | combined_hash | next move |',
        '|---|---|---|',
    ]
    for state in report['states']:
        lines.append(
            f"| `{state['state_id']}` | `{state['combined_hash']}` | {state['recommendation']['summary']} |"
        )
    lines.extend([
        '',
        '## Practical use',
        '',
        '1. Run `python3 scripts/tools/choose_rust_standing_bootstrap_path.py --target-root . --json` on the Rust-capable checkout before applying any bootstrap convenience patch.',
        '2. If the selector returns `clean_head`, use `docs/RUST_STANDING_BOOTSTRAP_COMEBACK_BUNDLE.md`.',
        '3. If the selector returns `patchset_only`, use `docs/RUST_STANDING_BOOTSTRAP_POST_PATCHSET_BUNDLE.md`.',
        '4. If it returns one of the partial-layer states, follow the exact remaining patch commands it prints instead of forcing a convenience bundle.',
        '5. If it returns `recognized=false`, diff the four target files first; that is a drift investigation problem, not a replay-the-known-bundle problem.',
        '',
        '## Unknown-state policy',
        '',
        f"- action_kind: `{report['unknown_policy']['recommendation']['action_kind']}`",
        f"- summary: {report['unknown_policy']['recommendation']['summary']}",
        '',
    ])
    return '\n'.join(lines)


def _check(expected_report: dict[str, Any], expected_markdown: str) -> int:
    if not OUT_JSON.exists() or not OUT_MD.exists():
        print('rust-standing-bootstrap-state-selector: missing report/doc', file=sys.stderr)
        return 1
    if json.loads(OUT_JSON.read_text(encoding='utf-8')) != expected_report:
        print('rust-standing-bootstrap-state-selector: report drift detected', file=sys.stderr)
        return 1
    if OUT_MD.read_text(encoding='utf-8').rstrip('\n') != expected_markdown.rstrip('\n'):
        print('rust-standing-bootstrap-state-selector: markdown drift detected', file=sys.stderr)
        return 1
    print('rust-standing-bootstrap-state-selector: ok exact branch-state selector matches known bootstrap/comeback states')
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    report, markdown = collect()
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
