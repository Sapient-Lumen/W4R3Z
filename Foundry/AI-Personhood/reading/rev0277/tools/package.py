#!/usr/bin/env python3
"""Build a deterministic ZIP; normalized 1980 member times are not publication dates."""
import argparse
import hashlib
from pathlib import Path
import subprocess
import sys
import zipfile

root = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('output', type=Path)
a = p.parse_args()
out = a.output.resolve()
if out.is_relative_to(root):
    p.error('put output outside the source cube')
files = []
for item in root.rglob('*'):
    if item.is_symlink():
        p.error('symbolic links are not permitted')
    if item.is_file() and item.name != 'MANIFEST.sha256':
        files.append(item.relative_to(root).as_posix())
manifest = ''.join(hashlib.sha256((root/n).read_bytes()).hexdigest()+'  '+n+'\n' for n in sorted(files))
(root/'MANIFEST.sha256').write_text(manifest, encoding='utf-8')
subprocess.run([sys.executable, str(root/'cube.py'), 'check'], check=True)
out.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for n in sorted(files+['MANIFEST.sha256']):
        i=zipfile.ZipInfo(n, (1980,1,1,0,0,0));i.create_system=3;i.external_attr=(0o100644<<16);i.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(i,(root/n).read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
b=out.read_bytes();print(str(out),len(b),hashlib.sha256(b).hexdigest())
