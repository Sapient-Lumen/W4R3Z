import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, "gpustorming-scopenarrow", {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['instance-narrowed, scope-pinned, or family-stripped variant', 'umbrella-scope privilege', 'family-level privilege', 'instance-blur privilege', 'family-resemblance privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['instance-narrowed, scope-pinned, or family-stripped variant', 'family-level privilege', 'instance-blur privilege'], 'docs/00-meta/trajectory-map.md': ['scope-narrowing problem'], 'docs/20-constitution/open-question-registry.md': ['instance-narrowed/scope-pinned/family-stripped variant'], 'docs/50-promptcraft/prompt-pairs.md': ['instance-narrowed, scope-pinned, or family-stripped variant worth checking'], 'docs/00-meta/llm-runbook.md': ['family-scoped, umbrella-scoped, program-scoped'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0155', 'umbrella-authority carry'], 'CHANGELOG.md': ['instance-narrowed / scope-pinned / family-stripped guard', 'check_gpustorming_scopenarrow_contract.py'], 'docs/10-method/gpustorming-control-family-crosswalk-and-sync-guards.md': ['scopenarrow', 'grouped-class artifacts being mistaken for named local instance authority']})
print("check_gpustorming_scopenarrow_contract: OK")
