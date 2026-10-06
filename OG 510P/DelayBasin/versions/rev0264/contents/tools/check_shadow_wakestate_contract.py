from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="wakestate",
    doc_required=[
        "wake-state / cold-start clause",
        "same hot-resident-versus-sleeping-versus-scale-from-zero posture",
        "same model/profile-cache or engine-ready posture",
        "same warmup / first-inference posture",
        "wake-state witness or explicit hot-start note",
        "cold-start mismatch, sleep/wake resume drift, profile-download or engine-build drift, or warmup mismatch",
    ],
    prompt_required=[
        "same hot-resident-versus-sleeping-versus-scale-from-zero posture",
        "wake-state witness or explicit hot-start note",
    ],
    runbook_required=[
        "wake-state / cold-start clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "a hot-resident lane compared against a sleeping or scale-from-zero lane",
    ],
    open_question_required=[
        "OQ-0116",
        "a hot-resident lane compared against a sleeping or scale-from-zero lane",
    ],
    quarantine_required=[
        "QWS-0130",
        "shadow-wake-state registry",
    ],
    extra_required=[
        ("CHANGELOG.md", ["wake-state / cold-start clause", "check_shadow_wakestate_contract.py"], "changelog"),
    ],
)
