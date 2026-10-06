import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-replicate', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['replicate bundle or repeated-inference sweep', 'lucky-path privilege', 'decode-regime privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['replicate bundle or repeated-inference sweep', 'lucky-path privilege', 'decode-regime privilege'], 'docs/00-meta/trajectory-map.md': ['lucky-path privilege', 'family plus placement/density/boundary/wrapper/neighborhood/history/replicate problem'], 'docs/20-constitution/open-question-registry.md': ['lucky-path privilege', 'replicate-bundle/repeated-inference variant'], 'docs/50-promptcraft/prompt-pairs.md': ['replicate-bundle or repeated-inference sweep worth checking', 'lucky-path privilege'], 'docs/00-meta/llm-runbook.md': ['replicate bundle or repeated-inference sweep', 'lucky-path privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0139', 'sampler-resonance or decode-lane scaffold'], 'CHANGELOG.md': ['replicate-bundle / repeated-inference sweep', 'check_gpustorming_replicate_contract.py']})
print('check_gpustorming_replicate_contract: OK')
