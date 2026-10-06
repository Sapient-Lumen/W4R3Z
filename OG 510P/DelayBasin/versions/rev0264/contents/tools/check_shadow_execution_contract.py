from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="execution",
    doc_required=[
        "execution-lane / kernel-and-precision clause",
        "same eager-versus-CUDA-graph posture",
        "same attention-backend or kernel-family posture",
        "same precision / quantization posture",
        "execution witness or explicit baseline-kernel note",
        "backend fallback, CUDA-graph downgrade, or precision drift",
    ],
    prompt_required=[
        "same eager-versus-CUDA-graph posture",
        "execution witness or explicit baseline-kernel note",
    ],
    runbook_required=[
        "execution-lane / kernel-and-precision clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "backend fallback, CUDA-graph downgrade, or precision drift",
    ],
    open_question_required=[
        "OQ-0116",
        "execution witness or explicit baseline-kernel note",
    ],
    quarantine_required=[
        "QWS-0124",
        "shadow-execution registry",
    ],
)
