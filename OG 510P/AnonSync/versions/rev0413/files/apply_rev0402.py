from pathlib import Path

root = Path(__file__).resolve().parent

def prepend(path: str, text: str):
    p = root / path
    old = p.read_text(encoding='utf-8')
    p.write_text(text.strip() + '

' + old, encoding='utf-8')

def write(path: str, text: str):
    p = root / path
    p.write_text(text.strip() + '
', encoding='utf-8')

# This revision adds rev0402 work-heartbeat docs and prepended addenda.
# Archive already contains the applied results.
