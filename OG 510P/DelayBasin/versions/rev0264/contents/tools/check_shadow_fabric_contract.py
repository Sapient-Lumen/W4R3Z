from shadow_contract_common import require_shadow_contract

require_shadow_contract(
    kind="fabric",
    doc_required=[
        "fabric-lane / interconnect-and-transfer clause",
        "same same-node-versus-cross-node and same NVLink-domain / NIC-rail posture",
        "same transport/backend posture such as GPUDirect-RDMA, UCX/NIXL/Mooncake, or socket fallback",
        "same zero-copy-versus-staged-copy / transfer-concurrency posture",
        "fabric witness or explicit local-fabric note",
        "socket fallback, fabric-domain drift, rail/NIC drift, or transfer-buffer/concurrency drift",
    ],
    prompt_required=[
        "same same-node-versus-cross-node and same NVLink-domain / NIC-rail posture",
        "fabric witness or explicit local-fabric note",
    ],
    runbook_required=[
        "fabric-lane / interconnect-and-transfer clause",
    ],
    trajectory_required=[
        "OQ-0116",
        "an RDMA or fast-interconnect lane compared against a socket-fallback or staged-copy lane",
    ],
    open_question_required=[
        "OQ-0116",
        "an RDMA or fast-interconnect lane compared against a socket-fallback or staged-copy lane",
    ],
    quarantine_required=[
        "QWS-0131",
        "shadow-fabric registry",
    ],
    extra_required=[
        ("CHANGELOG.md", ["fabric-lane / interconnect-and-transfer clause", "check_shadow_fabric_contract.py"], "changelog"),
    ],
)
