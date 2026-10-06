from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="scheduler",
    doc_required=[
        "scheduler / queue-discipline clause",
        "same fcfs versus priority posture",
        "same chunked-prefill / continuous-batching / decode-priority posture",
        "scheduler witness or explicit single-lane note",
        "queue-policy drift, priority mismatch, or preemption/resume divergence",
    ],
    prompt_required=[
        "scheduler witness or explicit single-lane note",
        "same fcfs versus priority posture",
    ],
    runbook_required=[
        "scheduler / queue-discipline clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "preemption/resume divergence",
    ],
    open_question_required=[
        "OQ-0116",
        "scheduler witness or explicit single-lane note",
    ],
    quarantine_required=[
        "QWS-0123",
        "shadow-scheduler registry",
    ],
)
