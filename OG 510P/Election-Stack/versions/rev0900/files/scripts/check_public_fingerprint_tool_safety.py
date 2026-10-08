#!/usr/bin/env python3
from __future__ import annotations
import json, os, re, shutil, sys, tempfile
from pathlib import Path
from _cli_harness import run_python_cli
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'artifacts/examples/evidence_packet_ed25519_threshold2_minimal'
PF=ROOT/'tools/public_fingerprint_report.py'; CMP=ROOT/'tools/compare_public_fingerprints.py'
def fail(m): print('FAIL:',m,file=sys.stderr); raise SystemExit(1)
def helper_profile():
    text=PF.read_text(encoding='utf-8')
    m=re.search(r'^REPORT_FORMAT_VERSION\s*=\s*["\']([^"\']+)["\']', text, re.M)
    if not m: fail('could not read public_fingerprint_report REPORT_FORMAT_VERSION')
    return m.group(1)
def runj(script,args,rc=0):
    code,out,err=run_python_cli(script,args,extra_sys_path=[ROOT,ROOT/'tools'],cwd=ROOT)
    if code!=rc: fail(f'{script.name} rc={code} want={rc}; {out[:200]} {err[:200]}')
    try: return json.loads(out)
    except Exception as e: fail(f'bad JSON from {script.name}: {e}; {out[:200]}')
def assert_warns(rep,prefix):
    ws=[str(w) for w in rep.get('warnings') or []]
    if not any(w.startswith(prefix) for w in ws): fail(f'expected warning {prefix!r}, got {ws}')
def main():
    expected_profile=helper_profile()
    clean=runj(PF,[PACKET,'--stable'])
    if clean.get('report_format_version')!=expected_profile: fail(f"profile drift: output={clean.get('report_format_version')} helper={expected_profile}")
    if clean.get('warnings'): fail(f"clean packet warned: {clean.get('warnings')}")
    cases_checked=0
    with tempfile.TemporaryDirectory(prefix='tes-pubfp-safety-') as td:
        t=Path(td)
        root_link=t/'packet-root-link'; os.symlink(PACKET,root_link,target_is_directory=True)
        root=runj(PF,[root_link,'--stable']); assert_warns(root,'packet_root_symlink_rejected_for_hash:.'); cases_checked+=1
        if int(root.get('included_file_count',-1))!=0: fail('root symlink included target entries')
        f=t/'file-symlink'; shutil.copytree(PACKET,f); (f/'README.txt').unlink(); os.symlink(PACKET/'README.txt',f/'README.txt')
        assert_warns(runj(PF,[f,'--stable']),'file_symlink_rejected_for_hash:README.txt'); cases_checked+=1
        dang=t/'dangling-file-symlink'; shutil.copytree(PACKET,dang); (dang/'README.txt').unlink(); os.symlink(t/'does-not-exist.txt',dang/'README.txt')
        assert_warns(runj(PF,[dang,'--stable']),'file_symlink_rejected_for_hash:README.txt'); cases_checked+=1
        nested=t/'nested-dangling-note-symlink'; shutil.copytree(PACKET,nested); (nested/'notes').mkdir(exist_ok=True); os.symlink(t/'missing-note.md',nested/'notes'/'missing-note.md')
        assert_warns(runj(PF,[nested,'--stable']),'file_symlink_rejected_for_hash:notes/missing-note.md'); cases_checked+=1
        nested_dir=t/'nested-note-dir-symlink'; shutil.copytree(PACKET,nested_dir); (nested_dir/'notes').mkdir(exist_ok=True); os.symlink(t/'missing-note-dir',nested_dir/'notes'/'missing-note-dir',target_is_directory=True)
        assert_warns(runj(PF,[nested_dir,'--stable']),'directory_symlink_rejected_for_hash:notes/missing-note-dir'); cases_checked+=1
        d=t/'dir-symlink'; shutil.copytree(PACKET,d); shutil.rmtree(d/'envelopes'); os.symlink(PACKET/'envelopes',d/'envelopes',target_is_directory=True)
        assert_warns(runj(PF,[d,'--stable']),'directory_symlink_rejected_for_hash:envelopes'); cases_checked+=1
        huge=t/'huge-public-file'; shutil.copytree(PACKET,huge); (huge/'README.txt').write_bytes(b'A'*(512*1024+1))
        huge_rep=runj(PF,[huge,'--stable','--include-file-hashes'])
        assert_warns(huge_rep,'file_exceeds_max_include_bytes_rejected_for_hash:README.txt')
        if any(str(x).endswith('  README.txt') for x in (huge_rep.get('file_hashes') or [])):
            fail('oversized README.txt was included in file hashes')
        cases_checked+=1
        nonfile=t/'non-file-public-route'; shutil.copytree(PACKET,nonfile); (nonfile/'README.txt').unlink(); (nonfile/'README.txt').mkdir()
        nonfile_rep=runj(PF,[nonfile,'--stable','--include-file-hashes'])
        assert_warns(nonfile_rep,'non_file_public_surface_rejected_for_hash:README.txt')
        if any(str(x).endswith('  README.txt') for x in (nonfile_rep.get('file_hashes') or [])):
            fail('non-file README.txt was included in file hashes')
        cases_checked+=1
        n=t/'name-ambiguity'; n.mkdir(); (n/'README.txt').write_text('one\n'); (n/'readme.TXT').write_text('two\n')
        assert_warns(runj(PF,[n,'--stable']),'public_relpath_casefold_collision_rejected_for_hash:'); cases_checked+=1
        bad=t/'portable-name'; bad.mkdir(); (bad/'bad:name.txt').write_text('colon\n'); (bad/'CON.txt').write_text('reserved\n'); (bad/'notes').mkdir(); (bad/'notes'/'dir.').mkdir(); (bad/'notes'/'dir.'/'ok.md').write_text('dot dir\n')
        rep=runj(PF,[bad,'--stable'])
        assert_warns(rep,'public_relpath_portable_component_rejected_for_hash:bad:name.txt:windows_reserved_character')
        assert_warns(rep,'public_relpath_portable_component_rejected_for_hash:CON.txt:windows_reserved_device_name')
        assert_warns(rep,'public_relpath_portable_component_rejected_for_hash:notes/dir./ok.md:windows_trailing_space_or_dot')
        cases_checked+=1
        if runj(CMP,[PACKET,PACKET,'--json']).get('status')!='MATCH': fail('clean compare did not MATCH')
        if runj(CMP,[PACKET,root_link,'--json'],rc=2).get('status')!='UNSAFE_WARNING': fail('symlink compare did not UNSAFE_WARNING')
        if runj(CMP,[PACKET,dang,'--json'],rc=2).get('status')!='UNSAFE_WARNING': fail('dangling symlink compare did not UNSAFE_WARNING')
        if runj(CMP,[PACKET,huge,'--json'],rc=2).get('status')!='UNSAFE_WARNING': fail('oversized public file compare did not UNSAFE_WARNING')
        if runj(CMP,[PACKET,nonfile,'--json'],rc=2).get('status')!='UNSAFE_WARNING': fail('non-file public route compare did not UNSAFE_WARNING')
        if runj(CMP,[PACKET,bad,'--json'],rc=2).get('status')!='UNSAFE_WARNING': fail('portable-name warning compare did not UNSAFE_WARNING')
    print(f'PASS: public fingerprint helper preserves unsafe-route, non-file, oversized-file, and portable-name warnings (profile={expected_profile}, cases_checked={cases_checked})')
if __name__=='__main__': main()
