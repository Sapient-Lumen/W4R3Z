#!/usr/bin/env python3
from __future__ import annotations
"""Create an external BagIt-style transfer copy for a datacube package root.

This helper deliberately writes outside the package root. The linked datacube ZIP
keeps its established root layout; the helper creates a separate transfer bag
with payload under data/<package-root>/ for institutions that expect BagIt.
"""
import argparse, hashlib, json, shutil, sys
from pathlib import Path

sys.dont_write_bytecode = True
EXCLUDE = {'SHA256SUMS.txt.sig'}


def sha256(path: Path) -> str:
    h=hashlib.sha256(); h.update(path.read_bytes()); return h.hexdigest()


def stable_files(root: Path) -> list[str]:
    out=[]
    for p in root.rglob('*'):
        if not p.is_file(): continue
        rel=str(p.relative_to(root)).replace('\\','/')
        parts=rel.split('/')
        if rel in EXCLUDE or p.suffix.lower()=='.zip' or '__pycache__' in parts or p.suffix.lower() in {'.pyc','.pyo'}:
            continue
        out.append(rel)
    return sorted(out)


def read_manifest(root: Path) -> dict:
    try: return json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    except Exception: return {}


def write_bag(root: Path, outdir: Path, force: bool=False) -> Path:
    manifest=read_manifest(root)
    bag=outdir/(root.name + '-bag')
    if bag.exists():
        if not force:
            raise SystemExit(f'Output bag already exists: {bag}; use --force to replace')
        shutil.rmtree(bag)
    payload_base=bag/'data'/root.name
    payload_base.mkdir(parents=True)
    for rel in stable_files(root):
        src=root/rel; dst=payload_base/rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src,dst)
    (bag/'bagit.txt').write_text('BagIt-Version: 1.0\nTag-File-Character-Encoding: UTF-8\n',encoding='utf-8')
    bag_info=[
        f"Source-Organization: LivingChristFigures cloudtainer session",
        f"External-Identifier: {manifest.get('export_name_without_zip', root.name)}",
        f"Bagging-Date: {manifest.get('date', '')}",
        f"Bag-Group-Identifier: {manifest.get('title', 'Living Christ Figures datacube')}",
        f"Internal-Sender-Description: closed preservation-transfer copy; public layer remains governed by package contract",
        '',
    ]
    (bag/'bag-info.txt').write_text('\n'.join(bag_info),encoding='utf-8')
    payload_lines=[]
    for p in sorted((bag/'data').rglob('*')):
        if p.is_file():
            rel=str(p.relative_to(bag)).replace('\\','/')
            payload_lines.append(f'{sha256(p)}  {rel}')
    (bag/'manifest-sha256.txt').write_text('\n'.join(payload_lines)+'\n',encoding='utf-8')
    tag_lines=[]
    for rel in ['bagit.txt','bag-info.txt']:
        tag_lines.append(f'{sha256(bag/rel)}  {rel}')
    (bag/'tagmanifest-sha256.txt').write_text('\n'.join(tag_lines)+'\n',encoding='utf-8')
    return bag


def main():
    ap=argparse.ArgumentParser(description='Create an external BagIt-style transfer copy outside the datacube root.')
    ap.add_argument('root', nargs='?', default='.', help='package root')
    ap.add_argument('output_directory', help='directory in which to create <package-root>-bag')
    ap.add_argument('--force', action='store_true', help='replace existing output bag')
    args=ap.parse_args()
    root=Path(args.root).resolve(); outdir=Path(args.output_directory).resolve(); outdir.mkdir(parents=True, exist_ok=True)
    bag=write_bag(root,outdir,args.force)
    print(f'WROTE {bag}')
if __name__ == '__main__': main()
