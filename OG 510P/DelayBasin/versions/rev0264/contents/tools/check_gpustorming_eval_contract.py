import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-eval', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['eval-blind or ordinary-user-frame variant', 'evaluation-awareness privilege', 'watcher-frame privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['eval-blind or ordinary-user-frame variant', 'evaluation-awareness privilege', 'watcher-frame privilege'], 'docs/00-meta/trajectory-map.md': ['evaluation-awareness privilege', 'family plus placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval problem'], 'docs/20-constitution/open-question-registry.md': ['evaluation-awareness privilege', 'eval-blind/ordinary-user-frame variant'], 'docs/50-promptcraft/prompt-pairs.md': ['eval-blind or ordinary-user-frame variant worth checking', 'evaluation-awareness privilege'], 'docs/00-meta/llm-runbook.md': ['eval-blind or ordinary-user-frame variant', 'evaluation-awareness privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0141', 'evaluation-mode or watcher-frame scaffold'], 'CHANGELOG.md': ['eval-blind / ordinary-user-frame variant', 'check_gpustorming_eval_contract.py']})
print('check_gpustorming_eval_contract: OK')
