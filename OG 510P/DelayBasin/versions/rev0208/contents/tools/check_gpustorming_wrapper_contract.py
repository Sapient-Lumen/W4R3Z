import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-wrapper', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['wrapper or role-slot variant', 'template privilege', 'begin-of-text privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['wrapper/serialization variants', 'wrapper or role-slot variant', 'template privilege'], 'docs/00-meta/trajectory-map.md': ['wrapper / role-slot privilege', 'family plus placement/density/boundary/wrapper problem'], 'docs/20-constitution/open-question-registry.md': ['wrapper / role-slot privilege', 'wrapper/role-slot variant'], 'docs/50-promptcraft/prompt-pairs.md': ['wrapper or role-slot variant worth checking', 'template privilege'], 'docs/00-meta/llm-runbook.md': ['wrapper or role-slot variant', 'begin-of-text privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0136', 'role-slot / template-slot scaffold'], 'CHANGELOG.md': ['wrapper / role-slot variant', 'check_gpustorming_wrapper_contract.py']})
print('check_gpustorming_wrapper_contract: OK')
