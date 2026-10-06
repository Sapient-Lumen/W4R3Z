from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="adapter",
    doc_required=[
        "adapter-lane / PEFT-residency clause",
        "same base-only-versus-adapter-augmented posture",
        "same adapter family / rank / target-module posture",
        "adapter witness or explicit no-adapter note",
        "hot-adapter mismatch, rank drift, mixed-batch interference, or adapter reload / eviction drift",
    ],
    prompt_required=[
        "same base-only-versus-adapter-augmented posture",
        "adapter witness or explicit no-adapter note",
    ],
    runbook_required=[
        "adapter-lane / PEFT-residency clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "hot-adapter mismatch, rank drift, mixed-batch interference, or adapter reload / eviction drift",
    ],
    open_question_required=[
        "OQ-0116",
        "adapter witness or explicit no-adapter note",
    ],
    quarantine_required=[
        "QWS-0126",
        "shadow-adapter registry",
    ],
    extra_required=[
        ("CHANGELOG.md", ["adapter-lane / PEFT-residency clause", "check_shadow_adapter_contract.py"], "changelog"),
    ],
)
