#!/usr/bin/env python3
"""Compile/verify auxiliary non-paper TeX surfaces."""
from __future__ import annotations
import argparse, hashlib, json, os, pathlib, re, shutil, signal, subprocess, sys, tempfile, time
from typing import Any

from live_compile_lock import LiveCompileLockTimeout, live_compile_lock
from tex_compile_receipts import (
    DEFAULT_SOURCE_DATE_EPOCH,
    LOG_NORMALIZATION_POLICY,
    PDF_NORMALIZATION_POLICY,
    RECEIPT_POLICY_VERSION,
    attach_compile_receipts,
    deterministic_compile_env,
    digest_receipt_failures,
    digest_receipt_missing_count,
    pdflatex_receipt_command,
    reproducible_receipt_failures,
    reproducible_receipt_missing_count,
    stable_pdf_trailer_id,
)

MIN_PASSES=3
UNRESOLVED_RE=re.compile(r"(?:LaTeX Warning: (?:Citation|Reference).*undefined|LaTeX Warning: There were undefined (?:references|citations)|Citation .* undefined|Reference .* undefined)",re.I)
RERUN_RE=re.compile(r"(?:Rerun to get cross-references right|Label\(s\) may have changed|Package rerunfilecheck Warning: File .* has changed|Rerun to get outlines right)",re.I)
NOTICE_RE=re.compile(r"(?:LaTeX|Package|Class|pdfTeX) .*?(?:Warning|Info|warning)",re.I)
OVER_RE=re.compile(r"Overfull \\hbox",re.I); UNDER_RE=re.compile(r"Underfull \\hbox",re.I)
FATALS=("! LaTeX Error:","! Emergency stop.","Fatal error occurred"," ==> Fatal error occurred")


def pdflatex_fingerprint() -> dict[str, str | bool]:
    path = shutil.which("pdflatex") or ""
    version = ""
    if path:
        try:
            proc = subprocess.run(["pdflatex", "--version"], text=True, capture_output=True, timeout=5)
            version = proc.stdout if proc.stdout else proc.stderr
        except Exception:
            version = ""
    return {
        "pdflatex_path": path,
        "pdflatex_version_line": version.splitlines()[0][:200] if version.splitlines() else "",
        "pdflatex_version_output_sha256": hashlib.sha256(version.encode("utf-8", errors="replace")).hexdigest() if version else "",
        "toolchain_available": bool(path),
    }

def load_json(p:pathlib.Path)->Any: return json.loads(p.read_text(encoding='utf-8'))
def sha_file(p:pathlib.Path)->str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def sha_bytes(b:bytes)->str: return hashlib.sha256(b).hexdigest()

def sources(root:pathlib.Path)->list[dict[str,str]]:
    """Return all *.tex minus series/**/paper.tex and published/**/paper.tex."""
    rows=[]
    for p in sorted(root.rglob('*.tex'), key=lambda q:q.relative_to(root).as_posix()):
        rel=p.relative_to(root).as_posix()
        if rel.startswith('series/') and rel.endswith('/paper.tex'): continue
        if rel.startswith('published/') and rel.endswith('/paper.tex'): continue
        if rel=='index/SERIES_INDEX.tex': role,title='series_index_auxiliary_source','Series Index auxiliary TeX source'
        elif rel.startswith('release_queue/freeze_packets/') and rel.endswith('/FROZEN_SOURCE.tex'): role,title='freeze_packet_frozen_source_copy','Frozen release-packet source copy'
        else: role,title='auxiliary_nonpaper_tex_source','Auxiliary non-paper TeX source'
        rows.append({'path':rel,'role':role,'title':title})
    return rows

def counts(text:str)->dict[str,int]:
    return {'latex_notice_lines':sum(1 for line in text.splitlines() if NOTICE_RE.search(line)), 'overfull_hbox':len(OVER_RE.findall(text)), 'underfull_hbox':len(UNDER_RE.findall(text)), 'unresolved_warning_hits':len(UNRESOLVED_RE.findall(text)), 'rerun_warning_hits':len(RERUN_RE.findall(text)), 'fatal_pattern_hits':sum(text.count(p) for p in FATALS)}

def run_one(root:pathlib.Path, source:str, outdir:pathlib.Path, log_path:pathlib.Path, timeout:int, label:str, *, draft_mode:bool=False)->int:
    source_path=root/source
    source_sha256=sha_file(source_path) if source_path.is_file() else ''
    cmd=pdflatex_receipt_command('pdflatex', source, outdir, source_sha256=source_sha256, draft_mode=draft_mode)
    env=deterministic_compile_env(os.environ.copy()); env['TZ']='UTC'
    start=time.monotonic(); deadline=start+max(1,timeout); last=start; beat=max(5,min(15,timeout//2 if timeout>1 else 1))
    with log_path.open('w',encoding='utf-8',errors='replace') as log:
        try: proc=subprocess.Popen(cmd,cwd=root,stdout=log,stderr=subprocess.STDOUT,text=True,env=env,start_new_session=True)
        except FileNotFoundError: log.write('pdflatex not found on PATH\n'); return 127
        while True:
            rc=proc.poll(); now=time.monotonic()
            if rc is not None: return rc
            if now>=deadline:
                print(f'auxiliary-tex-compile-triage timeout: {label}',file=sys.stderr,flush=True)
                try: os.killpg(proc.pid,signal.SIGTERM)
                except Exception: proc.terminate()
                try: rc=proc.wait(timeout=5); return 124 if rc in {-15,-9,143} else rc
                except subprocess.TimeoutExpired:
                    try: os.killpg(proc.pid,signal.SIGKILL)
                    except Exception: proc.kill()
                    proc.wait(timeout=5); return 124
            if now-last>=beat:
                print(f'auxiliary-tex-compile-triage heartbeat: {label} running {int(now-start)}s',file=sys.stderr,flush=True); last=now
            time.sleep(0.25)

def compile_source(root:pathlib.Path, src:dict[str,str], index:int, tmp:pathlib.Path, passes:int, timeout:int)->dict[str,Any]:
    rel=src['path']; out=tmp/'out'/str(index); logs=tmp/'logs'; out.mkdir(parents=True,exist_ok=True); logs.mkdir(parents=True,exist_ok=True)
    parts=[]; final=''; completed=0; rc=0; started=time.monotonic()
    for pno in range(1,passes+1):
        label=f'target {index} pass {pno}/{passes} {rel}'; print(f'auxiliary-tex-compile-triage start: {label}',file=sys.stderr,flush=True)
        lp=logs/f'{index}.pass{pno}.log'; rc=run_one(root,rel,out,lp,timeout,label,draft_mode=(pno<passes)); final=lp.read_text(encoding='utf-8',errors='replace') if lp.exists() else ''
        parts.append(f'=== pdflatex pass {pno}/{passes} rc={rc} ===\n{final}\n')
        if rc!=0: break
        completed=pno
    combined=''.join(parts); ac=counts(combined); fc=counts(final); pdf=out/pathlib.Path(rel).with_suffix('.pdf').name; pdf_ok=pdf.exists() and pdf.stat().st_size>0
    status,cat,err='pass','',''
    if rc!=0: status,cat,err='fail',('pdflatex_timeout' if rc==124 else 'pdflatex_failed'),f'pdflatex returned {rc}'
    elif completed<MIN_PASSES: status,cat,err='fail','pdflatex_pass_count_shortfall',f'completed {completed} passes'
    elif not pdf_ok: status,cat,err='fail','pdf_output_missing',f'{pdf.name} was not produced'
    elif fc['unresolved_warning_hits'] or fc['rerun_warning_hits']: status,cat,err='fail','final_warning_debt',f"final unresolved={fc['unresolved_warning_hits']} rerun={fc['rerun_warning_hits']}"
    row={'index':index,'path':rel,'role':src.get('role',''),'title':src.get('title',''),'status':status,'failure_category':cat,'error':err,'returncode':rc,'seconds':round(time.monotonic()-started,3),'passes_completed':completed,'passes_requested':passes,'source_sha256':sha_file(root/rel) if (root/rel).exists() else '', 'pdf_output_created':pdf_ok,'pdf_output_bytes':pdf.stat().st_size if pdf.exists() else 0,'pdf_sha256':'', 'combined_log_bytes':0,'combined_log_sha256':'','final_log_bytes':0,'final_log_sha256':'','log_excerpt':('\n'.join(final.splitlines()[-30:]) if status!='pass' else '')}
    row.update(ac)
    for k,v in fc.items(): row[f'final_{k}']=v
    attach_compile_receipts(row, pdf_path=pdf, combined_log_text=combined, final_log_text=final, log_normalization_paths=[tmp, root], source_date_epoch=DEFAULT_SOURCE_DATE_EPOCH, pdf_trailer_id=stable_pdf_trailer_id(rel, row.get('source_sha256','')))
    if row['status']=='pass' and digest_receipt_failures(row):
        row['status']='fail'; row['failure_category']='compile_digest_receipt_missing'; row['error']='PDF/log digest receipt fields are missing or malformed'
    if row['status']=='pass' and reproducible_receipt_failures(row):
        row['status']='fail'; row['failure_category']='compile_reproducible_receipt_missing'; row['error']='deterministic normalized PDF/log receipt fields are missing or malformed'
    return row

def rint(row:dict[str,Any], key:str)->int:
    try: return int(row.get(key,0) or 0)
    except Exception: return 0

def make_summary(rows:list[dict[str,Any]], total:int, passes:int)->dict[str,Any]:
    failed=[r for r in rows if r.get('status')!='pass']
    return {'checks_failed':0,'target_count_total':total,'targets_checked':len(rows),'targets_passed':len(rows)-len(failed),'targets_failed':len(failed),'passes_requested_per_target':passes,'minimum_required_passes':MIN_PASSES,'targets_with_short_pass_count':sum(1 for r in rows if rint(r,'passes_completed')<MIN_PASSES),'latex_notice_lines_total':sum(rint(r,'latex_notice_lines') for r in rows),'overfull_hbox_total':sum(rint(r,'overfull_hbox') for r in rows),'overfull_hbox_max_per_target':max([rint(r,'overfull_hbox') for r in rows] or [0]),'underfull_hbox_total':sum(rint(r,'underfull_hbox') for r in rows),'underfull_hbox_max_per_target':max([rint(r,'underfull_hbox') for r in rows] or [0]),'unresolved_warning_hits_total':sum(rint(r,'unresolved_warning_hits') for r in rows),'rerun_warning_hits_total':sum(rint(r,'rerun_warning_hits') for r in rows),'fatal_pattern_hits_total':sum(rint(r,'fatal_pattern_hits') for r in rows),'final_latex_notice_lines_total':sum(rint(r,'final_latex_notice_lines') for r in rows),'final_overfull_hbox_total':sum(rint(r,'final_overfull_hbox') for r in rows),'final_overfull_hbox_max_per_target':max([rint(r,'final_overfull_hbox') for r in rows] or [0]),'final_underfull_hbox_total':sum(rint(r,'final_underfull_hbox') for r in rows),'final_underfull_hbox_max_per_target':max([rint(r,'final_underfull_hbox') for r in rows] or [0]),'final_unresolved_warning_hits_total':sum(rint(r,'final_unresolved_warning_hits') for r in rows),'final_rerun_warning_hits_total':sum(rint(r,'final_rerun_warning_hits') for r in rows),'pdf_output_created_count':sum(1 for r in rows if r.get('pdf_output_created') is True and rint(r,'pdf_output_bytes')>0),'digest_receipt_count':sum(1 for r in rows if not digest_receipt_failures(r)),'digest_receipt_missing_count':digest_receipt_missing_count(rows),'reproducible_receipt_count':sum(1 for r in rows if not reproducible_receipt_failures(r)),'reproducible_receipt_missing_count':reproducible_receipt_missing_count(rows),'digest_receipts_required':True,'reproducible_receipts_required':True,'compile_receipt_policy':RECEIPT_POLICY_VERSION,'source_date_epoch':DEFAULT_SOURCE_DATE_EPOCH,'pdf_normalization_policy':PDF_NORMALIZATION_POLICY,'log_normalization_policy':LOG_NORMALIZATION_POLICY,'publication_authorized':False}

def build_report(root:pathlib.Path, rows:list[dict[str,Any]], partial:bool, start_index:int, max_targets:int, passes:int, timeout:int)->dict[str,Any]:
    relm=load_json(root/'RELEASE_MANIFEST.json'); expected=sources(root); paths=[r['path'] for r in expected]; expected_by={r['path']:r for r in expected}; by={str(r.get('path')):r for r in rows}
    # A merged carry-forward can lose an auxiliary target when a stale freeze packet is
    # retired. Rebind each surviving row to the current ordered universe; preserving an
    # old ordinal would make a semantically current receipt fail for bookkeeping drift.
    ordered=[]
    for index,path in enumerate(paths,1):
        if path not in by: continue
        row=dict(by[path]); meta=expected_by[path]
        row['index']=index; row['role']=meta['role']; row['title']=meta['title']
        ordered.append(row)
    summ=make_summary(ordered,len(paths),passes); roles={}
    for r in expected: roles[r['role']]=roles.get(r['role'],0)+1
    fails=len([r for r in ordered if r.get('status')!='pass'])
    if len(ordered)!=len(paths) or [r.get('path') for r in ordered]!=paths: fails+=1
    if summ['targets_with_short_pass_count']: fails+=1
    if summ['final_unresolved_warning_hits_total'] or summ['final_rerun_warning_hits_total']: fails+=1
    if summ['pdf_output_created_count']!=len(ordered): fails+=1
    if summ['digest_receipt_missing_count']!=0 or summ['reproducible_receipt_missing_count']!=0: fails+=1
    summ['checks_failed']=fails
    return {'status':'partial' if partial else ('pass' if fails==0 else 'fail'),'generated_for_revision':relm['revision'],'checked_bundle':relm['bundle'],'publication_authorized':False,'report_kind':'auxiliary_tex_compile_triage','partial':partial,'scope':{'source_rule':'all *.tex minus series/**/paper.tex and published/**/paper.tex','target_count_total':len(paths),'target_paths_total':paths,'role_counts':roles,'start_index':start_index,'max_targets':max_targets},'command_family':r'pdflatex -no-shell-escape -interaction=nonstopmode -halt-on-error -file-line-error -jobname <basename> -output-directory <tmpdir> \pdftrailerid{<stable><stable>}\input{<auxiliary_tex>}','toolchain':{'latex_command':'pdflatex',**pdflatex_fingerprint(),'timeout_seconds_per_pass':timeout,'semantic_limit':'bounded three-pass compile triage for non-paper TeX sources; not a publication authorization'},'summary':summ,'failures':[{k:r.get(k,'') for k in ('path','failure_category','error','returncode','log_excerpt')} for r in ordered if r.get('status')!='pass'],'results':ordered,'fail_closed_rule':'Auxiliary TeX compile triage does not authorize publication. If an uncovered TeX source is stale, non-compiling, short-pass, PDF-missing, or final-warning-bearing, repair source build hygiene before trusting auxiliary TeX surfaces.'}

def _live_unlocked(root:pathlib.Path, start:int, max_targets:int, passes:int, timeout:int)->dict[str,Any]:
    allsrc=sources(root); tmp=pathlib.Path(tempfile.mkdtemp(prefix='anonymity_auxiliary_tex_compile_triage.')); keep=os.getenv('KEEP_AUXILIARY_TEX_COMPILE_TMP')
    try:
        pairs=[(i,r) for i,r in enumerate(allsrc,1) if i>=start]
        if max_targets>0: pairs=pairs[:max_targets]
        rows=[compile_source(root,r,i,tmp,passes,timeout) for i,r in pairs]
        partial=not (start==1 and (max_targets==0 or max_targets>=len(allsrc)))
        return build_report(root,rows,partial,start,max_targets,passes,timeout)
    finally:
        if keep: print(f'auxiliary TeX compile triage tmp retained: {tmp}',file=sys.stderr)
        else: shutil.rmtree(tmp,ignore_errors=True)


def live(root:pathlib.Path, start:int, max_targets:int, passes:int, timeout:int)->dict[str,Any]:
    try:
        with live_compile_lock(root, "auxiliary_tex_compile_triage"):
            return _live_unlocked(root,start,max_targets,passes,timeout)
    except LiveCompileLockTimeout as exc:
        relm=load_json(root/'RELEASE_MANIFEST.json')
        return {'status':'fail','generated_for_revision':relm['revision'],'checked_bundle':relm['bundle'],'publication_authorized':False,'report_kind':'auxiliary_tex_compile_triage','failure_category':'live_compile_lock_busy','summary':{'checks_failed':1,'publication_authorized':False},'failures':[{'category':'live_compile_lock_busy','detail':str(exc)}],'results':[],'fail_closed_rule':'If another live compile refresh is already running, stop instead of overlapping TeX processes.'}


def merge(root:pathlib.Path, parts:list[pathlib.Path], passes:int, timeout:int)->dict[str,Any]:
    rows=[]; seen=set()
    for p in parts:
        rep=load_json(p)
        if rep.get('report_kind')!='auxiliary_tex_compile_triage': raise SystemExit(f'not an auxiliary TeX compile triage report: {p}')
        for row in rep.get('results',[]):
            path=str(row.get('path',''))
            if path in seen: raise SystemExit(f'duplicate auxiliary TeX compile triage path {path}')
            seen.add(path); rows.append(row)
    return build_report(root,rows,False,1,0,passes,timeout)

def verify(root:pathlib.Path, report_path:pathlib.Path)->dict[str,Any]:
    relm=load_json(root/'RELEASE_MANIFEST.json'); expected=sources(root); paths=[r['path'] for r in expected]; roles={r['path']:r['role'] for r in expected}; rep=load_json(report_path) if report_path.exists() else {}; rows=rep.get('results',[]) if isinstance(rep.get('results'),list) else []; row_paths=[str(r.get('path','')) for r in rows if isinstance(r,dict)]; fails=[]
    if not rep: fails.append({'category':'stored_report_missing','path':report_path.as_posix()})
    if rep.get('status')!='pass': fails.append({'category':'stored_report_not_passing','status':rep.get('status')})
    if rep.get('partial'): fails.append({'category':'stored_report_is_partial'})
    if rep.get('generated_for_revision')!=relm['revision']: fails.append({'category':'stored_report_revision_mismatch','expected':relm['revision'],'actual':rep.get('generated_for_revision')})
    if rep.get('checked_bundle')!=relm['bundle']: fails.append({'category':'stored_report_bundle_mismatch','expected':relm['bundle'],'actual':rep.get('checked_bundle')})
    if rep.get('publication_authorized') is not False or rep.get('summary',{}).get('publication_authorized') is not False: fails.append({'category':'stored_report_authorizes_publication'})
    if '-no-shell-escape' not in str(rep.get('command_family','')): fails.append({'category':'stored_report_missing_no_shell_escape_command_family'})
    if not rep.get('toolchain',{}).get('toolchain_available'): fails.append({'category':'stored_report_missing_toolchain_availability'})
    dups=sorted({p for p in row_paths if row_paths.count(p)>1})
    if dups: fails.append({'category':'stored_report_duplicate_paths','paths':dups})
    if row_paths!=paths: fails.append({'category':'stored_report_path_scope_mismatch','expected_count':len(paths),'actual_count':len(row_paths),'missing':sorted(set(paths)-set(row_paths)),'extra':sorted(set(row_paths)-set(paths))})
    stale=[]; nonpass=[]; short=[]; shortreq=[]; warn=[]; fatal=[]; pdfmiss=[]; rolemis=[]; idxmis=[]; digest=[]; reproducible=[]
    for i,row in enumerate(rows,1):
        if not isinstance(row,dict): fails.append({'category':'stored_report_row_not_object','index':i}); continue
        path=str(row.get('path',''))
        if path not in roles: continue
        if row.get('role')!=roles[path]: rolemis.append({'path':path,'expected':roles[path],'actual':str(row.get('role',''))})
        try: actual=int(row.get('index',-1))
        except Exception: actual=-1
        if actual!=i: idxmis.append({'path':path,'expected':i,'actual':actual})
        if not (root/path).exists() or row.get('source_sha256')!=sha_file(root/path): stale.append(path)
        if row.get('status')!='pass': nonpass.append(path)
        if rint(row,'passes_completed')<MIN_PASSES: short.append(path)
        if rint(row,'passes_requested')<MIN_PASSES: shortreq.append(path)
        if rint(row,'final_unresolved_warning_hits') or rint(row,'final_rerun_warning_hits'): warn.append(path)
        if rint(row,'fatal_pattern_hits'): fatal.append(path)
        if row.get('pdf_output_created') is not True or rint(row,'pdf_output_bytes')<=0: pdfmiss.append(path)
        if digest_receipt_failures(row): digest.append(path)
        if reproducible_receipt_failures(row): reproducible.append(path)
    expected_summary=make_summary([r for r in rows if isinstance(r,dict)],len(paths),rint(rep.get('summary',{}),'passes_requested_per_target') or MIN_PASSES); stored=rep.get('summary',{}) if isinstance(rep.get('summary'),dict) else {}
    for k,v in expected_summary.items():
        if stored.get(k)!=v: fails.append({'category':'stored_report_summary_metric_mismatch','metric':k,'expected':v,'actual':stored.get(k)})
    for cat,vals in [('stored_report_source_hash_mismatches',stale),('stored_report_nonpassing_rows',nonpass),('stored_report_short_pass_rows',short),('stored_report_short_requested_pass_rows',shortreq),('stored_report_final_warning_debt',warn),('stored_report_fatal_pattern_debt',fatal),('stored_report_pdf_output_evidence_missing',pdfmiss),('stored_report_role_mismatches',rolemis),('stored_report_row_index_mismatches',idxmis),('stored_report_digest_receipt_missing',digest),('stored_report_reproducible_receipt_missing',reproducible)]:
        if vals: fails.append({'category':cat,'count':len(vals),'rows':vals[:25]})
    return {'status':'pass' if not fails else 'fail','generated_for_revision':relm['revision'],'checked_bundle':relm['bundle'],'publication_authorized':False,'checked_report':report_path.relative_to(root).as_posix() if report_path.is_absolute() and root in report_path.parents else report_path.as_posix(),'failures':fails,'summary':{'checks_failed':len(fails),'target_count':len(paths),'stored_result_count':len(rows),'duplicate_path_count':len(dups),'stale_hash_count':len(stale),'nonpassing_row_count':len(nonpass),'short_pass_row_count':len(short),'short_requested_pass_row_count':len(shortreq),'role_mismatch_count':len(rolemis),'row_index_mismatch_count':len(idxmis),'final_warning_debt_count':len(warn),'fatal_pattern_debt_count':len(fatal),'pdf_output_evidence_missing_count':len(pdfmiss),'digest_receipt_missing_count':len(digest),'reproducible_receipt_missing_count':len(reproducible),'publication_authorized':False},'fail_closed_rule':'If auxiliary TeX compile triage evidence is partial, stale, warning-debt-bearing, summary-inconsistent, PDF-output-missing, digest-missing, role-divergent, or authorizing, treat auxiliary TeX build hygiene as untrusted until repaired.'}

def render_md(rep:dict[str,Any])->str:
    s=rep.get('summary',{}) if isinstance(rep.get('summary'),dict) else {}; lines=['# Auxiliary TeX Compile Triage','',f"Generated for revision: `{rep.get('generated_for_revision')}`",f"Checked bundle: `{rep.get('checked_bundle')}`",'Publication authorized: false','','This is build-rot triage for non-paper TeX sources outside the series/published paper compile partitions. It does not authorize publication.','','## Summary','',f"- Status: **{rep.get('status')}**",f"- Targets checked: {s.get('targets_checked')} / {s.get('target_count_total')}",f"- Passed: {s.get('targets_passed')}",f"- Failed: {s.get('targets_failed')}",f"- Final unresolved/rerun warning debt: {s.get('final_unresolved_warning_hits_total')} / {s.get('final_rerun_warning_hits_total')}",f"- Final overfull/underfull hbox telemetry: {s.get('final_overfull_hbox_total')} / {s.get('final_underfull_hbox_total')}",f"- Aggregate overfull/underfull hbox telemetry: {s.get('overfull_hbox_total')} / {s.get('underfull_hbox_total')}",f"- PDF outputs recorded: {s.get('pdf_output_created_count')}",f"- Normalized deterministic receipts present: {s.get('reproducible_receipt_count')}",f"- Normalized deterministic receipts missing: {s.get('reproducible_receipt_missing_count')}",'- Publication authorized: false','','## Results','','| # | Role | Source | Status | Passes | Final warnings | Final hbox | PDF SHA-256 |','|---:|---|---|---|---:|---:|---:|---|']
    for r in rep.get('results',[]):
        if isinstance(r,dict):
            h=str(r.get('pdf_sha256','')); lines.append(f"| {r.get('index')} | {r.get('role')} | `{r.get('path')}` | {r.get('status')} | {r.get('passes_completed')}/{r.get('passes_requested')} | {r.get('final_unresolved_warning_hits')}/{r.get('final_rerun_warning_hits')} | {r.get('final_overfull_hbox')}/{r.get('final_underfull_hbox')} | `{h[:16]}…` |")
    return '\n'.join(lines)+'\n'


def safe_stdout_write(text: str) -> None:
    try:
        sys.stdout.write(text)
    except (BrokenPipeError, BlockingIOError):
        try:
            sys.stdout.close()
        except Exception:
            pass


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='.'); ap.add_argument('--report-path',default='index/AUXILIARY_TEX_COMPILE_TRIAGE.json'); ap.add_argument('--write-report',default=''); ap.add_argument('--write-md',default=''); ap.add_argument('--run-live',action='store_true'); ap.add_argument('--merge-parts',nargs='*',default=[]); ap.add_argument('--start-index',type=int,default=1); ap.add_argument('--max-targets',type=int,default=0); ap.add_argument('--passes',type=int,default=MIN_PASSES); ap.add_argument('--timeout-seconds',type=int,default=30); args=ap.parse_args(); root=pathlib.Path(args.root).resolve()
    if args.run_live and args.merge_parts: raise SystemExit('choose either --run-live or --merge-parts, not both')
    rep=live(root,args.start_index,args.max_targets,args.passes,args.timeout_seconds) if args.run_live else (merge(root,[pathlib.Path(p) if pathlib.Path(p).is_absolute() else root/p for p in args.merge_parts],args.passes,args.timeout_seconds) if args.merge_parts else verify(root,root/args.report_path))
    text=json.dumps(rep,indent=2)+'\n'
    if args.write_report:
        out=pathlib.Path(args.write_report); out=out if out.is_absolute() else root/out; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text,encoding='utf-8')
    if args.write_md:
        out=pathlib.Path(args.write_md); out=out if out.is_absolute() else root/out; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(render_md(rep),encoding='utf-8')
    safe_stdout_write(text); return 0 if rep.get('status')=='pass' else (0 if args.run_live and rep.get('status')=='partial' else 1)
if __name__=='__main__': raise SystemExit(main())
