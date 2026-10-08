import pathlib, re, sys
root = pathlib.Path(sys.argv[1]).resolve()
errors = []
sources_text = (root / 'SOURCES.md').read_text(encoding='utf-8')
for p in root.rglob('*'):
    if p.is_file() and p.suffix.lower() == '.pdf':
        errors.append(f'pdf present: {p.relative_to(root)}')
for p in root.rglob('*.md'):
    text = p.read_text(encoding='utf-8')
    for sid in set(re.findall(r'\[(S\d+)\]', text)):
        if f'<a id="{sid}"></a>' not in sources_text:
            errors.append(f'missing source id {sid} in {p.relative_to(root)}')
if errors:
    raise SystemExit("\n".join(errors))
print('ok')
