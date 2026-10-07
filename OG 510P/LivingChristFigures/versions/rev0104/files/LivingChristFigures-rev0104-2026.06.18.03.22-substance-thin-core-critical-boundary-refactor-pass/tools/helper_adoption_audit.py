#!/usr/bin/env python3
from __future__ import annotations
import argparse, ast, csv, sys
from pathlib import Path

sys.dont_write_bytecode = True
from lib_cube import read_csv_header, write_csv_json_md_report

FIELDS=['finding_id','check','tool_path','expected_signal','observed_value','severity','status','note']
REFACTORED_TOOLS=[
    'tools/csv_json_mirror_audit.py',
    'tools/schema_coverage_audit.py',
    'tools/field_schema_consistency.py',
    'tools/checksum_scope_audit.py',
]
HELPER_FUNCTIONS=[
    'read_csv_rows',
    'read_csv_header',
    'read_json',
    'safe_md',
    'shape_rows',
    'write_csv_json_md_report',
    'high_or_fail',
]
REPORTS={
    'tools/csv_json_mirror_audit.py':'META/CSV-JSON-Mirror-Audit-current.csv',
    'tools/schema_coverage_audit.py':'META/Schema-Coverage-Audit-current.csv',
    'tools/field_schema_consistency.py':'META/Field-Schema-Consistency-Audit-current.csv',
    'tools/checksum_scope_audit.py':'META/Checksum-Scope-Audit-current.csv',
}

def add(rows, check, tool, expected, observed, ok, note):
    rows.append({
        'finding_id': f'helper_refactor_{len(rows)+1:03d}',
        'check': check,
        'tool_path': tool,
        'expected_signal': expected,
        'observed_value': observed,
        'severity': 'info' if ok else 'high',
        'status': 'pass' if ok else 'fail',
        'note': note,
    })

def parse_funcs(path: Path) -> set[str]:
    try:
        tree=ast.parse(path.read_text(encoding='utf-8'))
    except Exception:
        return set()
    return {node.name for node in tree.body if isinstance(node, ast.FunctionDef)}

def run(root: Path):
    rows=[]
    helper=root/'tools/lib_cube.py'
    funcs=parse_funcs(helper) if helper.exists() else set()
    add(rows,'helper_module_present','tools/lib_cube.py','module exists',str(helper.exists()),helper.exists(),'shared helper module is packaged')
    missing_funcs=[f for f in HELPER_FUNCTIONS if f not in funcs]
    add(rows,'helper_required_functions_present','tools/lib_cube.py','|'.join(HELPER_FUNCTIONS),'missing='+('|'.join(missing_funcs) if missing_funcs else 'none'),not missing_funcs,'helper exposes the required deterministic I/O/report helpers')
    for rel in REFACTORED_TOOLS:
        p=root/rel
        text=p.read_text(encoding='utf-8', errors='replace') if p.exists() else ''
        add(rows,'refactored_tool_present',rel,'tool exists',str(p.exists()),p.exists(),'refactored audit tool is present')
        imports='from lib_cube import' in text and 'write_csv_json_md_report' in text
        add(rows,'refactored_tool_imports_helper',rel,'from lib_cube import write_csv_json_md_report',str(imports),imports,'tool delegates companion report writing to shared helper')
        no_old_writer="csv.DictWriter(f, fieldnames=FIELDS)" not in text
        add(rows,'refactored_tool_no_local_companion_writer',rel,'no duplicated CSV/JSON/MD companion writer block',str(no_old_writer),no_old_writer,'legacy per-tool report-writer block has been removed from this refactored tool')
        report=REPORTS[rel]
        csv_path=root/report
        json_path=csv_path.with_suffix('.json')
        md_path=csv_path.with_suffix('.md')
        companions=csv_path.exists() and json_path.exists() and md_path.exists()
        add(rows,'refactored_tool_report_companions_exist',rel,f'{report}|{json_path.relative_to(root)}|{md_path.relative_to(root)}',str(companions),companions,'refactored tool report still has CSV/JSON/Markdown companions')
        header=read_csv_header(csv_path)
        has_header=bool(header)
        add(rows,'refactored_tool_csv_header_readable',rel,'nonempty CSV header','|'.join(header),has_header,'refactored report remains parseable as CSV')
    all_pass=not any(r['status']=='fail' for r in rows)
    add(rows,'helper_refactor_release_summary','tools/lib_cube.py',f'{len(REFACTORED_TOOLS)} adopted tools',f"adopted={sum(1 for r in rows if r['check']=='refactored_tool_imports_helper' and r['status']=='pass')}",all_pass,'helper refactor is release-safe only when module, functions, imports, companion outputs, and report parseability all pass')
    return rows

def write_reports(root: Path, rows):
    write_csv_json_md_report(
        root=root,
        csv_rel='META/Helper-Adoption-Audit-current.csv',
        fields=FIELDS,
        rows=rows,
        title='Helper Adoption Audit',
        generated_by='tools/helper_adoption_audit.py',
        columns=['finding_id','check','tool_path','severity','status','note'],
        intro_lines=[f'Adoption target tools: {len(REFACTORED_TOOLS)}', 'This report turns the rev0064 helper refactor into a machine-checkable release gate.'],
    )

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    high=[r for r in rows if r.get('severity')=='high']
    print(f"{'FAIL' if high else 'PASS'} helper adoption rows={len(rows)} high={len(high)}")
    for r in high[:20]: print(f"HIGH {r['check']} {r['tool_path']}: {r['note']}")
    if args.fail_on_high and high: sys.exit(1)
if __name__=='__main__': main()
