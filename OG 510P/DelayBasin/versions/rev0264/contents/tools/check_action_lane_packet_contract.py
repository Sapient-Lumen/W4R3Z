from packet_contract_common import require_packet_contract

require_packet_contract(
    kind="action_lane_packet_contract",
    surfaces=[
        ("docs/10-method/action-lane-packets-primary-next-step-classes-and-routing-overflow-tests.md", [
            "This is the compact successor surface for `OQ-0113`.",
            "## Practice / observation",
            "## External pressure from phased rollout and deployment-gate systems",
            "## Working synthesis",
            "## Primary lane vs state vs gate class",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`await-adjudication`",
        ], "action-lane packet doc"),
        ("docs/00-meta/llm-runbook.md", ["action-lane-packets-primary-next-step-classes-and-routing-overflow-tests.md"], "runbook"),
        ("docs/50-promptcraft/prompt-pairs.md", ["action-lane-packets-primary-next-step-classes-and-routing-overflow-tests.md"], "prompt pairs"),
        ("docs/20-constitution/claim-registry.md", ["action-lane-packets-primary-next-step-classes-and-routing-overflow-tests.md", "CL-0113"], "claim registry"),
        ("docs/20-constitution/open-question-registry.md", ["OQ-0113", "RS-0125", "action-lane-packets-primary-next-step-classes-and-routing-overflow-tests.md"], "open-question registry"),
        ("docs/00-meta/trajectory-map.md", ["OQ-0113", "RS-0125", "action-lane-packets-primary-next-step-classes-and-routing-overflow-tests.md"], "trajectory map"),
        ("docs/90-quarantine/wild-speculations-2026-03-08.md", ["QWS-0201", "route court / lane senate / next-step router board"], "quarantine"),
        ("CHANGELOG.md", ["action-lane-packets-primary-next-step-classes-and-routing-overflow-tests.md", "check_action_lane_packet_contract.py"], "changelog"),
        ("WITNESS-VOCABULARY.json", ["action_lane", "await-adjudication"], "vocabulary"),
    ],
)
