from packet_contract_common import require_packet_contract

require_packet_contract(
    kind="shadow_packet_contract",
    surfaces=[
        ("docs/10-method/shadow-comparison-packets-minimal-pre-promotion-lanes-and-overflow-tests.md", [
            "compact successor surface for `OQ-0116`",
            "candidate surface and control surface",
            "serve-authority and sink rule",
            "mirror responses are ignored",
            "selection and delivery geometry",
            "same endpoint/backend type/protocol/route kind",
            "one production/one shadow, one deployment, or one single destination endpoint",
            "comparison basis and verdict gate",
            "Overflow test",
        ], "shadow packet doc"),
        ("docs/10-method/external-optimizer-loops-public-slow-weights-and-archive-write-gates.md", ["shadow-comparison-packets-minimal-pre-promotion-lanes-and-overflow-tests.md"], "external-optimizer doc"),
        ("docs/50-promptcraft/prompt-pairs.md", ["shadow-comparison-packets-minimal-pre-promotion-lanes-and-overflow-tests.md"], "prompt pairs"),
        ("docs/00-meta/llm-runbook.md", ["shadow-comparison-packets-minimal-pre-promotion-lanes-and-overflow-tests.md"], "runbook"),
        ("docs/20-constitution/open-question-registry.md", ["OQ-0116", "RS-0123", "shadow-comparison-packets-minimal-pre-promotion-lanes-and-overflow-tests.md"], "open-question registry"),
        ("docs/00-meta/trajectory-map.md", ["OQ-0116", "RS-0123", "shadow-comparison-packets-minimal-pre-promotion-lanes-and-overflow-tests.md"], "trajectory map"),
        ("docs/90-quarantine/wild-speculations-2026-03-08.md", ["QWS-0199", "scorecourt / mirror senate / promotion-verdict board"], "quarantine"),
        ("CHANGELOG.md", ["shadow-comparison-packets-minimal-pre-promotion-lanes-and-overflow-tests.md", "check_shadow_packet_contract.py"], "changelog"),
    ],
)
