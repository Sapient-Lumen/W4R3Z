#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess, sys
from pathlib import Path
import jsonschema
ROOT=Path(__file__).resolve().parents[2]
SCHEMA=ROOT/'schemas'/'archive_report_semantic_handle_receipt.schema.json'
EXAMPLE=ROOT/'examples'/'snapshots'/'archive_report_semantic_handle_receipt.json'
TOOL=ROOT/'scripts'/'tools'/'build_archive_report_semantic_handle_receipt.py'
HOTSPOT=ROOT/'examples'/'snapshots'/'archive_report_hotspot_receipt.json'
def fail(msg:str)->int:
    print(f'archive-report-semantic-handle-receipt: {msg}', file=sys.stderr)
    return 1
def load_json(path):
    return json.loads(path.read_text(encoding='utf-8'))
def main()->int:
    for path in [SCHEMA,EXAMPLE,TOOL,HOTSPOT]:
        if not path.exists():
            return fail(f'missing {path.relative_to(ROOT)}')
    schema=load_json(SCHEMA)
    if schema.get('title')!='Archive Report Semantic Handle Receipt':
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
    if receipt['status_counts']!={'passed_check_count':8,'total_check_count':8,'ready_to_cite':True}:
        return fail('unexpected status counts')
    aliases=receipt['semantic_aliases']
    if receipt['measurement_scope']['hotspot_buffer_limit']!=13:
        return fail('expected the semantic-handle receipt to scan the buffered top-13 hotspot surface')
    if receipt['summary_metrics']['semantic_alias_count']!=len(aliases):
        return fail('semantic alias count should match the alias table length')
    if receipt['summary_metrics']['library_topic_alias_count']!=sum(1 for row in aliases if row['matched_handle']['kind']=='library_topic'):
        return fail('library-topic alias count should match the alias table')
    if receipt['summary_metrics']['semantic_alias_raw_bytes']!=sum(int(row['raw_bytes']) for row in aliases):
        return fail('semantic alias raw bytes should match the alias rows exactly')
    print('archive-report-semantic-handle-receipt: ok '
          f'({len(aliases)} semantic aliases rebuild-match the buffered live hotspot frontier)')
    return 0
if __name__=='__main__':
    raise SystemExit(main())
