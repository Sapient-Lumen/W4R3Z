from packet_contract_common import require_packet_contract, require_vocabulary_family

require_packet_contract(
    kind="renewal_witness_contract",
    surfaces=[
        ("docs/10-method/renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md", [
            "# Renewal witnesses, fresh approval acts, and carryforward drift",
            "This is the compact successor surface for `OQ-0123`.",
            "## Practice / observation",
            "## External pressure from expiring preserved exemptions, updated exceptions, temporary ignores, and approval windows",
            "## Working synthesis",
            "## Fresh renewal vs copied-forward residue vs changed basis",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`renewal_state`",
            "fresh-renewal",
            "copied-forward",
            "expired-residue",
            "basis-changed",
        ], "renewal witness doc"),
        ("docs/00-meta/llm-runbook.md", ["renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md"], "runbook"),
        ("docs/50-promptcraft/prompt-pairs.md", ["PP-0081", "Use `docs/10-method/renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md`", "fresh-renewal, copied-forward, expired-residue, or basis-changed"], "prompt pairs"),
        ("docs/20-constitution/claim-registry.md", ["CL-0121", "renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md"], "claim registry"),
        ("docs/20-constitution/open-question-registry.md", ["OQ-0123", "RS-0130", "renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md", "OQ-0124"], "open-question registry"),
        ("docs/00-meta/trajectory-map.md", ["OQ-0123", "RS-0130", "renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md", "OQ-0124"], "trajectory map"),
        ("docs/90-quarantine/wild-speculations-2026-03-08.md", ["QWS-0206", "reapproval court / renewal senate / tenure board"], "quarantine"),
        ("CHANGELOG.md", ["renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md", "check_renewal_witness_contract.py"], "changelog"),
    ],
)

require_vocabulary_family(
    family="renewal_state",
    allowed=["fresh-renewal", "copied-forward", "expired-residue", "basis-changed"],
    surfaces=[
        "WITNESS-VOCABULARY.json",
        "REVISION-RECEIPT.json",
        "docs/10-method/renewal-witnesses-fresh-approval-acts-and-carryforward-drift.md",
    ],
    excluded=["still-there", "implicitly-renewed", "same-exception-enough", "close-enough carryforward"],
)
print("check_renewal_witness_contract: OK")
