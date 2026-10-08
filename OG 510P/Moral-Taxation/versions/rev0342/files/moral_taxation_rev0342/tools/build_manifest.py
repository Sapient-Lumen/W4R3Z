import hashlib, json, pathlib, sys
root = pathlib.Path(sys.argv[1]).resolve()
items = []
for p in sorted(root.rglob('*')):
    if p.is_file() and p.name != 'MANIFEST.json':
        rel = p.relative_to(root).as_posix()
        data = p.read_bytes()
        items.append({
            'file': rel,
            'bytes': len(data),
            'sha256': hashlib.sha256(data).hexdigest(),
        })
(root / 'MANIFEST.json').write_text(json.dumps({'root': root.name, 'files': items}, separators=(',', ':')) + "\n", encoding='utf-8')
