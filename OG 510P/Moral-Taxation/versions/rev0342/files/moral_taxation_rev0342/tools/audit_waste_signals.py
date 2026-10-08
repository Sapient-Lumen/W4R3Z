#!/usr/bin/env python3
import json, pathlib, sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()
errors = []
version = (root / 'VERSION').read_text(encoding='utf-8').strip()
cube = json.loads((root / 'cube-index.json').read_text(encoding='utf-8'))
summary = cube.get('audit_summary', {})
metrics = summary.get('prose_bloat_metrics', {})
negative = {k: v for k, v in metrics.items() if k.endswith('_bytes_saved') and isinstance(v, int) and v < 0}
waste = summary.get('waste_signal_metrics', {})

if summary.get('waste_signal_audit_required') is not True:
    errors.append('cube audit_summary must mark waste_signal_audit_required=True')
if negative:
    errors.append('negative compactness savings remain: ' + ', '.join(f'{k}={v}' for k, v in sorted(negative.items())))
if waste.get('negative_bytes_saved_metrics') != negative:
    errors.append('waste_signal_metrics.negative_bytes_saved_metrics must match live negative prose metrics')
if waste.get('total_negative_bytes') != sum(-v for v in negative.values()):
    errors.append('waste_signal_metrics.total_negative_bytes is stale')
if not negative and waste.get('queue_status') != 'compressed_no_negative_savings':
    errors.append('waste_signal_metrics.queue_status must be compressed_no_negative_savings once the queue is closed')
report_rel = cube.get('waste_signal_audit_report_path')
if not report_rel or not (root / report_rel).exists():
    errors.append('cube-index.json waste_signal_audit_report_path must point to an existing report')
else:
    text = (root / report_rel).read_text(encoding='utf-8')
    if version not in text[:200]:
        errors.append('waste-signal audit report opening must name the active revision')
    if negative:
        for k, v in negative.items():
            if k not in text or str(v) not in text:
                errors.append(f'waste-signal audit report must name negative metric {k}={v}')
    elif 'No negative bytes-saved metrics remain.' not in text:
        errors.append('waste-signal audit report must explicitly say no negative bytes-saved metrics remain')
if errors:
    raise SystemExit('\n'.join(errors))
print('waste signal audit ok')
