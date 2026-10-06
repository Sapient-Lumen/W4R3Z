import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-provenance', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['de-authorized, source-blanded, or provenance-swapped variant', 'prestige privilege', 'provenance-cue privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['de-authorized, source-blanded, or provenance-swapped variant', 'prestige privilege', 'provenance-cue privilege'], 'docs/00-meta/trajectory-map.md': ['prestige privilege', 'family plus placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige problem'], 'docs/20-constitution/open-question-registry.md': ['prestige privilege', 'de-authorized/source-blanded/provenance-swapped variant'], 'docs/50-promptcraft/prompt-pairs.md': ['de-authorized, source-blanded, or provenance-swapped variant worth checking', 'prestige privilege'], 'docs/00-meta/llm-runbook.md': ['de-authorized, source-blanded, or provenance-swapped variant', 'prestige privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0143', 'prestige or provenance-cue scaffold'], 'CHANGELOG.md': ['de-authorized / source-blanded / provenance-swapped variant', 'check_gpustorming_provenance_contract.py']})
print('check_gpustorming_provenance_contract: OK')
