#!/usr/bin/env python3
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
report=json.loads((ROOT/'AUDIT-REPORT.json').read_text(encoding='utf-8'))
ref=json.loads((ROOT/'REFERENCE-INTEGRITY-REPORT.json').read_text(encoding='utf-8'))
hg=json.loads((ROOT/'HIGH-GATE-COVERAGE-AUDIT.json').read_text(encoding='utf-8'))
summary={
  'revision': report.get('revision'),
  'records': report.get('scope',{}).get('records_seen'),
  'public_records': report.get('scope',{}).get('public_records_seen'),
  'private_testimony': report.get('scope',{}).get('private_testimony_seen'),
  'source_cards': ref.get('source_integrity',{}).get('source_cards_count'),
  'alias_ids_match': ref.get('alias_integrity',{}).get('ids_match'),
  'review_missing_count': ref.get('review_integrity',{}).get('records_missing_required_review_fields_count'),
  'high_gate_domains': hg.get('domain_counts',{}),
  'posture': report.get('posture', 'no public release')
}
print(json.dumps(summary, indent=2))
