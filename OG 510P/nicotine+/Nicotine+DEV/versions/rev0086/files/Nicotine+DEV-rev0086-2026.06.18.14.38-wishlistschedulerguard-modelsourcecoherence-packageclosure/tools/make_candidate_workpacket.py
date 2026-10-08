#!/usr/bin/env python3
import csv, sys, pathlib
queue = pathlib.Path('data/rev0004_ranked_audit_queue.csv')
if len(sys.argv) != 2:
    raise SystemExit('usage: tools/make_candidate_workpacket.py U-169')
want = sys.argv[1]
rows = list(csv.DictReader(queue.open(newline='', encoding='utf-8')))
row = next((r for r in rows if r['id'] == want), None)
if row is None:
    raise SystemExit(f'not found: {want}')
out = pathlib.Path('workpackets') / f'{want}.md'
out.parent.mkdir(exist_ok=True)
out.write_text(f'''# Workpacket {want}

## Title

{row['title']}

## Cluster

{row['cluster']}

## Current status

{row['strict_doc_status']}

## Required checks

- [ ] Source trace in 3.3.10
- [ ] Source trace in 3.3.x
- [ ] Source trace in master
- [ ] Public overlap check
- [ ] Boundary/impact statement
- [ ] Evidence/repro note
- [ ] Promote/downgrade/defer decision

## Notes

''', encoding='utf-8')
print(out)
