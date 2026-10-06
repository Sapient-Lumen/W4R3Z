import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles, trajectory_problem_phrase

ensure_needles(ROOT, "gpustorming-freshness", {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['dated fresh-pass, as-of rerun, or post-break revalidation variant', 'stale-proof privilege', 'pre-break authority privilege'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['dated fresh-pass, as-of rerun, or post-break revalidation variant', 'stale-proof privilege', 'pre-break authority privilege'], 'docs/00-meta/trajectory-map.md': [trajectory_problem_phrase('freshness')], 'docs/20-constitution/open-question-registry.md': ['dated-fresh-pass/as-of-rerun/post-break-revalidation variant', 'stale-proof privilege', 'pre-break authority privilege'], 'docs/50-promptcraft/prompt-pairs.md': ['dated fresh-pass, as-of rerun, or post-break revalidation variant worth checking', 'stale-proof privilege'], 'docs/00-meta/llm-runbook.md': ['dated fresh-pass, as-of rerun, or post-break revalidation variant', 'old proof, old signoff'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0147', 'stale-proof carry or freshness scaffold'], 'CHANGELOG.md': ['dated fresh-pass / as-of rerun / post-break revalidation guard', 'check_gpustorming_freshness_contract.py']})
print("check_gpustorming_freshness_contract: OK")
