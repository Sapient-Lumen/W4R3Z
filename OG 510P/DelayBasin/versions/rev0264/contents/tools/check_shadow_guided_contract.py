from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="guided",
    doc_required=[
        "guided-decoding / structure-constraint clause",
        "same unconstrained-versus-guided-decoding posture",
        "same guide kind such as choice, JSON schema, regex, or grammar",
        "guide witness or explicit unconstrained note",
        "backend auto-selection drift, fallback, cold first-inference compile, profile restriction, or guide/speculation mismatch",
    ],
    prompt_required=[
        "same unconstrained-versus-guided-decoding posture",
        "guide witness or explicit unconstrained note",
    ],
    runbook_required=[
        "guided-decoding / structure-constraint clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "backend auto-selection drift, fallback, cold first-inference compile, profile restriction, or guide/speculation mismatch",
    ],
    open_question_required=[
        "OQ-0116",
        "guide witness or explicit unconstrained note",
    ],
    quarantine_required=[
        "QWS-0125",
        "shadow-guidance registry",
    ],
)
