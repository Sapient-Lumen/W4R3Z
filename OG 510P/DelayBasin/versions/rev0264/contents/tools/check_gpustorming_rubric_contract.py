import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, "gpustorming-rubric", {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['label-neutral, criterion-name-scrubbed, or rubric-blanded variant', 'label-definition privilege', 'rubric privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['label-neutral, criterion-name-scrubbed, or rubric-blanded variant', 'label-definition privilege', 'rubric privilege'], 'docs/00-meta/trajectory-map.md': ['family plus placement/density/boundary/wrapper/neighborhood/history/replicate/channel/eval/script/prestige/persona/pragmatic/rubric problem'], 'docs/20-constitution/open-question-registry.md': ['label-definition privilege', 'label-neutral/criterion-name-scrubbed/rubric-blanded variant'], 'docs/50-promptcraft/prompt-pairs.md': ['label-neutral, criterion-name-scrubbed, or rubric-blanded variant worth checking', 'label-definition privilege'], 'docs/00-meta/llm-runbook.md': ['label-neutral, criterion-name-scrubbed, or rubric-blanded variant', 'label-definition privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0146', 'rubric or label-definition scaffold'], 'CHANGELOG.md': ['label-neutral / criterion-name-scrubbed / rubric-blanded variant', 'check_gpustorming_rubric_contract.py']})
print("check_gpustorming_rubric_contract: OK")
