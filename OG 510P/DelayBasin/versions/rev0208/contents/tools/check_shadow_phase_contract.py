from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="phase",
    doc_required=[
        "phase-lane / prefill-decode-placement clause",
        "same aggregated-versus-disaggregated serving posture",
        "same prefill/decode role-binding or heterogeneous-parallelism posture",
        "same handoff/recompute-or-fallback posture",
        "phase-placement witness or explicit aggregated-serving note",
        "aggregated-versus-disaggregated mismatch, prefill/decode role-binding drift, or handoff/recompute-or-fallback drift",
    ],
    prompt_required=[
        "same aggregated-versus-disaggregated serving posture",
        "phase-placement witness or explicit aggregated-serving note",
    ],
    runbook_required=[
        "phase-lane / prefill-decode-placement clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "an aggregated lane compared against a split prefill/decode lane",
    ],
    open_question_required=[
        "OQ-0116",
        "an aggregated lane compared against a split prefill/decode lane",
    ],
    quarantine_required=[
        "QWS-0132",
        "shadow-phase registry",
    ],
    extra_required=[
        ("CHANGELOG.md", ["phase-lane / prefill-decode-placement clause", "check_shadow_phase_contract.py"], "changelog"),
    ],
)
