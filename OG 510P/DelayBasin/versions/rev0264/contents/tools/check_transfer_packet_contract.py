from packet_contract_common import require_packet_contract

require_packet_contract(
    kind="transfer_packet_contract",
    surfaces=[
        ("docs/10-method/transfer-packets-reviewed-datacube-sets-disposition-classes-and-overflow-tests.md", [
            "This is the compact successor surface for `OQ-0112`.",
            "## Practice / observation",
            "## External pressure from decision logs, review states, lineage, and migration practice",
            "## Working synthesis",
            "## Reviewed set vs disposition vs anchor surfaces",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`supporting-only`",
        ], "transfer-packet doc"),
        ("docs/00-meta/llm-runbook.md", ["transfer-packets-reviewed-datacube-sets-disposition-classes-and-overflow-tests.md"], "runbook"),
        ("docs/50-promptcraft/prompt-pairs.md", ["transfer-packets-reviewed-datacube-sets-disposition-classes-and-overflow-tests.md"], "prompt pairs"),
        ("docs/20-constitution/claim-registry.md", ["transfer-packets-reviewed-datacube-sets-disposition-classes-and-overflow-tests.md", "CL-0112"], "claim registry"),
        ("docs/20-constitution/open-question-registry.md", ["OQ-0112", "RS-0126", "transfer-packets-reviewed-datacube-sets-disposition-classes-and-overflow-tests.md"], "open-question registry"),
        ("docs/00-meta/trajectory-map.md", ["OQ-0112", "RS-0126", "transfer-packets-reviewed-datacube-sets-disposition-classes-and-overflow-tests.md"], "trajectory map"),
        ("docs/90-quarantine/wild-speculations-2026-03-08.md", ["QWS-0202", "transfer court / import senate / comparison-memory board"], "quarantine"),
        ("CHANGELOG.md", ["transfer-packets-reviewed-datacube-sets-disposition-classes-and-overflow-tests.md", "check_transfer_packet_contract.py"], "changelog"),
        ("WITNESS-VOCABULARY.json", ["assimilation_state", "supporting-only"], "vocabulary"),
    ],
)
