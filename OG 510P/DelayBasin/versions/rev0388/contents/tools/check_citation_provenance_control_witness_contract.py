from pathlib import Path

from packet_contract_common import require_standard_packet_and_vocabulary

DOC_PATH = "docs/10-method/provenance-control-witnesses-opt-out-attribution-compensation-exclusion-citation-dividend-and-mixed-control.md"
FAMILY = "provenance_control_state"
ALLOWED = ['access-opt-out-control', 'attribution-control', 'compensation-control', 'exclusion-control', 'citation-dividend-control', 'mixed-provenance-control']
EXCLUDED = ['robots-equals-payment', 'attribution-means-consent', 'opt-out-means-compensation', 'citation-dividend-by-default', 'provenance-control-ish']

require_standard_packet_and_vocabulary(
    kind="citation_provenance_control_witness_contract",
    doc_path=DOC_PATH,
    doc_needles=[
        "# Provenance-control witnesses, opt-out, attribution, compensation, exclusion, citation dividend, and mixed control",
        "This is the compact successor surface for `OQ-0163`.",
        "## Practice / observation",
        "## External pressure from robots.txt, AI crawler controls, snippet controls, user-triggered fetchers, content provenance, and content-use signals",
        "## Working synthesis",
        "## Opt-out vs attribution vs compensation vs exclusion vs citation dividend vs mixed provenance control",
        "## Countermodels / probes",
        "## Design consequences",
        "## Overflow test",
        "## Transformer-facing implication",
        f"`{FAMILY}`",
        *ALLOWED,
    ],
    runbook_ref=Path(DOC_PATH).name,
    prompt_id="PP-0133",
    prompt_needles=[
        f"Use `{DOC_PATH}`",
        "access-opt-out-control, attribution-control, compensation-control, exclusion-control, citation-dividend-control, or mixed-provenance-control",
    ],
    claim_id="CL-0173",
    oq_id="OQ-0163",
    resolution_id="RS-0183",
    trajectory_oq_id="OQ-0176",
    qws_id="QWS-0258",
    qws_label="provenance-rights clearinghouse / citation-dividend market / source-access court",
    changelog_needles=[Path(DOC_PATH).name, "check_citation_provenance_control_witness_contract.py", "provenance_control_state"],
    family=FAMILY,
    allowed=ALLOWED,
    surfaces=["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", DOC_PATH],
    excluded=EXCLUDED,
)
print("check_citation_provenance_control_witness_contract: OK")
