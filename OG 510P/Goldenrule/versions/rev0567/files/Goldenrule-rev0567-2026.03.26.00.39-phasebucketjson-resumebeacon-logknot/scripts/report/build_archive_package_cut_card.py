#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_package_cut_card.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_PACKAGE_CUT_CARD.md'
GUARDRAIL_JSON = REPORTS / 'archive_size_guardrail_card.json'
TRIAGE_JSON = REPORTS / 'archive_byte_triage_card.json'
HARNESS_SH = ROOT / 'scripts' / 'test' / 'run_harness.sh'


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path.relative_to(ROOT).as_posix())
    return json.loads(path.read_text(encoding='utf-8'))


def _load_live_mutators() -> list[dict[str, Any]]:
    text = HARNESS_SH.read_text(encoding='utf-8')
    if 'record_env_metadata.py' not in text:
        raise RuntimeError('scripts/test/run_harness.sh no longer records env metadata; revisit package cut mutator assumptions')
    return [
        {
            'command': 'make test-quick',
            'writes': ['artifacts/timing/env_quick.json'],
            'reason': 'scripts/test/run_harness.sh records env metadata before the Rust lane and can therefore perturb the retained tree even when the Rust step fails.',
        },
        {
            'command': 'make test-full',
            'writes': ['artifacts/timing/env_full.json'],
            'reason': 'the same harness records a full-mode env receipt before the slower test ladder continues, so full-mode gates also belong before the final package-boundary size refresh.',
        },
    ]


def build_report() -> dict[str, Any]:
    guardrail = _load_json(GUARDRAIL_JSON)
    triage = _load_json(TRIAGE_JSON)
    mutators = _load_live_mutators()

    archive_totals = guardrail['archive_totals']
    hygiene = guardrail['package_hygiene']
    protected_totals = triage['protected_stack_totals']
    cap_pack = triage['cap_first_markdown_pack']
    cap_pack_totals = triage['cap_first_markdown_pack_totals']

    refresh_sequence = [
        {
            'step': 1,
            'command': 'make test-quick',
            'purpose': 'Run any live mutating gate first so env/timing receipts land before the final package-boundary size snapshot.',
        },
        {
            'step': 2,
            'command': 'make update-command-inventory',
            'purpose': 'Refresh the command inventory before any size-sensitive package cards read the tree.',
        },
        {
            'step': 3,
            'command': 'make update-validator-inventory',
            'purpose': 'Refresh the validator inventory before any size-sensitive package cards read the tree.',
        },
        {
            'step': 4,
            'command': 'make update-artifact-buckets',
            'purpose': 'Refresh the artifact bucket summary before the package-boundary cards measure the live retained tree.',
        },
        {
            'step': 5,
            'command': 'make update-archive-size-guardrail-card',
            'purpose': 'Take a first live package-boundary size snapshot after the inventory writes have settled.',
        },
        {
            'step': 6,
            'command': 'make update-archive-byte-triage-card',
            'purpose': 'Refresh the protect-versus-trim card from the new size snapshot.',
        },
        {
            'step': 7,
            'command': 'make update-archive-size-guardrail-card',
            'purpose': 'Re-take the size snapshot after the triage card itself has rewritten retained files.',
        },
        {
            'step': 8,
            'command': 'make update-archive-byte-triage-card',
            'purpose': 'Reconfirm the trim-first pack against the final post-guardrail tree; this second pair is the fixed-point pass.',
        },
        {
            'step': 9,
            'command': 'make update-archive-package-cut-card',
            'purpose': 'Refresh the package-cut card itself from the settled size and triage surfaces.',
        },
        {
            'step': 10,
            'command': 'make update-archive-reentry-card',
            'purpose': 'Refresh the role-annotated head pointer after the package boundary and comeback surfaces have settled.',
        },
        {
            'step': 11,
            'command': 'make update-archive-handoff-pack',
            'purpose': 'Refresh the hash-bearing blocked-session control-plane pack after the reentry, comeback, package, and external zip surfaces have settled.',
        },
        {
            'step': 12,
            'command': 'make update-archive-revision-cut-card',
            'purpose': 'Refresh the normalized next-name card from the settled package boundary and current head.',
        },
        {
            'step': 13,
            'command': 'make update-archive-zip-lineage-card',
            'purpose': 'Refresh the sibling-zip audit card so the external package lane is checked against the settled current head before the cut.',
        },
        {
            'step': 14,
            'command': 'make update-archive-zip-chronology-card',
            'purpose': 'Refresh the sibling-zip chronology card so timestamp regressions across revision labels stay visible before the cut.',
        },
        {
            'step': 15,
            'command': 'make update-archive-zip-authority-card',
            'purpose': 'Refresh the exact sibling-zip reopen target after the lineage and chronology cards have settled.',
        },
        {
            'step': 16,
            'command': 'make update-archive-zip-digest-card',
            'purpose': 'Refresh the authoritative sibling-zip digest card so the winning external package bytes stay directly verifiable before the cut.',
        },
        {
            'step': 17,
            'command': 'make update-archive-zip-size-truth-card',
            'purpose': 'Refresh the zip-size truth card so the internal proxy is not mistaken for the final sibling zip bytes.',
        },
        {
            'step': 18,
            'command': 'make test-archive-size-guardrail-card && make test-archive-byte-triage-card && make test-archive-package-cut-card && make test-archive-reentry-card && make test-archive-handoff-pack && make test-archive-handoff-pack-verify-tool && make test-authoritative-archive-zip-verify-tool && make test-archive-revision-cut-card && make test-archive-zip-lineage-card && make test-archive-zip-chronology-card && make test-archive-zip-authority-card && make test-archive-zip-digest-card && make test-archive-zip-size-truth-card',
            'purpose': 'Verify that the package-boundary, head-pointer, hash-bearing handoff pack, naming, sibling-zip audit, sibling-zip chronology, exact sibling-zip authority card, authoritative sibling-zip digest card, and zip-size truth card all match the settled tree before cutting the revision zip.',
        },
    ]

    canonical_wrapper_command = 'make settle-archive-truth'
    revision_planner_command = 'python3 scripts/tools/plan_archive_revision_cut.py --descriptor your-summary-slug'
    canonical_cut_command = 'python3 scripts/tools/cut_archive_revision.py --descriptor your-summary-slug --summary "one-line summary"'

    headline_findings = [
        (
            f"The live archive is still package-ready: package_boundary_ready={hygiene['package_boundary_ready']} "
            f"with pdf_count={hygiene['pdf_count']} and scratch_file_count={hygiene['scratch_file_count']}."
        ),
        (
            f"The protected blocked-session handoff stack remains compact at {protected_totals['file_count']} files and "
            f"{protected_totals['raw_bytes']} raw bytes ({protected_totals['raw_mebibytes']} MiB), so package dieting should not start there."
        ),
        (
            f"The first safe diet pack still sits in {len(cap_pack)} large markdown files and would recover "
            f"{cap_pack_totals['recoverable_if_capped_at_128k_bytes']} bytes ({cap_pack_totals['recoverable_if_capped_at_128k_mebibytes']} MiB) "
            "at a 128 KiB cap."
        ),
        (
            'The archive cut should treat `make test-quick` and `make test-full` as pre-size mutators because the harness records '
            '`artifacts/timing/env_<mode>.json` before the Rust lane.'
        ),
        (
            'The minimal stable package-cut ritual is inventory writes first, then a two-pass `size -> triage -> size -> triage` refresh, '
            'then validator checks and only then the revision zip.'
        ),
        (
            'The compact control stack now has a one-command integrity probe: `python3 scripts/tools/verify_archive_handoff_pack.py` checks every retained handoff-pack doc/report hash before you trust the blocked-session surface.'
        ),
        (
            'The authoritative external winner now has a one-command verifier too: `python3 scripts/tools/verify_authoritative_archive_zip.py` proves that the winning sibling zip still exists and matches the live authority rule, selected path, and live bytes.'
        ),
        (
            f'The canonical one-command wrapper for that settle order is `{canonical_wrapper_command}`, which tolerates the expected blocked Rust gate and then refreshes the package-cut, reentry, handoff-pack, revision-cut, zip-lineage, zip-chronology, zip-authority, zip-digest, and zip-size-truth cards after the size/triage fixed point.'
        ),
        (
            f'The normalized next-name planner is `{revision_planner_command}`, so the final root/zip stem does not need to be improvised by hand after the tree is settled.'
        ),
        (
            f'The canonical last-mile cutter is `{canonical_cut_command}`, which runs the settle wrapper, appends the next changelog stub, renames the archive root, refreshes the name-sensitive cards, and writes the zip.'
        ),
    ]

    recommendations = [
        'Run any mutating harness gate (`make test-quick` or `make test-full`) before the final package-boundary refresh; otherwise the env receipt can stale the size card after you thought the tree was settled.',
        f'Prefer `{canonical_wrapper_command}` when you want the whole package-boundary truth surface settled from one command instead of retyping the ritual by hand.',
        'Run `python3 scripts/tools/verify_archive_handoff_pack.py` when you want the compact blocked-session control stack verified from one command before reopening neighboring docs.',
        'Run `python3 scripts/tools/verify_authoritative_archive_zip.py` when you want the external winning zip proved from one command before trusting the selected sibling package bytes.',
        f'Use `{revision_planner_command}` immediately after the settle pass when you need the exact normalized next root/zip stem for the new revision.',
        f'Prefer `{canonical_cut_command}` when you want the final rename/changelog/zip step executed from one command instead of stitching the last mile together by hand.',
        'Check the sibling zip lane after the cut so duplicate revision labels, missing current-root zips, revision/timestamp chronology inversions, and proxy-vs-exact zip-size confusion are caught from files on disk rather than inferred later from chat history.',
        'Treat the second `update-archive-size-guardrail-card` + `update-archive-byte-triage-card` pair as the fixed-point pass, not as redundant ceremony.',
        'If the archive needs bytes before a cut, condense the cap-first markdown pack before touching the protected Rust/cloudtainer/archive-size/package-cut handoff stack.',
        'Keep the long-term package boundary PDF-free and scratch-free; reacquire any large external body only as temporary scratch and delete it before the final size/triage refresh.',
    ]

    return {
        'card': 'archive_package_cut_card',
        'snapshot_date': str(guardrail.get('snapshot_date', '2026-03-23')),
        'archive_totals': archive_totals,
        'package_hygiene': hygiene,
        'protected_stack_totals': protected_totals,
        'cap_first_markdown_pack_totals': cap_pack_totals,
        'cap_first_markdown_pack_paths': [row['path'] for row in cap_pack],
        'canonical_wrapper_command': canonical_wrapper_command,
        'revision_planner_command': revision_planner_command,
        'canonical_cut_command': canonical_cut_command,
        'live_mutators': mutators,
        'refresh_sequence': refresh_sequence,
        'settle_rule': {
            'description': 'After the first inventory writes and the first package-card pass, rerun size and triage one more time. Cut the revision zip only after both package-card validators pass on that post-second-pass tree.',
            'fixed_point_pair': [
                'make update-archive-size-guardrail-card',
                'make update-archive-byte-triage-card',
            ],
            'validation_commands': [
                'make test-archive-size-guardrail-card',
                'make test-archive-byte-triage-card',
                'make test-archive-package-cut-card',
                'make test-archive-reentry-card',
                'make test-archive-handoff-pack',
                'make test-archive-handoff-pack-verify-tool',
                'make test-authoritative-archive-zip-verify-tool',
                'make test-archive-revision-cut-card',
                'make test-archive-zip-lineage-card',
                'make test-archive-zip-chronology-card',
                'make test-archive-zip-authority-card',
                'make test-archive-zip-digest-card',
                'make test-archive-zip-size-truth-card',
            ],
        },
        'headline_findings': headline_findings,
        'recommendations': recommendations,
        'metadata': {
            'source_reports': [
                GUARDRAIL_JSON.relative_to(ROOT).as_posix(),
                TRIAGE_JSON.relative_to(ROOT).as_posix(),
            ],
            'source_scripts': [
                HARNESS_SH.relative_to(ROOT).as_posix(),
                'scripts/report/build_archive_size_guardrail_card.py',
                'scripts/report/build_archive_byte_triage_card.py',
                'scripts/tools/settle_archive_truth.py',
                'scripts/tools/cut_archive_revision.py',
                'scripts/report/build_archive_handoff_pack.py',
                'scripts/test/check_archive_handoff_pack.py',
                'scripts/report/build_archive_zip_size_truth_card.py',
                'scripts/test/check_archive_zip_size_truth_card.py',
                'scripts/tools/verify_authoritative_archive_zip.py',
                'scripts/test/check_authoritative_archive_zip_verify_tool.py',
            ],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = [
        '# Archive Package Cut Card',
        '',
        'Compact package-cut discipline for future inheritors: which package-boundary facts matter, which files to protect or trim first, and in what order to refresh the small archive-truth surfaces before cutting the next revision zip.',
        '',
        '## Headline findings',
        '',
    ]
    for item in report['headline_findings']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Canonical wrapper',
        '',
        f"- wrapper_command: `{report['canonical_wrapper_command']}`",
        '- wrapper_role: run the mutating harness gate first, settle the inventory and size/triage fixed point, then refresh the package-cut, reentry, revision-cut, zip-lineage, zip-chronology, and zip-authority cards before final validation.',
        f"- revision_planner_command: `{report['revision_planner_command']}`",
        f"- canonical_cut_command: `{report['canonical_cut_command']}`",
        '',
        '## Current package boundary',
        '',
        f"- retained_file_count: `{report['archive_totals']['retained_file_count']}`",
        f"- raw_bytes: `{report['archive_totals']['raw_bytes']}` ({report['archive_totals']['raw_mebibytes']} MiB)",
        f"- approx_revision_zip_bytes: `{report['archive_totals']['approx_revision_zip_bytes']}` ({report['archive_totals']['approx_revision_zip_mebibytes']} MiB)",
        f"- package_boundary_ready: `{report['package_hygiene']['package_boundary_ready']}`",
        f"- pdf_count: `{report['package_hygiene']['pdf_count']}`",
        f"- scratch_file_count: `{report['package_hygiene']['scratch_file_count']}`",
        '',
        '## Protect first, trim second',
        '',
        f"- protected_stack_files: `{report['protected_stack_totals']['file_count']}`",
        f"- protected_stack_raw_bytes: `{report['protected_stack_totals']['raw_bytes']}` ({report['protected_stack_totals']['raw_mebibytes']} MiB)",
        f"- cap_first_pack_files: `{report['cap_first_markdown_pack_totals']['file_count']}`",
        f"- cap_first_pack_recoverable_bytes_at_128k: `{report['cap_first_markdown_pack_totals']['recoverable_if_capped_at_128k_bytes']}` ({report['cap_first_markdown_pack_totals']['recoverable_if_capped_at_128k_mebibytes']} MiB)",
        '',
        'Cap-first markdown pack:',
        '',
    ])
    for path in report['cap_first_markdown_pack_paths']:
        lines.append(f'- `{path}`')
    lines.extend([
        '',
        '## Live mutators that must run before the final size refresh',
        '',
    ])
    for row in report['live_mutators']:
        lines.append(f"- `{row['command']}` -> {', '.join(f'`{p}`' for p in row['writes'])}: {row['reason']}")
    lines.extend([
        '',
        '## Stable package-cut refresh order',
        '',
    ])
    for row in report['refresh_sequence']:
        lines.append(f"{row['step']}. `{row['command']}` — {row['purpose']}")
    lines.extend([
        '',
        '## Settle rule',
        '',
        f"- {report['settle_rule']['description']}",
        '- Fixed-point pair:',
    ])
    for cmd in report['settle_rule']['fixed_point_pair']:
        lines.append(f'  - `{cmd}`')
    lines.append('- Final validation commands:')
    for cmd in report['settle_rule']['validation_commands']:
        lines.append(f'  - `{cmd}`')
    lines.extend([
        '',
        '## Guardrails',
        '',
    ])
    for item in report['recommendations']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Source surfaces',
        '',
    ])
    for path in report['metadata']['source_reports']:
        lines.append(f'- `{path}`')
    for path in report['metadata']['source_scripts']:
        lines.append(f'- `{path}`')
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a compact package-cut card for the archive boundary.')
    parser.add_argument('--write', action='store_true', help='write the JSON and markdown outputs in place')
    args = parser.parse_args()

    report = build_report()
    rendered = render_markdown(report)

    if not args.write:
        existing = _load_json(OUT_JSON)
        if existing != report:
            raise SystemExit('archive_package_cut_card.json is stale; run with --write')
        if OUT_MD.read_text(encoding='utf-8') != rendered:
            raise SystemExit('ARCHIVE_PACKAGE_CUT_CARD.md is stale; run with --write')
        print(
            'archive-package-cut-card: ok '
            f"(package_ready={report['package_hygiene']['package_boundary_ready']} protected_bytes={report['protected_stack_totals']['raw_bytes']})"
        )
        return 0

    OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    OUT_MD.write_text(rendered, encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
