from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="multimodal",
    doc_required=[
        "multimodal-input / processor-and-encoder clause",
        "same text-only-versus-multimodal posture",
        "same processor / placeholder-and-media-sizing posture",
        "same vision-encoder / multimodal-cache posture",
        "multimodal witness or explicit no-media note",
        "media-token drift, placeholder-expansion drift, processor-cache mismatch, image/video resize-or-frame-sampling drift, or vision-encoder/backend mismatch",
    ],
    prompt_required=[
        "same text-only-versus-multimodal posture",
        "multimodal witness or explicit no-media note",
    ],
    runbook_required=[
        "multimodal-input / processor-and-encoder clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "image/video resize-or-frame-sampling drift",
    ],
    open_question_required=[
        "OQ-0116",
        "multimodal witness or explicit no-media note",
    ],
    quarantine_required=[
        "QWS-0128",
        "shadow-multimodal registry",
    ],
    extra_required=[
        ("CHANGELOG.md", ["multimodal-input / processor-and-encoder clause", "check_shadow_multimodal_contract.py"], "changelog"),
    ],
)
