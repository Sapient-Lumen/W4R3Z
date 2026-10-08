#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[2]
SCHEMA=ROOT/'schemas'/'archive_report_compaction_candidate_receipt.schema.json'
EXAMPLE=ROOT/'examples'/'snapshots'/'archive_report_compaction_candidate_receipt.json'
TOOL=ROOT/'scripts'/'tools'/'build_archive_report_compaction_candidate_receipt.py'
HOTSPOT=ROOT/'examples'/'snapshots'/'archive_report_hotspot_receipt.json'
SEMANTIC=ROOT/'examples'/'snapshots'/'archive_report_semantic_handle_receipt.json'
def fail(msg:str)->int:
    print(f'archive-report-compaction-candidate-receipt: {msg}', file=sys.stderr)
    return 1
def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))
def main()->int:
    for path in [SCHEMA,EXAMPLE,TOOL,HOTSPOT,SEMANTIC]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    schema=load_json(SCHEMA)
    if schema.get('title')!='Archive Report Compaction Candidate Receipt':
        return fail('schema title mismatch')
    receipt=load_json(EXAMPLE)
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.validate(receipt,schema)
    proc=subprocess.run([sys.executable,str(TOOL),'--strict'],cwd=ROOT,capture_output=True,text=True)
    if proc.returncode!=0:
        return fail(f'tool exited nonzero: {proc.stderr or proc.stdout}')
    live=load_json(EXAMPLE)
    if receipt!=live:
        return fail('example receipt should match the current live tool output exactly')
    if receipt['status_counts']!={'passed_check_count':7,'total_check_count':7,'ready_to_cite':True}:
        return fail('unexpected status counts')
    if receipt['semantic_handle_receipt_path']!='examples/snapshots/archive_report_semantic_handle_receipt.json':
        return fail('expected semantic handle receipt path to point at the standing semantic handle receipt example')
    rows=receipt['priority_candidates']
    metrics=receipt['summary_metrics']
    if metrics['priority_candidate_count']!=len(rows):
        return fail('priority candidate count should match the candidate table length')
    if metrics['priority_candidate_raw_bytes']!=sum(int(row['raw_bytes']) for row in rows):
        return fail('priority candidate bytes should match the candidate table exactly')
    if metrics['priority_candidates_with_library_topic_count']!=sum(1 for row in rows if 'library_topic' in row['backing_handle_kinds']):
        return fail('library-topic-backed candidate count should match the candidate table')
    if metrics['priority_candidates_with_snapshot_count']!=sum(1 for row in rows if 'snapshot' in row['backing_handle_kinds']):
        return fail('snapshot-backed candidate count should match the candidate table')
    if metrics['priority_candidates_using_semantic_alias_count']!=sum(1 for row in rows if row['semantic_alias_used']):
        return fail('semantic-alias-backed candidate count should match the candidate table')
    print('archive-report-compaction-candidate-receipt: ok '
          f'({len(rows)} citation-backed compaction candidates rebuild-match the current hotspot frontier)')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
