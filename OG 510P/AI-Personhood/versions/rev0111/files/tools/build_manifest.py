from pathlib import Path
import hashlib

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / 'MANIFEST.sha256'
lines = []
for path in sorted(ROOT.rglob('*')):
    if path.is_dir():
        continue
    if path.name == 'MANIFEST.sha256':
        continue
    if '__pycache__' in path.parts:
        continue
    rel = path.relative_to(ROOT).as_posix()
    h = hashlib.sha256(path.read_bytes()).hexdigest()
    lines.append(f'{h}  {rel}')
out.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(out)
