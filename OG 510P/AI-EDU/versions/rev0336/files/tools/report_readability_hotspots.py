from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIMIT = 1000
rows = []
for path in ROOT.rglob('*.md'):
    if any(part in {'__pycache__'} for part in path.parts):
        continue
    in_code = False
    for number, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
        stripped = line.strip()
        if stripped.startswith(('```', '~~~')):
            in_code = not in_code
            continue
        if in_code or stripped.startswith('|'):
            continue
        if len(line) > LIMIT:
            rows.append((len(line), path.relative_to(ROOT).as_posix(), number))

rows.sort(reverse=True)
print(f'readability_hotspots: {len(rows)} prose lines longer than {LIMIT} characters')
for length, path, number in rows[:25]:
    print(f'{length:6d} {path}:{number}')
