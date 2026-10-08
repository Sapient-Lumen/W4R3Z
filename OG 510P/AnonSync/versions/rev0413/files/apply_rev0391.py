from pathlib import Path

root = Path(__file__).resolve().parent
docs = root / 'docs'


def write(name: str, content: str):
    (docs / name).write_text(content.strip() + '\n', encoding='utf-8')


def prepend(path: Path, text: str):
    old = path.read_text(encoding='utf-8')
    path.write_text(text.strip() + '\n\n' + old, encoding='utf-8')

# This script documents rev0391 additions. The archive already contains the results.
