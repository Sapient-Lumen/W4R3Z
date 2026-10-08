#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[2]
SCHEMA=ROOT/'schemas'/'archive_report_compaction_gap_receipt.schema.json'
EXAMPLE=ROOT/'examples'/'snapshots'/'archive_report_compaction_gap_receipt.json'
TOOL=ROOT/'scripts'/'tools'/'build_archive_report_compaction_gap_receipt.py'
HOTSPOT=ROOT/'examples'/'snapshots'/'archive_report_hotspot_receipt.json'
SEMANTIC=ROOT/'examples'/'snapshots'/'archive_report_semantic_handle_receipt.json'
CANDIDATE=ROOT/'examples'/'snapshots'/'archive_report_compaction_candidate_receipt.json'
def fail(msg:str)->int: print(f'archive-report-compaction-gap-receipt: {msg}', file=sys.stderr); return 1
def load_json(path): return json.loads(path.read_text(encoding='utf-8'))
def main()->int:
    for path in [SCHEMA,EXAMPLE,TOOL,HOTSPOT,SEMANTIC,CANDIDATE]:
        if not path.exists(): return fail(f'missing {path.relative_to(ROOT)}')
    schema=load_json(SCHEMA)
    if schema.get('title')!='Archive Report Compaction Gap Receipt': return fail('schema title mismatch')
    receipt=load_json(EXAMPLE)
    jsonschema.Draft202012Validator.check_schema(schema); jsonschema.validate(receipt,schema)
    proc=subprocess.run([sys.executable,str(TOOL),'--strict'],cwd=ROOT,capture_output=True,text=True)
    if proc.returncode!=0: return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    live=load_json(EXAMPLE)
    if receipt!=live: return fail('example receipt should match the current live tool output exactly')
    if receipt['status_counts']!={'passed_check_count':8,'total_check_count':8,'ready_to_cite':True}: return fail('unexpected status counts')
    if receipt['semantic_handle_receipt_path']!='examples/snapshots/archive_report_semantic_handle_receipt.json': return fail('expected semantic handle receipt path to point at the standing semantic handle receipt example')
    rows=receipt['blocked_hotspots']; metrics=receipt['summary_metrics']
    if metrics['blocked_hotspot_count']!=len(rows): return fail('blocked hotspot count should match the blocked table length')
    if metrics['blocked_hotspot_raw_bytes']!=sum(int(row['raw_bytes']) for row in rows): return fail('blocked hotspot bytes should match the blocked table exactly')
    if any(int(row['backing_handle_count'])!=0 or row['backing_handles']!=[] for row in rows): return fail('blocked hotspot rows should carry zero backing handles')
    print('archive-report-compaction-gap-receipt: ok '
          f'({len(rows)} true handle gaps remain after semantic and candidate recovery on the live frontier)'); return 0
if __name__=='__main__':
    raise SystemExit(main())
