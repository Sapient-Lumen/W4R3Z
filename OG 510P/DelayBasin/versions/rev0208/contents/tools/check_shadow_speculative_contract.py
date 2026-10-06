from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="speculative",
    doc_required=[
        "speculative-decoding / draft-verifier clause",
        "same no-spec versus speculative-decoding posture",
        "draft-model or proposer witness, speculative-token budget, and acceptance-rate witness or explicit no-spec note",
        "draft-family mismatch, acceptance-policy drift, or load-triggered speculation disable",
    ],
    prompt_required=[
        "acceptance-rate witness or explicit no-spec note",
        "same no-spec versus speculative-decoding posture",
    ],
    runbook_required=[
        "speculative-decoding / draft-verifier clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "load-triggered speculation disable",
    ],
    open_question_required=[
        "OQ-0116",
        "acceptance-rate witness or explicit no-spec note",
    ],
    quarantine_required=[
        "QWS-0122",
        "shadow-speculation registry",
    ],
)
