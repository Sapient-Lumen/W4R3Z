from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
import json

from packet_contract_common import require_packet_contract
from witness_vocabulary_lib import load_families, expect_allowed, expect_family

require_packet_contract(
    kind="public_state_packet_contract",
    surfaces=[
        ("docs/10-method/public-state-packets-discoverability-exclusions-and-overflow-tests.md", [
            "# Public-state packets, discoverability exclusions, and overflow tests",
            "This is the compact successor surface for `OQ-0111`.",
            "## Practice / observation",
            "## External pressure from release maturity, access control, and search discoverability practice",
            "## Working synthesis",
            "## Public state vs maturity vs access vs discoverability",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`working`",
            "`frozen-citable`",
            "`deprecated-public`",
            "`absent`",
            "draft",
            "prerelease",
            "private",
            "noindex",
        ], "public-state packet doc"),
        ("docs/20-constitution/open-question-registry.md", [
            "`OQ-0111`",
            "resolved by `RS-0127` via `docs/10-method/public-state-packets-discoverability-exclusions-and-overflow-tests.md`",
        ], "open question registry"),
        ("docs/50-promptcraft/prompt-pairs.md", [
            "PP-0070",
            "Use `docs/10-method/public-state-packets-discoverability-exclusions-and-overflow-tests.md` when the family needs a compact successor surface.",
        ], "prompt pairs"),
    ],
)

families = load_families()
expect_family(
    families,
    "public_state",
    allowed=["working", "frozen-citable", "deprecated-public", "absent"],
    surfaces=["SURFACE-STATUS.json", "REVISION-RECEIPT.json"],
    excluded=["published", "current-public", "draft", "prerelease", "private", "search-indexed"],
)

status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
expect_allowed(families, "public_state", status["status_lanes"]["public_state"], "SURFACE-STATUS public_state")
expect_allowed(families, "public_state", receipt["status_witness"]["public_state"], "receipt status_witness public_state")
expect_allowed(families, "decision_state", status["status_lanes"]["decision_state"], "SURFACE-STATUS decision_state")
expect_allowed(families, "execution_state", status["status_lanes"]["execution_state"], "SURFACE-STATUS execution_state")
print("check_public_state_packet_contract: OK")
