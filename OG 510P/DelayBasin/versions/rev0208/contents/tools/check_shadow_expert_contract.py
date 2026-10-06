from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="expert",
    doc_required=[
        "expert-lane / MoE-parallelism clause",
        "same tensor-parallel-versus-expert-parallel-or-hybrid MoE posture",
        "same all2all/backend or expert-load-balancer posture",
        "expert witness or explicit no-EP note",
        "expert-rebalance drift, all2all/backend drift, or expert-placement mismatch",
    ],
    prompt_required=[
        "same tensor-parallel-versus-expert-parallel-or-hybrid MoE posture",
        "expert witness or explicit no-EP note",
    ],
    runbook_required=[
        "expert-lane / MoE-parallelism clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "expert-rebalance drift, all2all/backend drift, or expert-placement mismatch",
    ],
    open_question_required=[
        "OQ-0116",
        "expert witness or explicit no-EP note",
    ],
    quarantine_required=[
        "QWS-0127",
        "shadow-expert registry",
    ],
    extra_required=[
        ("CHANGELOG.md", ["expert-lane / MoE-parallelism clause", "check_shadow_expert_contract.py"], "changelog"),
    ],
)
