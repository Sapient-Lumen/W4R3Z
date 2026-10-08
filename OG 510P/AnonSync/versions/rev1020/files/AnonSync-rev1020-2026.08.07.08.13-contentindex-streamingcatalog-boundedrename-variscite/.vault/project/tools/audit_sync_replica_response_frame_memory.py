#!/usr/bin/env python3
"""Lexical audit for rev0997 response-frame memory ownership.

This is source-shape hygiene, not semantic or peak-RSS proof. Compiler,
sanitizer, allocation-regression, process, and package evidence remain
load-bearing.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

REQUIRED = (
    Path("CMakeLists.txt"),
    Path("README.md"),
    Path("DIRECT_RESPONSE_FRAME_AND_OWNED_TLS_HANDOFF_AUDIT_rev0997.md"),
    Path("REVISION_NOTES_rev0997.md"),
    Path("src/anonsync_replica.cpp"),
    Path("src/sync_replica_reconciliation_protocol.cpp"),
    Path("src/sync_replica_reconciliation_service.hpp"),
    Path("src/sync_replica_reconciliation_service.cpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.hpp"),
    Path("src/sync_replica_reconciliation_tls_exchange.cpp"),
    Path("src/sync_replica_tls_transport.hpp"),
    Path("src/sync_replica_tls_transport.cpp"),
    Path("src/sync_replica_tls_record_exchange.hpp"),
    Path("src/sync_replica_tls_record_exchange.cpp"),
    Path("tests/sync_replica_reconciliation_frame_memory_test.cpp"),
    Path("tests/sync_replica_tls_transport_test.cpp"),
    Path("tools/audit_sync_tls_write_continuation.py"),
    Path("tools/audit_sync_replica_response_frame_memory.py"),
    Path("tools/test_anonsync_replica_reconciliation_process.py"),
    Path("tools/test_anonsync_sync_process.py"),
    Path("tools/verify_release_package.py"),
)


@dataclass(frozen=True)
class Check:
    check_id: str
    passed: bool
    detail: str


def emit(root: Path, output: Path | None, checks: list[Check]) -> int:
    violations = [check.check_id for check in checks if not check.passed]
    report = {
        "format": "anonsync-response-frame-memory-source-audit-v1",
        "scope": "lexical-hygiene-not-semantic-or-peak-rss-proof",
        "root": str(root),
        "passed": not violations,
        "passed_checks": len(checks) - len(violations),
        "total_checks": len(checks),
        "checks": [asdict(check) for check in checks],
        "violations": violations,
    }
    rendered = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if output is None:
        sys.stdout.write(rendered)
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
    return 0 if not violations else 1


def body(text: str, signature: str) -> str:
    start = text.find(signature)
    if start < 0:
        return ""
    opening = text.find("{", start + len(signature))
    if opening < 0:
        return ""
    depth = 0
    for index in range(opening, len(text)):
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
            if depth == 0:
                return text[start : index + 1]
    return ""


def ordered(text: str, *tokens: str) -> bool:
    position = -1
    for token in tokens:
        position = text.find(token, position + 1)
        if position < 0:
            return False
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    checks: list[Check] = []

    def require(condition: bool, check_id: str, detail: str) -> None:
        checks.append(Check(check_id, bool(condition), detail))

    missing = [path.as_posix() for path in REQUIRED if not (root / path).is_file()]
    require(not missing, "required_files_exist", f"missing={missing}")
    bootstrap_path = root.parent.parent / "BOOTSTRAPROSE.md"
    require(
        bootstrap_path.is_file(),
        "release_root_bootstrap_exists",
        str(bootstrap_path),
    )
    if missing or not bootstrap_path.is_file():
        return emit(root, args.json, checks)

    text = {
        path.as_posix(): (root / path).read_text(encoding="utf-8")
        for path in REQUIRED
    }
    bootstrap = bootstrap_path.read_text(encoding="utf-8")
    cmake = text["CMakeLists.txt"]
    readme = text["README.md"]
    design = text["DIRECT_RESPONSE_FRAME_AND_OWNED_TLS_HANDOFF_AUDIT_rev0997.md"]
    notes = text["REVISION_NOTES_rev0997.md"]
    protocol = text["src/sync_replica_reconciliation_protocol.cpp"]
    service_h = text["src/sync_replica_reconciliation_service.hpp"]
    service = text["src/sync_replica_reconciliation_service.cpp"]
    tls_h = text["src/sync_replica_reconciliation_tls_exchange.hpp"]
    tls = text["src/sync_replica_reconciliation_tls_exchange.cpp"]
    transport_h = text["src/sync_replica_tls_transport.hpp"]
    transport = text["src/sync_replica_tls_transport.cpp"]
    record_h = text["src/sync_replica_tls_record_exchange.hpp"]
    record = text["src/sync_replica_tls_record_exchange.cpp"]
    memory_test = text["tests/sync_replica_reconciliation_frame_memory_test.cpp"]
    tls_test = text["tests/sync_replica_tls_transport_test.cpp"]
    continuation_audit = text["tools/audit_sync_tls_write_continuation.py"]
    process_test = text["tools/test_anonsync_replica_reconciliation_process.py"]
    sync_process_test = text["tools/test_anonsync_sync_process.py"]
    replica_cli = text["src/anonsync_replica.cpp"]
    verifier = text["tools/verify_release_package.py"]
    normalized_design = " ".join(design.split())
    normalized_notes = " ".join(notes.split())

    require(
        "anonsync_sync_replica_reconciliation_frame_memory_test" in cmake
        and "tests/sync_replica_reconciliation_frame_memory_test.cpp" in cmake
        and "LABELS \"product\"" in cmake,
        "allocation_regression_is_built_registered_and_product_labeled",
        "the direct-frame memory boundary is exercised in ordinary product validation",
    )
    require(
        "anonsync_sync_replica_response_frame_memory_source_audit" in cmake
        and "tools/audit_sync_replica_response_frame_memory.py" in cmake,
        "focused_source_audit_is_registered",
        "the rev0997 source-shape audit is in the ordinary registry",
    )

    response_frame = body(
        protocol,
        "encode_sync_replica_reconciliation_response_after_validation_or_throw(",
    )
    require(
        ordered(
            response_frame,
            "response_body_metrics_or_throw",
            "frame_bytes > limits.max_response_frame_bytes",
            "frame.reserve",
            "frame.append(kResponseMagic)",
            "append_response_body_or_throw",
            "std::string_view body",
            "body_digest_or_throw",
        )
        and "std::string body" not in response_frame,
        "response_encoder_builds_one_exact_final_frame",
        "the page is appended directly behind the header instead of copied from a body string",
    )
    require(
        "response direct encoder drifted from its exact body size" in protocol
        and "response direct encoder drifted from its exact frame size" in protocol
        and "response_body_metrics_or_throw" in protocol,
        "measurement_and_serialization_are_exactly_cross_checked",
        "size drift fails as an internal invariant instead of producing malformed wire bytes",
    )
    public_encode = body(
        protocol,
        "std::string encode_sync_replica_reconciliation_response_or_throw(",
    )
    require(
        "encode_sync_replica_reconciliation_response_after_validation_or_throw" in public_encode
        and "false" in public_encode
        and "make_frame_or_throw" not in public_encode
        and "response_body_or_throw" not in public_encode,
        "public_response_encode_uses_direct_frame_path",
        "the shipping encoder cannot reintroduce body-then-frame composition",
    )
    require(
        "std::string response_digest" not in service_h
        and "sync_replica_reconciliation_response_digest_or_throw" not in service,
        "unused_service_response_digest_is_removed",
        "serving no longer serializes the complete body a second time for dead evidence",
    )

    owned_prepare = body(
        transport,
        "prepare_sync_replica_tls_owned_record_write_or_throw(",
    )
    require(
        "std::string frame" in transport_h
        and ordered(
            owned_prepare,
            "validate_record_limit_or_throw",
            "frame_bytes > max_frame_bytes",
            "std::make_unique<detail::SyncReplicaTlsRecordWriteState>",
            "std::move(frame)",
            "begin_record_write_or_throw",
            "reservation_active = true",
        )
        and "std::string owned_frame(frame)" not in owned_prepare,
        "owned_tls_factory_moves_one_validated_frame_before_reservation",
        "the final frame allocation becomes continuation storage without another body copy",
    )
    owned_write = body(
        record,
        "write_sync_replica_tls_owned_record_until_or_throw(",
    )
    require(
        "write_sync_replica_tls_owned_record_until_or_throw" in record_h
        and ordered(
            owned_write,
            "prepare_sync_replica_tls_owned_record_write_or_throw",
            "result.frame_ownership_transferred = true",
            "writer.advance_or_throw()",
        ),
        "bounded_tls_driver_reports_actual_continuation_ownership",
        "an expired pre-prepare deadline cannot be counted as a TLS ownership handoff",
    )
    require(
        "std::string owned_frame(frame)" in transport
        and "prepare_sync_replica_tls_record_write_or_throw" in transport_h,
        "borrowed_tls_copy_contract_remains_available",
        "existing callers keep a separate explicit borrowed-frame authority path",
    )

    require(
        ordered(
            tls,
            "observe_served_response(inbound.response, result)",
            "response_disposition = inbound.response.disposition",
            "std::vector<SyncReplicaOperation>().swap",
            "std::vector<SyncReplicaReconciliationPayload>().swap",
            "write_sync_replica_tls_owned_record_until_or_throw",
            "std::move(inbound.response_frame)",
        ),
        "serve_path_releases_response_page_before_owned_tls_wait",
        "compact decisions survive while operation and payload vectors are dropped before backpressure",
    )
    require(
        "response_frame_owned_handoffs" in tls_h
        and "frame_ownership_transferred" in tls
        and "reconciliation_response_frame_owned_handoffs" in replica_cli
        and "reconciliation_response_frame_owned_handoffs" in process_test
        and "reconciliation_response_frame_owned_handoffs" in sync_process_test
        and "response_frame_owned_handoffs ==" in tls_test,
        "owned_handoff_accounting_reaches_runtime_and_shipping_json",
        "successful source responses prove one final-frame transfer into TLS continuation ownership",
    )

    require(
        "constexpr std::size_t payload_bytes = 8U * 1024U * 1024U" in memory_test
        and "AllocationScope measurement" in memory_test
        and "frame_bytes + auxiliary_budget" in memory_test
        and "largest_request <= frame.size() + 4096U" in memory_test
        and "decode_sync_replica_reconciliation_response_or_throw" in memory_test,
        "allocation_regression_rejects_second_page_sized_encode_copy",
        "an 8 MiB canonical response permits one final-frame allocation plus bounded auxiliary work",
    )
    require(
        "owned_factory_transfers_one_validated_frame_before_reservation"
        in continuation_audit
        and "borrowed factory copies the exact frame" in continuation_audit,
        "existing_tls_authority_audit_distinguishes_copy_and_transfer",
        "the refactor does not blur borrowed and owned frame semantics",
    )

    require(
        "not an operating-system peak-RSS claim" in normalized_design
        and "Companion receiver correction" in normalized_design
        and "not permission to raise the 64 MiB frontier" in normalized_design
        and "not measured 64 MiB or multi-terabyte peak RSS" in normalized_notes,
        "design_records_measurement_scope_and_remaining_copy_frontier",
        "allocator volume is not overstated as target-scale RSS or end-to-end streaming",
    )
    require(
        "DIRECT_RESPONSE_FRAME_AND_OWNED_TLS_HANDOFF_AUDIT_rev0997.md" in verifier
        and "REVISION_NOTES_rev0997.md" in verifier
        and "tests/sync_replica_reconciliation_frame_memory_test.cpp" in verifier
        and "tools/audit_sync_replica_response_frame_memory.py" in verifier,
        "release_verifier_binds_rev0997_slice",
        "the archive cannot omit implementation, memory regression, design, notes, or focused audit",
    )
    require(
        "rev0997" in readme.casefold()
        and "rev0997" in bootstrap.casefold()
        and "rev0997" in design.casefold()
        and "rev0997" in notes.casefold(),
        "visible_release_surfaces_name_rev0997",
        "README, runbook, design, and notes agree on the current revision",
    )
    require(
        all(
            token not in readme + bootstrap + design + notes
            for token in (
                "VALIDATION_PENDING_REV0997",
                "ARCHIVE_PENDING_REV0997",
                "CODENAME_PENDING_REV0997",
            )
        ),
        "final_validation_and_archive_are_sealed",
        "rev0997 cannot pass until validation and archive identity are final",
    )
    return emit(root, args.json, checks)


if __name__ == "__main__":
    raise SystemExit(main())
