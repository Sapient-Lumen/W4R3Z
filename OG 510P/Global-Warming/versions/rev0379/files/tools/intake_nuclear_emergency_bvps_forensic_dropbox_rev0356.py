#!/usr/bin/env python3
from pathlib import Path
import argparse, csv, hashlib, mimetypes, shutil, zipfile
DENY_EXT={'.exe','.dll','.js','.vbs','.scr','.bat','.cmd','.ps1','.lnk','.docm','.xlsm','.pptm','.hta','.html'}
HOLD_EXT={'.zip','.7z','.rar','.pst','.ost','.eml','.msg','.xlsx','.docx','.pptx','.pdf'}
MARKERS={'rejected_closure_attempt':['PUBLIC_CONTEXT_CLOSURE_ATTEMPT','FORBIDDEN_CLAIM','AUTO_CLOSE_REQUEST'],'hold_no_upgrade':['HOLD_NO_UPGRADE'],'candidate_for_adjudication_not_closure':['CANDIDATE_NOT_CLOSURE'],'accepted_reopen_signal':['REOPEN_SIGNAL'],'context_no_upgrade':['CONTEXT_NO_UPGRADE']}
def sha(p):
 h=hashlib.sha256();
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
 return h.hexdigest()
def txt(p):
 try: return p.read_text(encoding='utf-8',errors='ignore')[:200000]
 except Exception:
  try: return p.read_bytes()[:200000].decode('utf-8','ignore')
  except Exception: return ''
def zinfo(p):
 if p.suffix.lower()!='.zip': return ('','','')
 try:
  with zipfile.ZipFile(p) as z:
   infos=z.infolist(); total=sum(i.file_size for i in infos); flag='hold_zip_review'
   if len(infos)>1000 or total>50000000: flag='reject_zip_bomb_risk'
   return (str(len(infos)),str(total),flag)
 except Exception: return ('error','error','reject_corrupt_archive')
def classify(p):
 ext=p.suffix.lower(); text=txt(p); ze,zu,zf=zinfo(p); found=[]
 for cls,ms in MARKERS.items():
  for m in ms:
   if m in text: found.append(m)
 if zf.startswith('reject'): return 'rejected_closure_attempt','archive_reject',found,ze,zu,zf
 if ext in DENY_EXT or any(m in found for m in MARKERS['rejected_closure_attempt']): return 'rejected_closure_attempt','deny_extension_or_closure_marker',found,ze,zu,zf
 if any(m in found for m in MARKERS['accepted_reopen_signal']): return 'accepted_reopen_signal','counterevidence_marker',found,ze,zu,zf
 if any(m in found for m in MARKERS['context_no_upgrade']): return 'context_no_upgrade','context_marker',found,ze,zu,zf
 if ext in HOLD_EXT or any(m in found for m in MARKERS['hold_no_upgrade']): return 'hold_no_upgrade','hold_extension_or_marker',found,ze,zu,zf
 if any(m in found for m in MARKERS['candidate_for_adjudication_not_closure']): return 'candidate_for_adjudication_not_closure','candidate_marker_not_closure',found,ze,zu,zf
 return 'hold_no_upgrade','default_unknown_hold',found,ze,zu,zf
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--input-dir',required=True); ap.add_argument('--output-csv',required=True); ap.add_argument('--copy-root'); ap.add_argument('--revision',default='rev0356'); a=ap.parse_args(); rows=[]
 for p in sorted([x for x in Path(a.input_dir).iterdir() if x.is_file()]):
  cls,reason,found,ze,zu,zf=classify(p); lane={'rejected_closure_attempt':'rejected','hold_no_upgrade':'review','candidate_for_adjudication_not_closure':'candidate','accepted_reopen_signal':'review','context_no_upgrade':'review'}[cls]; dest=''
  if a.copy_root:
   d=Path(a.copy_root)/lane/p.name; d.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(p,d); dest=str(d)
  rows.append({'file_name':p.name,'source_path':str(p),'sha256':sha(p),'size_bytes':p.stat().st_size,'extension':p.suffix.lower(),'mime_guess':mimetypes.guess_type(str(p))[0] or '','observed_classification':cls,'lane':lane,'reason':reason,'markers':';'.join(found),'zip_entry_count':ze,'zip_uncompressed_bytes':zu,'zip_flag':zf,'copied_to':dest,'auto_closure':'no','claim_boundary':'intake classification is not readiness closure','revision_checked':a.revision})
 with open(a.output_csv,'w',newline='',encoding='utf-8') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
 print(f'wrote {len(rows)} rows to {a.output_csv}')
if __name__=='__main__': main()
