from packet_contract_common import require_packet_contract

require_packet_contract(
    kind="exception_witness_contract",
    surfaces=[
        ("docs/10-method/exception-witnesses-temporary-waivers-expiry-honesty-and-suppression-exclusions.md", [
            "# Exception witnesses, temporary waivers, expiry honesty, and suppression exclusions",
            "This is the compact successor surface for `OQ-0122`.",
            "## Practice / observation",
            "## External pressure from exemption categories, expiring ignores, and suppressed findings",
            "## Working synthesis",
            "## Waiver vs mitigated neighbor vs suppressed aggregate vs expired residue",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`waived`",
            "expired",
            "suppressed",
        ], "exception witness doc"),
        ("docs/00-meta/llm-runbook.md", ["exception-witnesses-temporary-waivers-expiry-honesty-and-suppression-exclusions.md"], "runbook"),
        ("docs/50-promptcraft/prompt-pairs.md", ["PP-0080", "Use `docs/10-method/exception-witnesses-temporary-waivers-expiry-honesty-and-suppression-exclusions.md` when the live question is whether neighboring waiver, mitigation, suppression, or expiry prose is being mistaken for a current honest waiver."], "prompt pairs"),
        ("docs/20-constitution/claim-registry.md", ["CL-0120", "exception-witnesses-temporary-waivers-expiry-honesty-and-suppression-exclusions.md"], "claim registry"),
        ("docs/20-constitution/open-question-registry.md", ["OQ-0122", "RS-0129", "exception-witnesses-temporary-waivers-expiry-honesty-and-suppression-exclusions.md"], "open-question registry"),
        ("docs/00-meta/trajectory-map.md", ["OQ-0122", "RS-0129", "exception-witnesses-temporary-waivers-expiry-honesty-and-suppression-exclusions.md", "OQ-0123"], "trajectory map"),
        ("docs/90-quarantine/wild-speculations-2026-03-08.md", ["QWS-0205", "renewal court / waiver-validity senate / expiry-arbitration board"], "quarantine"),
        ("CHANGELOG.md", ["exception-witnesses-temporary-waivers-expiry-honesty-and-suppression-exclusions.md", "check_exception_witness_contract.py"], "changelog"),
    ],
)
print("check_exception_witness_contract: OK")
