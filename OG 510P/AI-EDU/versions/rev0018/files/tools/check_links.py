import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
link_re = re.compile(r'\[[^\]]+\]\(([^)]+)\)')
errors = []
for path in ROOT.rglob('*.md'):
    text = path.read_text(encoding='utf-8')
    for target in link_re.findall(text):
        if target.startswith('http://') or target.startswith('https://') or target.startswith('#'):
            continue
        local = (path.parent / target.split('#', 1)[0]).resolve()
        try:
            local.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f'{path.relative_to(ROOT)} -> escapes root: {target}')
            continue
        if not local.exists():
            errors.append(f'{path.relative_to(ROOT)} -> missing: {target}')
if errors:
    raise SystemExit('link errors:\n' + '\n'.join(errors))
print('check_links: OK')
