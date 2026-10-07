#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path


def run(root: Path) -> list[dict]:
    findings=[]
    contract_path=root/'SCHEMA/Package-Release-Contract-current.json'
    public_manifest_path=root/'PUBLIC/PUBLIC-EXPORT-MANIFEST-current.json'
    if not contract_path.exists():
        return [{'severity':'high','check':'contract_exists','file':str(contract_path.relative_to(root)),'detail':'missing'}]
    contract=json.loads(contract_path.read_text(encoding='utf-8'))
    allowed=set(contract.get('allowed_public_layer_files',[]))
    actual={str(p.relative_to(root)) for p in (root/'PUBLIC').glob('*') if p.is_file()}
    extra=sorted(actual-allowed)
    missing=sorted(allowed-actual)
    if extra:
        findings.append({'severity':'high','check':'public_layer_extra_files','file':'PUBLIC/','detail':'; '.join(extra)})
    if missing:
        findings.append({'severity':'high','check':'public_layer_missing_files','file':'PUBLIC/','detail':'; '.join(missing)})
    if public_manifest_path.exists():
        pub=json.loads(public_manifest_path.read_text(encoding='utf-8'))
        included=set(pub.get('included_files',[]))
        public_included={x for x in included if x.startswith('PUBLIC/')}
        not_in_manifest=sorted(actual-public_included)
        if not_in_manifest:
            findings.append({'severity':'medium','check':'public_files_not_in_public_manifest_included_files','file':'PUBLIC-EXPORT-MANIFEST-current.json','detail':'; '.join(not_in_manifest)})
    return findings


def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument('root', nargs='?', default='.')
    ap.add_argument('--json', action='store_true')
    args=ap.parse_args()
    root=Path(args.root).resolve()
    findings=run(root)
    if args.json:
        print(json.dumps(findings, ensure_ascii=False, indent=2))
    elif not findings:
        print('PASS public contract check — PUBLIC/ matches allowed public-layer files')
    else:
        for f in findings:
            print(f"{f['severity'].upper()} {f['check']} {f['file']}: {f['detail']}")
    if any(f.get('severity')=='high' for f in findings):
        raise SystemExit(1)

if __name__=='__main__':
    main()
