from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="cache",
    doc_required=[
        "cache-residency / prefill-reuse clause",
        "same prefix-caching, KV-cache reuse, cache-offload, or disaggregated-prefill posture",
        "cache-residency witness or explicit cold-prefill note",
        "hot-cache mismatch, offload-tier drift, or prefill/decode transfer mismatch",
    ],
    prompt_required=[
        "cache-residency witness or explicit cold-prefill note",
        "same prefix-caching, KV-cache reuse, cache-offload, or disaggregated-prefill posture",
    ],
    runbook_required=[
        "cache-residency / prefill-reuse clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "offload-tier drift, or prefill/decode transfer mismatch",
    ],
    open_question_required=[
        "OQ-0116",
        "cache-residency witness or explicit cold-prefill note",
    ],
    quarantine_required=[
        "QWS-0121",
        "shadow-cache-topology registry",
    ],
)
