import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
queue = json.loads((ROOT / 'FOLLOWTHROUGH_QUEUE.json').read_text(encoding='utf-8'))['items']
receipt = json.loads((ROOT / 'REVISION_RECEIPT.json').read_text(encoding='utf-8'))

ids = [item['id'] for item in queue]
if len(ids) != len(set(ids)):
    dupes = sorted({item for item in ids if ids.count(item) > 1})
    raise SystemExit('duplicate followthrough IDs: ' + ', '.join(dupes))

live = sorted(item['id'] for item in queue if item.get('state') == 'queued')
closed = sorted(item['id'] for item in queue if item.get('state') == 'done')
other = sorted(item['id'] for item in queue if item.get('state') not in {'queued', 'done'})
if other:
    raise SystemExit('unsupported followthrough states: ' + ', '.join(other))

revision = receipt.get('revision')
for item in queue:
    if item.get('state') != 'queued':
        continue
    next_surface = item.get('next_surface', '')
    if not next_surface:
        raise SystemExit(f'live followthrough {item["id"]} missing next_surface')
    if revision not in next_surface:
        raise SystemExit(f'live followthrough {item["id"]} next_surface must name current revision {revision}: {next_surface}')
    if not (ROOT / next_surface).exists():
        raise SystemExit(f'live followthrough {item["id"]} next_surface missing: {next_surface}')
    for field in ['why_live', 'current_blocker', 'current_action']:
        if revision not in item.get(field, ''):
            raise SystemExit(f'live followthrough {item["id"]} {field} must mention current revision {revision}')


receipt_live = sorted(receipt.get('live_followthrough', []))
receipt_closed = sorted(receipt.get('closed_followthrough', []))

if receipt_live != live:
    raise SystemExit(
        'receipt live_followthrough mismatch\n'
        + 'expected: ' + ', '.join(live) + '\n'
        + 'receipt: ' + ', '.join(receipt_live)
    )
if receipt_closed != closed:
    missing = sorted(set(closed) - set(receipt_closed))
    extra = sorted(set(receipt_closed) - set(closed))
    raise SystemExit(
        'receipt closed_followthrough mismatch\n'
        + 'missing: ' + ', '.join(missing) + '\n'
        + 'extra: ' + ', '.join(extra)
    )

print(f'check_followthrough_receipt: OK ({len(live)} live, {len(closed)} closed)')
