from pathlib import Path

from packet_contract_common import require_standard_packet_and_vocabulary

DOC_PATH = "docs/10-method/evidence-ecology-witnesses-selector-source-bias-citation-loop-pressure-and-retrieval-contamination-collapse.md"
FAMILY = "evidence_ecology_state"
ALLOWED = ['selector-source-bias', 'citation-loop-pressure', 'retrieval-contamination-collapse', 'mixed-evidence-ecology']
EXCLUDED = ['any-ai-search-error-is-collapse', 'citations-mean-independent-evidence', 'seo-visibility-is-source-quality', 'evidence-ecology-ish']

require_standard_packet_and_vocabulary(
    kind="evidence_ecology_witness_contract",
    doc_path=DOC_PATH,
    doc_needles=[
        "# Evidence-ecology witnesses, selector source bias, citation-loop pressure, and retrieval-contamination collapse",
        "This is the compact successor surface for `OQ-0161`.",
        "## Practice / observation",
        "## External pressure from LLM search source coverage, SourceBench source quality, GEO citation optimization, Google AI Mode self-citation, publisher AI opt-out pressure, and retrieval collapse",
        "## Working synthesis",
        "## Selector source bias vs citation-loop pressure vs retrieval-contamination collapse vs mixed evidence ecology",
        "## Countermodels / probes",
        "## Design consequences",
        "## Overflow test",
        "## Transformer-facing implication",
        "`evidence_ecology_state`",
        *ALLOWED,
    ],
    runbook_ref=Path(DOC_PATH).name,
    prompt_id="PP-0119",
    prompt_needles=[
        f"Use `{DOC_PATH}`",
        "selector-source-bias, citation-loop-pressure, retrieval-contamination-collapse, or mixed-evidence-ecology",
    ],
    claim_id="CL-0159",
    oq_id="OQ-0161",
    resolution_id="RS-0168",
    trajectory_oq_id="OQ-0162",
    qws_id="QWS-0244",
    qws_label="citation-incentive / evidence-market / provenance-dividend board",
    changelog_needles=[Path(DOC_PATH).name, "check_evidence_ecology_witness_contract.py"],
    family=FAMILY,
    allowed=ALLOWED,
    surfaces=["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", DOC_PATH],
    excluded=EXCLUDED,
)
print("check_evidence_ecology_witness_contract: OK")
