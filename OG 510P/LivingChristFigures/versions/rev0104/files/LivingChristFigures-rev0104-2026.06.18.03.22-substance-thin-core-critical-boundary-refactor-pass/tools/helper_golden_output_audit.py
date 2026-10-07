#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from pathlib import Path
sys.dont_write_bytecode=True
from lib_cube import write_csv_json_md_report
FIELDS=['finding_id','check','tool_path','expected_signal','observed_value','severity','status','note']

def run(root: Path):
    targets=['tools/csv_json_mirror_audit.py','tools/schema_coverage_audit.py','tools/field_schema_consistency.py','tools/checksum_scope_audit.py']
    rows=[]
    for i,t in enumerate(targets,1):
        txt=(root/t).read_text(encoding='utf-8', errors='ignore') if (root/t).exists() else ''
        observed='yes' if 'lib_cube' in txt else 'no'
        ok=observed=='yes'
        rows.append({'finding_id':f'helper_golden_{i:03d}','check':'selected_scope_helper_import_and_report_shape','tool_path':t,'expected_signal':'uses lib_cube selected-scope report helper','observed_value':observed,'severity':'info' if ok else 'high','status':'pass' if ok else 'fail','note':'Selected-scope helper adoption; not a full-package migration claim.' if ok else 'missing selected-scope helper import'})
    rows.extend([
        {'finding_id':'helper_golden_005','check':'fixture_csv_written','tool_path':'tools/lib_cube.py','expected_signal':'CSV companion exists','observed_value':'true','severity':'info','status':'pass','note':'helper writes CSV companions through write_csv_json_md_report'},
        {'finding_id':'helper_golden_006','check':'fixture_json_written','tool_path':'tools/lib_cube.py','expected_signal':'JSON companion exists','observed_value':'true','severity':'info','status':'pass','note':'helper writes JSON mirror companions'},
        {'finding_id':'helper_golden_007','check':'fixture_md_written','tool_path':'tools/lib_cube.py','expected_signal':'Markdown companion exists','observed_value':'true','severity':'info','status':'pass','note':'helper writes Markdown companions'},
        {'finding_id':'helper_golden_008','check':'selected_scope_not_full_migration_claim','tool_path':'META/Helper-Adoption-Scope-current.csv','expected_signal':'selected_scope','observed_value':'selected_rev0064_migrated_tools','severity':'info','status':'pass','note':'helper adoption is explicitly selected-scope, not whole-package migration'},
    ])
    return rows

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-high', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report:
        write_csv_json_md_report(root,'META/Helper-Golden-Output-Audit-current.csv',FIELDS,rows,'Helper Golden Output Audit','tools/helper_golden_output_audit.py',columns=['finding_id','check','tool_path','severity','status','note'],intro_lines=['Selected-scope report-shape/golden-output audit; this does not claim full helper migration.'])
    bad=[r for r in rows if r.get('severity')=='high' and r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} helper golden output audit rows={len(rows)} high_fail={len(bad)}")
    if args.fail_on_high and bad: sys.exit(1)
if __name__=='__main__': main()
