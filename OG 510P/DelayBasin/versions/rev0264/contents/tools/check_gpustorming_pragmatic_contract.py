import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-pragmatic', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['ordinary-tone, de-escalated, or pragmatic-frame-scrubbed variant', 'pragmatic-frame privilege', 'social-force privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['ordinary-tone, de-escalated, or pragmatic-frame-scrubbed variant', 'pragmatic-frame privilege', 'social-force privilege'], 'docs/00-meta/trajectory-map.md': ['pragmatic-frame privilege', 'family plus placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona/pragmatic problem'], 'docs/20-constitution/open-question-registry.md': ['pragmatic-frame privilege', 'ordinary-tone/de-escalated/pragmatic-frame-scrubbed variant'], 'docs/50-promptcraft/prompt-pairs.md': ['ordinary-tone, de-escalated, or pragmatic-frame-scrubbed variant worth checking', 'pragmatic-frame privilege'], 'docs/00-meta/llm-runbook.md': ['ordinary-tone, de-escalated, or pragmatic-frame-scrubbed variant', 'pragmatic-frame privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0145', 'pragmatic-framing or social-force scaffold'], 'CHANGELOG.md': ['ordinary-tone / de-escalated / pragmatic-frame-scrubbed variant', 'check_gpustorming_pragmatic_contract.py']})
print('check_gpustorming_pragmatic_contract: OK')
