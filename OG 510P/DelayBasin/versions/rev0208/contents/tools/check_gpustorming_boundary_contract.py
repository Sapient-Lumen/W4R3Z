import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-boundary', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['boundary or normalization variant', 'retokenization privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['boundary/normalization variants', 'retokenization privilege'], 'docs/00-meta/trajectory-map.md': ['boundary / retokenization privilege', 'family plus placement/density/boundary problem'], 'docs/20-constitution/open-question-registry.md': ['boundary / retokenization privilege', 'boundary/normalization variant'], 'docs/50-promptcraft/prompt-pairs.md': ['boundary or normalization variant worth checking', 'retokenization privilege'], 'docs/00-meta/llm-runbook.md': ['boundary or normalization variant'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0135', 'tokenizer-resonance / merge-boundary scaffold'], 'CHANGELOG.md': ['retokenization / normalization variant', 'check_gpustorming_boundary_contract.py']})
print('check_gpustorming_boundary_contract: OK')
