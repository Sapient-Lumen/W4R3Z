#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from math import floor
from pathlib import Path
from typing import Any

try:
    from support_records import load_support_records, summarize_support
    from support_bundle_queue import _list_bundle_paths, _read_json, _default_bundles_dir, validate_bundle_manifest
except ModuleNotFoundError:  # pragma: no cover - import path differs under tests
    import importlib.util

    _RECORDS_PATH = Path(__file__).resolve().parent / 'support_records.py'
    _RECORDS_SPEC = importlib.util.spec_from_file_location('support_records', _RECORDS_PATH)
    _RECORDS_MODULE = importlib.util.module_from_spec(_RECORDS_SPEC)
    assert _RECORDS_SPEC.loader is not None
    _RECORDS_SPEC.loader.exec_module(_RECORDS_MODULE)
    load_support_records = _RECORDS_MODULE.load_support_records
    summarize_support = _RECORDS_MODULE.summarize_support

    _QUEUE_PATH = Path(__file__).resolve().parent / 'support_bundle_queue.py'
    _QUEUE_SPEC = importlib.util.spec_from_file_location('support_bundle_queue', _QUEUE_PATH)
    _QUEUE_MODULE = importlib.util.module_from_spec(_QUEUE_SPEC)
    assert _QUEUE_SPEC.loader is not None
    _QUEUE_SPEC.loader.exec_module(_QUEUE_MODULE)
    _list_bundle_paths = _QUEUE_MODULE._list_bundle_paths
    _read_json = _QUEUE_MODULE._read_json
    _default_bundles_dir = _QUEUE_MODULE._default_bundles_dir
    validate_bundle_manifest = _QUEUE_MODULE.validate_bundle_manifest

ROOT = Path(__file__).resolve().parent.parent
LOCK_PATH = ROOT / 'SUPPORT-SOURCE-LOCK.json'
ROOT_OUTPUT_PATH = ROOT / 'SUPPORT-SOURCE-BASELINE.json'
DEFAULT_OUTPUT_DIR = ROOT / 'validation' / 'latest' / 'support-source-baseline'
DEFAULT_HISTORY_PATH = ROOT / 'validation' / 'support-source-baseline-captures.json'
REPORT_COMMAND = 'python scripts/support-source-baseline.py --pretty'
CAPTURE_COMMAND = 'python scripts/support-source-baseline.py capture --output-dir validation/latest/support-source-baseline'
HISTORY_COMMAND = 'python scripts/support-source-baseline.py history --pretty'
WRITE_ROOT_COMMAND = 'python scripts/support-source-baseline.py write-root'
SHARED_SURFACE_KEYS = {'shared-browser-substrate', 'shared', 'all-surfaces'}
DEFAULT_MAX_LOCK_REVIEW_AGE_DAYS = 30
DEFAULT_MAX_SOURCE_REVIEW_AGE_DAYS = 30


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')


def _display_path(path: Path, *, root: Path = ROOT) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _changed_fields(previous: dict[str, Any] | None, current: dict[str, Any]) -> list[str]:
    if not previous:
        return sorted(current.keys())
    return [key for key in sorted(set(previous) | set(current)) if previous.get(key) != current.get(key)]


def _parse_review_value(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    raw = value.strip()
    try:
        if len(raw) == 10:
            return datetime.fromisoformat(raw + 'T00:00:00+00:00')
        normalized = raw.replace('Z', '+00:00')
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def _normalize_positive_int(value: Any, default: int) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed > 0 else default


def _review_status(reviewed_at: Any, *, max_age_days: int, now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(timezone.utc)
    parsed = _parse_review_value(reviewed_at)
    if parsed is None:
        return {
            'reviewed_at': reviewed_at if isinstance(reviewed_at, str) else None,
            'parsed_reviewed_at': None,
            'max_age_days': max_age_days,
            'age_days': None,
            'missing_reviewed_at': True,
            'stale': True,
        }
    age_days = max(0, floor((now - parsed).total_seconds() / 86400))
    return {
        'reviewed_at': reviewed_at,
        'parsed_reviewed_at': parsed.replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'max_age_days': max_age_days,
        'age_days': age_days,
        'missing_reviewed_at': False,
        'stale': age_days > max_age_days,
    }


def _tier_rank_map(lock: dict[str, Any]) -> dict[str, int]:
    return {
        str(item.get('tier')): int(item.get('rank'))
        for item in (lock.get('hierarchy') or [])
        if isinstance(item, dict) and item.get('tier') is not None and item.get('rank') is not None
    }


def _review_policy(lock_payload: dict[str, Any]) -> dict[str, Any]:
    raw = lock_payload.get('review_policy') if isinstance(lock_payload.get('review_policy'), dict) else {}
    per_tier_raw = raw.get('per_tier_max_age_days') if isinstance(raw.get('per_tier_max_age_days'), dict) else {}
    per_tier = {
        str(tier): _normalize_positive_int(days, DEFAULT_MAX_SOURCE_REVIEW_AGE_DAYS)
        for tier, days in per_tier_raw.items()
        if str(tier).strip()
    }
    return {
        'max_lock_review_age_days': _normalize_positive_int(raw.get('max_lock_review_age_days'), DEFAULT_MAX_LOCK_REVIEW_AGE_DAYS),
        'max_source_review_age_days': _normalize_positive_int(raw.get('max_source_review_age_days'), DEFAULT_MAX_SOURCE_REVIEW_AGE_DAYS),
        'per_tier_max_age_days': per_tier,
    }


def _max_age_days_for_source(source: dict[str, Any], *, policy: dict[str, Any]) -> int:
    tier = str(source.get('tier') or '')
    per_tier = policy.get('per_tier_max_age_days') if isinstance(policy.get('per_tier_max_age_days'), dict) else {}
    if tier in per_tier:
        return _normalize_positive_int(per_tier.get(tier), DEFAULT_MAX_SOURCE_REVIEW_AGE_DAYS)
    return _normalize_positive_int(policy.get('max_source_review_age_days'), DEFAULT_MAX_SOURCE_REVIEW_AGE_DAYS)


def load_source_lock(*, root: Path = ROOT) -> dict[str, Any]:
    path = root / 'SUPPORT-SOURCE-LOCK.json'
    if not path.exists():
        review_policy = _review_policy({})
        return {
            'project': 'GlassTTY',
            'lock_path': _display_path(path, root=root),
            'exists': False,
            'issues': ['SUPPORT-SOURCE-LOCK.json is missing'],
            'review_policy': review_policy,
            'review_status': _review_status(None, max_age_days=review_policy['max_lock_review_age_days']),
            'hierarchy': [],
            'sources': [],
        }
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict):
        raise ValueError('SUPPORT-SOURCE-LOCK.json is not a JSON object')
    issues: list[str] = []
    hierarchy = payload.get('hierarchy')
    sources = payload.get('sources')
    if not isinstance(hierarchy, list) or not hierarchy:
        issues.append('hierarchy must be a non-empty list')
        hierarchy = []
    if not isinstance(sources, list) or not sources:
        issues.append('sources must be a non-empty list')
        sources = []
    review_policy = _review_policy(payload)
    tier_ranks = _tier_rank_map({'hierarchy': hierarchy})
    normalized_sources: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            issues.append(f'sources[{index}] is not an object')
            continue
        source_key = source.get('source_key')
        if not isinstance(source_key, str) or not source_key.strip():
            issues.append(f'sources[{index}] missing source_key')
            continue
        if source_key in seen_keys:
            issues.append(f'duplicate source_key: {source_key}')
        seen_keys.add(source_key)
        surface_keys = source.get('surface_keys') if isinstance(source.get('surface_keys'), list) else []
        if not surface_keys:
            issues.append(f'source {source_key} missing surface_keys')
        tier = source.get('tier')
        if not isinstance(tier, str) or not tier.strip():
            issues.append(f'source {source_key} missing tier')
        elif tier not in tier_ranks:
            issues.append(f'source {source_key} tier is not declared in hierarchy: {tier}')
        title = source.get('title')
        if not isinstance(title, str) or not title.strip():
            issues.append(f'source {source_key} missing title')
        url = source.get('url')
        if not isinstance(url, str) or not url.strip():
            issues.append(f'source {source_key} missing url')
        max_age_days = _max_age_days_for_source(source, policy=review_policy)
        review_status = _review_status(source.get('reviewed_at'), max_age_days=max_age_days)
        normalized_sources.append({
            'source_key': source_key,
            'title': title,
            'url': url,
            'tier': tier,
            'tier_rank': tier_ranks.get(str(tier), 999),
            'surface_keys': [str(item) for item in surface_keys if str(item).strip()],
            'required_for_publication': bool(source.get('required_for_publication')),
            'claim_uses': [str(item) for item in (source.get('claim_uses') or []) if str(item).strip()],
            'reviewed_at': source.get('reviewed_at'),
            'review_status': review_status,
            'notes': source.get('notes'),
        })
    lock_review_status = _review_status(payload.get('last_reviewed'), max_age_days=review_policy['max_lock_review_age_days'])
    return {
        **payload,
        'lock_path': _display_path(path, root=root),
        'exists': True,
        'issues': issues,
        'review_policy': review_policy,
        'review_status': lock_review_status,
        'hierarchy': hierarchy,
        'sources': normalized_sources,
    }


def source_refs_for_surface(surface_key: str, *, lock: dict[str, Any]) -> dict[str, Any]:
    approved: list[dict[str, Any]] = []
    for source in lock.get('sources') or []:
        if not isinstance(source, dict):
            continue
        surface_keys = {str(item) for item in (source.get('surface_keys') or []) if str(item).strip()}
        if surface_key in surface_keys or SHARED_SURFACE_KEYS.intersection(surface_keys):
            approved.append(source)
    approved.sort(key=lambda item: (int(item['tier_rank']) if isinstance(item, dict) and item.get('tier_rank') is not None else 999, str(item.get('source_key') or '')))
    required = [str(item.get('source_key')) for item in approved if item.get('required_for_publication')]
    recommended = [str(item.get('source_key')) for item in approved if not item.get('required_for_publication')]
    stale = [str(item.get('source_key')) for item in approved if (item.get('review_status') or {}).get('stale')]
    stale_required = [str(item.get('source_key')) for item in approved if item.get('required_for_publication') and (item.get('review_status') or {}).get('stale')]
    return {
        'approved_sources': approved,
        'approved_source_keys': [str(item.get('source_key')) for item in approved],
        'required_source_keys': required,
        'recommended_source_keys': recommended,
        'stale_source_keys': stale,
        'stale_required_source_keys': stale_required,
    }


def bundle_source_report(bundle_payload: dict[str, Any], *, surface_key: str, lock: dict[str, Any]) -> dict[str, Any]:
    source_refs = bundle_payload.get('source_refs') if isinstance(bundle_payload.get('source_refs'), list) else []
    source_refs = [str(item) for item in source_refs if isinstance(item, str) and item.strip()]
    source_index = {str(item.get('source_key')): item for item in (lock.get('sources') or []) if isinstance(item, dict) and item.get('source_key')}
    surface_refs = source_refs_for_surface(surface_key, lock=lock)
    approved_keys = set(surface_refs['approved_source_keys'])
    cited_approved = [key for key in source_refs if key in approved_keys]
    unknown = [key for key in source_refs if key not in source_index]
    foreign = [key for key in source_refs if key in source_index and key not in approved_keys]
    missing_required = [key for key in surface_refs['required_source_keys'] if key not in cited_approved]
    missing_recommended = [key for key in surface_refs['recommended_source_keys'] if key not in cited_approved]
    stale_cited = [key for key in cited_approved if (source_index.get(key) or {}).get('review_status', {}).get('stale')]
    stale_required = [key for key in surface_refs['required_source_keys'] if (source_index.get(key) or {}).get('review_status', {}).get('stale')]
    cited_tiers = Counter(str((source_index.get(key) or {}).get('tier') or 'unknown') for key in cited_approved)
    return {
        'source_refs': source_refs,
        'source_ref_count': len(source_refs),
        'cited_approved_source_keys': cited_approved,
        'cited_tier_counts': dict(sorted(cited_tiers.items())),
        'unknown_source_keys': unknown,
        'foreign_source_keys': foreign,
        'missing_required_source_keys': missing_required,
        'missing_recommended_source_keys': missing_recommended,
        'stale_cited_source_keys': stale_cited,
        'stale_required_source_keys': stale_required,
        **surface_refs,
    }


def build_support_source_baseline(*, root: Path = ROOT) -> dict[str, Any]:
    lock = load_source_lock(root=root)
    support = summarize_support(load_support_records(root=root))
    bundles_dir = _default_bundles_dir(root)
    bundle_reports: list[dict[str, Any]] = []
    by_surface: dict[str, list[dict[str, Any]]] = {}
    warnings: list[dict[str, Any]] = []

    lock_review_status = lock.get('review_status') if isinstance(lock.get('review_status'), dict) else {}
    if lock_review_status.get('stale'):
        warnings.append({
            'surface_key': None,
            'severity': 'blocking',
            'message': 'support-source lock review is stale or missing under the current review policy',
        })

    for source in lock.get('sources') or []:
        if not isinstance(source, dict):
            continue
        review_status = source.get('review_status') if isinstance(source.get('review_status'), dict) else {}
        if review_status.get('stale'):
            warnings.append({
                'surface_key': None,
                'source_key': source.get('source_key'),
                'severity': 'advisory',
                'message': f"approved source review is stale or missing: {source.get('source_key')}",
            })

    for path in _list_bundle_paths(bundles_dir=bundles_dir):
        validated = validate_bundle_manifest(path, root=root, bundles_dir=bundles_dir)
        raw = _read_json(path)
        surface_key = str(validated.get('surface_key') or raw.get('surface_key') or '')
        source_report = bundle_source_report(raw, surface_key=surface_key, lock=lock)
        item = {
            'bundle_key': validated.get('bundle_key') or path.stem,
            'bundle_status': validated.get('bundle_status'),
            'surface_key': surface_key,
            'bundle_path': _display_path(path, root=root),
            'ok': validated.get('ok'),
            'issues': validated.get('issues') or [],
            'source_report': source_report,
        }
        bundle_reports.append(item)
        by_surface.setdefault(surface_key, []).append(item)
        if not source_report['source_refs']:
            warnings.append({
                'surface_key': surface_key,
                'bundle_key': item['bundle_key'],
                'severity': 'advisory',
                'message': 'bundle has no source_refs yet',
            })
        if source_report['unknown_source_keys']:
            warnings.append({
                'surface_key': surface_key,
                'bundle_key': item['bundle_key'],
                'severity': 'advisory',
                'message': f"bundle cites unknown source keys: {source_report['unknown_source_keys']}",
            })
        if source_report['foreign_source_keys']:
            warnings.append({
                'surface_key': surface_key,
                'bundle_key': item['bundle_key'],
                'severity': 'advisory',
                'message': f"bundle cites source keys outside the approved hierarchy for this surface: {source_report['foreign_source_keys']}",
            })
        if source_report['stale_cited_source_keys']:
            warnings.append({
                'surface_key': surface_key,
                'bundle_key': item['bundle_key'],
                'severity': 'advisory',
                'message': f"bundle cites approved sources whose review is stale or missing: {source_report['stale_cited_source_keys']}",
            })
        if item['bundle_status'] in {'published-ready', 'published'} and source_report['missing_required_source_keys']:
            warnings.append({
                'surface_key': surface_key,
                'bundle_key': item['bundle_key'],
                'severity': 'blocking',
                'message': f"publishable bundle is missing required source refs: {source_report['missing_required_source_keys']}",
            })
        if item['bundle_status'] in {'published-ready', 'published'} and source_report['stale_required_source_keys']:
            warnings.append({
                'surface_key': surface_key,
                'bundle_key': item['bundle_key'],
                'severity': 'blocking',
                'message': f"publishable bundle cites required source refs whose review is stale or missing: {source_report['stale_required_source_keys']}",
            })

    surfaces: list[dict[str, Any]] = []
    surfaces_without_approved_sources = 0
    surfaces_with_bundle_source_refs = 0
    surfaces_with_stale_approved_sources = 0
    for surface in support.get('surfaces') or []:
        if not isinstance(surface, dict):
            continue
        surface_key = str(surface.get('surface_key') or '')
        approved = source_refs_for_surface(surface_key, lock=lock)
        bundles = by_surface.get(surface_key, [])
        cited = sorted({key for bundle in bundles for key in (bundle.get('source_report') or {}).get('cited_approved_source_keys', [])})
        stale_cited = sorted({key for bundle in bundles for key in (bundle.get('source_report') or {}).get('stale_cited_source_keys', [])})
        if approved['approved_source_keys']:
            if cited:
                surfaces_with_bundle_source_refs += 1
            if approved['stale_source_keys']:
                surfaces_with_stale_approved_sources += 1
        else:
            surfaces_without_approved_sources += 1
        if bundles and approved['approved_source_keys'] and not cited:
            next_source_action = 'Backfill source_refs onto the existing bundle and keep live workflow evidence as the separate blocker.'
        elif stale_cited or approved['stale_required_source_keys']:
            next_source_action = 'Refresh the stale approved-source reviews before strengthening support or publication language.'
        elif cited:
            next_source_action = 'Keep the cited approved sources current and refresh them again before stronger publication claims.'
        elif approved['approved_source_keys']:
            next_source_action = 'No bundle exists yet; start with the first-party product source and then attach it to the first support bundle.'
        else:
            next_source_action = 'Curate at least one approved first-party source for this surface before stronger support claims.'
        surfaces.append({
            **surface,
            'approved_source_keys': approved['approved_source_keys'],
            'required_source_keys': approved['required_source_keys'],
            'recommended_source_keys': approved['recommended_source_keys'],
            'stale_source_keys': approved['stale_source_keys'],
            'stale_required_source_keys': approved['stale_required_source_keys'],
            'approved_source_count': len(approved['approved_source_keys']),
            'required_source_count': len(approved['required_source_keys']),
            'stale_source_count': len(approved['stale_source_keys']),
            'cited_bundle_source_keys': cited,
            'stale_cited_bundle_source_keys': stale_cited,
            'bundle_count': len(bundles),
            'bundles': [
                {
                    'bundle_key': bundle.get('bundle_key'),
                    'bundle_status': bundle.get('bundle_status'),
                    'source_ref_count': (bundle.get('source_report') or {}).get('source_ref_count'),
                    'missing_required_source_keys': (bundle.get('source_report') or {}).get('missing_required_source_keys'),
                    'stale_required_source_keys': (bundle.get('source_report') or {}).get('stale_required_source_keys'),
                    'unknown_source_keys': (bundle.get('source_report') or {}).get('unknown_source_keys'),
                }
                for bundle in bundles
            ],
            'next_source_action': next_source_action,
        })
        if bundles and approved['approved_source_keys'] and not cited:
            warnings.append({
                'surface_key': surface_key,
                'severity': 'advisory',
                'message': 'surface has approved sources but no current bundle cites them yet',
            })
        if not approved['approved_source_keys']:
            warnings.append({
                'surface_key': surface_key,
                'severity': 'advisory',
                'message': 'surface has no approved source entries yet',
            })

    shared_source_count = sum(1 for item in (lock.get('sources') or []) if isinstance(item, dict) and SHARED_SURFACE_KEYS.intersection({str(v) for v in (item.get('surface_keys') or [])}))
    stale_source_count = sum(1 for item in (lock.get('sources') or []) if isinstance(item, dict) and (item.get('review_status') or {}).get('stale'))
    missing_review_count = sum(1 for item in (lock.get('sources') or []) if isinstance(item, dict) and (item.get('review_status') or {}).get('missing_reviewed_at'))
    stale_required_source_count = sum(1 for item in (lock.get('sources') or []) if isinstance(item, dict) and item.get('required_for_publication') and (item.get('review_status') or {}).get('stale'))
    counts = {
        'lock_issue_count': len(lock.get('issues') or []),
        'source_count': len(lock.get('sources') or []),
        'surface_count': len(surfaces),
        'shared_source_count': shared_source_count,
        'bundle_count': len(bundle_reports),
        'surfaces_without_approved_sources': surfaces_without_approved_sources,
        'surfaces_with_bundle_source_refs': surfaces_with_bundle_source_refs,
        'surfaces_with_stale_approved_sources': surfaces_with_stale_approved_sources,
        'bundles_missing_source_refs': sum(1 for item in bundle_reports if not (item.get('source_report') or {}).get('source_ref_count')),
        'publishable_bundles_missing_required_refs': sum(1 for item in bundle_reports if item.get('bundle_status') in {'published-ready', 'published'} and (item.get('source_report') or {}).get('missing_required_source_keys')),
        'stale_lock_review': bool(lock_review_status.get('stale')),
        'stale_source_count': stale_source_count,
        'stale_required_source_count': stale_required_source_count,
        'sources_missing_review_count': missing_review_count,
        'warning_count': len(warnings),
        'blocking_warning_count': sum(1 for item in warnings if item.get('severity') == 'blocking'),
    }
    return {
        'project': 'GlassTTY',
        'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
        'root': str(root),
        'lock_path': lock.get('lock_path'),
        'lock_valid': not bool(lock.get('issues')),
        'lock_review_status': lock_review_status,
        'lock_issues': lock.get('issues') or [],
        'review_policy': lock.get('review_policy') or {},
        'counts': counts,
        'hierarchy': lock.get('hierarchy') or [],
        'sources': lock.get('sources') or [],
        'surfaces': surfaces,
        'bundle_source_reports': bundle_reports,
        'warnings': warnings,
        'commands': {
            'report': REPORT_COMMAND,
            'capture_latest': CAPTURE_COMMAND,
            'capture_history': HISTORY_COMMAND,
            'write_root': WRITE_ROOT_COMMAND,
        },
    }


def _summary_markdown(payload: dict[str, Any]) -> str:
    counts = payload.get('counts') or {}
    lock_review = payload.get('lock_review_status') or {}
    lines = [
        '# Support-source baseline',
        '',
        f"- generated_at: {payload.get('generated_at')}",
        f"- source_count: {counts.get('source_count')}",
        f"- shared_source_count: {counts.get('shared_source_count')}",
        f"- surface_count: {counts.get('surface_count')}",
        f"- bundle_count: {counts.get('bundle_count')}",
        f"- stale_lock_review: {counts.get('stale_lock_review')}",
        f"- stale_source_count: {counts.get('stale_source_count')}",
        f"- stale_required_source_count: {counts.get('stale_required_source_count')}",
        f"- sources_missing_review_count: {counts.get('sources_missing_review_count')}",
        f"- bundles_missing_source_refs: {counts.get('bundles_missing_source_refs')}",
        f"- publishable_bundles_missing_required_refs: {counts.get('publishable_bundles_missing_required_refs')}",
        f"- warning_count: {counts.get('warning_count')}",
        f"- lock_review_age_days: {lock_review.get('age_days')}",
        '',
        '| surface | approved sources | stale approved | cited bundle sources | bundles | next source action |',
        '|---|---:|---:|---:|---:|---|',
    ]
    for surface in payload.get('surfaces') or []:
        lines.append(
            f"| `{surface.get('surface_key')}` | {surface.get('approved_source_count')} | {surface.get('stale_source_count')} | {len(surface.get('cited_bundle_source_keys') or [])} | {surface.get('bundle_count')} | {surface.get('next_source_action')} |"
        )
    return '\n'.join(lines) + '\n'


def _history_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {'captures': []}
    payload = json.loads(path.read_text(encoding='utf-8'))
    captures = payload.get('captures') if isinstance(payload, dict) else None
    if not isinstance(captures, list):
        return {'captures': []}
    return payload


def capture_support_source_baseline(*, root: Path = ROOT, output_dir: Path = DEFAULT_OUTPUT_DIR, history_path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = build_support_source_baseline(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    previous = None
    target = output_dir / 'support-source-baseline.json'
    if target.exists():
        try:
            candidate = json.loads(target.read_text(encoding='utf-8'))
            previous = candidate if isinstance(candidate, dict) else None
        except Exception:
            previous = None
    _write_json(target, payload)
    (output_dir / 'SUMMARY.md').write_text(_summary_markdown(payload), encoding='utf-8')
    diff = {
        'changed_fields': _changed_fields(previous, payload),
        'previous_generated_at': previous.get('generated_at') if isinstance(previous, dict) else None,
        'current_generated_at': payload.get('generated_at'),
    }
    _write_json(output_dir / 'capture-diff.json', diff)
    history_payload = _history_payload(history_path)
    captures = history_payload.setdefault('captures', [])
    capture_entry = {
        'captured_at': payload.get('generated_at'),
        'output_dir': _display_path(output_dir, root=root),
        'root': str(root),
        'source_count': (payload.get('counts') or {}).get('source_count'),
        'warning_count': (payload.get('counts') or {}).get('warning_count'),
        'publishable_bundles_missing_required_refs': (payload.get('counts') or {}).get('publishable_bundles_missing_required_refs'),
        'bundles_missing_source_refs': (payload.get('counts') or {}).get('bundles_missing_source_refs'),
        'lock_valid': payload.get('lock_valid'),
    }
    captures.append(capture_entry)
    _write_json(history_path, history_payload)
    _write_json(output_dir / 'capture-history.json', {
        'path': _display_path(history_path, root=root),
        'exists': True,
        'capture_count': len(captures),
        'latest_capture': capture_entry,
    })
    return {
        'snapshot': payload,
        'history_update': {
            'path': _display_path(history_path, root=root),
            'capture_count_after_write': len(captures),
            'latest_capture': capture_entry,
        },
        'output_dir': _display_path(output_dir, root=root),
    }


def summarize_capture_history(path: Path = DEFAULT_HISTORY_PATH) -> dict[str, Any]:
    payload = _history_payload(path)
    captures = [item for item in (payload.get('captures') or []) if isinstance(item, dict)]
    latest = captures[-1] if captures else None
    return {
        'path': str(path),
        'exists': path.exists(),
        'capture_count': len(captures),
        'latest_capture': latest,
        'history': payload,
    }


def write_root_support_source_baseline(*, root: Path = ROOT) -> dict[str, Any]:
    payload = build_support_source_baseline(root=root)
    _write_json(root / 'SUPPORT-SOURCE-BASELINE.json', payload)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Summarize the approved-source hierarchy and the source basis currently attached to GlassTTY support surfaces and support bundles.')
    parser.add_argument('--pretty', action='store_true')
    subparsers = parser.add_subparsers(dest='command')
    capture_parser = subparsers.add_parser('capture', help='Write the current support-source baseline into validation/latest.')
    capture_parser.add_argument('--output-dir', default=str(DEFAULT_OUTPUT_DIR))
    capture_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    capture_parser.add_argument('--pretty', action='store_true')
    history_parser = subparsers.add_parser('history', help='Show support-source baseline capture history.')
    history_parser.add_argument('--history-path', default=str(DEFAULT_HISTORY_PATH))
    history_parser.add_argument('--pretty', action='store_true')
    write_root_parser = subparsers.add_parser('write-root', help='Write SUPPORT-SOURCE-BASELINE.json at the repo root.')
    write_root_parser.add_argument('--pretty', action='store_true')
    args = parser.parse_args()

    if args.command == 'capture':
        payload = capture_support_source_baseline(root=ROOT, output_dir=Path(args.output_dir), history_path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'history':
        payload = summarize_capture_history(path=Path(args.history_path))
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return
    if args.command == 'write-root':
        payload = write_root_support_source_baseline(root=ROOT)
        print(json.dumps(payload, indent=2 if args.pretty else None))
        return

    payload = build_support_source_baseline(root=ROOT)
    print(json.dumps(payload, indent=2 if args.pretty else None))


if __name__ == '__main__':
    main()
