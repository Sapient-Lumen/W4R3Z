#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_handoff_pack.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_HANDOFF_PACK.md'
ROOT_RE = re.compile(r'^Goldenrule-rev(?P<revision>\d+)-(?P<stamp>\d{4}\.\d{2}\.\d{2}\.\d{2}\.\d{2})-(?P<descriptor>.+)$')

SOURCE_REPORTS = {
    'archive_reentry_card': REPORTS / 'archive_reentry_card.json',
    'cloudtainer_rust_recovery_card': REPORTS / 'cloudtainer_rust_recovery_card.json',
    'rust_comeback_execution_card': REPORTS / 'rust_comeback_execution_card.json',
    'archive_package_cut_card': REPORTS / 'archive_package_cut_card.json',
    'archive_zip_lineage_card': REPORTS / 'archive_zip_lineage_card.json',
    'archive_zip_chronology_card': REPORTS / 'archive_zip_chronology_card.json',
    'archive_zip_authority_card': REPORTS / 'archive_zip_authority_card.json',
    'archive_zip_digest_card': REPORTS / 'archive_zip_digest_card.json',
    'archive_zip_size_truth_card': REPORTS / 'archive_zip_size_truth_card.json',
    'archive_revision_cut_card': REPORTS / 'archive_revision_cut_card.json',
    'archive_byte_triage_card': REPORTS / 'archive_byte_triage_card.json',
}

GROUP_SPECS = [
    {
        'id': 'archive_head_reentry',
        'role': 'current_head_entry',
        'doc_path': 'docs/ARCHIVE_REENTRY_CARD.md',
        'report_path': 'artifacts/reports/archive_reentry_card.json',
        'verify_command': 'make test-archive-reentry-card',
        'refresh_command': 'make update-archive-reentry-card',
        'intent_summary': 'open the current head card first and recover the exact blocked-cloudtainer, first-machine, and package-steward branches without rescanning neighboring docs',
        'outcome_summary': 'current head, blocked-cloudtainer first move, first Rust foothold, and package closeout route remain path-addressable from one compact entry surface',
    },
    {
        'id': 'blocked_cloudtainer',
        'role': 'blocked_cloudtainer_operator',
        'doc_path': 'docs/CLOUDTAINER_RUST_RECOVERY_CARD.md',
        'report_path': 'artifacts/reports/cloudtainer_rust_recovery_card.json',
        'verify_command': 'make test-cloudtainer-rust-recovery-card',
        'refresh_command': 'make update-cloudtainer-rust-recovery-card',
        'intent_summary': 'decide whether in-place Rust recovery is even possible here or whether to stay on the static lanes',
        'outcome_summary': 'the current cloudtainer stays on the static lane and the local first move remains the shadow-pass medium profile',
    },
    {
        'id': 'first_rust_machine',
        'role': 'first_rust_capable_implementor',
        'doc_path': 'docs/RUST_COMEBACK_EXECUTION_CARD.md',
        'report_path': 'artifacts/reports/rust_comeback_execution_card.json',
        'verify_command': 'make test-rust-comeback-execution-card',
        'refresh_command': 'make update-rust-comeback-execution-card',
        'intent_summary': 'land the first patch shard and run the exact first witness on the first machine that can execute cargo tests',
        'outcome_summary': 'the quick foothold stays one apply plus one exact witness and the full closure still ends at the final dual-lane shard',
    },
    {
        'id': 'package_cut',
        'role': 'package_cut_steward',
        'doc_path': 'docs/ARCHIVE_PACKAGE_CUT_CARD.md',
        'report_path': 'artifacts/reports/archive_package_cut_card.json',
        'verify_command': 'make test-archive-package-cut-card',
        'refresh_command': 'make update-archive-package-cut-card',
        'intent_summary': 'settle the archive truth surfaces in the right order before cutting the next revision zip',
        'outcome_summary': 'the package steward retains the expected-gate settle wrapper, fixed-point size and triage pair, and canonical cut command',
    },
    {
        'id': 'external_zip_lineage',
        'role': 'external_package_lane_audit',
        'doc_path': 'docs/ARCHIVE_ZIP_LINEAGE_CARD.md',
        'report_path': 'artifacts/reports/archive_zip_lineage_card.json',
        'verify_command': 'make test-archive-zip-lineage-card',
        'refresh_command': 'make update-archive-zip-lineage-card',
        'intent_summary': 'show the visible sibling zip chain and detect duplicate revision labels or missing current-root zips',
        'outcome_summary': 'the sibling zip lane stays aligned to the live root and keeps duplicate revision hazards explicit instead of implicit',
    },
    {
        'id': 'external_zip_chronology',
        'role': 'external_package_lane_ordering',
        'doc_path': 'docs/ARCHIVE_ZIP_CHRONOLOGY_CARD.md',
        'report_path': 'artifacts/reports/archive_zip_chronology_card.json',
        'verify_command': 'make test-archive-zip-chronology-card',
        'refresh_command': 'make update-archive-zip-chronology-card',
        'intent_summary': 'keep timestamp inversions across revision order explicit so head authority stays revision-first',
        'outcome_summary': 'the sibling lane still records timestamp regressions that would mislead anyone choosing “latest timestamp” instead of “highest revision”',
    },
    {
        'id': 'external_zip_authority',
        'role': 'authoritative_reopen_target',
        'doc_path': 'docs/ARCHIVE_ZIP_AUTHORITY_CARD.md',
        'report_path': 'artifacts/reports/archive_zip_authority_card.json',
        'verify_command': 'make test-archive-zip-authority-card',
        'refresh_command': 'make update-archive-zip-authority-card',
        'intent_summary': 'emit the exact sibling zip path to reopen after duplicate revisions and chronology inversions are taken into account',
        'outcome_summary': 'the exact external zip winner remains machine-emittable instead of guessed from filenames by hand',
    },
    {
        'id': 'external_zip_digest',
        'role': 'authoritative_zip_bytes',
        'doc_path': 'docs/ARCHIVE_ZIP_DIGEST_CARD.md',
        'report_path': 'artifacts/reports/archive_zip_digest_card.json',
        'verify_command': 'make test-archive-zip-digest-card',
        'refresh_command': 'make update-archive-zip-digest-card',
        'intent_summary': 'publish the authoritative sibling zip size and sha256 so the winning external package bytes can be verified directly',
        'outcome_summary': 'the exact external zip winner is not only locatable but also hash-verifiable from one compact control-plane surface',
    },
    {
        'id': 'external_zip_size_truth',
        'role': 'authoritative_zip_size_truth',
        'doc_path': 'docs/ARCHIVE_ZIP_SIZE_TRUTH_CARD.md',
        'report_path': 'artifacts/reports/archive_zip_size_truth_card.json',
        'verify_command': 'make test-archive-zip-size-truth-card',
        'refresh_command': 'make update-archive-zip-size-truth-card',
        'intent_summary': 'keep the internal packaged-size proxy distinct from the exact sibling zip bytes and calibrate the gap from the immutable predecessor zip',
        'outcome_summary': 'the current head is no longer allowed to pretend its internal proxy is the same as the final external zip bytes',
    },
    {
        'id': 'revision_cut',
        'role': 'next_revision_naming',
        'doc_path': 'docs/ARCHIVE_REVISION_CUT_CARD.md',
        'report_path': 'artifacts/reports/archive_revision_cut_card.json',
        'verify_command': 'make test-archive-revision-cut-card',
        'refresh_command': 'make update-archive-revision-cut-card',
        'intent_summary': 'derive the next safe revision label and normalized root and zip stem before the cut',
        'outcome_summary': 'the next safe revision label remains explicit and the canonical cutter need not improvise root or zip stems by hand',
    },
    {
        'id': 'byte_diet',
        'role': 'archive_byte_diet',
        'doc_path': 'docs/ARCHIVE_BYTE_TRIAGE_CARD.md',
        'report_path': 'artifacts/reports/archive_byte_triage_card.json',
        'verify_command': 'make test-archive-byte-triage-card',
        'refresh_command': 'make update-archive-byte-triage-card',
        'intent_summary': 'recover bytes from the smallest safe markdown compaction pack instead of shaving the compact blocked-session handoff surfaces',
        'outcome_summary': 'the first safe diet pack still outweighs the protected blocked-session control plane and remains the correct place to save bytes first',
    },
]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path.relative_to(ROOT).as_posix())
    return json.loads(path.read_text(encoding='utf-8'))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_sha256(obj: Any) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(',', ':')).encode('utf-8')
    return hashlib.sha256(payload).hexdigest()


def _parse_root_identity() -> dict[str, Any]:
    match = ROOT_RE.match(ROOT.name)
    if not match:
        raise RuntimeError(f'root name does not match archive naming pattern: {ROOT.name}')
    stamp = match.group('stamp')
    return {
        'root_name': ROOT.name,
        'revision': int(match.group('revision')),
        'revision_label': f"rev{match.group('revision')}",
        'timestamp_compact': stamp,
        'timestamp_iso_minute': f"{stamp[0:4]}-{stamp[5:7]}-{stamp[8:10]}T{stamp[11:13]}:{stamp[14:16]}",
        'descriptor_slug': match.group('descriptor'),
    }


def build_report() -> dict[str, Any]:
    root_identity = _parse_root_identity()
    loaded = {name: _load_json(path) for name, path in SOURCE_REPORTS.items()}
    reentry = loaded['archive_reentry_card']
    recovery = loaded['cloudtainer_rust_recovery_card']
    comeback = loaded['rust_comeback_execution_card']
    package = loaded['archive_package_cut_card']
    lineage = loaded['archive_zip_lineage_card']
    chronology = loaded['archive_zip_chronology_card']
    authority = loaded['archive_zip_authority_card']
    zip_size_truth = loaded['archive_zip_size_truth_card']
    revision = loaded['archive_revision_cut_card']
    triage = loaded['archive_byte_triage_card']

    manifest_entries: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []
    for spec in GROUP_SPECS:
        doc = ROOT / spec['doc_path']
        report = ROOT / spec['report_path']
        if not doc.exists() or not report.exists():
            missing = doc if not doc.exists() else report
            raise FileNotFoundError(missing.relative_to(ROOT).as_posix())
        doc_entry = {
            'group_id': spec['id'],
            'role': spec['role'],
            'path': spec['doc_path'],
            'kind': 'doc',
            'bytes': doc.stat().st_size,
            'sha256': _sha256(doc),
        }
        report_entry = {
            'group_id': spec['id'],
            'role': spec['role'],
            'path': spec['report_path'],
            'kind': 'report',
            'bytes': report.stat().st_size,
            'sha256': _sha256(report),
        }
        manifest_entries.extend([doc_entry, report_entry])
        groups.append(
            {
                'id': spec['id'],
                'role': spec['role'],
                'doc_path': spec['doc_path'],
                'doc_bytes': doc_entry['bytes'],
                'doc_sha256': doc_entry['sha256'],
                'report_path': spec['report_path'],
                'report_bytes': report_entry['bytes'],
                'report_sha256': report_entry['sha256'],
                'verify_command': spec['verify_command'],
                'refresh_command': spec['refresh_command'],
                'intent_summary': spec['intent_summary'],
                'outcome_summary': spec['outcome_summary'],
            }
        )

    primary_group = next(group for group in groups if group['id'] == 'archive_head_reentry')
    blocked_group = next(group for group in groups if group['id'] == 'blocked_cloudtainer')
    rust_group = next(group for group in groups if group['id'] == 'first_rust_machine')
    package_group = next(group for group in groups if group['id'] == 'package_cut')
    authority_group = next(group for group in groups if group['id'] == 'external_zip_authority')

    total_bytes = sum(entry['bytes'] for entry in manifest_entries)
    file_count = len(manifest_entries)
    recoverable = triage['cap_first_markdown_pack_totals']['recoverable_if_capped_at_128k_bytes']

    headline_findings = [
        (
            f"The compact archive handoff pack spans {file_count} retained files and {total_bytes} raw bytes "
            f"({round(total_bytes / (1024 * 1024), 3)} MiB), so the exact blocked-session control stack can be verified without reopening the wider tree."
        ),
        (
            f"The primary open target stays `{primary_group['doc_path']}` with verify `{primary_group['verify_command']}` and refresh `{primary_group['refresh_command']}`; "
            f"doc_sha256=`{primary_group['doc_sha256']}`."
        ),
        (
            f"The blocked local move remains `{recovery['current_bridge']['next_commands'][0]}`, and the first Rust foothold remains "
            f"`{comeback['plateau_cards'][0]['apply_hint']}` then `{comeback['plateau_cards'][0]['new_exact_witness_commands'][0]}`."
        ),
        (
            f"The package steward still settles through `{package['canonical_wrapper_command']}` and cuts through `{package['canonical_cut_command']}`, "
            f"while the exact external reopen winner remains `{authority['authoritative_external_head']['zip_name']}`."
        ),
        (
            'The pack itself is now executable: `python3 scripts/tools/verify_archive_handoff_pack.py` verifies every retained doc/report hash in the compact control stack from one command.'
        ),
        (
            'The authoritative external winner now has a one-command verifier too: `python3 scripts/tools/verify_authoritative_archive_zip.py` proves the winning zip path, authority rule, and live bytes together.'
        ),
        (
            f"The cap-first markdown diet pack would still recover {recoverable} bytes, which is {round(recoverable / total_bytes, 3)}x this whole hash-bearing handoff pack."
        ),
        (
            f"The sibling-lane hazards that justify revision-first authority remain explicit in-pack: duplicate_revision_count={lineage['duplicate_revision_count']} and chronology_inversion_count={chronology['adjacent_revision_timestamp_inversion_count']}."
        ),
    ]

    return {
        'card': 'archive_handoff_pack',
        'snapshot_date': reentry.get('snapshot_date', '2026-03-23'),
        'archive_identity': root_identity,
        'primary_open_group_id': primary_group['id'],
        'primary_open_path': primary_group['doc_path'],
        'primary_verify_command': primary_group['verify_command'],
        'primary_refresh_command': primary_group['refresh_command'],
        'ordered_group_ids': [group['id'] for group in groups],
        'pack_totals': {
            'file_count': file_count,
            'raw_bytes': total_bytes,
            'raw_mebibytes': round(total_bytes / (1024 * 1024), 3),
            'manifest_sha256': _canonical_sha256(manifest_entries),
        },
        'headline_findings': headline_findings,
        'groups': groups,
        'manifest_entries': manifest_entries,
        'direct_witnesses': {
            'blocked_cloudtainer_primary_command': recovery['current_bridge']['next_commands'][0],
            'first_rust_apply_hint': comeback['plateau_cards'][0]['apply_hint'],
            'first_rust_exact_witness_command': comeback['plateau_cards'][0]['new_exact_witness_commands'][0],
            'package_settle_command': package['canonical_wrapper_command'],
            'canonical_cut_command': package['canonical_cut_command'],
            'handoff_pack_verify_command': 'python3 scripts/tools/verify_archive_handoff_pack.py',
            'authoritative_zip_basename': authority['authoritative_external_head']['zip_name'],
            'authoritative_zip_resolver_command': 'python3 scripts/tools/resolve_authoritative_archive_zip.py --emit zip-path',
            'authoritative_zip_digest_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256',
            'authoritative_zip_verify_command': 'python3 scripts/tools/verify_authoritative_archive_zip.py',
            'next_revision_label': revision['next_revision_plan']['next_revision_label'],
            'cap_first_markdown_recoverable_bytes': recoverable,
            'duplicate_revision_count': lineage['duplicate_revision_count'],
            'chronology_inversion_count': chronology['adjacent_revision_timestamp_inversion_count'],
        },
        'metadata': {
            'source_reports': [path.relative_to(ROOT).as_posix() for path in SOURCE_REPORTS.values()],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    lines = [
        '# Archive Handoff Pack',
        '',
        'Compact hash-bearing manifest for the blocked-session archive control plane: one primary reentry target plus the exact doc/report pairs and verify/refresh commands that future inheritors should trust first.',
        '',
        '## Headline findings',
        '',
    ]
    for item in report['headline_findings']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Primary entry target',
        '',
        f"- primary_open_path: `{report['primary_open_path']}`",
        f"- primary_verify_command: `{report['primary_verify_command']}`",
        f"- primary_refresh_command: `{report['primary_refresh_command']}`",
        f"- manifest_sha256: `{report['pack_totals']['manifest_sha256']}`",
        f"- pack_file_count: `{report['pack_totals']['file_count']}`",
        f"- pack_raw_bytes: `{report['pack_totals']['raw_bytes']}` ({report['pack_totals']['raw_mebibytes']} MiB)",
        '',
        '## Ordered group manifest',
        '',
    ])
    for group in report['groups']:
        lines.extend([
            f"### {group['id']}",
            '',
            f"- role: `{group['role']}`",
            f"- doc_path: `{group['doc_path']}`",
            f"- doc_bytes: `{group['doc_bytes']}`",
            f"- doc_sha256: `{group['doc_sha256']}`",
            f"- report_path: `{group['report_path']}`",
            f"- report_bytes: `{group['report_bytes']}`",
            f"- report_sha256: `{group['report_sha256']}`",
            f"- verify_command: `{group['verify_command']}`",
            f"- refresh_command: `{group['refresh_command']}`",
            f"- intent_summary: {group['intent_summary']}",
            f"- outcome_summary: {group['outcome_summary']}",
            '',
        ])
    lines.extend([
        '## Direct witnesses',
        '',
        f"- blocked_cloudtainer_primary_command: `{report['direct_witnesses']['blocked_cloudtainer_primary_command']}`",
        f"- first_rust_apply_hint: `{report['direct_witnesses']['first_rust_apply_hint']}`",
        f"- first_rust_exact_witness_command: `{report['direct_witnesses']['first_rust_exact_witness_command']}`",
        f"- package_settle_command: `{report['direct_witnesses']['package_settle_command']}`",
        f"- canonical_cut_command: `{report['direct_witnesses']['canonical_cut_command']}`",
        f"- handoff_pack_verify_command: `{report['direct_witnesses']['handoff_pack_verify_command']}`",
        f"- authoritative_zip_resolver_command: `{report['direct_witnesses']['authoritative_zip_resolver_command']}`",
        f"- authoritative_zip_verify_command: `{report['direct_witnesses']['authoritative_zip_verify_command']}`",
        f"- authoritative_zip_basename: `{report['direct_witnesses']['authoritative_zip_basename']}`",
        f"- next_revision_label: `{report['direct_witnesses']['next_revision_label']}`",
        f"- cap_first_markdown_recoverable_bytes: `{report['direct_witnesses']['cap_first_markdown_recoverable_bytes']}`",
        f"- duplicate_revision_count: `{report['direct_witnesses']['duplicate_revision_count']}`",
        f"- chronology_inversion_count: `{report['direct_witnesses']['chronology_inversion_count']}`",
        '',
        '## Source reports',
        '',
    ])
    for path in report['metadata']['source_reports']:
        lines.append(f'- `{path}`')
    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description='Build a compact hash-bearing handoff pack for the blocked-session archive control plane.')
    parser.add_argument('--write', action='store_true', help='write the JSON report and markdown doc to disk')
    args = parser.parse_args()

    report = build_report()
    markdown = render_markdown(report)
    if args.write:
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        OUT_MD.write_text(markdown, encoding='utf-8')
    else:
        print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
