from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

ROLLOUT_PRIORITY_ORDER = {
    'reference adapter': 0,
    'recommended second adapter': 1,
    'phase-2': 2,
    'phase-3': 3,
}
TIER_ORDER = {
    'unsupported': 0,
    'investigated': 1,
    'experimental': 2,
    'provisional': 3,
    'supported': 4,
}
RECORD_STATUS_ORDER = {
    'seeded': 0,
    'backfilled-from-evidence': 1,
    'current': 2,
    'stale': 3,
}
WORKFLOW_ORDER = {
    'surface-detect': 0,
    'receiver-resolve': 1,
    'composer-read': 2,
    'composer-write': 3,
    'turn-submit': 4,
    'generation-read': 5,
    'latest-turn-read': 6,
    'support-capture': 7,
}

REQUIRED_METADATA_FIELDS = (
    'surface key',
    'record status',
    'default browser lane',
    'last reviewed',
    'rollout priority',
)
CORE_WORKFLOWS = tuple(WORKFLOW_ORDER.keys())
_ALLOWED_RECORD_STATUSES = set(RECORD_STATUS_ORDER)
_ALLOWED_ROLLOUT_PRIORITIES = set(ROLLOUT_PRIORITY_ORDER)
_ALLOWED_TIERS = set(TIER_ORDER)
_DATE_RE = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def _markdown_table_rows(lines: list[str]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    table_lines = [line.rstrip('\n') for line in lines if line.strip()]
    if len(table_lines) < 3:
        return rows
    headers = [cell.strip() for cell in table_lines[0].strip().strip('|').split('|')]
    for line in table_lines[2:]:
        if '|' not in line:
            continue
        values = [cell.strip() for cell in line.strip().strip('|').split('|')]
        if len(values) != len(headers):
            continue
        rows.append({headers[i]: values[i] for i in range(len(headers))})
    return rows


def parse_support_record(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding='utf-8')
    title_match = re.search(r'^# Support record — (.+)$', text, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.stem
    metadata: dict[str, str] = {}
    for key, value in re.findall(r'^- \*\*(.+?):\*\* `(.*?)`$', text, flags=re.MULTILINE):
        metadata[key.strip().lower()] = value.strip()
    next_action = None
    next_action_match = re.search(r'^## Next action\n(.+?)(?:\n## |\Z)', text, flags=re.MULTILINE | re.DOTALL)
    if next_action_match:
        next_action = ' '.join(
            line.strip('- ').strip()
            for line in next_action_match.group(1).strip().splitlines()
            if line.strip()
        )
    known_blockers: list[str] = []
    blockers_match = re.search(r'^## Known blockers and risk notes\n(.+?)(?:\n## |\Z)', text, flags=re.MULTILINE | re.DOTALL)
    if blockers_match:
        known_blockers = [line.strip('- ').strip() for line in blockers_match.group(1).splitlines() if line.strip().startswith('-')]
    workflow_match = re.search(r'^## Workflow rows\n\n((?:\|.*\n)+)', text, flags=re.MULTILINE)
    workflows = _markdown_table_rows(workflow_match.group(1).splitlines()) if workflow_match else []
    normalized_rows = []
    for row in workflows:
        normalized_rows.append({
            'workflow': row.get('workflow', ''),
            'current_tier': row.get('current tier', ''),
            'lane': row.get('lane', ''),
            'evidence_posture': row.get('evidence refs / posture', ''),
            'caveats': row.get('caveats', ''),
            'promotion_requirement': row.get('promotion requirement', ''),
        })
    return {
        'path': str(path),
        'title': title,
        'surface_key': metadata.get('surface key', path.stem),
        'record_status': metadata.get('record status', 'unknown'),
        'default_browser_lane': metadata.get('default browser lane', 'unknown'),
        'last_reviewed': metadata.get('last reviewed'),
        'rollout_priority': metadata.get('rollout priority', 'unknown'),
        'workflow_rows': normalized_rows,
        'workflow_row_count': len(normalized_rows),
        'known_blockers': known_blockers,
        'next_action': next_action,
        'metadata': metadata,
    }


def load_support_records(*, root: Path = ROOT) -> list[dict[str, Any]]:
    records_dir = root / 'docs' / 'support-records'
    records = []
    if not records_dir.exists():
        return records
    for path in sorted(records_dir.glob('*.md')):
        if path.name.lower() == 'readme.md':
            continue
        records.append(parse_support_record(path))
    return records


def _tier_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counter = Counter(row.get('current_tier') or 'unknown' for row in rows)
    return dict(sorted(counter.items(), key=lambda item: (TIER_ORDER.get(item[0], 999), item[0])))


def _surface_summary(record: dict[str, Any]) -> dict[str, Any]:
    rows = record.get('workflow_rows') or []
    tiers = [row.get('current_tier') for row in rows if row.get('current_tier')]
    strongest = max(tiers, key=lambda value: TIER_ORDER.get(value, -1)) if tiers else None
    weakest = min(tiers, key=lambda value: TIER_ORDER.get(value, 999)) if tiers else None
    return {
        'surface_key': record.get('surface_key'),
        'title': record.get('title'),
        'path': record.get('path'),
        'record_status': record.get('record_status'),
        'rollout_priority': record.get('rollout_priority'),
        'default_browser_lane': record.get('default_browser_lane'),
        'last_reviewed': record.get('last_reviewed'),
        'workflow_row_count': record.get('workflow_row_count', 0),
        'workflow_tier_counts': _tier_counts(rows),
        'strongest_tier': strongest,
        'weakest_tier': weakest,
        'known_blockers': record.get('known_blockers') or [],
        'next_action': record.get('next_action'),
    }


def _review_priority(record: dict[str, Any], row: dict[str, Any]) -> tuple[int, int, int, int, str, str]:
    rollout = ROLLOUT_PRIORITY_ORDER.get(record.get('rollout_priority', ''), 99)
    tier = TIER_ORDER.get(row.get('current_tier', ''), -1)
    tier_pressure = 10 - max(tier, 0)
    record_status = record.get('record_status', '')
    if record_status == 'seeded':
        status_pressure = 0
    elif record_status == 'stale':
        status_pressure = 1
    elif record_status == 'backfilled-from-evidence':
        status_pressure = 2
    else:
        status_pressure = 3
    workflow = WORKFLOW_ORDER.get(row.get('workflow', ''), 99)
    return (rollout, tier_pressure, status_pressure, workflow, record.get('surface_key', ''), row.get('workflow', ''))


def build_review_queue(records: list[dict[str, Any]], *, limit: int = 16) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for record in records:
        for row in record.get('workflow_rows') or []:
            rationale_bits = [
                f"{record.get('surface_key')} is a {record.get('rollout_priority')} surface",
                f"{row.get('workflow')} is only {row.get('current_tier')}",
            ]
            if record.get('record_status') == 'seeded':
                rationale_bits.append('record is still seeded, so support truth is not yet backfilled from named artifacts')
            elif record.get('record_status') == 'stale':
                rationale_bits.append('record is stale and should be refreshed before stronger claims')
            items.append({
                'surface_key': record.get('surface_key'),
                'workflow': row.get('workflow'),
                'lane': row.get('lane') or record.get('default_browser_lane'),
                'current_tier': row.get('current_tier'),
                'record_status': record.get('record_status'),
                'rollout_priority': record.get('rollout_priority'),
                'promotion_requirement': row.get('promotion_requirement'),
                'evidence_posture': row.get('evidence_posture'),
                'caveats': row.get('caveats'),
                'next_action': record.get('next_action'),
                'rationale': '; '.join(bit for bit in rationale_bits if bit),
            })
    items.sort(key=lambda item: _review_priority(item, item))
    for index, item in enumerate(items, start=1):
        item['priority'] = index
    return items[:limit]


def summarize_support(records: list[dict[str, Any]]) -> dict[str, Any]:
    all_rows = [row for record in records for row in (record.get('workflow_rows') or [])]
    record_status_counts = Counter(record.get('record_status') or 'unknown' for record in records)
    rollout_priority_counts = Counter(record.get('rollout_priority') or 'unknown' for record in records)
    workflow_counts = Counter(row.get('workflow') or 'unknown' for row in all_rows)
    return {
        'surface_count': len(records),
        'record_status_counts': dict(sorted(record_status_counts.items(), key=lambda item: (RECORD_STATUS_ORDER.get(item[0], 999), item[0]))),
        'rollout_priority_counts': dict(sorted(rollout_priority_counts.items(), key=lambda item: (ROLLOUT_PRIORITY_ORDER.get(item[0], 999), item[0]))),
        'workflow_tier_counts': _tier_counts(all_rows),
        'workflow_counts': dict(sorted(workflow_counts.items(), key=lambda item: (WORKFLOW_ORDER.get(item[0], 999), item[0]))),
        'surfaces': [_surface_summary(record) for record in records],
        'review_queue': build_review_queue(records),
    }


def flatten_workflow_rows(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []
    for record in records:
        for row in record.get('workflow_rows') or []:
            flattened.append({
                'surface_key': record.get('surface_key'),
                'record_status': record.get('record_status'),
                'rollout_priority': record.get('rollout_priority'),
                'default_browser_lane': record.get('default_browser_lane'),
                **row,
            })
    flattened.sort(
        key=lambda item: (
            ROLLOUT_PRIORITY_ORDER.get(item.get('rollout_priority', ''), 999),
            WORKFLOW_ORDER.get(item.get('workflow', ''), 999),
            item.get('surface_key', ''),
        )
    )
    return flattened


def validate_support_record(record: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    metadata = record.get('metadata') if isinstance(record.get('metadata'), dict) else {}
    for field in REQUIRED_METADATA_FIELDS:
        if not metadata.get(field):
            errors.append(f'missing metadata field: {field}')
    surface_key = record.get('surface_key')
    path = Path(str(record.get('path') or ''))
    if path.name and surface_key and path.stem != str(surface_key):
        warnings.append(f'path stem {path.stem!r} does not match surface key {surface_key!r}')
    record_status = record.get('record_status')
    if record_status not in _ALLOWED_RECORD_STATUSES:
        errors.append(f'unknown record status: {record_status!r}')
    rollout_priority = record.get('rollout_priority')
    if rollout_priority not in _ALLOWED_ROLLOUT_PRIORITIES:
        errors.append(f'unknown rollout priority: {rollout_priority!r}')
    last_reviewed = record.get('last_reviewed')
    if not isinstance(last_reviewed, str) or not _DATE_RE.match(last_reviewed):
        errors.append(f'last reviewed is not YYYY-MM-DD: {last_reviewed!r}')
    if not record.get('next_action'):
        warnings.append('missing next action section or empty next action text')
    rows = record.get('workflow_rows') or []
    seen: set[str] = set()
    missing = set(CORE_WORKFLOWS)
    for row in rows:
        workflow = str(row.get('workflow') or '').strip()
        tier = str(row.get('current_tier') or '').strip()
        if not workflow:
            errors.append('workflow row missing workflow key')
            continue
        if workflow in seen:
            errors.append(f'duplicate workflow row: {workflow}')
        seen.add(workflow)
        missing.discard(workflow)
        if workflow not in WORKFLOW_ORDER:
            errors.append(f'unknown workflow: {workflow!r}')
        if tier not in _ALLOWED_TIERS:
            errors.append(f'unknown workflow tier for {workflow}: {tier!r}')
        if not str(row.get('lane') or '').strip():
            errors.append(f'workflow row missing lane: {workflow}')
        if not str(row.get('evidence_posture') or '').strip():
            errors.append(f'workflow row missing evidence posture: {workflow}')
        if not str(row.get('caveats') or '').strip():
            warnings.append(f'workflow row missing caveat summary: {workflow}')
        if not str(row.get('promotion_requirement') or '').strip():
            warnings.append(f'workflow row missing promotion requirement: {workflow}')
    for workflow in sorted(missing, key=lambda value: WORKFLOW_ORDER.get(value, 999)):
        errors.append(f'missing core workflow row: {workflow}')
    return {
        'surface_key': surface_key,
        'path': str(path),
        'error_count': len(errors),
        'warning_count': len(warnings),
        'errors': errors,
        'warnings': warnings,
    }


def validate_support_records(records: list[dict[str, Any]]) -> dict[str, Any]:
    results = [validate_support_record(record) for record in records]
    surface_keys = [result.get('surface_key') for result in results if result.get('surface_key')]
    duplicate_surface_keys = sorted({key for key in surface_keys if surface_keys.count(key) > 1})
    errors = sum(result.get('error_count', 0) for result in results)
    warnings = sum(result.get('warning_count', 0) for result in results)
    if duplicate_surface_keys:
        errors += len(duplicate_surface_keys)
    return {
        'record_count': len(records),
        'error_count': errors,
        'warning_count': warnings,
        'duplicate_surface_keys': duplicate_surface_keys,
        'records': results,
        'all_valid': errors == 0,
    }
