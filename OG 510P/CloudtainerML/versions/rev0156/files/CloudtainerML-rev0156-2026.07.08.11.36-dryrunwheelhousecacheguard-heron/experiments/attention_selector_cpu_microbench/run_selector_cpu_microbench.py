#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, platform, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
META=json.loads((ROOT/'CUBE-META.json').read_text(encoding='utf-8')) if (ROOT/'CUBE-META.json').exists() else {'revision':'rev0046'}
REV=META.get('revision','rev0046'); REVUP=REV.upper()
SRC=Path(__file__).with_name('attention_selector_cpu_microbench.cpp')
BIN=Path(__file__).with_name('attention_selector_cpu_microbench.bin')
OUT=ROOT/'artifacts'/'probe-results'/f'{REVUP}_ATTENTION_SELECTOR_CPU_MICROBENCH.json'
MAN=ROOT/'artifacts'/'run-manifests'/f'{REVUP}_ATTENTION_SELECTOR_CPU_MICROBENCH_RUN_MANIFEST.json'
def sha(p:Path):
 h=hashlib.sha256();
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1<<20),b''): h.update(c)
 return h.hexdigest()
def main():
 OUT.parent.mkdir(parents=True, exist_ok=True); MAN.parent.mkdir(parents=True, exist_ok=True)
 compile_cmd=['g++','-std=c++17','-O3','-march=native',str(SRC.relative_to(ROOT)),'-o',str(BIN.relative_to(ROOT))]
 subprocess.run(compile_cmd, check=True, cwd=ROOT)
 subprocess.run([str(BIN.relative_to(ROOT)), str(OUT.relative_to(ROOT))], check=True, cwd=ROOT)
 data=json.loads(OUT.read_text())
 data.update({
  'revision': REV,
  'run_provenance': {
   'source_path': str(SRC.relative_to(ROOT)),
   'source_sha256': sha(SRC),
   'wrapper_path': str(Path(__file__).relative_to(ROOT)),
   'wrapper_sha256': sha(Path(__file__)),
   'compile_command': ' '.join(compile_cmd),
   'run_command': f'{BIN.relative_to(ROOT)} {OUT.relative_to(ROOT)}',
   'platform': platform.platform(),
   'machine': platform.machine(),
   'processor': platform.processor(),
   'python': sys.version.split()[0],
  },
  'interpretation': 'Native C++ selector-only timing closes part of the Python-proxy gap, but this is still CPU selection timing, not GPU attention-kernel or end-to-end model timing.'
 })
 OUT.write_text(json.dumps(data, indent=2)+'\n')
 MAN.write_text(json.dumps({'project':'CloudtainerML','revision':REV,'run':'attention_selector_cpu_microbench','artifact':str(OUT.relative_to(ROOT)),'artifact_sha256':sha(OUT),'source':str(SRC.relative_to(ROOT)),'source_sha256':sha(SRC),'compile_command':' '.join(compile_cmd),'platform':platform.platform()}, indent=2)+'\n')
 print(json.dumps({'artifact':str(OUT.relative_to(ROOT)),'rows':len(data.get('rows',[])),'scope':data.get('timing_scope')}, indent=2))
if __name__=='__main__': main()
