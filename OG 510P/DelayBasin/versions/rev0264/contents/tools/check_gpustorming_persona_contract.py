import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-persona', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['identity-neutral, persona-scrubbed, or audience-agnostic variant', 'persona privilege', 'interlocutor-identity privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['identity-neutral, persona-scrubbed, or audience-agnostic variant', 'persona privilege', 'interlocutor-identity privilege'], 'docs/00-meta/trajectory-map.md': ['persona privilege', 'family plus placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona problem'], 'docs/20-constitution/open-question-registry.md': ['persona privilege', 'identity-neutral/persona-scrubbed/audience-agnostic variant'], 'docs/50-promptcraft/prompt-pairs.md': ['identity-neutral, persona-scrubbed, or audience-agnostic variant worth checking', 'persona privilege'], 'docs/00-meta/llm-runbook.md': ['identity-neutral, persona-scrubbed, or audience-agnostic variant', 'persona privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0144', 'persona or interlocutor-identity scaffold'], 'CHANGELOG.md': ['identity-neutral / persona-scrubbed / audience-agnostic variant', 'check_gpustorming_persona_contract.py']})
print('check_gpustorming_persona_contract: OK')
