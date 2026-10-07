#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, csv, json, re, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import write_csv_json_md_report

FIELDS=['tool_path','syntax_status','entrypoint_status','argparse_status','bytecode_policy_status','libcube_import_status','declared_outputs','severity','status','note']

def read_text(p: Path) -> str:
    return p.read_text(encoding='utf-8', errors='ignore')

def generated_specs(root: Path):
    out={}
    try:
        import importlib.util
        gp=root/'tools/generated_artifact_provenance.py'
        spec=importlib.util.spec_from_file_location('gap_for_executability', gp)
        mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod)
        for artifact, generator, _inputs in getattr(mod,'ARTIFACTS',[]): out.setdefault(generator,[]).append(artifact)
    except Exception:
        pass
    return out

def has_main_guard(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            src=ast.unparse(node.test) if hasattr(ast,'unparse') else ''
            if "__name__" in src and "__main__" in src: return True
    return False

def has_argparse(tree: ast.AST, text: str) -> bool:
    if 'argparse.ArgumentParser' in text: return True
    return any(isinstance(n, ast.Import) and any(a.name=='argparse' for a in n.names) for n in ast.walk(tree))

def run(root: Path):
    prov=generated_specs(root); rows=[]
    for p in sorted((root/'tools').glob('*.py')):
        rel=str(p.relative_to(root)).replace('\\','/')
        text=read_text(p); syntax='pass'; tree=None; note=[]
        try:
            tree=ast.parse(text, filename=rel)
        except SyntaxError as e:
            syntax='fail'; note.append(f'syntax error line {e.lineno}: {e.msg}')
        entry='not_applicable' if rel=='tools/lib_cube.py' else ('pass' if tree and has_main_guard(tree) else 'review')
        if rel!='tools/lib_cube.py' and entry!='pass': note.append('no explicit __main__ entrypoint found')
        argparse_status='not_applicable' if rel=='tools/lib_cube.py' else ('pass' if tree and has_argparse(tree,text) else 'review')
        if rel!='tools/lib_cube.py' and argparse_status!='pass': note.append('no argparse CLI contract detected')
        bytecode='pass' if 'sys.dont_write_bytecode' in text else 'review'
        if bytecode!='pass': note.append('does not set sys.dont_write_bytecode; package must still strip caches before handoff')
        libstat='imports_lib_cube' if 'from lib_cube import' in text or 'import lib_cube' in text else ('helper_or_not_applicable' if rel=='tools/lib_cube.py' else 'does_not_import_lib_cube')
        severity='high' if syntax=='fail' else 'info'
        status='fail' if syntax=='fail' else 'pass'
        rows.append({'tool_path':rel,'syntax_status':syntax,'entrypoint_status':entry,'argparse_status':argparse_status,'bytecode_policy_status':bytecode,'libcube_import_status':libstat,'declared_outputs':'|'.join(sorted(prov.get(rel,[]))),'severity':severity,'status':status,'note':'; '.join(note) if note else 'syntax and static entrypoint audit completed'})
    return rows

def write_reports(root: Path, rows):
    high=sum(1 for r in rows if r.get('severity')=='high' and r.get('status')!='pass')
    review=sum(1 for r in rows if 'review' in (r.get('entrypoint_status','')+r.get('argparse_status','')+r.get('bytecode_policy_status','')))
    write_csv_json_md_report(root,'META/Tool-Executability-Audit-current.csv',FIELDS,rows,'Tool Executability Audit','tools/tool_executability_audit.py',columns=['tool_path','syntax_status','entrypoint_status','argparse_status','bytecode_policy_status','severity','status','note'],intro_lines=[f'Tools audited: {len(rows)}',f'High failures: {high}',f'Review-only rows: {review}','This audit intentionally does not execute tools; it checks syntax and static CLI/bytecode posture without producing pycache artifacts.'])

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if high else 'PASS'} tool executability audit tools={len(rows)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['tool_path']}: {r['note']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
