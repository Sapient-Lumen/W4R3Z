from packet_contract_common import require_packet_contract, require_vocabulary_family, standard_packet_surfaces

require_packet_contract(
    kind="renewal_scope_witness_contract",
    surfaces=standard_packet_surfaces(
        doc_path="docs/10-method/renewal-scope-witnesses-local-refresh-boundaries-and-spillover-drift.md",
        doc_needles=[
            "# Renewal-scope witnesses, local refresh boundaries, and spillover drift",
            "This is the compact successor surface for `OQ-0124`.",
            "## Practice / observation",
            "## External pressure from scoped exemptions, exact-scope filters, per-resource exceptions, path-narrow ignores, and environment-bound approvals",
            "## Working synthesis",
            "## Local refresh vs broadened carryover vs spillover vs effect drift",
            "## Countermodels / probes",
            "## Design consequences",
            "## Overflow test",
            "## Transformer-facing implication",
            "`renewal_scope_state`",
            "local-refresh",
            "broadened-carryover",
            "spillover",
            "effect-drift",
        ],
        runbook_ref="renewal-scope-witnesses-local-refresh-boundaries-and-spillover-drift.md",
        prompt_id="PP-0082",
        prompt_needles=["Use `docs/10-method/renewal-scope-witnesses-local-refresh-boundaries-and-spillover-drift.md`", "local-refresh, broadened-carryover, spillover, or effect-drift"],
        claim_id="CL-0122",
        oq_id="OQ-0124",
        resolution_id="RS-0131",
        trajectory_oq_id="OQ-0125",
        qws_id="QWS-0207",
        qws_label="scope court / blast-radius senate / inheritance board",
        changelog_needles=["renewal-scope-witnesses-local-refresh-boundaries-and-spillover-drift.md", "check_renewal_scope_witness_contract.py"],
    ),
)

require_vocabulary_family(
    family="renewal_scope_state",
    allowed=["local-refresh", "broadened-carryover", "spillover", "effect-drift"],
    surfaces=[
        "WITNESS-VOCABULARY.json",
        "REVISION-RECEIPT.json",
        "docs/10-method/renewal-scope-witnesses-local-refresh-boundaries-and-spillover-drift.md",
    ],
    excluded=["same-enough-scope", "nearby-counts", "same-approval-glow", "scope-ish"],
)

print("check_renewal_scope_witness_contract: OK")
