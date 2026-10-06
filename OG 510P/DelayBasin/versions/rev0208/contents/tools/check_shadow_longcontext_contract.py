from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="longcontext",
    doc_required=[
        "long-context / window-and-positioning clause",
        "same max-model-len / truncation posture",
        "same sliding-window / attention-sink / cyclic-KV posture",
        "same position-scaling posture such as RoPE scaling or sink-relative positions",
        "long-context witness or explicit base-context note",
        "truncation drift, window/sink drift, or position-scaling drift",
    ],
    prompt_required=[
        "same max-model-len / truncation posture",
        "long-context witness or explicit base-context note",
    ],
    runbook_required=[
        "long-context / window-and-positioning clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "an unclipped base-context lane compared against a truncated, sliding-window, sink-token, or RoPE-scaled lane",
    ],
    open_question_required=[
        "OQ-0116",
        "an unclipped base-context lane compared against a truncated, sliding-window, sink-token, or RoPE-scaled lane",
    ],
    quarantine_required=[
        "QWS-0133",
        "shadow-long-context registry",
    ],
    extra_required=[
        ("CHANGELOG.md", ["long-context / window-and-positioning clause", "check_shadow_longcontext_contract.py"], "changelog"),
    ],
)
