#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, tempfile, warnings
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from zipfile import ZIP_BZIP2, ZIP_STORED, ZipFile, ZipInfo
ROOT=Path(__file__).resolve().parents[1]; REVISION='rev0108'; PREFIX='REV0108'; VERSION='0.0.108'
STAMP='2026.06.17.03.10'; SLUG='archive-evidence-verifier-fixture'; ARCHIVE_NAME=f'BrowserRT-{REVISION}-{STAMP}-{SLUG}.zip'; DT=(2026,6,17,3,10,0)
spec=importlib.util.spec_from_file_location('browserrt_verify_release',ROOT/'tools'/'verify_release.py'); verify_release=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(verify_release)
def h(b): return hashlib.sha256(b).hexdigest()
def j(v): return (json.dumps(v,separators=(',',':'),sort_keys=True)+'\n').encode()
def zi(n):
    z=ZipInfo(n); z.date_time=DT; z.compress_type=ZIP_STORED; z.external_attr=0o100644<<16; z.create_system=3; return z
PATHS={
 'support-bundle-proof-artifact':f'artifacts/validation/{PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-PROBE.json',
 'support-bundle-audit-artifact':f'artifacts/audit/{PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-CONTRACT-AUDIT.json',
 'support-bundle-import-artifact':f'artifacts/validation/{PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-IMPORT-PROBE.json',
 'readiness-gate-artifact':f'artifacts/validation/{PREFIX}-KERNEL-KIT-READINESS-GATE-PROBE.json',
 'browser-kernel-kit-artifact':f'artifacts/validation/{PREFIX}-BROWSER-KERNEL-KIT-DEMO-PROBE.json',
 'browser-session-coordination-artifact':f'artifacts/validation/{PREFIX}-BROWSER-KERNEL-KIT-SESSION-COORDINATION-CHECKPOINT-PROBE.json',
 'browser-recovery-artifact':f'artifacts/validation/{PREFIX}-BROWSER-KERNEL-KIT-RECOVERY-CHECKPOINT-PROBE.json'}
def payloads():
    return {
    'support-bundle-proof-artifact':{'project':'BrowserRT','revision':REVISION,'version':VERSION,'status':'passed','probe_id':f'{REVISION}-kernel-kit-support-bundle-probe','supportBundle':{'revision':REVISION,'evidenceLedger':{'revision':REVISION}}},
    'support-bundle-audit-artifact':{'project':'BrowserRT','revision':REVISION,'version':VERSION,'status':'passed','audit_id':f'{REVISION}-kernel-kit-support-bundle-contract-audit'},
    'support-bundle-import-artifact':{'project':'BrowserRT','revision':REVISION,'version':VERSION,'status':'passed','probe_id':f'{REVISION}-kernel-kit-support-bundle-import-probe','sourceProbeId':f'{REVISION}-kernel-kit-support-bundle-probe','reports':{'fromObject':{'revision':REVISION}}},
    'readiness-gate-artifact':{'project':'BrowserRT','revision':REVISION,'version':VERSION,'status':'passed','probe_id':f'{REVISION}-kernel-kit-readiness-gate-probe','readinessGate':{'revision':REVISION}},
    'browser-kernel-kit-artifact':{'project':'BrowserRT','revision':REVISION,'version':VERSION,'status':'passed','probe_id':f'{REVISION}-browser-kernel-kit-demo-probe','proofId':f'{REVISION}-browser-kernel-kit-demo'},
    'browser-session-coordination-artifact':{'project':'BrowserRT','revision':REVISION,'version':VERSION,'status':'passed','probe_id':f'{REVISION}-browser-kernel-kit-session-coordination-checkpoint-probe','proof':{'exclusiveIfAvailableDenied':True,'queuedAcquiredAfterRelease':True,'staleReadReturnedNull':True}},
    'browser-recovery-artifact':{'project':'BrowserRT','revision':REVISION,'version':VERSION,'status':'passed','probe_id':f'{REVISION}-browser-kernel-kit-recovery-checkpoint-probe','proof':{'sameOriginProfileRestartObserved':True,'interruptedWriteNotAcceptedCorrupt':True,'transientOpenFailureRetryObserved':True,'unsettledOrphanReviewGateObserved':True}}}
def build(out,mutate=None):
    p=payloads()
    if mutate=='browser-wrong-proof-id': p['browser-kernel-kit-artifact']['proofId']='rev9999-browser-kernel-kit-demo'
    if mutate=='session-wrong-stale-read': p['browser-session-coordination-artifact']['proof']['staleReadReturnedNull']=False
    if mutate=='recovery-wrong-open-retry': p['browser-recovery-artifact']['proof']['transientOpenFailureRetryObserved']=False
    if mutate=='support-wrong-revision':
        p['support-bundle-proof-artifact']['revision']='rev9999'; p['support-bundle-proof-artifact']['supportBundle']['revision']='rev9999'; p['support-bundle-proof-artifact']['supportBundle']['evidenceLedger']['revision']='rev9999'
    if mutate=='import-wrong-source': p['support-bundle-import-artifact']['sourceProbeId']='rev9999-kernel-kit-support-bundle-probe'
    files={PATHS[k]:j(v) for k,v in p.items()}; rows=[]; line=[]
    for k,path in PATHS.items():
        b=files[path]; rows.append({'id':k,'path':path,'status':'sealed','lineageStatus':'bound','size':len(b),'sha256':h(b)}); line.append({'id':k,'path':path,'status':'bound'})
    line.append({'id':'cube-sanity-command','path':None,'status':'command-only'})
    sp=f'artifacts/validation/{PREFIX}-KERNEL-KIT-SUPPORT-BUNDLE-PACKAGE-EVIDENCE-SEAL-PROBE.json'
    files[sp]=j({'project':'BrowserRT','revision':REVISION,'version':VERSION,'status':'passed','format':'browserrt-kernel-kit-support-bundle-package-evidence-seal-v1','probe_id':f'{REVISION}-kernel-kit-support-bundle-package-evidence-seal-probe','proof':{'releaseManifestVerifierExpected':True,'allSealedArtifactsLineageBound':True,'staleOrWrongRevisionEvidenceRejected':True},'sealedArtifactRows':rows,'evidenceLineageRows':line,'lineageNegativeCheck':{'rejected':True},'nonClaims':['No artifact authenticity or signature claim.']})
    if mutate=='unsafe-path-traversal': files['../evil.json']=j({'project':'BrowserRT','revision':REVISION,'status':'passed','purpose':'unsafe path fixture'})
    if mutate=='symlink-entry': files[f'artifacts/validation/{PREFIX}-SYMLINK-FIXTURE.json']=b'../../outside-target'
    if mutate=='casefold-zip-entry': files[PATHS['support-bundle-proof-artifact'].lower()]=files[PATHS['support-bundle-proof-artifact']]
    if mutate=='oversized-entry': files[f'artifacts/validation/{PREFIX}-OVERSIZED-FIXTURE.json']=b'0'*(2*1024*1024+1)
    if mutate=='unsupported-compression-method': files[f'artifacts/validation/{PREFIX}-UNSUPPORTED-COMPRESSION-FIXTURE.json']=b'unsupported compression fixture'
    manifest_rows=[{'path':path,'size':len(b),'sha256':h(b)} for path,b in sorted(files.items())]
    if mutate=='duplicate-manifest-path': manifest_rows.append(dict(manifest_rows[0]))
    manifest={'manifest_version':1,'project':'BrowserRT','archive_name':ARCHIVE_NAME,'revision':REVISION,'revision_date':'2026-06-17','packaging_timestamp':STAMP,'slug':SLUG,'summary_highlight':'archive verifier fixture','codename':'Archive Verifier Fixture','source_file_count':len(manifest_rows),'files':manifest_rows}
    archive=out/ARCHIVE_NAME
    with ZipFile(archive,'w',compression=ZIP_STORED) as z:
        for path,b in sorted(files.items()):
            info=zi(path)
            if mutate=='symlink-entry' and path.endswith('-SYMLINK-FIXTURE.json'):
                info.external_attr=0o120777<<16
            if mutate=='unsupported-compression-method' and path.endswith('-UNSUPPORTED-COMPRESSION-FIXTURE.json'):
                info.compress_type=ZIP_BZIP2
            z.writestr(info,b)
        if mutate=='duplicate-zip-entry':
            duplicate_path=PATHS['support-bundle-proof-artifact']
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                z.writestr(zi(duplicate_path),files[duplicate_path])
        z.writestr(zi('RELEASE-MANIFEST.json'),j(manifest))
    return archive
def verify_case(path):
    buf=StringIO()
    try:
        with redirect_stdout(buf): verify_release.verify(path)
        return True,buf.getvalue().strip() or None
    except SystemExit:
        return False,buf.getvalue().strip() or None
def run_probe():
    with tempfile.TemporaryDirectory(prefix='browserrt-archive-evidence-') as tmp:
        ok,err=verify_case(build(Path(tmp))); cases=[]
        lineage_mutations=['browser-wrong-proof-id','session-wrong-stale-read','recovery-wrong-open-retry','support-wrong-revision','import-wrong-source']
        structure_mutations=['duplicate-zip-entry','unsafe-path-traversal','duplicate-manifest-path','symlink-entry','casefold-zip-entry','oversized-entry','unsupported-compression-method']
        for m in lineage_mutations+structure_mutations:
            cok,cerr=verify_case(build(Path(tmp),m)); cases.append({'mutation':m,'expected':'rejected','rejected':cok is False,'error':cerr,'guardsIndependentArtifactLineage':m in lineage_mutations and cerr is not None and 'independent lineage check failed' in cerr,'guardsArchiveStructure':m in structure_mutations and cerr is not None and any(needle in cerr for needle in ['duplicate zip entry names rejected','unsafe zip entry path rejected','duplicate manifest file paths rejected','unsafe zip entry metadata rejected','case-colliding zip entry names rejected','case-colliding manifest file paths rejected','zip entry budget rejected','zip uncompressed size budget rejected','zip file count budget rejected'])})
    lineage_cases=[c for c in cases if c['mutation'] in {'browser-wrong-proof-id','session-wrong-stale-read','recovery-wrong-open-retry','support-wrong-revision','import-wrong-source'}]
    structure_cases=[c for c in cases if c['mutation'] in {'duplicate-zip-entry','unsafe-path-traversal','duplicate-manifest-path','symlink-entry','casefold-zip-entry','oversized-entry','unsupported-compression-method'}]
    proof={'validArchiveAccepted':ok,'validArchiveError':err,'mutatedArchivesRejected':all(c['rejected'] for c in cases),'independentArtifactLineageGuarded':all(c['guardsIndependentArtifactLineage'] for c in lineage_cases),'unsafeArchiveStructureGuarded':all(c['guardsArchiveStructure'] for c in structure_cases),'zipEntryMetadataGuarded':any(c['mutation']=='symlink-entry' and c['guardsArchiveStructure'] for c in structure_cases),'casefoldPathCollisionGuarded':any(c['mutation']=='casefold-zip-entry' and c['guardsArchiveStructure'] for c in structure_cases),'zipBombBudgetGuarded':all(any(c['mutation']==m and c['guardsArchiveStructure'] for c in structure_cases) for m in ['oversized-entry','unsupported-compression-method']),'fixturesUseZipContainedArtifacts':True}
    return {'project':'BrowserRT','revision':REVISION,'version':VERSION,'schema':1,'probe_id':f'{REVISION}-release-archive-evidence-verifier-probe','status':'passed' if proof['validArchiveAccepted'] and proof['mutatedArchivesRejected'] and proof['independentArtifactLineageGuarded'] and proof['unsafeArchiveStructureGuarded'] and proof['zipEntryMetadataGuarded'] and proof['casefoldPathCollisionGuarded'] and proof['zipBombBudgetGuarded'] else 'failed','purpose':'Fixture proof for independent archive evidence lineage checks.','proof':proof,'negativeCases':cases,'nonClaims':['Minimal verifier fixtures; not product release archives.','No artifact signing or authenticity claim.','No package command execution or browser launch.']}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--json',default=f'artifacts/validation/{PREFIX}-RELEASE-ARCHIVE-EVIDENCE-VERIFIER-PROBE.json'); a=ap.parse_args(); r=run_probe(); out=Path(a.json); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(r,indent=2)+'\n'); print(out); return 0 if r['status']=='passed' else 1
if __name__=='__main__': raise SystemExit(main())
