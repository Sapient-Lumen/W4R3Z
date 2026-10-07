#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

FIELDS=['selftest_id','target_tool','mutation','expected_failure_signal','observed_failure_signal','status','detail']


def _link_or_copy(src: str, dst: str) -> None:
    """Fast fixture copy: hardlink files into the temp package, copying only on fallback.

    Audit selftests mutate only a few known files and report outputs. Those paths are
    materialized with copy-on-write before edits or report generation, so the source
    package is not modified. This keeps the selftests substantive while avoiding the
    repeated full-package byte copies that can stall in constrained cloudtainers.
    """
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def copy_pkg(root: Path, tmp: Path) -> Path:
    dst=tmp/'pkg'
    def ignore(_dir, names):
        return {n for n in names if n == '__pycache__' or n.endswith(('.pyc','.pyo'))}
    shutil.copytree(root, dst, ignore=ignore, copy_function=_link_or_copy)
    return dst


def materialize(path: Path) -> None:
    """Break a hardlink before a selftest mutates a fixture file or report output."""
    if not path.exists() or path.is_dir():
        return
    data=path.read_bytes()
    tmp=path.with_name(path.name+'.cowtmp')
    tmp.write_bytes(data)
    shutil.copystat(path, tmp, follow_symlinks=True)
    tmp.replace(path)


REPORT_OUTPUTS={
    'tools/public_release_lint.py':[
        'META/Public-Release-Lint-current.csv','META/Public-Release-Lint-current.json','META/Public-Release-Lint-current.md'],
    'tools/csv_json_mirror_audit.py':[
        'META/CSV-JSON-Mirror-Audit-current.csv','META/CSV-JSON-Mirror-Audit-current.json','META/CSV-JSON-Mirror-Audit-current.md'],
    'tools/revision_surface_audit.py':[
        'META/Revision-Surface-Audit-current.csv','META/Revision-Surface-Audit-current.json','META/Revision-Surface-Audit-current.md'],
    'tools/path_reference_audit.py':[
        'META/Path-Reference-Audit-current.csv','META/Path-Reference-Audit-current.json','META/Path-Reference-Audit-current.md'],
    'tools/row_validate.py':[
        'SCHEMA/Row-Validation-Report-current.csv','SCHEMA/Row-Validation-Report-current.json','SCHEMA/Row-Validation-Report-current.md'],
    'tools/public_index_semantic_audit.py':[
        'META/Public-Index-Semantic-Audit-current.csv','META/Public-Index-Semantic-Audit-current.json','META/Public-Index-Semantic-Audit-current.md'],
}


def read_json(path: Path):
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return []


def run_py(pkg: Path, tool_rel: str, *args: str) -> subprocess.CompletedProcess:
    for rel in REPORT_OUTPUTS.get(tool_rel, []):
        materialize(pkg/rel)
    return subprocess.run([sys.executable, str(pkg/tool_rel), str(pkg), *args], text=True, capture_output=True, timeout=60)


def high_rows(path: Path) -> list[dict]:
    data=read_json(path)
    return [r for r in data if isinstance(r, dict) and r.get('severity')=='high']


def add(rows, sid, tool, mutation, expected, observed, ok, detail):
    rows.append({
        'selftest_id':sid,
        'target_tool':tool,
        'mutation':mutation,
        'expected_failure_signal':expected,
        'observed_failure_signal':observed,
        'status':'pass' if ok else 'fail',
        'detail':detail,
    })


def selftest_public_lint(root: Path, rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory() as td:
        pkg=copy_pkg(root, Path(td))
        p=pkg/'PUBLIC/README-public-edition.md'
        materialize(p)
        p.write_text(p.read_text(encoding='utf-8')+'\nAudit self-test leak: https://example.org/selftest-leak\n', encoding='utf-8')
        cp=run_py(pkg,'tools/public_release_lint.py','--write-report')
        highs=high_rows(pkg/'META/Public-Release-Lint-current.json')
        ok=any(r.get('risk_type')=='raw_url' and 'example.org' in r.get('match','') for r in highs)
        add(rows,'selftest_001','tools/public_release_lint.py','append raw URL to public README','high raw_url finding',f'returncode={cp.returncode}; high={len(highs)}',ok,'public layer URL leak must be caught as a high finding')


def selftest_mirror(root: Path, rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory() as td:
        pkg=copy_pkg(root, Path(td))
        p=pkg/'Candidate-Ledger-current.json'
        materialize(p)
        data=read_json(p)
        data[0]['name']=data[0].get('name','')+' [SELFTEST MIRROR BREAK]'
        p.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        cp=run_py(pkg,'tools/csv_json_mirror_audit.py','--write-report')
        highs=high_rows(pkg/'META/CSV-JSON-Mirror-Audit-current.json')
        ok=any(r.get('check')=='cell_value_mismatch' for r in highs)
        add(rows,'selftest_002','tools/csv_json_mirror_audit.py','mutate Candidate-Ledger JSON mirror cell','high cell_value_mismatch finding',f'returncode={cp.returncode}; high={len(highs)}',ok,'CSV/JSON mirror drift must be caught')


def selftest_revision(root: Path, rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory() as td:
        pkg=copy_pkg(root, Path(td))
        manifest=read_json(pkg/'manifest.json') or {}
        cur=manifest.get('revision','rev9999')
        p=pkg/'000-START-HERE.txt'
        materialize(p)
        text=p.read_text(encoding='utf-8')
        if f'Current revision: {cur}' in text:
            text=text.replace(f'Current revision: {cur}', 'Current revision: rev0000', 1)
        elif cur in text:
            # Prefer mutating an actual header/current-revision pattern; otherwise add one.
            text=text.replace(cur,'rev0000',1)
            text='Current revision: rev0000\n'+text
        else:
            text='Current revision: rev0000\n'+text
        p.write_text(text, encoding='utf-8')
        cp=run_py(pkg,'tools/revision_surface_audit.py','--write-report')
        highs=high_rows(pkg/'META/Revision-Surface-Audit-current.json')
        ok=any(r.get('check')=='frontdoor_header_revision_current' for r in highs)
        add(rows,'selftest_003','tools/revision_surface_audit.py','stale front-door revision string','high frontdoor_header_revision_current finding',f'returncode={cp.returncode}; high={len(highs)}',ok,'stale opening revision metadata must be caught')


def selftest_path(root: Path, rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory() as td:
        pkg=copy_pkg(root, Path(td))
        p=pkg/'CURRENT-SPINE.md'
        materialize(p)
        p.write_text(p.read_text(encoding='utf-8')+'\nSelf-test broken path: `SCHEMA/DOES-NOT-EXIST-current.csv`\n', encoding='utf-8')
        cp=run_py(pkg,'tools/path_reference_audit.py','--write-report')
        highs=high_rows(pkg/'META/Path-Reference-Audit-current.json')
        ok=any(r.get('check')=='path_reference_missing' and 'DOES-NOT-EXIST' in r.get('reference','') for r in highs)
        add(rows,'selftest_004','tools/path_reference_audit.py','append missing package path reference','high path_reference_missing finding',f'returncode={cp.returncode}; high={len(highs)}',ok,'missing package-relative paths must be caught')


def selftest_row_validation(root: Path, rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory() as td:
        pkg=copy_pkg(root, Path(td))
        p=pkg/'Candidate-Ledger-current.csv'
        materialize(p)
        with p.open(encoding='utf-8', newline='') as f:
            csv_rows=list(csv.DictReader(f))
            fields=list(csv_rows[0].keys())
        csv_rows[0]['candidate_id']=''
        with p.open('w', encoding='utf-8', newline='') as f:
            w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(csv_rows)
        cp=run_py(pkg,'tools/row_validate.py','--write-report')
        highs=high_rows(pkg/'SCHEMA/Row-Validation-Report-current.json')
        ok=any(r.get('check') in {'row_required_nonempty','required_nonempty','unique_field'} and r.get('field')=='candidate_id' for r in highs)
        add(rows,'selftest_005','tools/row_validate.py','blank required Candidate-Ledger candidate_id','high candidate_id required/unique finding',f'returncode={cp.returncode}; high={len(highs)}',ok,'row-level contract violations must be caught')


def selftest_public_contract(root: Path, rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory() as td:
        pkg=copy_pkg(root, Path(td))
        (pkg/'PUBLIC/UNALLOWED-SELFTEST.txt').write_text('selftest', encoding='utf-8')
        cp=run_py(pkg,'tools/public_contract_check.py','--json')
        observed='returncode='+str(cp.returncode)
        ok=cp.returncode != 0 and 'public_layer_extra_files' in (cp.stdout+cp.stderr)
        add(rows,'selftest_006','tools/public_contract_check.py','add unallowlisted PUBLIC file','nonzero exit and public_layer_extra_files finding',observed,ok,'PUBLIC/ allowlist drift must be caught')


def selftest_public_index_semantics(root: Path, rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory() as td:
        pkg=copy_pkg(root, Path(td))
        p=pkg/'PUBLIC/Candidate-Index-public.csv'
        materialize(p)
        with p.open(encoding='utf-8', newline='') as f:
            csv_rows=list(csv.DictReader(f))
            fields=list(csv_rows[0].keys())
        for row in csv_rows:
            if row.get('candidate_id') == 'cand_abuelas_de_plaza_de_mayo_identity_restitution':
                row['public_shape_template']='mmiwg_family_led_boundary'
                row['location']='Canada; translocal Indigenous-led family/search witness context; no event, contact, case, route, or support geography released'
                row['office']='Indigenous-led search, remembrance, and accountability witness; boundary-only public shape'
                row['public_use_note']='MMIWG2S+/family-governed boundary shape only; not a case list, vigil/event map, contact/support path, family-story reuse, red-dress image reuse, testimony fragment, pathway map, public URL release, or implementation-completion claim.'
                break
        with p.open('w', encoding='utf-8', newline='') as f:
            w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(csv_rows)
        cp=run_py(pkg,'tools/public_index_semantic_audit.py','--write-report')
        highs=high_rows(pkg/'META/Public-Index-Semantic-Audit-current.json')
        ok=any(r.get('candidate_id')=='cand_abuelas_de_plaza_de_mayo_identity_restitution' and r.get('check') in {'critical_template_rendered','critical_location_forbidden','critical_note_forbidden','non_mmiwg_forbidden_language'} for r in highs)
        add(rows,'selftest_007','tools/public_index_semantic_audit.py','mutate Abuelas public row to inherited MMIWG/Canada template','high public-index semantic finding for Abuelas',f'returncode={cp.returncode}; high={len(highs)}',ok,'public index cross-template semantic drift must be caught')



def selftest_public_template_overreach(root: Path, rows: list[dict]) -> None:
    with tempfile.TemporaryDirectory() as td:
        pkg=copy_pkg(root, Path(td))
        p=pkg/'PUBLIC/Candidate-Index-public.csv'
        materialize(p)
        with p.open(encoding='utf-8', newline='') as f:
            csv_rows=list(csv.DictReader(f))
            fields=list(csv_rows[0].keys())
        mutated=''
        for row in csv_rows:
            if row.get('candidate_id') not in {
                'cand_bridget_tolley_fsis_mmiwg_canada',
                'cand_abuelas_de_plaza_de_mayo_identity_restitution',
                'cand_las_patronas_veracruz_migrant_train_food_water',
                'cand_eaaf_forensic_return_of_names_and_remains',
                'cand_mothers_srebrenica_zepa_truth_justice_remembrance',
            }:
                mutated=row.get('candidate_id','')
                row['public_shape_template']='forensic_return_no_case_dna'
                row['location']='Argentina and international human-rights forensic context; selftest overreach'
                row['office']='Forensic return of names/remains and family/court/community search witness; selftest overreach'
                break
        with p.open('w', encoding='utf-8', newline='') as f:
            w=csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(csv_rows)
        cp=run_py(pkg,'tools/public_index_semantic_audit.py','--write-report')
        highs=high_rows(pkg/'META/Public-Index-Semantic-Audit-current.json')
        ok=any(r.get('candidate_id')==mutated and r.get('check')=='exclusive_template_candidate_scope' for r in highs)
        add(rows,'selftest_008','tools/public_index_semantic_audit.py','mutate non-critical candidate to EAAF forensic template','high exclusive_template_candidate_scope finding',f'returncode={cp.returncode}; high={len(highs)}; mutated={mutated}',ok,'domain-specific public templates must not be assigned by broad keyword overreach')

def run(root: Path) -> list[dict]:
    rows=[]
    for fn in [selftest_public_lint,selftest_mirror,selftest_revision,selftest_path,selftest_row_validation,selftest_public_contract,selftest_public_index_semantics,selftest_public_template_overreach]:
        try:
            fn(root, rows)
        except Exception as e:
            add(rows, f'selftest_{len(rows)+1:03d}', 'unknown', fn.__name__, 'controlled mutation should be detected', 'exception', False, repr(e))
    return rows


def write_reports(root: Path, rows: list[dict]) -> None:
    out=root/'META'; out.mkdir(exist_ok=True)
    with (out/'Audit-Selftest-current.csv').open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows([{k:r.get(k,'') for k in FIELDS} for r in rows])
    (out/'Audit-Selftest-current.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    bad=[r for r in rows if r.get('status')!='pass']
    lines=['# Audit Selftest — current','', 'Generated by `tools/audit_selftest.py`.', '', f'Selftests: {len(rows)}', f'Failed selftests: {len(bad)}', '', 'This report uses temporary copies with controlled mutations. It proves selected auditors still fail when public-safety, mirror, revision, path, row-contract, public-contract, and public semantic-template defects and domain-template overreach are injected.', '', '| selftest_id | target_tool | status | expected_failure_signal | observed_failure_signal |', '|---|---|---|---|---|']
    for r in rows:
        lines.append(f"| {r['selftest_id']} | `{r['target_tool']}` | {r['status']} | {r['expected_failure_signal']} | {r['observed_failure_signal']} |")
    (out/'Audit-Selftest-current.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('root', nargs='?', default='.'); ap.add_argument('--write-report', action='store_true'); ap.add_argument('--fail-on-fail', action='store_true')
    args=ap.parse_args(); root=Path(args.root).resolve(); rows=run(root)
    if args.write_report: write_reports(root, rows)
    bad=[r for r in rows if r.get('status')!='pass']
    print(f"{'FAIL' if bad else 'PASS'} audit selftest cases={len(rows)} failed={len(bad)}")
    for r in rows: print(f"{r['status'].upper()} {r['selftest_id']} {r['target_tool']}: {r['observed_failure_signal']}")
    if args.fail_on_fail and bad: sys.exit(1)
if __name__=='__main__': main()
