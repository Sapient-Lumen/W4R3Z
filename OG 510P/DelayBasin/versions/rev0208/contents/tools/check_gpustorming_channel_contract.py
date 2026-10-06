import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from gpustorming_contract_lib import ensure_needles

ensure_needles(ROOT, 'gpustorming-channel', {'docs/10-method/operator-tokens-and-bootstrap-grammar.md': ['quoted, code-fenced, or literal-mention variant', 'actuation-channel privilege', 'instruction-data confusion'], 'docs/10-method/alias-packets-handle-collision-budgets-and-namespace-hygiene.md': ['quoted, code-fenced, or literal-mention variant', 'actuation-channel privilege', 'instruction-data confusion'], 'docs/00-meta/trajectory-map.md': ['actuation-channel privilege', 'family plus placement/density/boundary/wrapper/neighborhood/history/replicate/channel problem'], 'docs/20-constitution/open-question-registry.md': ['actuation-channel privilege', 'quoted/code-fenced/literal-mention variant'], 'docs/50-promptcraft/prompt-pairs.md': ['quoted, code-fenced, or literal-mention variant worth checking', 'actuation-channel privilege'], 'docs/00-meta/llm-runbook.md': ['quoted, code-fenced, or literal-mention variant', 'actuation-channel privilege'], 'docs/90-quarantine/wild-speculations-2026-03-08.md': ['QWS-0140', 'actuation-channel scaffold'], 'CHANGELOG.md': ['quoted, code-fenced, or literal-mention variant', 'check_gpustorming_channel_contract.py']})
print('check_gpustorming_channel_contract: OK')
