import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-history', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['history-light or residue-stripped variant', 'carryover privilege', 'failed-attempt residue privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['history-light or residue-stripped variant', 'carryover privilege', 'failed-attempt residue privilege'], 'docs/00-meta/trajectory-map.md': ['history or carryover privilege', 'family plus placement/density/boundary/wrapper/neighborhood/history problem'], 'docs/20-constitution/open-question-registry.md': ['history or carryover privilege', 'history-light/residue-stripped variant'], 'docs/50-promptcraft/prompt-pairs.md': ['history-light or residue-stripped variant worth checking', 'carryover privilege'], 'docs/00-meta/llm-runbook.md': ['history-light or residue-stripped variant', 'carryover privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0138', 'history-drag or failed-attempt-residue scaffold'], 'CHANGELOG.md': ['history-light / residue-stripped variant', 'check_gpustorming_history_contract.py']})
print('check_gpustorming_history_contract: OK')
