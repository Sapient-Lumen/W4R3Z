#!/usr/bin/env python3
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / 'artifacts' / 'reports'
OUT_JSON = REPORTS / 'archive_zip_size_truth_card.json'
OUT_MD = ROOT / 'docs' / 'ARCHIVE_ZIP_SIZE_TRUTH_CARD.md'
SIZE_JSON = REPORTS / 'archive_size_guardrail_card.json'
AUTHORITY_JSON = REPORTS / 'archive_zip_authority_card.json'


def _mib(size_bytes: int) -> float:
    return round(size_bytes / (1024 * 1024), 6)


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path.relative_to(ROOT).as_posix())
    return json.loads(path.read_text(encoding='utf-8'))


def _load_embedded_guardrail(zip_path: Path) -> dict[str, Any]:
    with zipfile.ZipFile(zip_path) as zf:
        matches = [name for name in zf.namelist() if name.endswith('artifacts/reports/archive_size_guardrail_card.json')]
        if len(matches) != 1:
            raise RuntimeError(
                f'expected exactly one embedded archive_size_guardrail_card.json in {zip_path.name}, found {len(matches)}'
            )
        return json.loads(zf.read(matches[0]).decode('utf-8'))


def build_report() -> dict[str, Any]:
    size = _load_json(SIZE_JSON)
    authority = _load_json(AUTHORITY_JSON)

    current_archive = authority['current_archive']
    selected = authority['authoritative_external_head']
    scan_dir = Path(authority['scan_dir'])
    current_zip_name = f"{current_archive['root_name']}.zip"
    selected_matches_current = selected['zip_name'] == current_zip_name

    current_proxy = {
        'approx_revision_zip_bytes': int(size['archive_totals']['approx_revision_zip_bytes']),
        'approx_revision_zip_mebibytes': float(size['archive_totals']['approx_revision_zip_mebibytes']),
        'raw_bytes': int(size['archive_totals']['raw_bytes']),
        'raw_mebibytes': float(size['archive_totals']['raw_mebibytes']),
        'source_report': SIZE_JSON.relative_to(ROOT).as_posix(),
    }

    predecessor = None
    predecessor_row = authority.get('immediate_predecessor_zip')
    if isinstance(predecessor_row, dict):
        predecessor_zip_path = scan_dir / predecessor_row['zip_name']
        if predecessor_zip_path.exists():
            embedded_guardrail = _load_embedded_guardrail(predecessor_zip_path)
            proxy = int(embedded_guardrail['archive_totals']['approx_revision_zip_bytes'])
            actual = int(predecessor_zip_path.stat().st_size)
            delta = actual - proxy
            predecessor = {
                'zip_name': predecessor_row['zip_name'],
                'zip_path': predecessor_zip_path.as_posix(),
                'revision_label': predecessor_row['revision_label'],
                'embedded_proxy_bytes': proxy,
                'embedded_proxy_mebibytes': _mib(proxy),
                'actual_external_zip_bytes': actual,
                'actual_external_zip_mebibytes': _mib(actual),
                'actual_minus_proxy_bytes': delta,
                'actual_minus_proxy_mebibytes': _mib(delta),
                'actual_over_proxy_ratio': round(actual / proxy, 6) if proxy else None,
                'actual_minus_proxy_share_of_proxy': round(delta / proxy, 6) if proxy else None,
                'embedded_guardrail_snapshot_date': embedded_guardrail.get('snapshot_date'),
            }

    headline_findings = [
        (
            f"The current archive's internal zip proxy remains {current_proxy['approx_revision_zip_bytes']} bytes "
            f"({current_proxy['approx_revision_zip_mebibytes']} MiB), but the exact current head zip bytes stay live-only because "
            'embedding them inside that same current-head zip would be self-referential.'
        ),
        (
            'Use `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit size-bytes` for the exact current head zip size '
            'and `python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256` for the live digest.'
        ),
    ]
    if predecessor is not None:
        headline_findings.append(
            (
                f"The immutable predecessor `{predecessor['zip_name']}` calibrates the gap: embedded proxy "
                f"{predecessor['embedded_proxy_bytes']} bytes versus actual sibling zip {predecessor['actual_external_zip_bytes']} bytes, "
                f"a delta of {predecessor['actual_minus_proxy_bytes']} bytes ({predecessor['actual_minus_proxy_mebibytes']} MiB, "
                f"share {predecessor['actual_minus_proxy_share_of_proxy']})."
            )
        )
    else:
        headline_findings.append(
            'No immutable predecessor zip was available for empirical calibration, so treat the current proxy strictly as an internal trend metric.'
        )

    stewardship = {
        'primary_open_doc': 'docs/ARCHIVE_ZIP_SIZE_TRUTH_CARD.md',
        'primary_refresh_command': 'make update-archive-zip-size-truth-card',
        'primary_verify_command': 'make test-archive-zip-size-truth-card',
        'live_emit_zip_path_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit zip-path',
        'live_emit_size_bytes_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit size-bytes',
        'live_emit_sha256_command': 'python3 scripts/tools/inspect_authoritative_archive_zip.py --emit sha256',
    }

    return {
        'card': 'archive_zip_size_truth_card',
        'scan_dir': authority['scan_dir'],
        'current_archive': current_archive,
        'authoritative_external_head': selected,
        'current_root_vs_authoritative_head_aligned': authority['current_root_vs_authoritative_head_aligned'],
        'exact_current_zip_present': authority['exact_current_zip_present'],
        'selected_matches_current_root_zip': selected_matches_current,
        'current_internal_proxy': current_proxy,
        'predecessor_empirical_calibration': predecessor,
        'headline_findings': headline_findings,
        'stewardship': stewardship,
        'interpretation': {
            'internal_proxy_scope': 'approx_revision_zip_bytes is a retained-tree packaging proxy used for archive drift and byte budgeting inside the repo.',
            'external_exact_scope': 'the exact current head zip bytes must be read from the sibling zip on disk, not embedded inside the same current-head zip.',
            'selection_rule': 'pick the authoritative head zip by revision-first authority, then verify its live bytes with inspect_authoritative_archive_zip.',
        },
        'metadata': {
            'source_reports': [
                SIZE_JSON.relative_to(ROOT).as_posix(),
                AUTHORITY_JSON.relative_to(ROOT).as_posix(),
            ],
            'source_tools': [
                'scripts/tools/inspect_authoritative_archive_zip.py',
            ],
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    current = report['current_internal_proxy']
    predecessor = report['predecessor_empirical_calibration']
    lines = [
        '# Archive Zip Size Truth Card',
        '',
        "Compact package-size truth surface: distinguish the archive's internal zip proxy from the exact sibling zip bytes on disk, and use the immutable predecessor zip to calibrate the gap without pretending the current head can embed its own final size.",
        '',
        '## Headline findings',
        '',
    ]
    for item in report['headline_findings']:
        lines.append(f'- {item}')
    lines.extend([
        '',
        '## Current internal proxy',
        '',
        f"- approx_revision_zip_bytes: `{current['approx_revision_zip_bytes']}`",
        f"- approx_revision_zip_mebibytes: `{current['approx_revision_zip_mebibytes']}`",
        f"- raw_bytes: `{current['raw_bytes']}`",
        f"- raw_mebibytes: `{current['raw_mebibytes']}`",
        f"- selected_matches_current_root_zip: `{report['selected_matches_current_root_zip']}`",
        f"- exact_current_zip_present: `{report['exact_current_zip_present']}`",
        f"- current_root_vs_authoritative_head_aligned: `{report['current_root_vs_authoritative_head_aligned']}`",
        '',
        '## Live verification commands',
        '',
        f"- emit_zip_path_command: `{report['stewardship']['live_emit_zip_path_command']}`",
        f"- emit_size_bytes_command: `{report['stewardship']['live_emit_size_bytes_command']}`",
        f"- emit_sha256_command: `{report['stewardship']['live_emit_sha256_command']}`",
        '',
        '## Immutable predecessor calibration',
        '',
    ])
    if predecessor is None:
        lines.append('- No predecessor zip calibration was available.')
    else:
        lines.extend([
            f"- zip_name: `{predecessor['zip_name']}`",
            f"- zip_path: `{predecessor['zip_path']}`",
            f"- revision_label: `{predecessor['revision_label']}`",
            f"- embedded_proxy_bytes: `{predecessor['embedded_proxy_bytes']}`",
            f"- actual_external_zip_bytes: `{predecessor['actual_external_zip_bytes']}`",
            f"- actual_minus_proxy_bytes: `{predecessor['actual_minus_proxy_bytes']}`",
            f"- actual_minus_proxy_mebibytes: `{predecessor['actual_minus_proxy_mebibytes']}`",
            f"- actual_over_proxy_ratio: `{predecessor['actual_over_proxy_ratio']}`",
            f"- actual_minus_proxy_share_of_proxy: `{predecessor['actual_minus_proxy_share_of_proxy']}`",
            f"- embedded_guardrail_snapshot_date: `{predecessor['embedded_guardrail_snapshot_date']}`",
        ])
    lines.extend([
        '',
        '## Interpretation',
        '',
        f"- {report['interpretation']['internal_proxy_scope']}",
        f"- {report['interpretation']['external_exact_scope']}",
        f"- {report['interpretation']['selection_rule']}",
        '',
    ])
    return '\n'.join(lines)


def main() -> int:
    report = build_report()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    OUT_MD.write_text(render_markdown(report), encoding='utf-8')
    print(f'wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
