#!/usr/bin/env python3
import ast, hashlib, json
from pathlib import Path
BASE=Path('/mnt/data/nicotine_rev0003_sources/Nicotine+DEV-rev0003-upstream-sources-20260612T181540Z/source-trees')
lanes=['github-tag-3.3.10','github-branch-3.3.x','github-branch-master']
targets={
    'pynicotine/transfers.py':['Transfers._activate_transfer','Transfers._deactivate_transfer'],
    'pynicotine/downloads.py':['Downloads._transfer_request_downloads','Downloads._transfer_request','Downloads._file_transfer_init','Downloads._file_download_progress','Downloads._file_connection_closed','Downloads._transfer_timeout'],
}

def find_method(src, qual):
    cls_name, meth_name=qual.split('.')
    tree=ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name==cls_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name==meth_name:
                    return item.lineno, getattr(item,'end_lineno', item.lineno)
    return None

rows=[]
md=['# rev0008 U-123 source trace: transfer session map and F-connection callbacks','']
for lane in lanes:
    md += [f'## {lane}', '']
    for rel, quals in targets.items():
        path=BASE/lane/rel
        src=path.read_text(encoding='utf-8')
        lines=src.splitlines()
        for qual in quals:
            pos=find_method(src, qual)
            if not pos:
                rows.append({'lane':lane,'path':rel,'symbol':qual,'present':False})
                continue
            start,end=pos
            snippet='\n'.join(f'{i:5d}: {lines[i-1]}' for i in range(start,end+1))
            h=hashlib.sha256('\n'.join(lines[start-1:end]).encode()).hexdigest()
            rows.append({'lane':lane,'path':rel,'symbol':qual,'present':True,'start_line':start,'end_line':end,'sha256':h})
            md += [f'### `{rel}` `{qual}` lines {start}-{end}', '', f'Function SHA256: `{h}`', '', '```text', snippet, '```', '']
Path('/mnt/data/rev0008_u123_source_trace.md').write_text('\n'.join(md), encoding='utf-8')
Path('/mnt/data/rev0008_u123_source_trace.json').write_text(json.dumps(rows, indent=2, sort_keys=True), encoding='utf-8')
# csv simple
import csv
with open('/mnt/data/rev0008_u123_source_trace.csv','w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f, fieldnames=['lane','path','symbol','present','start_line','end_line','sha256'])
    w.writeheader(); w.writerows(rows)
print('/mnt/data/rev0008_u123_source_trace.md')
