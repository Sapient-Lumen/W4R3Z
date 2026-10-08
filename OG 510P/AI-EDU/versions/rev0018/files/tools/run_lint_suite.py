import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for tool in [
    'check_required_surfaces.py',
    'check_links.py',
    'check_json.py',
    'check_receipt_sync.py',
    'gen_context_pack.py',
]:
    print(f'== {tool} ==', flush=True)
    runpy.run_path(str(ROOT / 'tools' / tool), run_name='__main__')
print('run_lint_suite: OK')
