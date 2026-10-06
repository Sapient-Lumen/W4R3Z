import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-script', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['translation, transliteration, or script-swapped variant', 'language-selection privilege', 'script-barrier privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['translation, transliteration, or script-swapped variant', 'language-selection privilege', 'script-barrier privilege'], 'docs/00-meta/trajectory-map.md': ['language-selection privilege', 'family plus placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script problem'], 'docs/20-constitution/open-question-registry.md': ['language-selection privilege', 'translation/transliteration/script-swapped variant'], 'docs/50-promptcraft/prompt-pairs.md': ['translation, transliteration, or script-swapped variant worth checking', 'language-selection privilege'], 'docs/00-meta/llm-runbook.md': ['translation, transliteration, or script-swapped variant', 'language-selection privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0142', 'language-selection or script-barrier scaffold'], 'CHANGELOG.md': ['translation / transliteration / script-swapped variant', 'check_gpustorming_script_contract.py']})
print('check_gpustorming_script_contract: OK')
