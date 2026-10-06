from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="parallelism",
    doc_required=[
        "parallelism-lane / shard-and-replica clause",
        "same single-replica-versus-tensor/pipeline/context/data-parallel posture",
        "same node-count / per-node-GPU / cross-node posture",
        "same internal-versus-hybrid-versus-external replica-balancing posture",
        "parallelism witness or explicit single-replica note",
        "TP/PP/CP/DP drift, node-layout drift, or replica-balancer drift",
    ],
    prompt_required=[
        "same single-replica-versus-tensor/pipeline/context/data-parallel posture",
        "parallelism witness or explicit single-replica note",
    ],
    runbook_required=[
        "parallelism-lane / shard-and-replica clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "internal API-head lane compared against hybrid or external replica balancing",
    ],
    open_question_required=[
        "OQ-0116",
        "internal API-head lane compared against hybrid or external replica balancing",
    ],
    quarantine_required=[
        "QWS-0129",
        "shadow-parallelism registry",
    ],
    extra_required=[
        ("CHANGELOG.md", ["parallelism-lane / shard-and-replica clause", "check_shadow_parallelism_contract.py"], "changelog"),
    ],
)
