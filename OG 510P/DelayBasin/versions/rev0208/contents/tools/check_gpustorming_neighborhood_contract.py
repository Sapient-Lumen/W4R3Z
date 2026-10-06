import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-neighborhood', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['nearby sham or cue-neighborhood variant', 'adjacency privilege', 'local cue-neighborhood privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['nearby sham or cue-neighborhood variant', 'adjacency privilege', 'local cue-neighborhood privilege'], 'docs/00-meta/trajectory-map.md': ['local cue-neighborhood privilege', 'family plus placement/density/boundary/wrapper/neighborhood problem'], 'docs/20-constitution/open-question-registry.md': ['local cue-neighborhood privilege', 'nearby sham/cue-neighborhood variant'], 'docs/50-promptcraft/prompt-pairs.md': ['nearby sham or cue-neighborhood variant worth checking', 'adjacency privilege'], 'docs/00-meta/llm-runbook.md': ['nearby sham or cue-neighborhood variant', 'adjacency privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0137', 'local cue-neighborhood scaffold'], 'CHANGELOG.md': ['nearby sham / cue-neighborhood variant', 'check_gpustorming_neighborhood_contract.py']})
print('check_gpustorming_neighborhood_contract: OK')
