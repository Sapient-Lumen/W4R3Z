#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_RUST_GATE_MARKERS = (
    'rust_exec: junest not found',
    'could not find junest',
    'cargo unavailable',
    'command not found: cargo',
    'command not found: rustc',
)

STEPS: list[dict[str, Any]] = [
    {
        'id': 'gate_quick',
        'command': ['make', 'test-quick'],
        'purpose': 'run the live mutating harness gate before any size-sensitive archive-truth refresh',
        'allow_expected_rust_gate_failure': True,
    },
    {
        'id': 'command_inventory',
        'command': ['make', 'update-command-inventory'],
        'purpose': 'refresh the command inventory before size-sensitive cards read the tree',
    },
    {
        'id': 'validator_inventory',
        'command': ['make', 'update-validator-inventory'],
        'purpose': 'refresh the validator inventory before size-sensitive cards read the tree',
    },
    {
        'id': 'artifact_buckets',
        'command': ['make', 'update-artifact-buckets'],
        'purpose': 'refresh the artifact-bucket summary before package-boundary cards read the tree',
    },
    {
        'id': 'size_pass_1',
        'command': ['make', 'update-archive-size-guardrail-card'],
        'purpose': 'take the first live package-boundary size snapshot after inventories settle',
    },
    {
        'id': 'triage_pass_1',
        'command': ['make', 'update-archive-byte-triage-card'],
        'purpose': 'refresh the protect-versus-trim card from the first live size snapshot',
    },
    {
        'id': 'size_pass_2',
        'command': ['make', 'update-archive-size-guardrail-card'],
        'purpose': 'retake the size snapshot after the first triage write',
    },
    {
        'id': 'triage_pass_2',
        'command': ['make', 'update-archive-byte-triage-card'],
        'purpose': 'reconfirm the trim-first pack on the post-guardrail tree',
    },
    {
        'id': 'package_cut_update',
        'command': ['make', 'update-archive-package-cut-card'],
        'purpose': 'refresh the package-cut card from the settled size and triage surfaces',
    },
    {
        'id': 'reentry_update',
        'command': ['make', 'update-archive-reentry-card'],
        'purpose': 'refresh the archive head pointer from the settled package and comeback surfaces',
    },
    {
        'id': 'handoff_pack_update',
        'command': ['make', 'update-archive-handoff-pack'],
        'purpose': 'refresh the hash-bearing blocked-session control-plane pack after the package, reentry, and comeback surfaces have settled',
    },
    {
        'id': 'revision_cut_update',
        'command': ['make', 'update-archive-revision-cut-card'],
        'purpose': 'refresh the normalized next-revision naming card from the settled package boundary and current head',
    },
    {
        'id': 'zip_lineage_update',
        'command': ['make', 'update-archive-zip-lineage-card'],
        'purpose': 'refresh the sibling-zip audit card from the live external package lane after the settled current head is known',
    },
    {
        'id': 'zip_chronology_update',
        'command': ['make', 'update-archive-zip-chronology-card'],
        'purpose': 'refresh the sibling-zip chronology card so timestamp regressions across revision labels stay visible before the cut',
    },
    {
        'id': 'zip_authority_update',
        'command': ['make', 'update-archive-zip-authority-card'],
        'purpose': 'refresh the sibling-zip authority card so future reopen attempts know exactly which external zip should win',
    },
    {
        'id': 'zip_digest_update',
        'command': ['make', 'update-archive-zip-digest-card'],
        'purpose': 'refresh the authoritative sibling-zip digest card so the winning external package bytes remain directly verifiable',
    },
    {
        'id': 'zip_size_truth_update',
        'command': ['make', 'update-archive-zip-size-truth-card'],
        'purpose': 'refresh the zip-size truth card so internal proxy bytes stay distinct from the exact external sibling zip bytes',
    },
    {
        'id': 'command_inventory_validate',
        'command': ['make', 'test-command-inventory'],
        'purpose': 'verify the command inventory now matches the settled command surface',
    },
    {
        'id': 'validator_inventory_validate',
        'command': ['make', 'test-validator-inventory'],
        'purpose': 'verify the validator inventory now matches the settled validator surface',
    },
    {
        'id': 'artifact_buckets_validate',
        'command': ['make', 'test-artifact-buckets'],
        'purpose': 'verify the artifact-bucket summary now matches the settled retained tree',
    },
    {
        'id': 'size_validate',
        'command': ['make', 'test-archive-size-guardrail-card'],
        'purpose': 'verify the size guardrail card still matches the settled retained tree',
    },
    {
        'id': 'triage_validate',
        'command': ['make', 'test-archive-byte-triage-card'],
        'purpose': 'verify the byte-triage card still matches the settled retained tree',
    },
    {
        'id': 'package_cut_validate',
        'command': ['make', 'test-archive-package-cut-card'],
        'purpose': 'verify the package-cut card still agrees with the settled size and triage surfaces',
    },
    {
        'id': 'reentry_validate',
        'command': ['make', 'test-archive-reentry-card'],
        'purpose': 'verify the archive reentry pointer still agrees with the settled package and comeback surfaces',
    },
    {
        'id': 'handoff_pack_validate',
        'command': ['make', 'test-archive-handoff-pack'],
        'purpose': 'verify the hash-bearing blocked-session control-plane pack still agrees with the settled retained files',
    },
    {
        'id': 'handoff_pack_verify_tool_validate',
        'command': ['make', 'test-archive-handoff-pack-verify-tool'],
        'purpose': 'verify the one-command handoff-pack integrity probe still succeeds on the settled retained control-plane files',
    },
    {
        'id': 'revision_cut_validate',
        'command': ['make', 'test-archive-revision-cut-card'],
        'purpose': 'verify the normalized next-revision naming card still agrees with the settled package boundary and current head',
    },
    {
        'id': 'zip_lineage_validate',
        'command': ['make', 'test-archive-zip-lineage-card'],
        'purpose': 'verify the sibling-zip audit card still agrees with the live external package lane and current head',
    },
    {
        'id': 'zip_chronology_validate',
        'command': ['make', 'test-archive-zip-chronology-card'],
        'purpose': 'verify the sibling-zip chronology card still agrees with the live external package lane and its head-ordering rule',
    },
    {
        'id': 'zip_authority_validate',
        'command': ['make', 'test-archive-zip-authority-card'],
        'purpose': 'verify the sibling-zip authority card still agrees with the live external package lane, duplicates, and chronology hazards',
    },
    {
        'id': 'zip_digest_validate',
        'command': ['make', 'test-archive-zip-digest-card'],
        'purpose': 'verify the authoritative sibling-zip digest card still agrees with the selected external package bytes',
    },
    {
        'id': 'authoritative_zip_verify_validate',
        'command': ['make', 'test-authoritative-archive-zip-verify-tool'],
        'purpose': 'verify that the winning sibling zip still exists and matches the live authority rule, selected path, and bytes from one command',
    },
    {
        'id': 'zip_size_truth_validate',
        'command': ['make', 'test-archive-zip-size-truth-card'],
        'purpose': 'verify the zip-size truth card still distinguishes the internal proxy from exact external sibling zip bytes',
    },
]


def _step_summary(step: dict[str, Any]) -> dict[str, Any]:
    return {
        'id': step['id'],
        'command': ' '.join(step['command']),
        'purpose': step['purpose'],
        'allow_expected_rust_gate_failure': bool(step.get('allow_expected_rust_gate_failure', False)),
    }


def _is_expected_rust_gate_failure(output: str) -> bool:
    lowered = output.lower()
    return any(marker.lower() in lowered for marker in EXPECTED_RUST_GATE_MARKERS)


def _run_step(step: dict[str, Any]) -> str:
    command = list(step['command'])
    proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    if proc.stdout:
        print(proc.stdout, end='')
    if proc.stderr:
        print(proc.stderr, end='', file=sys.stderr)
    if proc.returncode == 0:
        return 'ok'
    combined = (proc.stdout or '') + '\n' + (proc.stderr or '')
    if step.get('allow_expected_rust_gate_failure') and _is_expected_rust_gate_failure(combined):
        print(
            'settle-archive-truth: continuing after expected Rust gate boundary '
            f"during {step['id']} ({' '.join(command)})",
            file=sys.stderr,
        )
        return 'expected_rust_gate_failure'
    raise SystemExit(
        'settle-archive-truth: step failed unexpectedly: '
        f"{step['id']} ({' '.join(command)})"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description='Settle the archive truth surfaces in a stable order before cutting the next revision zip.')
    parser.add_argument('--dry-run', action='store_true', help='print the step order without executing it')
    parser.add_argument('--list-steps', action='store_true', help='emit the canonical step plan as JSON and exit')
    args = parser.parse_args()
    if args.list_steps:
        json.dump({'tool': 'settle_archive_truth', 'steps': [_step_summary(step) for step in STEPS]}, sys.stdout, indent=2)
        sys.stdout.write('\n')
        return 0
    if args.dry_run:
        for index, step in enumerate(STEPS, start=1):
            print(f"{index:02d}. {' '.join(step['command'])} -- {step['purpose']}")
        return 0
    statuses: list[dict[str, str]] = []
    for index, step in enumerate(STEPS, start=1):
        print(f"== [{index}/{len(STEPS)}] {' '.join(step['command'])}", flush=True)
        status = _run_step(step)
        statuses.append({'id': str(step['id']), 'status': status})
    json.dump({'tool': 'settle_archive_truth', 'statuses': statuses}, sys.stdout, indent=2)
    sys.stdout.write('\n')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
