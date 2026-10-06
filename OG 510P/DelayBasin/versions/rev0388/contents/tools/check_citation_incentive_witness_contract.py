from pathlib import Path

from packet_contract_common import require_standard_packet_and_vocabulary

DOC_PATH = "docs/10-method/citation-incentive-witnesses-quality-preserving-visibility-optimization-evidence-market-distortion-and-source-grooming.md"
FAMILY = "citation_incentive_state"
ALLOWED = [
    "quality-preserving-visibility-optimization",
    "evidence-market-distortion",
    "source-grooming-distortion",
    "mixed-citation-incentive",
]
EXCLUDED = [
    "citation-count-means-quality",
    "geo-is-always-spam",
    "payment-means-provenance",
    "citation-incentive-ish",
]

require_standard_packet_and_vocabulary(
    kind="citation_incentive_witness_contract",
    doc_path=DOC_PATH,
    doc_needles=[
        "# Citation-incentive witnesses, quality-preserving visibility optimization, evidence-market distortion, and source grooming",
        "This is the compact successor surface for `OQ-0162`.",
        "## Practice / observation",
        "## External pressure from GEO visibility optimization, AgentGEO citation diagnostics, adversarial SEO preference manipulation, arbitrary content injection, retrieval collapse, and AI-search publisher controls",
        "## Working synthesis",
        "## Quality-preserving visibility optimization vs evidence-market distortion vs source-grooming distortion vs mixed citation incentive",
        "## Countermodels / probes",
        "## Design consequences",
        "## Overflow test",
        "## Transformer-facing implication",
        f"`{FAMILY}`",
        *ALLOWED,
    ],
    runbook_ref=Path(DOC_PATH).name,
    prompt_id="PP-0120",
    prompt_needles=[
        f"Use `{DOC_PATH}`",
        "quality-preserving-visibility-optimization, evidence-market-distortion, source-grooming-distortion, or mixed-citation-incentive",
    ],
    claim_id="CL-0160",
    oq_id="OQ-0162",
    resolution_id="RS-0169",
    trajectory_oq_id="OQ-0163",
    qws_id="QWS-0245",
    qws_label="provenance-rights / citation-dividend / evidence-market clearinghouse",
    changelog_needles=[Path(DOC_PATH).name, "check_citation_incentive_witness_contract.py"],
    family=FAMILY,
    allowed=ALLOWED,
    surfaces=["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", DOC_PATH],
    excluded=EXCLUDED,
)
print("check_citation_incentive_witness_contract: OK")
