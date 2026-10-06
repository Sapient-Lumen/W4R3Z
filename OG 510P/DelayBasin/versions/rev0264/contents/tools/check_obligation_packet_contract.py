from packet_contract_common import require_packet_contract
from witness_vocabulary_lib import load_families, expect_family

require_packet_contract(
    kind="obligation_packet_contract",
    surfaces=[
        ("docs/10-method/obligation-packets-waivers-remediation-expiry-and-overflow-tests.md", [
            "# Obligation packets, waivers, remediation, expiry, and overflow tests",
            "This is the compact successor surface for `OQ-0110`.",
            "## Practice / observation",
            "## External pressure from exemptions, remediation exceptions, POA&Ms, and status-check systems",
            "## Working synthesis",
            "## Obligation core vs waiver vs suppression vs followthrough",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`open`",
            "`staged`",
            "`satisfied`",
            "`waived`",
            "`retired`",
            "suppressed",
            "expiresOn",
        ], "obligation packet doc"),
        ("docs/00-meta/llm-runbook.md", ["obligation-packets-waivers-remediation-expiry-and-overflow-tests.md"], "runbook"),
        ("docs/50-promptcraft/prompt-pairs.md", ["PP-0069", "Use `docs/10-method/obligation-packets-waivers-remediation-expiry-and-overflow-tests.md` when the family needs a compact successor surface."], "prompt pairs"),
        ("docs/20-constitution/claim-registry.md", ["CL-0110", "obligation-packets-waivers-remediation-expiry-and-overflow-tests.md"], "claim registry"),
        ("docs/20-constitution/open-question-registry.md", ["OQ-0110", "RS-0128", "obligation-packets-waivers-remediation-expiry-and-overflow-tests.md"], "open-question registry"),
        ("docs/00-meta/trajectory-map.md", ["OQ-0110", "RS-0128", "obligation-packets-waivers-remediation-expiry-and-overflow-tests.md"], "trajectory map"),
        ("docs/90-quarantine/wild-speculations-2026-03-08.md", ["QWS-0204", "exception court / waiver senate / debt-governance board"], "quarantine"),
        ("CHANGELOG.md", ["obligation-packets-waivers-remediation-expiry-and-overflow-tests.md", "check_obligation_packet_contract.py"], "changelog"),
    ],
)

families = load_families()
expect_family(
    families,
    "obligation_state",
    allowed=["open", "staged", "satisfied", "waived", "retired"],
    surfaces=["OBLIGATION-LEDGER.json", "REVISION-RECEIPT.json"],
)
print("check_obligation_packet_contract: OK")
