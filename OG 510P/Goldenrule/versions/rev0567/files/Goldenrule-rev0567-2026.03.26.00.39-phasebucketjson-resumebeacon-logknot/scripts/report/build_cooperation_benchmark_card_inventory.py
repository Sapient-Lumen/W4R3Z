#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

import jsonschema


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load module {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROOT = Path(__file__).resolve().parents[2]
CARD_TOOL = ROOT / 'scripts' / 'tools' / 'cooperation_benchmark_card.py'
card_tool = load_module('cooperation_benchmark_card_tool', CARD_TOOL)

CARD_SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card.schema.json'
FREEZE_SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_freeze_receipt.schema.json'
DELTA_SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_delta_receipt.schema.json'
INVENTORY_SCHEMA_PATH = ROOT / 'schemas' / 'cooperation_benchmark_card_inventory.schema.json'


TITLE = '# Cooperation Benchmark Card Inventory'
SUBTITLE = (
    'Generated from schema-valid cooperation benchmark cards and compact freeze/delta receipts found '
    'in the repository. Freeze and delta status both fail closed on receipt drift.'
)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def try_validate(obj: Any, schema: dict[str, Any]) -> bool:
    try:
        jsonschema.validate(obj, schema)
    except jsonschema.ValidationError:
        return False
    return True


def freeze_receipt_drift_reasons(receipt: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    card_abs = ROOT / receipt['card_path']
    render_abs = ROOT / receipt['rendered_markdown_path']
    if not card_abs.exists():
        reasons.append('freeze-card-missing')
    elif receipt['card_sha256'] != sha256_file(card_abs):
        reasons.append('freeze-card-sha-drift')
    if not render_abs.exists():
        reasons.append('freeze-render-missing')
    elif receipt['rendered_markdown_sha256'] != sha256_file(render_abs):
        reasons.append('freeze-render-sha-drift')
    return reasons


def delta_receipt_drift_reasons(receipt: dict[str, Any]) -> list[str]:
    reasons: list[str] = []
    old_card_abs = ROOT / receipt['old_card_path']
    new_card_abs = ROOT / receipt['new_card_path']
    if not old_card_abs.exists():
        reasons.append('delta-old-card-missing')
    elif receipt['old_card_sha256'] != sha256_file(old_card_abs):
        reasons.append('delta-old-card-sha-drift')
    if not new_card_abs.exists():
        reasons.append('delta-new-card-missing')
    elif receipt['new_card_sha256'] != sha256_file(new_card_abs):
        reasons.append('delta-new-card-sha-drift')
    return reasons


def collect() -> dict[str, Any]:
    card_schema = load_json(CARD_SCHEMA_PATH)
    freeze_schema = load_json(FREEZE_SCHEMA_PATH)
    delta_schema = load_json(DELTA_SCHEMA_PATH)
    inventory_schema = load_json(INVENTORY_SCHEMA_PATH)
    for schema in [card_schema, freeze_schema, delta_schema, inventory_schema]:
        jsonschema.Draft202012Validator.check_schema(schema)

    cards: dict[str, dict[str, Any]] = {}
    freeze_receipts: list[dict[str, Any]] = []
    delta_receipts: list[dict[str, Any]] = []

    for path in sorted(ROOT.rglob('*.json')):
        rel = relative(path)
        if rel.startswith('.git/'):
            continue
        obj = load_json(path)
        if try_validate(obj, card_schema):
            issues = list(card_tool.readiness_issues(obj))
            cards[rel] = {
                'id': obj['id'],
                'benchmark_name': obj['benchmark_name'],
                'result_kind': obj['result_kind'],
                'path': rel,
                'claim_ready': not issues,
                'readiness_issue_count': len(issues),
                'freeze_receipt_paths': [],
                'verified_freeze_receipt_paths': [],
                'drifted_freeze_receipt_paths': [],
                'incoming_delta_receipt_paths': [],
                'outgoing_delta_receipt_paths': [],
                'verified_incoming_delta_receipt_paths': [],
                'verified_outgoing_delta_receipt_paths': [],
                'drifted_incoming_delta_receipt_paths': [],
                'drifted_outgoing_delta_receipt_paths': [],
                'predecessor_card_ids': [],
                'successor_card_ids': [],
            }
            continue
        if try_validate(obj, freeze_schema):
            freeze_receipts.append({
                'path': rel,
                'card_id': obj['card_id'],
                'card_path': obj['card_path'],
                'claim_ready': bool(obj['claim_ready']),
                'rendered_markdown_path': obj['rendered_markdown_path'],
                'card_sha256': obj['card_sha256'],
                'rendered_markdown_sha256': obj['rendered_markdown_sha256'],
                'drift_reason_codes': [],
                'matches_current_surface': True,
            })
            continue
        if try_validate(obj, delta_schema):
            delta_receipts.append({
                'path': rel,
                'old_card_id': obj['old_card_id'],
                'new_card_id': obj['new_card_id'],
                'old_card_path': obj['old_card_path'],
                'old_card_sha256': obj['old_card_sha256'],
                'new_card_path': obj['new_card_path'],
                'new_card_sha256': obj['new_card_sha256'],
                'claim_surface_changed': bool(obj['claim_surface_changed']),
                'drift_reason_codes': [],
                'matches_current_surface': True,
            })

    orphan_freeze_receipt_paths: list[str] = []
    orphan_delta_receipt_paths: list[str] = []

    for receipt in freeze_receipts:
        card = cards.get(receipt['card_path'])
        if card is None or card['id'] != receipt['card_id']:
            orphan_freeze_receipt_paths.append(receipt['path'])
            continue
        drift_reasons = freeze_receipt_drift_reasons(receipt)
        receipt['drift_reason_codes'] = drift_reasons
        receipt['matches_current_surface'] = not drift_reasons
        card['freeze_receipt_paths'].append(receipt['path'])
        if drift_reasons:
            card['drifted_freeze_receipt_paths'].append(receipt['path'])
        else:
            card['verified_freeze_receipt_paths'].append(receipt['path'])

    for receipt in delta_receipts:
        old_card = cards.get(receipt['old_card_path'])
        new_card = cards.get(receipt['new_card_path'])
        linked = True
        if old_card is None or old_card['id'] != receipt['old_card_id']:
            linked = False
        if new_card is None or new_card['id'] != receipt['new_card_id']:
            linked = False
        if not linked:
            orphan_delta_receipt_paths.append(receipt['path'])
            continue
        drift_reasons = delta_receipt_drift_reasons(receipt)
        receipt['drift_reason_codes'] = drift_reasons
        receipt['matches_current_surface'] = not drift_reasons
        old_card['outgoing_delta_receipt_paths'].append(receipt['path'])
        old_card['successor_card_ids'].append(receipt['new_card_id'])
        new_card['incoming_delta_receipt_paths'].append(receipt['path'])
        new_card['predecessor_card_ids'].append(receipt['old_card_id'])
        if drift_reasons:
            old_card['drifted_outgoing_delta_receipt_paths'].append(receipt['path'])
            new_card['drifted_incoming_delta_receipt_paths'].append(receipt['path'])
        else:
            old_card['verified_outgoing_delta_receipt_paths'].append(receipt['path'])
            new_card['verified_incoming_delta_receipt_paths'].append(receipt['path'])

    card_rows = []
    for row in cards.values():
        row['freeze_receipt_paths'].sort()
        row['verified_freeze_receipt_paths'].sort()
        row['drifted_freeze_receipt_paths'].sort()
        row['incoming_delta_receipt_paths'].sort()
        row['outgoing_delta_receipt_paths'].sort()
        row['verified_incoming_delta_receipt_paths'].sort()
        row['verified_outgoing_delta_receipt_paths'].sort()
        row['drifted_incoming_delta_receipt_paths'].sort()
        row['drifted_outgoing_delta_receipt_paths'].sort()
        row['predecessor_card_ids'].sort()
        row['successor_card_ids'].sort()
        row['frozen'] = bool(row['verified_freeze_receipt_paths'])
        row['freeze_drift'] = bool(row['drifted_freeze_receipt_paths'])
        row['delta_drift'] = bool(row['drifted_incoming_delta_receipt_paths'] or row['drifted_outgoing_delta_receipt_paths'])
        row['latest_known'] = not row['outgoing_delta_receipt_paths']
        card_rows.append(row)
    card_rows.sort(key=lambda r: r['path'])
    freeze_receipts.sort(key=lambda r: r['path'])
    delta_receipts.sort(key=lambda r: r['path'])
    orphan_freeze_receipt_paths.sort()
    orphan_delta_receipt_paths.sort()

    latest_claim_ready = [r['id'] for r in card_rows if r['claim_ready'] and r['latest_known']]

    data = {
        'card_inventory_kind': 'cooperation_benchmark_card_inventory',
        'cards': card_rows,
        'freeze_receipts': freeze_receipts,
        'delta_receipts': delta_receipts,
        'counts': {
            'card_count': len(card_rows),
            'claim_ready_card_count': sum(1 for r in card_rows if r['claim_ready']),
            'frozen_card_count': sum(1 for r in card_rows if r['frozen']),
            'freeze_drift_card_count': sum(1 for r in card_rows if r['freeze_drift']),
            'delta_drift_card_count': sum(1 for r in card_rows if r['delta_drift']),
            'latest_known_card_count': sum(1 for r in card_rows if r['latest_known']),
            'freeze_receipt_count': len(freeze_receipts),
            'verified_freeze_receipt_count': sum(1 for r in freeze_receipts if r['matches_current_surface']),
            'drifted_freeze_receipt_count': sum(1 for r in freeze_receipts if not r['matches_current_surface']),
            'delta_receipt_count': len(delta_receipts),
            'verified_delta_receipt_count': sum(1 for r in delta_receipts if r['matches_current_surface']),
            'drifted_delta_receipt_count': sum(1 for r in delta_receipts if not r['matches_current_surface']),
            'orphan_freeze_receipt_count': len(orphan_freeze_receipt_paths),
            'orphan_delta_receipt_count': len(orphan_delta_receipt_paths),
        },
        'latest_claim_ready_card_ids': latest_claim_ready,
        'orphan_freeze_receipt_paths': orphan_freeze_receipt_paths,
        'orphan_delta_receipt_paths': orphan_delta_receipt_paths,
    }
    jsonschema.validate(data, inventory_schema)
    return data


def render(data: dict[str, Any]) -> str:
    counts = data['counts']
    lines = [
        TITLE,
        '',
        SUBTITLE,
        '',
        f"- card_count: {counts['card_count']}",
        f"- claim_ready_card_count: {counts['claim_ready_card_count']}",
        f"- frozen_card_count: {counts['frozen_card_count']}",
        f"- freeze_drift_card_count: {counts['freeze_drift_card_count']}",
        f"- delta_drift_card_count: {counts['delta_drift_card_count']}",
        f"- latest_known_card_count: {counts['latest_known_card_count']}",
        f"- freeze_receipt_count: {counts['freeze_receipt_count']}",
        f"- verified_freeze_receipt_count: {counts['verified_freeze_receipt_count']}",
        f"- drifted_freeze_receipt_count: {counts['drifted_freeze_receipt_count']}",
        f"- delta_receipt_count: {counts['delta_receipt_count']}",
        f"- verified_delta_receipt_count: {counts['verified_delta_receipt_count']}",
        f"- drifted_delta_receipt_count: {counts['drifted_delta_receipt_count']}",
        f"- orphan_freeze_receipt_count: {counts['orphan_freeze_receipt_count']}",
        f"- orphan_delta_receipt_count: {counts['orphan_delta_receipt_count']}",
        '',
        '## Cards',
        '',
        '| id | path | claim_ready | frozen | freeze_drift | delta_drift | latest_known | predecessors | successors |',
        '|---|---|---:|---:|---:|---:|---:|---|---|',
    ]
    for card in data['cards']:
        preds = ', '.join(card['predecessor_card_ids']) or '—'
        succs = ', '.join(card['successor_card_ids']) or '—'
        lines.append(
            f"| `{card['id']}` | `{card['path']}` | {'yes' if card['claim_ready'] else 'no'} | "
            f"{'yes' if card['frozen'] else 'no'} | {'yes' if card['freeze_drift'] else 'no'} | {'yes' if card['delta_drift'] else 'no'} | {'yes' if card['latest_known'] else 'no'} | {preds} | {succs} |"
        )
    lines.extend([
        '',
        '## Freeze receipts',
        '',
        '| receipt_path | card_id | card_path | claim_ready | matches_current_surface | drift_reason_codes |',
        '|---|---|---|---:|---:|---|',
    ])
    for receipt in data['freeze_receipts']:
        lines.append(
            f"| `{receipt['path']}` | `{receipt['card_id']}` | `{receipt['card_path']}` | {'yes' if receipt['claim_ready'] else 'no'} | "
            f"{'yes' if receipt['matches_current_surface'] else 'no'} | {', '.join(receipt['drift_reason_codes']) or '—'} |"
        )
    lines.extend([
        '',
        '## Delta receipts',
        '',
        '| receipt_path | old_card_id | new_card_id | claim_surface_changed | matches_current_surface | drift_reason_codes |',
        '|---|---|---|---:|---:|---|',
    ])
    for receipt in data['delta_receipts']:
        lines.append(
            f"| `{receipt['path']}` | `{receipt['old_card_id']}` | `{receipt['new_card_id']}` | {'yes' if receipt['claim_surface_changed'] else 'no'} | "
            f"{'yes' if receipt['matches_current_surface'] else 'no'} | {', '.join(receipt['drift_reason_codes']) or '—'} |"
        )

    if data['latest_claim_ready_card_ids']:
        lines.extend(['', '## Latest claim-ready cards', ''])
        for card_id in data['latest_claim_ready_card_ids']:
            lines.append(f"- `{card_id}`")

    if data['orphan_freeze_receipt_paths'] or data['orphan_delta_receipt_paths']:
        lines.extend(['', '## Orphan receipts', ''])
        for path in data['orphan_freeze_receipt_paths']:
            lines.append(f"- freeze receipt without linked card: `{path}`")
        for path in data['orphan_delta_receipt_paths']:
            lines.append(f"- delta receipt without linked cards: `{path}`")

    lines.append('')
    return '\n'.join(lines)


def main() -> int:
    write = '--write' in sys.argv
    data = collect()
    out_json = ROOT / 'artifacts' / 'reports' / 'cooperation_benchmark_card_inventory.json'
    out_md = ROOT / 'docs' / 'COOPERATION_BENCHMARK_CARD_INVENTORY.md'
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    expected_md = render(data) + '\n'
    if write or not out_md.exists():
        out_md.write_text(expected_md, encoding='utf-8')
        print(f"cooperation-benchmark-card-inventory: wrote {out_md}")
        print(f"cooperation-benchmark-card-inventory: wrote {out_json}")
        return 0
    current_md = out_md.read_text(encoding='utf-8')
    if current_md != expected_md:
        print('cooperation-benchmark-card-inventory: drift detected; run with --write', file=sys.stderr)
        return 1
    print(f"cooperation-benchmark-card-inventory: ok ({data['counts']['card_count']} cards)")
    print(f"cooperation-benchmark-card-inventory: wrote {out_json}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
