import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, "gpustorming-claimlabel", {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['label-scrubbed, claim-spelled-out, state-disambiguated, or semantics-explicit variant', 'same-label privilege', 'claim-equivalence privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['label-scrubbed, claim-spelled-out, state-disambiguated, or semantics-explicit variant', 'state-word privilege', 'approval-word privilege'], 'docs/00-meta/trajectory-map.md': ['same-label privilege', 'claim-equivalence privilege', 'state-word privilege', 'approval-word privilege'], 'docs/20-constitution/open-question-registry.md': ['label-scrubbed/claim-spelled-out/state-disambiguated/semantics-explicit variant', 'same-label privilege', 'approval-word privilege'], 'docs/50-promptcraft/prompt-pairs.md': ['label-scrubbed, claim-spelled-out, state-disambiguated, or semantics-explicit variant worth checking', 'claim-equivalence privilege'], 'docs/00-meta/llm-runbook.md': ['label-scrubbed, claim-spelled-out, state-disambiguated, or semantics-explicit variant', 'repeated state labels, approval words, current-status words'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0153', 'same-label carry or claim-equivalence scaffold'], 'CHANGELOG.md': ['label-scrubbed / claim-spelled-out / state-disambiguated / semantics-explicit guard', 'check_gpustorming_claimlabel_contract.py']})
print("check_gpustorming_claimlabel_contract: OK")
