#!/usr/bin/env python3
"""Prove strict linked-peer configuration and immutable live status.

Two config-driven retained services converge nested files in both directions,
serve owner-only Unix status snapshots while running, and remove their sockets
on graceful stop. Admission checks reject world-readable and unknown-key
configuration documents before any listener or status owner is created.
"""

from __future__ import annotations

import argparse
import errno
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import stat
import subprocess
import tempfile
import time
from typing import Any, Callable


VALID_ONION = (
    "pg6mmjiyjmcrsslvykfwnntlaru7p5svn6y2ymmju6nubxndf4pscryd.onion"
)
I2P_PEER = "peer-config-check.b32.i2p"

from test_anonsync_service_process import (
    finish_service,
    wait_for_service_listener,
    wait_for_tree_convergence,
)
from test_anonsync_sync_process import (
    fail,
    generate_tls_fixture,
    init_combined,
    reserve_port,
    run_json,
    tree_snapshot,
    unique_json_object_pairs,
)


def write_private_bytes(path: Path, value: bytes, label: str) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        os.write(descriptor, value)
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        fail(f"{label} {path} did not retain exact mode 0600")


def write_private_json(path: Path, value: dict[str, Any]) -> None:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"
    write_private_bytes(path, encoded.encode("utf-8"), "configuration")


def overwrite_regular_file(path: Path, value: bytes, label: str) -> None:
    observation = path.lstat()
    if not stat.S_ISREG(observation.st_mode) or stat.S_ISLNK(
        observation.st_mode
    ):
        fail(f"{label} target is not an exact regular file: {path}")
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        written = 0
        while written < len(value):
            count = os.write(descriptor, value[written:])
            if count <= 0:
                fail(f"{label} made no forward write progress")
            written += count
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


PRODUCT_PAYLOAD_STORE_IDENTITY_BASENAME = (
    ".anonsync-payload-store-identity-v3-reader-fence-v1"
)


def overwrite_payload_under_exclusive_store_lease(
    path: Path,
    value: bytes,
    label: str,
    *,
    timeout_seconds: float = 15.0,
    while_lease_held: Callable[[], None] | None = None,
) -> None:
    """Mutate one deliberate fault image without racing an authority scan.

    The payload store's cooperative writer protocol is an exclusive flock on
    the exact product identity inode. A corruption regression that truncates a
    digest-named object without that lease can race a shared authoritative scan
    and test a generic namespace-instability exit instead of the intended stable
    current-byte mismatch/recovery path.
    """

    identity_path = path.parent / PRODUCT_PAYLOAD_STORE_IDENTITY_BASENAME
    flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    descriptor = os.open(identity_path, flags)
    locked = False
    try:
        opened = os.fstat(descriptor)
        named = identity_path.lstat()
        if (
            not stat.S_ISREG(opened.st_mode)
            or stat.S_ISLNK(named.st_mode)
            or opened.st_dev != named.st_dev
            or opened.st_ino != named.st_ino
            or opened.st_nlink != 1
        ):
            fail(
                f"{label} identity anchor was not one exact linked regular "
                f"file: {identity_path}"
            )

        deadline = time.monotonic() + timeout_seconds
        while True:
            try:
                fcntl.flock(
                    descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB
                )
                locked = True
                break
            except OSError as error:
                if error.errno not in (errno.EACCES, errno.EAGAIN):
                    raise
                if time.monotonic() >= deadline:
                    fail(
                        f"{label} could not acquire the exact payload-store "
                        "exclusive lease"
                    )
                time.sleep(0.01)

        locked_named = identity_path.lstat()
        if (
            opened.st_dev != locked_named.st_dev
            or opened.st_ino != locked_named.st_ino
            or stat.S_ISLNK(locked_named.st_mode)
        ):
            fail(f"{label} identity pathname changed before lease acquisition")

        overwrite_regular_file(path, value, label)

        final_opened = os.fstat(descriptor)
        final_named = identity_path.lstat()
        if (
            final_opened.st_dev != opened.st_dev
            or final_opened.st_ino != opened.st_ino
            or final_named.st_dev != opened.st_dev
            or final_named.st_ino != opened.st_ino
        ):
            fail(f"{label} identity anchor changed while exclusively leased")
        if while_lease_held is not None:
            while_lease_held()
    finally:
        if locked:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def require_payload_quarantine_result(
    value: Any, label: str
) -> None:
    if not isinstance(value, dict):
        fail(f"{label} result was not an object")
    action = value.get("action")
    if action not in {"preserve", "release"}:
        fail(f"{label} reported unknown action {action!r}")
    disposition = value.get("disposition")
    preserve_dispositions = {
        "quarantined",
        "active_fault_mismatch",
        "payload_absent",
        "payload_already_repaired",
        "observed_digest_changed",
        "exact_quarantine_already_present",
    }
    release_dispositions = {
        "released",
        "exact_quarantine_absent",
        "active_fault_present",
    }
    accepted_dispositions = (
        preserve_dispositions if action == "preserve" else release_dispositions
    )
    if disposition not in accepted_dispositions:
        fail(
            f"{label} action {action!r} reported incompatible disposition "
            f"{disposition!r}"
        )
    expected = value.get("expected_content_sha256")
    requested = value.get("requested_observed_content_sha256")
    for field_name, digest in (
        ("expected_content_sha256", expected),
        ("requested_observed_content_sha256", requested),
    ):
        if not isinstance(digest, str) or len(digest) != 64:
            fail(f"{label} omitted exact {field_name}")
    current = value.get("current_observed_content_sha256")
    if current is not None and (
        not isinstance(current, str) or len(current) != 64
    ):
        fail(f"{label} current observed digest was neither exact nor null")
    basename = value.get("quarantine_basename")
    if basename is not None:
        exact_basename = (
            ".anonsync-payload-quarantine-v1-"
            f"{expected}-{requested}"
        )
        if basename != exact_basename:
            fail(
                f"{label} quarantine basename was {basename!r}, expected "
                f"{exact_basename!r}"
            )
    size_bytes = value.get("size_bytes")
    if not isinstance(size_bytes, int) or size_bytes < 0:
        fail(f"{label} omitted bounded size_bytes")


def require_payload_quarantine_inventory(
    value: Any, label: str
) -> None:
    if not isinstance(value, dict):
        fail(f"{label} inventory was not an object")
    known = value.get("observation_known")
    if not isinstance(known, bool):
        fail(f"{label} inventory omitted observation_known")
    age = value.get("last_observation_age_milliseconds")
    if known:
        if not isinstance(age, int) or age < 0:
            fail(f"{label} known inventory omitted a bounded observation age")
    elif age is not None:
        fail(f"{label} unknown inventory invented an observation age")

    entry_limit = value.get("entry_limit")
    byte_limit = value.get("byte_limit")
    entry_count = value.get("entry_count")
    total_bytes = value.get("total_bytes")
    entries = value.get("entries")
    if entry_limit != 16:
        fail(f"{label} inventory entry limit was {entry_limit!r}, expected 16")
    for field_name, field in (
        ("byte_limit", byte_limit),
        ("entry_count", entry_count),
        ("total_bytes", total_bytes),
    ):
        if not isinstance(field, int) or field < 0:
            fail(f"{label} inventory omitted bounded {field_name}")
    if not isinstance(entries, list):
        fail(f"{label} inventory entries were not an array")
    if entry_count != len(entries) or entry_count > entry_limit:
        fail(
            f"{label} inventory count disagreed with its bounded entries: "
            f"{json.dumps(value, sort_keys=True)}"
        )
    if total_bytes > byte_limit:
        fail(f"{label} inventory exceeded its byte frontier")

    canonical_pairs: list[tuple[str, str]] = []
    summed_bytes = 0
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"{label} inventory entry {index} was not an object")
        if set(entry) != {
            "expected_content_sha256",
            "observed_content_sha256",
            "size_bytes",
        }:
            fail(
                f"{label} inventory entry {index} had a noncanonical shape: "
                f"{json.dumps(entry, sort_keys=True)}"
            )
        expected = entry.get("expected_content_sha256")
        observed = entry.get("observed_content_sha256")
        for digest_name, digest in (("expected", expected), ("observed", observed)):
            if not isinstance(digest, str) or len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                fail(
                    f"{label} inventory entry {index} omitted canonical "
                    f"{digest_name} SHA-256"
                )
        if expected == observed:
            fail(f"{label} inventory entry {index} used an identical digest pair")
        size_bytes = entry.get("size_bytes")
        if not isinstance(size_bytes, int) or size_bytes < 0:
            fail(f"{label} inventory entry {index} omitted bounded size_bytes")
        canonical_pairs.append((expected, observed))
        summed_bytes += size_bytes
    if canonical_pairs != sorted(canonical_pairs) or len(set(canonical_pairs)) != len(
        canonical_pairs
    ):
        fail(f"{label} inventory was not canonical and duplicate-free")
    if summed_bytes != total_bytes:
        fail(f"{label} inventory byte total disagreed with its entries")
    if not known and (entry_count != 0 or total_bytes != 0):
        fail(f"{label} unknown inventory invented retained evidence")


def is_canonical_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def is_canonical_historical_source_cutpoint(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    if len(value) == 268 and value.startswith("v4:exact:"):
        return (
            value[73] == ":"
            and value[138] == ":"
            and value[203] == ":"
            and is_canonical_sha256(value[9:73])
            and is_canonical_sha256(value[74:138])
            and is_canonical_sha256(value[139:203])
            and is_canonical_sha256(value[204:268])
        )
    if len(value) == 203 and value.startswith("v3:exact:"):
        return (
            value[73] == ":"
            and value[138] == ":"
            and is_canonical_sha256(value[9:73])
            and is_canonical_sha256(value[74:138])
            and is_canonical_sha256(value[139:203])
        )
    if len(value) == 132 and value.startswith("v1:"):
        return (
            value[67] == ":"
            and is_canonical_sha256(value[3:67])
            and is_canonical_sha256(value[68:132])
        )
    if len(value) == 141 and value.startswith("v4:metadata:"):
        return (
            value[76] == ":"
            and is_canonical_sha256(value[12:76])
            and is_canonical_sha256(value[77:141])
        )
    return len(value) == 76 and value.startswith("v2:metadata:") and (
        is_canonical_sha256(value[12:76])
    )


def require_historical_version_query(query: Any, label: str) -> None:
    if not isinstance(query, dict) or set(query) != {
        "inspection_mode", "maximum_entries", "canonical_path",
        "start_after_operation_id", "expected_source_cutpoint",
    }:
        fail(f"{label} historical query was not canonical")
    inspection_mode = query.get("inspection_mode")
    if inspection_mode not in {
        "exact_payload_availability", "causal_metadata_only",
    }:
        fail(f"{label} historical query omitted its inspection mode")
    maximum_entries = query.get("maximum_entries")
    if not isinstance(maximum_entries, int) or not (1 <= maximum_entries <= 1024):
        fail(f"{label} historical query omitted its bounded entry limit")
    canonical_path = query.get("canonical_path")
    if canonical_path is not None and (
        not isinstance(canonical_path, str) or not canonical_path
    ):
        fail(f"{label} historical query path was neither string nor null")
    cursor = query.get("start_after_operation_id")
    if cursor is not None and not is_canonical_sha256(cursor):
        fail(f"{label} historical query cursor was neither digest nor null")
    source_cutpoint = query.get("expected_source_cutpoint")
    if source_cutpoint is not None:
        if not is_canonical_historical_source_cutpoint(source_cutpoint):
            fail(f"{label} historical query source cutpoint was not canonical")
        if inspection_mode == "exact_payload_availability" and not (
            source_cutpoint.startswith("v4:exact:")
            or source_cutpoint.startswith("v3:exact:")
            or source_cutpoint.startswith("v1:")
        ):
            fail(f"{label} exact historical query carried a metadata cutpoint")
        if inspection_mode == "causal_metadata_only" and not (
            source_cutpoint.startswith("v4:metadata:")
            or source_cutpoint.startswith("v2:metadata:")
        ):
            fail(f"{label} metadata historical query carried an exact cutpoint")


def require_historical_payload_reachability(value: Any, label: str) -> None:
    if not isinstance(value, dict) or set(value) != {
        "scope", "reclaimable_authority", "class_totals_overlap",
        "payload_entry_count", "payload_indexed_bytes", "current_visible",
        "superseded_active", "inactive_evidence", "explicit_pins",
        "retained_union",
        "unreferenced_by_retained_file_operations_count",
        "unreferenced_by_retained_file_operations_bytes",
    }:
        fail(f"{label} retained-payload reachability was not canonical")
    if value["scope"] != "share_retained_file_operations":
        fail(f"{label} retained-payload reachability changed scope")
    if value["reclaimable_authority"] is not False:
        fail(f"{label} retained-payload reachability claimed collection authority")
    if value["class_totals_overlap"] is not True:
        fail(f"{label} retained-payload reachability hid overlapping classes")
    for field in (
        "payload_entry_count", "payload_indexed_bytes",
        "unreferenced_by_retained_file_operations_count",
        "unreferenced_by_retained_file_operations_bytes",
    ):
        if not isinstance(value[field], int) or value[field] < 0:
            fail(f"{label} retained-payload reachability omitted bounded {field}")

    classes: dict[str, dict[str, int]] = {}
    class_fields = {
        "file_operation_count", "distinct_content_count",
        "present_content_count", "present_content_bytes",
        "missing_content_count",
    }
    for name in (
        "current_visible", "superseded_active", "inactive_evidence",
        "explicit_pins", "retained_union",
    ):
        item = value[name]
        if not isinstance(item, dict) or set(item) != class_fields:
            fail(f"{label} retained-payload class {name} was not canonical")
        for field in class_fields:
            if not isinstance(item[field], int) or item[field] < 0:
                fail(f"{label} retained-payload class {name} omitted {field}")
        if item["present_content_count"] + item["missing_content_count"] != item[
            "distinct_content_count"
        ]:
            fail(f"{label} retained-payload class {name} did not partition content")
        classes[name] = item

    if classes["retained_union"]["file_operation_count"] != sum(
        classes[name]["file_operation_count"]
        for name in ("current_visible", "superseded_active", "inactive_evidence")
    ):
        fail(f"{label} retained-payload operation classes did not partition evidence")
    if classes["retained_union"]["present_content_count"] + value[
        "unreferenced_by_retained_file_operations_count"
    ] != value["payload_entry_count"]:
        fail(f"{label} retained-payload objects did not partition the snapshot")
    if classes["retained_union"]["present_content_bytes"] + value[
        "unreferenced_by_retained_file_operations_bytes"
    ] != value["payload_indexed_bytes"]:
        fail(f"{label} retained-payload bytes did not partition the snapshot")


def require_historical_version_inventory(
    inventory: Any, label: str
) -> None:
    if not isinstance(inventory, dict):
        fail(f"{label} historical inventory was not an object")
    query = inventory.get("query")
    require_historical_version_query(query, label)
    mode = query["inspection_mode"]
    for digest_field in (
        "source_operation_set_digest",
        "source_historical_version_pin_set_digest",
        "source_visible_state_digest",
    ):
        if not is_canonical_sha256(inventory.get(digest_field)):
            fail(f"{label} historical inventory omitted {digest_field}")
    evidence_digest = inventory.get("source_evidence_set_digest")
    payload_digest = inventory.get("source_payload_snapshot_digest")
    if mode == "exact_payload_availability":
        if not is_canonical_sha256(evidence_digest):
            fail(f"{label} exact historical inventory omitted evidence digest")
        if not is_canonical_sha256(payload_digest):
            fail(f"{label} exact historical inventory omitted payload digest")
    elif evidence_digest is not None or payload_digest is not None:
        fail(f"{label} metadata historical inventory invented an exact digest")
    source_cutpoint = inventory.get("source_cutpoint")
    if not is_canonical_historical_source_cutpoint(source_cutpoint):
        fail(f"{label} historical inventory omitted canonical source_cutpoint")
    expected_source_cutpoint = (
        "v4:exact:" + inventory["source_operation_set_digest"] + ":" +
        evidence_digest + ":" +
        inventory["source_historical_version_pin_set_digest"] + ":" +
        payload_digest
        if mode == "exact_payload_availability"
        else "v4:metadata:" + inventory["source_operation_set_digest"] +
        ":" + inventory["source_historical_version_pin_set_digest"]
    )
    if source_cutpoint != expected_source_cutpoint:
        fail(f"{label} historical inventory source token disagreed with its mode")

    always_integer_fields = (
        "source_replica_state_generation",
        "historical_version_pin_count",
        "historical_file_operation_count",
        "historical_file_operation_count_after_cursor",
        "entry_limit",
    )
    for integer_field in always_integer_fields:
        value = inventory.get(integer_field)
        if not isinstance(value, int) or value < 0:
            fail(
                f"{label} historical inventory omitted bounded "
                f"{integer_field}"
            )
    payload_integer_fields = (
        "payload_scan_hashed_entries",
        "payload_scan_hashed_bytes",
        "payload_scan_reused_entries",
        "payload_scan_reused_bytes",
        "payload_present_count",
        "restore_ready_count",
    )
    for integer_field in payload_integer_fields:
        value = inventory.get(integer_field)
        if mode == "exact_payload_availability":
            if not isinstance(value, int) or value < 0:
                fail(
                    f"{label} exact historical inventory omitted bounded "
                    f"{integer_field}"
                )
        elif value is not None:
            fail(
                f"{label} metadata historical inventory invented "
                f"{integer_field}"
            )
    reachability = inventory.get("retained_payload_reachability")
    if mode == "exact_payload_availability":
        require_historical_payload_reachability(reachability, label)
    elif reachability is not None:
        fail(f"{label} metadata historical inventory invented reachability")

    if inventory.get("entry_limit") != query["maximum_entries"]:
        fail(f"{label} historical inventory disagreed with its query limit")
    if not isinstance(inventory.get("entry_limit_frontier_reached"), bool):
        fail(f"{label} historical inventory omitted entry frontier state")
    if inventory.get("status_byte_limit") != 256 * 1024:
        fail(f"{label} historical inventory omitted its status byte limit")
    if not isinstance(inventory.get("status_byte_frontier_reached"), bool):
        fail(f"{label} historical inventory omitted status byte frontier state")
    if not isinstance(inventory.get("truncated"), bool):
        fail(f"{label} historical inventory omitted truncation state")
    next_cursor = inventory.get("next_start_after_operation_id")
    if next_cursor is not None and not is_canonical_sha256(next_cursor):
        fail(f"{label} historical inventory next cursor was invalid")
    entries = inventory.get("entries")
    if not isinstance(entries, list) or len(entries) > query["maximum_entries"]:
        fail(f"{label} historical inventory entries were not bounded")
    total_count = inventory["historical_file_operation_count"]
    after_cursor_count = inventory[
        "historical_file_operation_count_after_cursor"
    ]
    if total_count < after_cursor_count or after_cursor_count < len(entries):
        fail(f"{label} historical inventory cursor counts were incoherent")
    if mode == "exact_payload_availability" and (
        inventory["payload_present_count"] > total_count
        or inventory["restore_ready_count"] > inventory["payload_present_count"]
    ):
        fail(f"{label} historical inventory aggregate counts were incoherent")
    canonical_order: list[tuple[str, str, int, int, str]] = []
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            fail(f"{label} historical entry {index} was not an object")
        for digest_field in (
            "operation_id",
            "content_sha256",
            "current_primary_operation_id",
        ):
            if not is_canonical_sha256(entry.get(digest_field)):
                fail(
                    f"{label} historical entry {index} omitted "
                    f"{digest_field}"
                )
        if not isinstance(entry.get("canonical_path"), str) or not entry[
            "canonical_path"
        ]:
            fail(f"{label} historical entry {index} omitted canonical_path")
        if query["canonical_path"] is not None and entry[
            "canonical_path"
        ] != query["canonical_path"]:
            fail(f"{label} historical entry escaped its selected path")
        if not isinstance(entry.get("actor_device_id"), str) or not entry[
            "actor_device_id"
        ]:
            fail(f"{label} historical entry {index} omitted actor_device_id")
        for integer_field in (
            "size_bytes",
            "actor_epoch",
            "counter",
            "visible_head_count",
        ):
            field = entry.get(integer_field)
            if not isinstance(field, int) or field < 0:
                fail(
                    f"{label} historical entry {index} omitted bounded "
                    f"{integer_field}"
                )
        if entry.get("current_primary_kind") not in {"file", "tombstone"}:
            fail(f"{label} historical entry {index} omitted primary kind")
        if not isinstance(entry.get("pinned"), bool):
            fail(f"{label} historical entry {index} omitted pinned state")
        for availability_field in ("payload_present", "restore_ready"):
            field = entry.get(availability_field)
            if mode == "exact_payload_availability":
                if not isinstance(field, bool):
                    fail(
                        f"{label} exact historical entry {index} omitted "
                        f"{availability_field}"
                    )
            elif field is not None:
                fail(
                    f"{label} metadata historical entry {index} invented "
                    f"{availability_field}"
                )
        if mode == "exact_payload_availability" and entry[
            "restore_ready"
        ] and not entry["payload_present"]:
            fail(f"{label} historical entry was restore-ready without bytes")
        canonical_order.append(
            (
                entry["canonical_path"],
                entry["actor_device_id"],
                entry["actor_epoch"],
                -entry["counter"],
                entry["operation_id"],
            )
        )
    if canonical_order != sorted(canonical_order):
        fail(f"{label} historical inventory was not canonical")
    expected_entry_frontier = after_cursor_count > query["maximum_entries"]
    expected_byte_frontier = len(entries) < min(
        after_cursor_count, query["maximum_entries"]
    )
    if inventory["entry_limit_frontier_reached"] != expected_entry_frontier:
        fail(f"{label} historical entry frontier disagreed with source count")
    if inventory["status_byte_frontier_reached"] != expected_byte_frontier:
        fail(f"{label} historical byte frontier disagreed with returned prefix")
    expected_truncated = expected_entry_frontier or expected_byte_frontier
    if inventory["truncated"] != expected_truncated:
        fail(f"{label} historical truncation disagreed with its stop reasons")
    if expected_truncated and not entries:
        fail(f"{label} historical truncated page retained no continuation")
    expected_next = entries[-1]["operation_id"] if expected_truncated else None
    if next_cursor != expected_next:
        fail(f"{label} historical next cursor did not bind the page tail")


def require_historical_version_restore(restored: Any, label: str) -> None:
    if not isinstance(restored, dict):
        fail(f"{label} historical restore was not an object")
    if restored.get("disposition") not in {
        "published",
        "adopted_visible_operation",
    }:
        fail(f"{label} historical restore omitted its disposition")
    for digest_field in (
        "historical_operation_id",
        "replaced_visible_operation_id",
        "restored_operation_id",
        "content_sha256",
        "catalog_operation_id",
    ):
        if not is_canonical_sha256(restored.get(digest_field)):
            fail(f"{label} historical restore omitted {digest_field}")
    if restored["restored_operation_id"] != restored["catalog_operation_id"]:
        fail(f"{label} historical restore catalog did not name its successor")
    if restored["restored_operation_id"] in {
        restored["historical_operation_id"],
        restored["replaced_visible_operation_id"],
    }:
        fail(f"{label} historical restore reactivated prior evidence")
    if not isinstance(restored.get("canonical_path"), str) or not restored[
        "canonical_path"
    ]:
        fail(f"{label} historical restore omitted canonical_path")
    if not isinstance(restored.get("size_bytes"), int) or restored[
        "size_bytes"
    ] < 0:
        fail(f"{label} historical restore omitted bounded size_bytes")


def require_historical_version_pin_update(update: Any, label: str) -> None:
    if not isinstance(update, dict) or set(update) != {
        "disposition", "operation_id", "state_generation", "pin_count",
        "pin_set_digest",
    }:
        fail(f"{label} historical pin update was not canonical")
    if update["disposition"] not in {
        "pinned", "already_pinned", "unpinned", "already_unpinned",
    }:
        fail(f"{label} historical pin update omitted its disposition")
    if not is_canonical_sha256(update["operation_id"]) or not (
        isinstance(update["state_generation"], int)
        and update["state_generation"] >= 0
        and isinstance(update["pin_count"], int)
        and update["pin_count"] >= 0
        and is_canonical_sha256(update["pin_set_digest"])
    ):
        fail(f"{label} historical pin update omitted durable result fields")


def require_retention_plan_query(query: Any, label: str) -> None:
    if not isinstance(query, dict) or set(query) != {
        "maximum_entries", "start_after_content_sha256",
        "expected_source_cutpoint",
    }:
        fail(f"{label} retention-plan query was not canonical")
    if not isinstance(query["maximum_entries"], int) or not (
        1 <= query["maximum_entries"] <= 1024
    ):
        fail(f"{label} retention-plan query omitted its bounded limit")
    cursor = query["start_after_content_sha256"]
    if cursor is not None and not is_canonical_sha256(cursor):
        fail(f"{label} retention-plan query cursor was not canonical")
    cutpoint = query["expected_source_cutpoint"]
    if cutpoint is not None and not (
        isinstance(cutpoint, str) and cutpoint.startswith("v4:exact:")
    ):
        fail(f"{label} retention-plan query accepted a non-exact cutpoint")


def require_retention_plan(plan: Any, label: str) -> None:
    if not isinstance(plan, dict):
        fail(f"{label} retention plan was not an object")
    require_retention_plan_query(plan.get("query"), label)
    if plan.get("scope") != "complete_physical_payload_namespace":
        fail(f"{label} retention plan omitted its physical namespace scope")
    for forbidden_authority in (
        "reclaimable_authority", "quota_policy_applied",
        "grace_period_applied", "writer_fenced_collection",
        "durable_mark_persisted",
    ):
        if plan.get(forbidden_authority) is not False:
            fail(
                f"{label} retention plan invented {forbidden_authority}"
            )
    if plan.get("writer_fenced_observation") is not True or plan.get(
        "cooperating_new_namespace_activity_excluded_during_observation"
    ) is not True:
        fail(f"{label} retention plan omitted its writer-fenced observation")
    for digest_field in (
        "source_operation_set_digest", "source_evidence_set_digest",
        "source_historical_version_pin_set_digest",
        "source_visible_state_digest", "source_payload_snapshot_digest",
        "source_payload_transient_namespace_digest",
        "unreferenced_candidate_set_digest",
        "durable_candidate_witness_digest",
        "writer_fenced_candidate_page_digest",
        "exact_deletion_free_mark_digest",
    ):
        if not is_canonical_sha256(plan.get(digest_field)):
            fail(f"{label} retention plan omitted {digest_field}")
    live_capabilities = plan.get("live_payload_capabilities")
    if not isinstance(live_capabilities, dict) or set(live_capabilities) != {
        "process_store_scope_digest",
        "process_store_scope_incarnation_digest", "capability_set_digest",
        "snapshot_count", "opened_payload_count", "targeted_access_count",
        "mutation_batch_count", "distinct_opened_payload_root_count",
        "distinct_opened_payload_root_bytes",
        "may_reopen_all_current_payloads", "rooted_physical_payload_count",
        "rooted_physical_payload_bytes", "unreferenced_rooted_payload_count",
        "unreferenced_rooted_payload_bytes",
    }:
        fail(f"{label} retention plan omitted its live capability cutpoint")
    for digest_field in (
        "process_store_scope_digest",
        "process_store_scope_incarnation_digest", "capability_set_digest",
    ):
        if not is_canonical_sha256(live_capabilities.get(digest_field)):
            fail(f"{label} live capability cutpoint omitted {digest_field}")
    for integer_field in (
        "snapshot_count", "opened_payload_count", "targeted_access_count",
        "mutation_batch_count", "distinct_opened_payload_root_count",
        "distinct_opened_payload_root_bytes", "rooted_physical_payload_count",
        "rooted_physical_payload_bytes", "unreferenced_rooted_payload_count",
        "unreferenced_rooted_payload_bytes",
    ):
        value = live_capabilities.get(integer_field)
        if not isinstance(value, int) or value < 0:
            fail(f"{label} live capability cutpoint omitted {integer_field}")
    if not isinstance(
        live_capabilities.get("may_reopen_all_current_payloads"), bool
    ):
        fail(f"{label} live capability cutpoint omitted all-payload scope")
    if live_capabilities["may_reopen_all_current_payloads"] != any(
        live_capabilities[field] != 0
        for field in (
            "snapshot_count", "targeted_access_count", "mutation_batch_count",
        )
    ):
        fail(f"{label} live capability all-payload scope was incoherent")
    if (
        live_capabilities["unreferenced_rooted_payload_count"]
        > live_capabilities["rooted_physical_payload_count"]
        or live_capabilities["unreferenced_rooted_payload_bytes"]
        > live_capabilities["rooted_physical_payload_bytes"]
    ):
        fail(f"{label} live capability unreferenced roots exceeded all roots")
    expected_transient_authority = {
        "payload_store_transient_namespace_bound": True,
        "durable_receiver_restart_obligations_bound": True,
        "same_process_store_live_payload_capabilities_bound": True,
        "independently_opened_same_process_store_owner_live_payload_capabilities_bound": True,
        "independent_store_owner_live_payload_capabilities_bound": False,
        "cross_process_live_payload_capabilities_bound": False,
        "already_copied_response_bytes_bound": False,
        "active_pass_transient_roots_bound": False,
        "opened_sender_transient_roots_bound": False,
        "mutation_batch_transient_roots_bound": False,
        "external_transient_root_model_complete": False,
    }
    for field, expected in expected_transient_authority.items():
        if plan.get(field) is not expected:
            fail(
                f"{label} retention plan reported invalid {field}: "
                f"{plan.get(field)!r}"
            )
    if plan.get("writer_fenced_observation") is not True:
        fail(f"{label} retention plan omitted its store-global writer fence")
    if plan.get(
        "cooperating_new_namespace_activity_excluded_during_observation"
    ) is not True:
        fail(f"{label} retention plan did not exclude cooperating namespace activity")
    source_cutpoint = plan.get("source_cutpoint")
    if not isinstance(source_cutpoint, str) or not source_cutpoint.startswith(
        "v4:exact:"
    ):
        fail(f"{label} retention plan omitted its exact v4 cutpoint")
    if not is_canonical_sha256(
        plan.get("source_replica_database_incarnation_sha256")
    ):
        fail(f"{label} retention plan omitted its database incarnation")
    recovery_epoch = plan.get("source_replica_database_recovery_epoch")
    if not isinstance(recovery_epoch, int) or recovery_epoch <= 0:
        fail(f"{label} retention plan omitted its database recovery epoch")
    for integer_field in (
        "source_replica_state_generation", "historical_version_pin_count",
        "payload_transient_entries", "payload_transient_bytes",
        "payload_transient_reserved_bytes",
        "payload_scan_hashed_entries", "payload_scan_hashed_bytes",
        "payload_scan_reused_entries", "payload_scan_reused_bytes",
        "physical_payload_count_after_cursor", "entry_limit",
        "writer_fenced_candidate_page_entry_count",
        "returned_unreferenced_candidate_count",
        "returned_candidate_payload_use_exclusive_available_count",
        "returned_candidate_payload_use_busy_count",
    ):
        field = plan.get(integer_field)
        if not isinstance(field, int) or field < 0:
            fail(f"{label} retention plan omitted bounded {integer_field}")
    if plan["payload_transient_reserved_bytes"] < plan[
        "payload_transient_bytes"
    ]:
        fail(f"{label} retention reservation fell below physical transient bytes")
    entries = plan.get("entries")
    if not isinstance(entries, list):
        fail(f"{label} retention plan omitted entries")
    digests: list[str] = []
    class_counts = {
        "current_or_explicit_pin": [0, 0],
        "retained_history_or_evidence": [0, 0],
        "unreferenced_by_retained_file_operations": [0, 0],
    }
    visible_candidate_count = 0
    visible_candidate_available_count = 0
    visible_candidate_busy_count = 0
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != {
            "content_sha256", "size_bytes", "current_visible",
            "superseded_active", "inactive_evidence", "explicit_pin",
            "same_process_store_live_capability",
            "payload_use_disposition", "disposition",
        }:
            fail(f"{label} retention entry {index} was not canonical")
        digest = entry["content_sha256"]
        if not is_canonical_sha256(digest):
            fail(f"{label} retention entry {index} omitted its digest")
        digests.append(digest)
        size = entry["size_bytes"]
        if not isinstance(size, int) or size < 0:
            fail(f"{label} retention entry {index} omitted bounded bytes")
        for root_field in (
            "current_visible", "superseded_active", "inactive_evidence",
            "explicit_pin", "same_process_store_live_capability",
        ):
            if not isinstance(entry[root_field], bool):
                fail(f"{label} retention entry omitted {root_field}")
        payload_use_disposition = entry["payload_use_disposition"]
        if payload_use_disposition not in (
            "not_applicable", "exclusive_available_at_cutpoint",
            "busy_at_cutpoint",
        ):
            fail(f"{label} retention entry omitted payload-use disposition")
        disposition = entry["disposition"]
        if disposition not in class_counts:
            fail(f"{label} retention entry omitted its disposition")
        if disposition == "current_or_explicit_pin" and not (
            entry["current_visible"] or entry["explicit_pin"]
        ):
            fail(f"{label} required payload had neither current nor pin root")
        if disposition == "retained_history_or_evidence" and not (
            entry["superseded_active"] or entry["inactive_evidence"]
        ):
            fail(f"{label} history payload had no historical evidence root")
        if disposition == "unreferenced_by_retained_file_operations" and any(
            entry[root_field]
            for root_field in (
                "current_visible", "superseded_active", "inactive_evidence",
                "explicit_pin",
            )
        ):
            fail(f"{label} unreferenced payload retained a replica root")
        if disposition == "unreferenced_by_retained_file_operations":
            visible_candidate_count += 1
            if payload_use_disposition == "exclusive_available_at_cutpoint":
                visible_candidate_available_count += 1
            elif payload_use_disposition == "busy_at_cutpoint":
                visible_candidate_busy_count += 1
            else:
                fail(f"{label} unreferenced payload was not inode-probed")
        elif payload_use_disposition != "not_applicable":
            fail(f"{label} retained payload carried candidate-only probe state")
        class_counts[disposition][0] += 1
        class_counts[disposition][1] += size
    if digests != sorted(digests) or len(set(digests)) != len(digests):
        fail(f"{label} retention plan was not exact digest order")
    logical_page_entry_count = plan[
        "writer_fenced_candidate_page_entry_count"
    ]
    if (
        logical_page_entry_count < len(entries)
        or logical_page_entry_count > min(
            plan["physical_payload_count_after_cursor"], plan["entry_limit"]
        )
        or (
            not plan.get("status_byte_frontier_reached")
            and logical_page_entry_count != len(entries)
        )
    ):
        fail(f"{label} writer-fenced logical page cardinality was incoherent")
    returned_candidate_count = plan["returned_unreferenced_candidate_count"]
    returned_available_count = plan[
        "returned_candidate_payload_use_exclusive_available_count"
    ]
    returned_busy_count = plan["returned_candidate_payload_use_busy_count"]
    if (
        returned_candidate_count > logical_page_entry_count
        or returned_available_count + returned_busy_count
        != returned_candidate_count
    ):
        fail(f"{label} retention candidate probe partition was incoherent")
    if (
        visible_candidate_count > returned_candidate_count
        or visible_candidate_available_count > returned_available_count
        or visible_candidate_busy_count > returned_busy_count
    ):
        fail(f"{label} visible candidate prefix exceeded writer-fenced evidence")
    if not plan.get("status_byte_frontier_reached") and (
        visible_candidate_count != returned_candidate_count
        or visible_candidate_available_count != returned_available_count
        or visible_candidate_busy_count != returned_busy_count
    ):
        fail(f"{label} complete returned page disagreed with probe accounting")
    totals = plan.get("disposition_totals")
    if not isinstance(totals, dict) or set(totals) != set(class_counts):
        fail(f"{label} retention plan omitted disposition totals")
    # Totals cover the complete physical namespace, so a paginated page may be
    # only a prefix. It can never exceed the complete aggregate.
    for disposition, page in class_counts.items():
        total = totals.get(disposition)
        if not isinstance(total, dict) or set(total) != {
            "payload_count", "payload_bytes",
        }:
            fail(f"{label} retention class {disposition} was not canonical")
        if total["payload_count"] < page[0] or total["payload_bytes"] < page[1]:
            fail(f"{label} retention class total was below its page prefix")
    after_cursor = plan["physical_payload_count_after_cursor"]
    if after_cursor < len(entries):
        fail(f"{label} retention cursor count was below returned entries")
    entry_frontier = after_cursor > plan["entry_limit"]
    byte_frontier = len(entries) < min(after_cursor, plan["entry_limit"])
    if plan.get("entry_limit_frontier_reached") != entry_frontier or plan.get(
        "status_byte_frontier_reached"
    ) != byte_frontier:
        fail(f"{label} retention plan frontiers disagreed with the page")
    if plan.get("truncated") != (entry_frontier or byte_frontier):
        fail(f"{label} retention plan truncation was incoherent")
    expected_next = entries[-1]["content_sha256"] if plan["truncated"] else None
    if plan.get("next_start_after_content_sha256") != expected_next:
        fail(f"{label} retention plan next cursor did not bind its tail")


def require_historical_version_status(
    value: dict[str, Any], label: str
) -> None:
    history = value.get("historical_versions")
    if not isinstance(history, dict):
        fail(f"{label} status omitted historical-version state")
    for integer_field in (
        "requested_generation",
        "started_generation",
        "completed_generation",
        "retry_delay_milliseconds",
    ):
        field = history.get(integer_field)
        if not isinstance(field, int) or field < 0:
            fail(f"{label} historical versions omitted {integer_field}")
    requested = history["requested_generation"]
    started = history["started_generation"]
    completed = history["completed_generation"]
    if completed > started or started > requested:
        fail(f"{label} historical-version generations were incoherent")
    if not isinstance(history.get("pending"), bool) or history[
        "pending"
    ] != (requested > completed):
        fail(f"{label} historical-version pending state was incoherent")
    action = history.get("action")
    query = history.get("query")
    retention_plan_query = history.get("retention_plan_query")
    operation_id = history.get("operation_id")
    expected_current_operation_id = history.get(
        "expected_current_operation_id"
    )
    if requested == 0:
        if (
            action is not None
            or query is not None
            or retention_plan_query is not None
            or operation_id is not None
            or expected_current_operation_id is not None
        ):
            fail(f"{label} invented historical-version request state")
    elif action == "inspect":
        if (
            retention_plan_query is not None
            or
            operation_id is not None
            or expected_current_operation_id is not None
        ):
            fail(f"{label} inspection invented restore identity")
        require_historical_version_query(query, label)
    elif action == "retention_plan":
        if (
            query is not None
            or operation_id is not None
            or expected_current_operation_id is not None
        ):
            fail(f"{label} retention plan invented another action identity")
        require_retention_plan_query(retention_plan_query, label)
    elif action == "restore":
        if (
            query is not None
            or retention_plan_query is not None
            or not is_canonical_sha256(operation_id)
        ):
            fail(f"{label} restore omitted its exact operation ID")
        if expected_current_operation_id is not None and (
            not is_canonical_sha256(expected_current_operation_id)
            or expected_current_operation_id == operation_id
        ):
            fail(f"{label} restore omitted its exact distinct current head")
    elif action in {"pin", "unpin"}:
        if (
            query is not None
            or retention_plan_query is not None
            or not is_canonical_sha256(operation_id)
            or expected_current_operation_id is not None
        ):
            fail(f"{label} retention update omitted its exact operation ID")
    else:
        fail(f"{label} historical versions omitted its exact action")
    inventory = history.get("last_inventory")
    if inventory is not None:
        require_historical_version_inventory(inventory, label)
        if action == "inspect" and inventory.get("query") != query:
            fail(f"{label} historical status changed the completed query")
    retention_plan = history.get("last_retention_plan")
    if retention_plan is not None:
        require_retention_plan(retention_plan, label)
        if action == "retention_plan" and retention_plan.get("query") != (
            retention_plan_query
        ):
            fail(f"{label} retention status changed the completed query")
    restored = history.get("last_restore")
    if restored is not None:
        require_historical_version_restore(restored, label)
    pin_update = history.get("last_pin_update")
    if pin_update is not None:
        require_historical_version_pin_update(pin_update, label)
    failure = history.get("last_failure")
    failure_class = history.get("last_failure_class")
    source_change_stage = history.get("last_source_change_stage")
    if failure is not None and not isinstance(failure, str):
        fail(f"{label} historical-version failure was neither string nor null")
    if failure is None:
        if failure_class is not None or source_change_stage is not None:
            fail(f"{label} historical-version status classified no failure")
    elif failure_class == "operation_failed":
        if source_change_stage is not None:
            fail(f"{label} ordinary historical failure invented source drift")
    elif failure_class == "source_changed":
        if source_change_stage not in {
            "operation_set_before_payload_observation",
            "operation_set_during_payload_observation",
            "historical_version_pin_set_before_payload_observation",
            "historical_version_pin_set_during_payload_observation",
            "payload_snapshot",
            "restore_current_operation",
        }:
            fail(f"{label} historical source drift omitted its exact stage")
    else:
        fail(f"{label} historical-version failure class was invalid")


def require_payload_terminal_verification_work(
    value: Any, label: str
) -> tuple[int, int]:
    if not isinstance(value, dict) or set(value) != {
        "content_sha256", "total_size_bytes", "verified_offset_bytes",
        "remaining_bytes",
    }:
        fail(f"{label} terminal-verification work was not canonical")
    if not is_canonical_sha256(value.get("content_sha256")):
        fail(f"{label} terminal-verification work omitted its exact digest")
    total = value.get("total_size_bytes")
    offset = value.get("verified_offset_bytes")
    remaining = value.get("remaining_bytes")
    if (
        not isinstance(total, int) or total <= 0
        or not isinstance(offset, int) or offset < 0 or offset >= total
        or not isinstance(remaining, int) or remaining != total - offset
    ):
        fail(f"{label} terminal-verification work had an invalid byte frontier")
    return total, offset


def require_payload_terminal_verification_status(
    value: dict[str, Any], label: str
) -> None:
    terminal = value.get("payload_terminal_verification")
    if not isinstance(terminal, dict) or set(terminal) != {
        "observation_known", "pending_entry_count", "pending_total_bytes",
        "pending_verified_bytes", "next_work",
    }:
        fail(f"{label} status omitted canonical terminal-verification state")
    known = terminal.get("observation_known")
    count = terminal.get("pending_entry_count")
    total = terminal.get("pending_total_bytes")
    verified = terminal.get("pending_verified_bytes")
    if not isinstance(known, bool):
        fail(f"{label} terminal-verification observation state was not boolean")
    if any(not isinstance(field, int) or field < 0 for field in (
        count, total, verified,
    )):
        fail(f"{label} terminal-verification totals were not bounded integers")
    if verified > total:
        fail(f"{label} terminal-verification verified bytes exceeded total bytes")
    work = terminal.get("next_work")
    if not known:
        if count != 0 or total != 0 or verified != 0 or work is not None:
            fail(f"{label} unknown terminal-verification state carried work")
        return
    if count == 0:
        if total != 0 or verified != 0 or work is not None:
            fail(f"{label} empty terminal-verification state was inconsistent")
        return
    if work is None:
        fail(f"{label} pending terminal-verification state omitted next work")
    work_total, work_offset = require_payload_terminal_verification_work(
        work, label
    )
    if work_total > total or work_offset > verified:
        fail(f"{label} terminal-verification next work exceeded aggregate state")


def require_payload_terminal_verification_step(
    value: Any, label: str
) -> None:
    if value is None:
        return
    if not isinstance(value, dict) or set(value) != {
        "disposition", "work_before", "verified_offset_after_bytes",
        "hashed_bytes", "terminal_verification_steps",
    }:
        fail(f"{label} last-step terminal verification was not canonical")
    disposition = value.get("disposition")
    if disposition not in {
        "progress", "completed_inserted", "completed_already_present",
    }:
        fail(f"{label} last-step terminal verification was unexpectedly idle")
    work = value.get("work_before")
    total, offset = require_payload_terminal_verification_work(work, label)
    after = value.get("verified_offset_after_bytes")
    hashed = value.get("hashed_bytes")
    steps = value.get("terminal_verification_steps")
    if (
        not isinstance(after, int) or after < offset or after > total
        or not isinstance(hashed, int) or hashed < 0
        or not isinstance(steps, int) or steps < 0 or steps > 1
    ):
        fail(f"{label} last-step terminal verification had invalid accounting")
    if disposition == "progress":
        if steps != 1 or hashed != after - offset or hashed <= 0 or after >= total:
            fail(f"{label} terminal-verification progress crossed its bound")
    elif disposition == "completed_inserted":
        if steps != 1 or hashed != after - offset or after != total:
            fail(f"{label} terminal-verification insertion was incomplete")
    elif after != total or (
        (steps == 0 and hashed != 0)
        or (steps == 1 and hashed != after - offset)
    ):
        fail(f"{label} terminal-verification reconciliation was incoherent")



def require_source_manifest_projection_object(
    value: Any, label: str
) -> None:
    expected_keys = {
        "pending", "operation_id", "content_sha256", "total_size_bytes",
        "next_offset_bytes", "remaining_bytes", "completed_chunk_count",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        fail(f"{label} source-manifest projection was not canonical")
    pending = value.get("pending")
    if not isinstance(pending, bool):
        fail(f"{label} source-manifest projection omitted pending state")
    operation_id = value.get("operation_id")
    digest = value.get("content_sha256")
    total = value.get("total_size_bytes")
    offset = value.get("next_offset_bytes")
    remaining = value.get("remaining_bytes")
    chunks = value.get("completed_chunk_count")
    for name, member in (
        ("total_size_bytes", total),
        ("next_offset_bytes", offset),
        ("remaining_bytes", remaining),
        ("completed_chunk_count", chunks),
    ):
        if not isinstance(member, int) or isinstance(member, bool) or member < 0:
            fail(f"{label} source-manifest projection omitted bounded {name}")
    if not pending:
        if (
            operation_id is not None or digest is not None or total != 0
            or offset != 0 or remaining != 0 or chunks != 0
        ):
            fail(f"{label} idle source-manifest projection carried work")
        return
    if (
        not is_canonical_sha256(operation_id)
        or not is_canonical_sha256(digest)
        or total <= 0 or offset < 0 or offset >= total
        or remaining != total - offset
    ):
        fail(f"{label} pending source-manifest projection was incoherent")


def require_source_manifest_projection_status(
    value: dict[str, Any], label: str
) -> None:
    require_source_manifest_projection_object(
        value.get("source_manifest_projection"), label
    )


def require_source_manifest_projection_step(
    value: Any, label: str
) -> None:
    if value is None:
        return
    expected_keys = {
        "disposition", "before", "after", "hashed_bytes",
        "newly_completed_chunk_count", "projection_restarted",
    }
    if not isinstance(value, dict) or set(value) != expected_keys:
        fail(f"{label} last-step source-manifest projection was not canonical")
    disposition = value.get("disposition")
    if disposition not in {
        "no_pending_work", "progress", "completed", "payload_unavailable",
    }:
        fail(f"{label} last-step source-manifest disposition was invalid")
    require_source_manifest_projection_object(value.get("before"), label)
    require_source_manifest_projection_object(value.get("after"), label)
    hashed = value.get("hashed_bytes")
    chunks = value.get("newly_completed_chunk_count")
    restarted = value.get("projection_restarted")
    if (
        not isinstance(hashed, int) or isinstance(hashed, bool) or hashed < 0
        or not isinstance(chunks, int) or isinstance(chunks, bool) or chunks < 0
        or not isinstance(restarted, bool)
    ):
        fail(f"{label} last-step source-manifest accounting was invalid")
    before_pending = value["before"]["pending"]
    after_pending = value["after"]["pending"]
    if disposition == "progress":
        if not before_pending or not after_pending or hashed <= 0:
            fail(f"{label} source-manifest progress did not advance work")
    elif disposition == "completed":
        if not before_pending or after_pending or hashed <= 0:
            fail(f"{label} source-manifest completion was incoherent")
    elif disposition == "payload_unavailable":
        if not before_pending or after_pending or hashed != 0 or chunks != 0:
            fail(f"{label} source-manifest unavailability fabricated work")
    elif before_pending or after_pending or hashed != 0 or chunks != 0:
        fail(f"{label} idle source-manifest step carried work")

def require_payload_operator_status(
    value: dict[str, Any], label: str
) -> None:
    scrub = value.get("payload_scrub")
    if not isinstance(scrub, dict):
        fail(f"{label} status omitted payload scrub state")
    expected_scrub = {
        "enabled": True,
        "max_bytes_per_attempt": 4 * 1024 * 1024,
        "max_entries_per_attempt": 4,
    }
    for key, wanted in expected_scrub.items():
        if scrub.get(key) != wanted:
            fail(
                f"{label} payload scrub field {key!r} was "
                f"{scrub.get(key)!r}, expected {wanted!r}: "
                f"{json.dumps(scrub, sort_keys=True)}"
            )
    report = scrub.get("last_report")
    if report is not None:
        if not isinstance(report, dict):
            fail(f"{label} scrub report was neither object nor null")
        if not isinstance(report.get("disposition"), str) or not isinstance(
            report.get("age_milliseconds"), int
        ):
            fail(
                f"{label} scrub report omitted disposition/age: "
                f"{json.dumps(report, sort_keys=True)}"
            )
        for boolean_field in (
            "state_rebuilt",
            "reverified_active_completed",
            "reverified_failure_cleared",
        ):
            if not isinstance(report.get(boolean_field), bool):
                fail(
                    f"{label} scrub report omitted boolean "
                    f"{boolean_field!r}: {json.dumps(report, sort_keys=True)}"
                )
    completion_age = scrub.get("last_completed_cycle_age_milliseconds")
    if completion_age is not None and not isinstance(completion_age, int):
        fail(f"{label} scrub completion age was neither integer nor null")
    if report is None and completion_age is not None:
        fail(f"{label} invented a completed-cycle age without any report")

    require_payload_terminal_verification_status(value, label)
    require_source_manifest_projection_status(value, label)

    counters = value.get("counters")
    if not isinstance(counters, dict):
        fail(f"{label} status omitted service counters")
    for counter_name in (
        "payload_store_lease_busy_deferrals",
        "payload_store_lease_backoff_deferrals",
        "payload_authority_network_outcome_uncertain_steps",
        "payload_terminal_verification_scheduler_steps",
        "payload_terminal_verification_progress_steps",
        "payload_terminal_verification_completions",
        "payload_terminal_verification_insertions",
        "payload_terminal_verification_reconciliations",
        "payload_terminal_verification_hashed_bytes",
        "payload_terminal_verification_ordinary_turn_yields",
        "source_manifest_projection_scheduler_steps",
        "source_manifest_projection_progress_steps",
        "source_manifest_projection_completions",
        "source_manifest_projection_payload_unavailable",
        "source_manifest_projection_restarts",
        "source_manifest_projection_hashed_bytes",
        "source_manifest_projection_ordinary_turn_yields",
        "payload_recheck_requests_observed",
        "payload_recheck_requests_coalesced",
        "payload_recheck_attempts",
        "payload_recheck_completions",
        "payload_recheck_integrity_recoveries",
        "payload_recheck_snapshot_handoffs",
        "payload_recheck_convergence_snapshot_observations",
        "payload_recheck_convergence_mutation_full_scans",
        "payload_quarantine_requests_observed",
        "payload_quarantine_requests_coalesced",
        "payload_quarantine_attempts",
        "payload_quarantine_completions",
        "payload_quarantine_images_preserved",
        "payload_quarantine_images_released",
        "payload_quarantine_observed_content_changes",
        "historical_version_requests_observed",
        "historical_version_requests_coalesced",
        "historical_version_attempts",
        "historical_version_completions",
        "historical_version_inspections",
        "historical_version_retention_plans",
        "historical_version_restores",
        "historical_version_pins",
        "historical_version_unpins",
        "historical_version_failures",
    ):
        counter = counters.get(counter_name)
        if not isinstance(counter, int) or counter < 0:
            fail(f"{label} status omitted bounded {counter_name}")

    last_step = value.get("last_step")
    if last_step is not None:
        if not isinstance(last_step, dict):
            fail(f"{label} last step was neither object nor null")
        for boolean_field in (
            "network_outcome_known",
            "payload_store_lease_conflict_observed",
            "payload_recheck_recovered_integrity_fault",
        ):
            if not isinstance(last_step.get(boolean_field), bool):
                fail(f"{label} last step omitted {boolean_field}")
        require_payload_terminal_verification_step(
            last_step.get("payload_terminal_verification"), label
        )
        require_source_manifest_projection_step(
            last_step.get("source_manifest_projection"), label
        )
        for integer_field in (
            "payload_recheck_generation",
            "payload_recheck_hashed_entries",
            "payload_recheck_hashed_bytes",
            "payload_recheck_snapshot_handoffs",
            "payload_recheck_convergence_snapshot_observations",
            "payload_recheck_convergence_mutation_full_scans",
        ):
            field = last_step.get(integer_field)
            if not isinstance(field, int) or field < 0:
                fail(f"{label} last step omitted bounded {integer_field}")
        quarantine_generation = last_step.get("payload_quarantine_generation")
        if not isinstance(quarantine_generation, int) or (
            quarantine_generation < 0
        ):
            fail(f"{label} last step omitted payload quarantine generation")
        quarantine_result = last_step.get("payload_quarantine_result")
        if quarantine_result is not None:
            require_payload_quarantine_result(
                quarantine_result, f"{label} last-step payload quarantine"
            )
        historical_restore_request = last_step.get(
            "historical_version_restore_request"
        )
        if historical_restore_request is not None:
            if not isinstance(historical_restore_request, dict) or set(
                historical_restore_request
            ) != {"operation_id", "expected_current_operation_id"}:
                fail(
                    f"{label} last step historical restore request was malformed"
                )
            historical_operation_id = historical_restore_request.get(
                "operation_id"
            )
            historical_expected_current = historical_restore_request.get(
                "expected_current_operation_id"
            )
            if not is_canonical_sha256(historical_operation_id):
                fail(
                    f"{label} last step historical restore request omitted operation ID"
                )
            if historical_expected_current is not None and (
                not is_canonical_sha256(historical_expected_current)
                or historical_expected_current == historical_operation_id
            ):
                fail(
                    f"{label} last step historical restore request omitted exact current head"
                )
        historical_failure = last_step.get("historical_version_failure")
        historical_failure_class = last_step.get(
            "historical_version_failure_class"
        )
        historical_source_stage = last_step.get(
            "historical_version_source_change_stage"
        )
        if historical_failure is None:
            if (
                historical_failure_class is not None
                or historical_source_stage is not None
            ):
                fail(f"{label} last step classified no historical failure")
        elif not isinstance(historical_failure, str):
            fail(f"{label} last step historical failure was not a string")
        elif historical_failure_class == "operation_failed":
            if historical_source_stage is not None:
                fail(f"{label} last step ordinary failure invented source drift")
        elif historical_failure_class == "source_changed":
            if historical_source_stage not in {
                "operation_set_before_payload_observation",
                "operation_set_during_payload_observation",
                "payload_snapshot",
                "restore_current_operation",
            }:
                fail(f"{label} last step source drift omitted its exact stage")
        else:
            fail(f"{label} last step historical failure class was invalid")

    recheck = value.get("payload_recheck")
    if not isinstance(recheck, dict):
        fail(f"{label} status omitted payload recheck state")
    for integer_field in (
        "requested_generation",
        "started_generation",
        "completed_generation",
        "retry_delay_milliseconds",
        "last_hashed_entries",
        "last_hashed_bytes",
        "last_snapshot_handoffs",
        "last_convergence_snapshot_observations",
        "last_convergence_mutation_full_scans",
    ):
        field = recheck.get(integer_field)
        if not isinstance(field, int) or field < 0:
            fail(f"{label} payload recheck omitted bounded {integer_field}")
    for boolean_field in (
        "pending",
        "last_completion_recovered_integrity_fault",
    ):
        if not isinstance(recheck.get(boolean_field), bool):
            fail(f"{label} payload recheck omitted {boolean_field}")
    requested = recheck["requested_generation"]
    started = recheck["started_generation"]
    completed = recheck["completed_generation"]
    if completed > started or started > requested:
        fail(
            f"{label} payload recheck generations were incoherent: "
            f"{json.dumps(recheck, sort_keys=True)}"
        )
    if recheck["pending"] != (requested > completed):
        fail(
            f"{label} payload recheck pending state disagreed with its "
            f"generations: {json.dumps(recheck, sort_keys=True)}"
        )

    quarantine = value.get("payload_quarantine")
    if not isinstance(quarantine, dict):
        fail(f"{label} status omitted payload quarantine state")
    for integer_field in (
        "requested_generation",
        "started_generation",
        "completed_generation",
        "retry_delay_milliseconds",
    ):
        field = quarantine.get(integer_field)
        if not isinstance(field, int) or field < 0:
            fail(
                f"{label} payload quarantine omitted bounded "
                f"{integer_field}"
            )
    if not isinstance(quarantine.get("pending"), bool):
        fail(f"{label} payload quarantine omitted pending state")
    quarantine_requested = quarantine["requested_generation"]
    quarantine_started = quarantine["started_generation"]
    quarantine_completed = quarantine["completed_generation"]
    if quarantine_completed > quarantine_started or (
        quarantine_started > quarantine_requested
    ):
        fail(
            f"{label} payload quarantine generations were incoherent: "
            f"{json.dumps(quarantine, sort_keys=True)}"
        )
    if quarantine["pending"] != (
        quarantine_requested > quarantine_completed
    ):
        fail(
            f"{label} payload quarantine pending state disagreed with its "
            f"generations: {json.dumps(quarantine, sort_keys=True)}"
        )
    quarantine_action = quarantine.get("action")
    if quarantine_requested == 0:
        if quarantine_action is not None:
            fail(f"{label} payload quarantine invented an action before any request")
    elif quarantine_action not in {"preserve", "release"}:
        fail(f"{label} payload quarantine omitted its exact action")
    for digest_field in (
        "expected_content_sha256", "observed_content_sha256"
    ):
        digest = quarantine.get(digest_field)
        if quarantine_requested == 0:
            if digest is not None:
                fail(
                    f"{label} payload quarantine invented {digest_field} "
                    "before any request"
                )
        elif not isinstance(digest, str) or len(digest) != 64:
            fail(
                f"{label} payload quarantine omitted exact {digest_field}"
            )
    last_quarantine_result = quarantine.get("last_result")
    if last_quarantine_result is not None:
        require_payload_quarantine_result(
            last_quarantine_result, f"{label} payload quarantine"
        )

    require_payload_quarantine_inventory(
        quarantine.get("inventory"), f"{label} payload quarantine"
    )
    require_historical_version_status(value, label)

    integrity = value.get("payload_integrity")
    if not isinstance(integrity, dict):
        fail(f"{label} status omitted payload integrity state")
    state = integrity.get("state")
    active = integrity.get("active_fault")
    recovery = integrity.get("most_recent_recovery")
    if recovery is not None and not isinstance(recovery, dict):
        fail(f"{label} payload recovery history was neither object nor null")
    for evidence_label, evidence in (
        ("active fault", active),
        ("recovery history", recovery),
    ):
        if evidence is None:
            continue
        for digest_field in (
            "expected_content_sha256",
            "observed_content_sha256",
        ):
            digest = evidence.get(digest_field)
            if not isinstance(digest, str) or len(digest) != 64:
                fail(
                    f"{label} payload {evidence_label} omitted exact "
                    f"{digest_field}"
                )
        if not isinstance(evidence.get("failure_persisted"), bool):
            fail(
                f"{label} payload {evidence_label} omitted exact-pair "
                "persistence evidence"
            )
        for counter_field in (
            "detection_count",
            "observed_content_change_count",
        ):
            counter = evidence.get(counter_field)
            if not isinstance(counter, int) or counter < 0:
                fail(
                    f"{label} payload {evidence_label} omitted bounded "
                    f"{counter_field}"
                )
    if state == "healthy":
        if active is not None:
            fail(f"{label} healthy integrity state retained an active fault")
    elif state == "faulted":
        if not isinstance(active, dict):
            fail(f"{label} faulted integrity state omitted fault evidence")
    else:
        fail(f"{label} reported unknown payload integrity state {state!r}")


def wait_for_payload_integrity_state(
    sync: Path,
    process: subprocess.Popen[str],
    socket_path: Path,
    expected_state: str,
    label: str,
    *,
    timeout_seconds: float = 15.0,
    expected_observed_content_sha256: str | None = None,
    minimum_detection_count: int = 0,
    minimum_observed_content_change_count: int = 0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_value: dict[str, Any] | None = None
    last_error = "no status response"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} service exited while waiting for payload integrity "
                f"state {expected_state!r} with {process.returncode}\n"
                f"stdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            mode = socket_path.lstat().st_mode
            if not stat.S_ISSOCK(mode) or stat.S_IMODE(mode) != 0o600:
                last_error = "owner-only status socket was not preserved"
            else:
                value = run_json(
                    [
                        str(sync), "status", "--socket", str(socket_path),
                        "--timeout-milliseconds", "1000",
                    ],
                    label=f"{label} status query",
                )
                last_value = value
                require_payload_operator_status(value, label)
                integrity = value["payload_integrity"]
                if integrity.get("state") == expected_state:
                    active = integrity.get("active_fault")
                    if expected_state != "faulted":
                        return value
                    if not isinstance(active, dict):
                        last_error = "faulted state omitted active evidence"
                    elif (
                        expected_observed_content_sha256 is not None
                        and active.get("observed_content_sha256")
                        != expected_observed_content_sha256
                    ):
                        last_error = (
                            "active observed digest was "
                            f"{active.get('observed_content_sha256')!r}"
                        )
                    elif active.get("detection_count", -1) < (
                        minimum_detection_count
                    ):
                        last_error = (
                            "active detection count was "
                            f"{active.get('detection_count')!r}"
                        )
                    elif active.get("observed_content_change_count", -1) < (
                        minimum_observed_content_change_count
                    ):
                        last_error = (
                            "active observed-content change count was "
                            f"{active.get('observed_content_change_count')!r}"
                        )
                    else:
                        return value
                else:
                    last_error = (
                        "payload integrity state was "
                        f"{integrity.get('state')!r}"
                    )
        except (FileNotFoundError, OSError, RuntimeError) as error:
            last_error = str(error)
        time.sleep(0.02)
    suffix = (
        ""
        if last_value is None
        else f": {json.dumps(last_value, sort_keys=True)}"
    )
    fail(
        f"{label} did not reach payload integrity state "
        f"{expected_state!r}: {last_error}{suffix}"
    )


def relocate_deployment_manifest(source: Path, destination: Path) -> None:
    """Write one canonical manifest with only its committed pathname changed."""
    exact = source.read_text(encoding="utf-8")
    try:
        parsed = json.loads(exact)
    except json.JSONDecodeError as error:
        fail(f"source deployment manifest is not JSON: {error}")
    prior_path = parsed.get("manifest_path")
    if not isinstance(prior_path, str):
        fail("source deployment manifest omitted manifest_path")
    before = '"manifest_path":' + json.dumps(prior_path, separators=(",", ":"))
    after = '"manifest_path":' + json.dumps(
        str(destination), separators=(",", ":")
    )
    if exact.count(before) != 1:
        fail("deployment manifest pathname substitution is not unique")
    relocated = exact.replace(before, after, 1)
    marker = ',"manifest_digest":'
    if relocated.count(marker) != 1 or not relocated.endswith("}\n"):
        fail("deployment manifest is not a canonical terminal-digest document")
    unsigned_prefix, _ = relocated[:-1].split(marker, 1)
    unsigned_document = unsigned_prefix + "}"
    digest = hashlib.sha256(
        b"anonsync:replica-deployment-manifest:v2\n"
        + unsigned_document.encode("utf-8")
    ).hexdigest()
    encoded = unsigned_prefix + marker + json.dumps(digest) + "}\n"
    descriptor = os.open(
        destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600
    )
    try:
        os.write(descriptor, encoded.encode("utf-8"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def wait_for_payload_quarantine_completion(
    sync: Path,
    process: subprocess.Popen[str],
    socket_path: Path,
    generation: int,
    expected_action: str,
    expected_disposition: str,
    label: str,
    *,
    timeout_seconds: float = 15.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_value: dict[str, Any] | None = None
    last_error = "no status response"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} service exited while waiting for payload quarantine "
                f"generation {generation} with {process.returncode}\n"
                f"stdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            value = run_json(
                [
                    str(sync), "status", "--socket", str(socket_path),
                    "--timeout-milliseconds", "1000",
                ],
                label=f"{label} status query",
            )
            last_value = value
            require_payload_operator_status(value, label)
            quarantine = value["payload_quarantine"]
            result = quarantine.get("last_result")
            if (
                quarantine.get("completed_generation", 0) >= generation
                and quarantine.get("pending") is False
                and isinstance(result, dict)
                and result.get("action") == expected_action
                and result.get("disposition") == expected_disposition
            ):
                return value
            last_error = (
                "quarantine state was "
                f"{json.dumps(quarantine, sort_keys=True)}"
            )
        except (FileNotFoundError, OSError, RuntimeError) as error:
            last_error = str(error)
        time.sleep(0.02)
    suffix = "" if last_value is None else f"; last status={json.dumps(last_value, sort_keys=True)}"
    fail(f"{label} did not complete: {last_error}{suffix}")


def wait_for_historical_version_completion(
    sync: Path,
    process: subprocess.Popen[str],
    socket_path: Path,
    generation: int,
    expected_action: str,
    label: str,
    *,
    timeout_seconds: float = 15.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_value: dict[str, Any] | None = None
    last_error = "no status response"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} service exited while waiting for historical-version "
                f"generation {generation} with {process.returncode}\n"
                f"stdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            value = run_json(
                [
                    str(sync), "status", "--socket", str(socket_path),
                    "--timeout-milliseconds", "1000",
                ],
                label=f"{label} status query",
            )
            last_value = value
            require_payload_operator_status(value, label)
            history = value["historical_versions"]
            completed_result = (
                history.get("last_inventory")
                if expected_action == "inspect"
                else (
                    history.get("last_retention_plan")
                    if expected_action == "retention_plan"
                    else (
                        history.get("last_restore")
                        if expected_action == "restore"
                        else history.get("last_pin_update")
                    )
                )
            )
            if (
                history.get("completed_generation", 0) >= generation
                and history.get("pending") is False
                and history.get("action") == expected_action
                and history.get("last_failure") is None
                and isinstance(completed_result, dict)
            ):
                last_step = value.get("last_step")
                if (
                    isinstance(last_step, dict)
                    and last_step.get("historical_version_generation")
                    == generation
                    and (
                        (
                            expected_action == "inspect"
                            and last_step.get("historical_version_inventory")
                            is not None
                        )
                        or (
                            expected_action == "retention_plan"
                            and last_step.get(
                                "historical_version_retention_plan"
                            ) is not None
                        )
                    )
                ):
                    fail(
                        f"{label} duplicated the stable history result "
                        "inside generic last_step status"
                    )
                return value
            last_error = (
                "historical-version state was "
                f"{json.dumps(history, sort_keys=True)}"
            )
        except (FileNotFoundError, OSError, RuntimeError) as error:
            last_error = str(error)
        time.sleep(0.02)
    suffix = (
        ""
        if last_value is None
        else f"; last status={json.dumps(last_value, sort_keys=True)}"
    )
    fail(f"{label} did not complete: {last_error}{suffix}")


def wait_for_historical_version_source_change(
    sync: Path,
    process: subprocess.Popen[str],
    socket_path: Path,
    generation: int,
    expected_stage: str,
    label: str,
    *,
    expected_action: str = "inspect",
    timeout_seconds: float = 15.0,
) -> dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    last_value: dict[str, Any] | None = None
    last_error = "no status response"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} service exited while waiting for historical source "
                f"failure generation {generation} with {process.returncode}\n"
                f"stdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            value = run_json(
                [
                    str(sync), "status", "--socket", str(socket_path),
                    "--timeout-milliseconds", "1000",
                ],
                label=f"{label} status query",
            )
            last_value = value
            require_payload_operator_status(value, label)
            history = value["historical_versions"]
            if (
                history.get("completed_generation") == generation
                and history.get("pending") is False
                and history.get("action") == expected_action
                and history.get("last_inventory") is None
                and history.get("last_restore") is None
                and history.get("last_failure_class") == "source_changed"
                and history.get("last_source_change_stage") == expected_stage
                and isinstance(history.get("last_failure"), str)
            ):
                # Generic last_step is deliberately transient: a completed
                # history action can be followed immediately by an inbound or
                # outbound network step. Validate the per-step projection only
                # when this poll actually catches the matching action generation;
                # the retained historical_versions object is the stable result.
                last_step = value.get("last_step")
                if (
                    isinstance(last_step, dict)
                    and last_step.get("historical_version_generation")
                    == generation
                    and (
                        last_step.get("historical_version_failure_class")
                        != "source_changed"
                        or last_step.get(
                            "historical_version_source_change_stage"
                        ) != expected_stage
                        or last_step.get("historical_version_failure")
                        != history.get("last_failure")
                    )
                ):
                    fail(
                        f"{label} matching historical step omitted exact "
                        f"source drift: {json.dumps(last_step, sort_keys=True)}"
                    )
                return value
            last_error = (
                "historical-version state was "
                f"{json.dumps(history, sort_keys=True)}"
            )
        except (FileNotFoundError, OSError, RuntimeError) as error:
            last_error = str(error)
        time.sleep(0.02)
    suffix = (
        ""
        if last_value is None
        else f"; last status={json.dumps(last_value, sort_keys=True)}"
    )
    fail(f"{label} did not complete: {last_error}{suffix}")


def receive_notify_until_ready(
    receiver: socket.socket,
    process: subprocess.Popen[str],
    label: str,
) -> list[str]:
    deadline = time.monotonic() + 10.0
    messages: list[str] = []
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} exited before READY=1 with {process.returncode}\n"
                f"stdout:\n{stdout}\nstderr:\n{stderr}"
            )
        receiver.settimeout(max(0.01, deadline - time.monotonic()))
        try:
            payload = receiver.recv(4096)
        except TimeoutError:
            break
        try:
            message = payload.decode("utf-8")
        except UnicodeDecodeError as error:
            fail(f"{label} emitted a non-UTF-8 notification: {error}")
        messages.append(message)
        if message.startswith("READY=1\n"):
            break
    expected = {
        "STATUS=Starting: claiming configured deployment",
        "STATUS=Starting: loading TLS identity",
        "READY=1\nSTATUS=Running: initial repair and required ingress are ready",
    }
    missing = expected.difference(messages)
    if missing:
        fail(
            f"{label} notification sequence omitted {sorted(missing)!r}: "
            f"{messages!r}"
        )
    return messages


def linked_peer_configuration(
    *,
    manifest: Path,
    certificates: Path,
    local_device: str,
    remote_device: str,
    remote_pin: str,
    listen_port: int,
    remote_port: int,
    status_socket: Path,
) -> dict[str, Any]:
    return {
        "schema": "anonsync.linked-peer-service.v2",
        "manifest": str(manifest),
        "peer": {
            "device_id": remote_device,
            "epoch": 1,
            "spki_sha256": remote_pin,
        },
        "tls": {
            "certificate": str(certificates / f"{local_device}.pem"),
            "private_key": str(certificates / f"{local_device}.key"),
            "ca_file": str(certificates / "ca.pem"),
        },
        "listen": {"address": "127.0.0.1", "port": listen_port},
        "route": {
            "kind": "direct",
            "address": "127.0.0.1",
            "port": remote_port,
        },
        "ingress": {"kind": "direct"},
        "status_socket": str(status_socket),
        "service": {
            "timeout_seconds": 3,
            "cycle_runtime_seconds": 15,
            "max_round_trips": 8,
            "max_source_resets": 2,
            "inbound_timeout_seconds": 2,
            "inbound_max_round_trips": 7,
            "accept_poll_milliseconds": 50,
            "scan_interval_seconds": 1,
            "retry_initial_seconds": 1,
            "retry_maximum_seconds": 2,
            "maximum_service_runtime_seconds": 90,
        },
    }


def wait_for_status(
    sync: Path,
    process: subprocess.Popen[str],
    socket_path: Path,
    local_device: str,
    remote_device: str,
    config_path: Path,
    label: str,
) -> dict[str, Any]:
    deadline = time.monotonic() + 10.0
    last_error = "status socket did not appear"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=1.0)
            fail(
                f"{label} exited before status was readable with "
                f"{process.returncode}\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )
        try:
            mode = socket_path.lstat().st_mode
            if not stat.S_ISSOCK(mode):
                last_error = "status path exists but is not a socket"
            elif stat.S_IMODE(mode) != 0o600:
                last_error = (
                    "status socket mode was "
                    f"{oct(stat.S_IMODE(mode))}, expected 0o600"
                )
            else:
                value = run_json(
                    [
                        str(sync), "status", "--socket", str(socket_path),
                        "--timeout-milliseconds", "1000",
                    ],
                    label=f"{label} status query",
                )
                expected = {
                    "schema": "anonsync.peer-service.status.v26",
                    "service_state": "running",
                    "ready": True,
                    "configuration_path": str(config_path),
                    "status_socket": str(socket_path),
                    "local_device_id": local_device,
                    "remote_device_id": remote_device,
                    "transport": "direct_tcp",
                    "ingress_transport": "direct_tcp",
                    "ingress_ready": True,
                }
                for key, wanted in expected.items():
                    if value.get(key) != wanted:
                        fail(
                            f"{label} status field {key!r} was "
                            f"{value.get(key)!r}, expected {wanted!r}: "
                            f"{json.dumps(value, sort_keys=True)}"
                        )
                if value.get("pid") != process.pid:
                    fail(f"{label} status did not bind the serving PID")
                counters = value.get("counters")
                if not isinstance(counters, dict):
                    fail(f"{label} status omitted counters")
                if counters.get("initial_repairs") != 1 or (
                    counters.get("initial_repair_payload_snapshot_handoffs") != 1
                ) or counters.get(
                    "initial_repair_convergence_snapshot_observations"
                ) != 0:
                    fail(
                        f"{label} ready service did not retain exactly one "
                        "initial payload snapshot handoff without a duplicate "
                        "convergence observation: "
                        f"{json.dumps(value, sort_keys=True)}"
                    )
                if value.get("generation", -1) < 0:
                    fail(f"{label} status generation was invalid")
                require_payload_operator_status(value, label)
                initial_inventory = value["payload_quarantine"]["inventory"]
                if initial_inventory.get("observation_known") is not True:
                    fail(
                        f"{label} reported ready without its complete empty "
                        "quarantine observation: "
                        f"observation_known was "
                        f"{initial_inventory.get('observation_known')!r}"
                    )
                if initial_inventory.get("entry_count") != 0 or (
                    initial_inventory.get("total_bytes") != 0
                ):
                    fail(
                        f"{label} initial service unexpectedly retained "
                        "quarantine evidence"
                    )
                if value["payload_integrity"].get("state") != "healthy":
                    fail(f"{label} was unexpectedly integrity-faulted")
                return value
        except (FileNotFoundError, OSError, RuntimeError) as error:
            last_error = str(error)
        time.sleep(0.02)
    fail(f"{label} status was not ready: {last_error}")


def expect_checked_config(
    sync: Path,
    config: Path,
    *,
    transport: str,
    local_device: str,
    remote_device: str,
    label: str,
    ingress_transport: str = "direct_tcp",
    configuration_schema: str = "anonsync.linked-peer-service.v2",
    network_step_horizon_seconds: int | None = None,
) -> dict[str, Any]:
    value = run_json(
        [str(sync), "check-config", "--config", str(config)],
        label=label,
    )
    expected = {
        "command": "check-config",
        "terminal_class": "completed",
        "configuration_schema": configuration_schema,
        "configuration_path": str(config),
        "local_device_id": local_device,
        "remote_device_id": remote_device,
        "transport": transport,
        "ingress_transport": ingress_transport,
    }
    for key, wanted in expected.items():
        if value.get(key) != wanted:
            fail(
                f"{label} field {key!r} was {value.get(key)!r}, "
                f"expected {wanted!r}: {json.dumps(value, sort_keys=True)}"
            )
    numeric_listener_expected = ingress_transport != "i2p_sam_accept"
    if value.get("numeric_listener_active") is not numeric_listener_expected:
        fail(
            f"{label} numeric-listener state was "
            f"{value.get('numeric_listener_active')!r}, expected "
            f"{numeric_listener_expected!r}: "
            f"{json.dumps(value, sort_keys=True)}"
        )
    if numeric_listener_expected:
        if not isinstance(value.get("bind_address"), str):
            fail(f"{label} omitted the normalized bind address")
        listen_port = value.get("listen_port")
        if not isinstance(listen_port, int) or listen_port <= 0:
            fail(f"{label} omitted the normalized listen port")
    elif value.get("bind_address") is not None or value.get("listen_port") is not None:
        fail(
            f"{label} retained a numeric ingress endpoint for native I2P: "
            f"{json.dumps(value, sort_keys=True)}"
        )
    if value.get("maximum_file_bytes", 0) <= 0:
        fail(f"{label} omitted the normalized folder limit")
    if value.get("maximum_remote_apply_operations") != 4096:
        fail(f"{label} omitted the effective remote-apply operation frontier")
    if value.get("maximum_remote_inspection_paths") != 4096:
        fail(f"{label} omitted the effective remote-inspection path frontier")
    if value.get("installed_service_maximum_network_step_seconds") != 3600:
        fail(f"{label} did not report the installed network-step policy")
    if value.get("installed_service_stop_timeout_seconds") != 3660:
        fail(f"{label} did not report the installed graceful-stop policy")
    if network_step_horizon_seconds is not None and value.get(
        "network_step_horizon_seconds"
    ) != network_step_horizon_seconds:
        fail(
            f"{label} network-step horizon was "
            f"{value.get('network_step_horizon_seconds')!r}, expected "
            f"{network_step_horizon_seconds}"
        )
    return value


def expect_terminal(
    value: dict[str, Any],
    *,
    local_device: str,
    remote_device: str,
    config_path: Path,
    status_socket: Path,
    label: str,
    stop_reason: str = "stop_requested",
    payload_integrity_recovery_expected: bool = False,
) -> None:
    expected = {
        "command": "run",
        "terminal_class": "completed",
        "stop_reason": stop_reason,
        "listener_started": True,
        "configuration_path": str(config_path),
        "status_socket": str(status_socket),
        "local_device_id": local_device,
        "remote_device_id": remote_device,
        "transport": "direct_tcp",
        "ingress_transport": "direct_tcp",
        "ingress_ready": True,
    }
    for key, wanted in expected.items():
        if value.get(key) != wanted:
            fail(
                f"{label} terminal field {key!r} was {value.get(key)!r}, "
                f"expected {wanted!r}: {json.dumps(value, sort_keys=True)}"
            )
    if value.get("cycles_complete", 0) < 1:
        fail(f"{label} completed no sync cycle")
    if value.get("cycles_failed", 0) > value.get("cycles_attempted", 0):
        fail(f"{label} cycle accounting is incoherent")
    if payload_integrity_recovery_expected:
        if value.get("payload_integrity_fault_active") is not False:
            fail(f"{label} terminal retained an active payload fault")
        for field in (
            "payload_integrity_faults_observed",
            "payload_recheck_requests_observed",
            "payload_recheck_requests_coalesced",
            "payload_recheck_attempts",
            "payload_recheck_completions",
            "payload_recheck_integrity_recoveries",
        ):
            if value.get(field, 0) < 1:
                fail(f"{label} terminal omitted successful {field}")
        recheck = value.get("payload_recheck")
        if not isinstance(recheck, dict) or recheck.get("pending") is not False:
            fail(f"{label} terminal did not settle its payload recheck")
        if recheck.get("requested_generation", 0) < 1 or (
            recheck.get("completed_generation")
            != recheck.get("requested_generation")
        ):
            fail(f"{label} terminal lost payload recheck generations")
        if recheck.get("last_completion_recovered_integrity_fault") is not True:
            fail(f"{label} terminal omitted operator-driven fault recovery")
        if value.get("payload_recheck_snapshot_handoffs", 0) < 1:
            fail(f"{label} terminal omitted the successful recheck handoff")
        if (
            value.get(
                "payload_recheck_convergence_snapshot_observations",
                -1,
            )
            != 0
        ):
            fail(
                f"{label} recovery convergence repeated the complete "
                "payload-root observation"
            )
        if value.get(
            "payload_recheck_convergence_mutation_full_scans", -1
        ) != 1:
            fail(
                f"{label} quarantine recovery did not expose the one full "
                "scan required to establish mutation authority before "
                "re-admission"
            )
        quarantine = value.get("payload_quarantine")
        if not isinstance(quarantine, dict) or (
            quarantine.get("pending") is not False
        ) or quarantine.get("completed_generation", 0) < 1:
            fail(f"{label} terminal did not settle payload quarantine")
        last_result = quarantine.get("last_result")
        require_payload_quarantine_result(
            last_result, f"{label} terminal payload quarantine"
        )
        if last_result.get("action") != "release" or (
            last_result.get("disposition") != "released"
        ):
            fail(f"{label} terminal lost successful payload quarantine release")
        terminal_inventory = quarantine.get("inventory")
        require_payload_quarantine_inventory(
            terminal_inventory, f"{label} terminal payload quarantine"
        )
        if (
            terminal_inventory.get("observation_known") is not True
            or terminal_inventory.get("entry_count") != 0
            or terminal_inventory.get("total_bytes") != 0
            or terminal_inventory.get("entries") != []
        ):
            fail(f"{label} terminal lost the exact empty quarantine inventory")
        for field in (
            "payload_quarantine_requests_observed",
            "payload_quarantine_attempts",
            "payload_quarantine_completions",
            "payload_quarantine_images_preserved",
            "payload_quarantine_images_released",
        ):
            if value.get(field, 0) < 1:
                fail(f"{label} terminal omitted successful {field}")


def expect_config_failure(
    sync: Path,
    config: Path,
    label: str,
    *,
    message_contains: str | None = None,
    error_code: str = "invalid_arguments",
) -> None:
    # Exercise the admission-only command. A malformed configuration must be
    # rejected before listener, status-socket, or deployment ownership exists.
    completed = subprocess.run(
        [str(sync), "check-config", "--config", str(config)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        timeout=5.0,
        check=False,
    )
    if completed.returncode == 0:
        fail(f"{label} unexpectedly succeeded: {completed.stdout}")
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        fail(f"{label} did not emit JSON failure: {error}: {completed.stdout}")
    if value.get("terminal_class") != "stopped":
        fail(f"{label} failure was not classified as stopped")
    if value.get("error_code") != error_code:
        fail(
            f"{label} did not report {error_code}: "
            f"{json.dumps(value, sort_keys=True)}"
        )
    if message_contains is not None and message_contains not in str(
        value.get("message", "")
    ):
        fail(
            f"{label} did not report {message_contains!r}: "
            f"{json.dumps(value, sort_keys=True)}"
        )


def expect_deployment_ownership_failure(
    command: list[str], label: str,
) -> None:
    completed = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        timeout=5.0, check=False,
    )
    if completed.returncode != 1:
        fail(
            f"{label} returned {completed.returncode}, expected operation "
            f"failure 1\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    try:
        value = json.loads(
            completed.stdout, object_pairs_hook=unique_json_object_pairs
        )
    except (json.JSONDecodeError, ValueError) as error:
        fail(f"{label} did not emit strict JSON failure: {error}: {completed.stdout}")
    if value.get("terminal_class") != "stopped" or (
        value.get("error_code") != "operation_failed"
    ) or "already owned" not in str(value.get("message", "")):
        fail(
            f"{label} did not report exact deployment ownership: "
            f"{json.dumps(value, sort_keys=True)}"
        )
    if "already owned" not in completed.stderr:
        fail(f"{label} stderr omitted exact deployment ownership")


def expect_singleton_failure(sync: Path, config: Path, label: str) -> None:
    expect_deployment_ownership_failure(
        [str(sync), "run", "--config", str(config)], label
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--replica", required=True, type=Path)
    parser.add_argument("--folder", required=True, type=Path)
    parser.add_argument("--sync", required=True, type=Path)
    args = parser.parse_args()
    replica = args.replica.resolve(strict=True)
    folder = args.folder.resolve(strict=True)
    sync = args.sync.resolve(strict=True)
    openssl_executable = shutil.which("openssl")
    if openssl_executable is None:
        fail("openssl executable is unavailable")

    with tempfile.TemporaryDirectory(
        prefix="anonsync-service-config-status-"
    ) as raw:
        root = Path(raw)
        os.chmod(root, 0o700)
        certificates = root / "certificates"
        certificates.mkdir(mode=0o700)
        generate_tls_fixture(certificates, openssl_executable)

        source_manifest, source_files = init_combined(
            replica, root / "source", "source"
        )
        receiver_manifest, receiver_files = init_combined(
            replica, root / "receiver", "receiver"
        )
        run_json(
            [str(folder), "init", "--manifest", str(source_manifest)],
            label="source config-service folder init",
        )
        run_json(
            [str(folder), "init", "--manifest", str(receiver_manifest)],
            label="receiver config-service folder init",
        )

        source_pin = run_json(
            [
                str(replica), "certificate-spki", "--certificate",
                str(certificates / "source.pem"),
            ],
            label="source config-service certificate pin",
        )["spki_sha256"]
        receiver_pin = run_json(
            [
                str(replica), "certificate-spki", "--certificate",
                str(certificates / "receiver.pem"),
            ],
            label="receiver config-service certificate pin",
        )["spki_sha256"]
        run_json(
            [
                str(replica), "membership-publish", "--manifest",
                str(source_manifest), "--policy-epoch", "1", "--peer",
                f"receiver:1:{receiver_pin}",
            ],
            label="source config-service membership",
        )
        run_json(
            [
                str(replica), "membership-publish", "--manifest",
                str(receiver_manifest), "--policy-epoch", "1", "--peer",
                f"source:1:{source_pin}",
            ],
            label="receiver config-service membership",
        )

        (source_files / "source-side" / "nested").mkdir(
            parents=True, mode=0o700
        )
        (receiver_files / "receiver-side" / "nested").mkdir(
            parents=True, mode=0o700
        )
        (source_files / "source-side" / "nested" / "alpha.txt").write_bytes(
            b"config-driven source payload\n"
        )
        (receiver_files / "receiver-side" / "nested" / "beta.txt").write_bytes(
            b"config-driven receiver payload\n"
        )

        source_port = reserve_port()
        receiver_port = reserve_port()
        while receiver_port == source_port:
            receiver_port = reserve_port()
        source_runtime = root / "source-runtime"
        receiver_runtime = root / "receiver-runtime"
        source_runtime.mkdir(mode=0o700)
        receiver_runtime.mkdir(mode=0o700)
        source_status = source_runtime / "status.sock"
        receiver_status = receiver_runtime / "status.sock"
        source_config = source_runtime / "linked-peer.json"
        receiver_config = receiver_runtime / "linked-peer.json"
        source_value = linked_peer_configuration(
            manifest=source_manifest,
            certificates=certificates,
            local_device="source",
            remote_device="receiver",
            remote_pin=receiver_pin,
            listen_port=source_port,
            remote_port=receiver_port,
            status_socket=source_status,
        )
        receiver_value = linked_peer_configuration(
            manifest=receiver_manifest,
            certificates=certificates,
            local_device="receiver",
            remote_device="source",
            remote_pin=source_pin,
            listen_port=receiver_port,
            remote_port=source_port,
            status_socket=receiver_status,
        )
        write_private_json(source_config, source_value)
        write_private_json(receiver_config, receiver_value)

        expect_checked_config(
            sync, source_config, transport="direct_tcp",
            local_device="source", remote_device="receiver",
            label="direct linked-peer configuration check",
            network_step_horizon_seconds=15,
        )

        over_capacity_entries = (
            source_runtime / "linked-peer-over-capacity-entries.json"
        )
        over_capacity_entries_value = json.loads(json.dumps(source_value))
        over_capacity_entries_value["folder_limits"] = {
            "maximum_entries": 100001
        }
        write_private_json(
            over_capacity_entries, over_capacity_entries_value
        )
        decoupled_capacity = expect_checked_config(
            sync,
            over_capacity_entries,
            transport="direct_tcp",
            local_device="source",
            remote_device="receiver",
            label="independent namespace-entry configuration check",
            network_step_horizon_seconds=15,
        )
        if decoupled_capacity.get("maximum_entries") != 100001 or (
            decoupled_capacity.get("maximum_regular_files") != 100000
        ):
            fail(
                "independent namespace-entry configuration did not retain "
                "the distinct default regular-file capacity: "
                f"{json.dumps(decoupled_capacity, sort_keys=True)}"
            )

        over_capacity_regular_files = (
            source_runtime / "linked-peer-over-capacity-regular-files.json"
        )
        over_capacity_regular_files_value = json.loads(
            json.dumps(source_value)
        )
        over_capacity_regular_files_value["folder_limits"] = {
            "maximum_regular_files": 100001
        }
        write_private_json(
            over_capacity_regular_files,
            over_capacity_regular_files_value,
        )
        expect_config_failure(
            sync,
            over_capacity_regular_files,
            "over-capacity regular-file configuration",
            message_contains=(
                "maximum_regular_files exceeds the production durable capacity"
            ),
        )

        over_capacity_remote_paths = (
            source_runtime / "linked-peer-over-capacity-remote-paths.json"
        )
        over_capacity_remote_paths_value = json.loads(
            json.dumps(source_value)
        )
        over_capacity_remote_paths_value["folder_limits"] = {
            "maximum_remote_paths": 100001
        }
        write_private_json(
            over_capacity_remote_paths, over_capacity_remote_paths_value
        )
        expect_config_failure(
            sync,
            over_capacity_remote_paths,
            "over-capacity remote-path configuration",
            message_contains=(
                "maximum_remote_paths exceeds the production durable capacity"
            ),
        )

        over_capacity_remote_inspection_paths = (
            source_runtime
            / "linked-peer-over-capacity-remote-inspection-paths.json"
        )
        over_capacity_remote_inspection_paths_value = json.loads(
            json.dumps(source_value)
        )
        over_capacity_remote_inspection_paths_value["folder_limits"] = {
            "maximum_remote_inspection_paths": 100001
        }
        write_private_json(
            over_capacity_remote_inspection_paths,
            over_capacity_remote_inspection_paths_value,
        )
        expect_config_failure(
            sync,
            over_capacity_remote_inspection_paths,
            "over-capacity remote-inspection configuration",
            message_contains=(
                "maximum_remote_inspection_paths exceeds the production "
                "durable capacity"
            ),
        )

        stop_boundary_config = source_runtime / "linked-peer-stop-boundary.json"
        stop_boundary_value = json.loads(json.dumps(source_value))
        stop_boundary_value["service"]["ingress_timeout_seconds"] = 3600
        write_private_json(stop_boundary_config, stop_boundary_value)
        expect_checked_config(
            sync, stop_boundary_config, transport="direct_tcp",
            local_device="source", remote_device="receiver",
            label="installed graceful-stop boundary configuration check",
            network_step_horizon_seconds=3600,
        )

        overlong_cycle = source_runtime / "linked-peer-overlong-cycle.json"
        overlong_cycle_value = json.loads(json.dumps(source_value))
        overlong_cycle_value["service"]["cycle_runtime_seconds"] = 3601
        write_private_json(overlong_cycle, overlong_cycle_value)
        expect_config_failure(
            sync, overlong_cycle, "overlong installed outbound-step configuration",
            message_contains="graceful-stop policy of 3600 seconds",
        )

        overlong_inbound = source_runtime / "linked-peer-overlong-inbound.json"
        overlong_inbound_value = json.loads(json.dumps(source_value))
        overlong_inbound_value["service"]["inbound_timeout_seconds"] = 721
        write_private_json(overlong_inbound, overlong_inbound_value)
        expect_config_failure(
            sync, overlong_inbound, "overlong installed inbound-step configuration",
            message_contains="graceful-stop policy of 3600 seconds",
        )

        legacy_config = source_runtime / "linked-peer-v1.json"
        legacy_value = json.loads(json.dumps(source_value))
        legacy_value["schema"] = "anonsync.linked-peer-service.v1"
        del legacy_value["ingress"]
        write_private_json(legacy_config, legacy_value)
        expect_checked_config(
            sync, legacy_config, transport="direct_tcp",
            local_device="source", remote_device="receiver",
            label="legacy v1 linked-peer configuration check",
            configuration_schema="anonsync.linked-peer-service.v1",
        )

        tor_config = source_runtime / "linked-peer-tor.json"
        tor_value = json.loads(json.dumps(source_value))
        tor_value["route"] = {
            "kind": "tor",
            "onion_address": VALID_ONION,
            "onion_port": 443,
            "isolation_token": "config-check-source-receiver",
        }
        write_private_json(tor_config, tor_value)
        expect_checked_config(
            sync, tor_config, transport="tor_socks5",
            local_device="source", remote_device="receiver",
            label="Tor linked-peer configuration check",
        )

        i2p_config = source_runtime / "linked-peer-i2p.json"
        i2p_value = json.loads(json.dumps(source_value))
        i2p_value["route"] = {
            "kind": "i2p",
            "destination": I2P_PEER,
            "session_id": "anonsync-config-check-source",
        }
        i2p_value["service"]["timeout_seconds"] = 180
        i2p_value["service"]["cycle_runtime_seconds"] = 1080
        write_private_json(i2p_config, i2p_value)
        expect_checked_config(
            sync, i2p_config, transport="i2p_sam",
            local_device="source", remote_device="receiver",
            label="I2P linked-peer configuration check",
        )

        tor_ingress_config = source_runtime / "linked-peer-tor-ingress.json"
        tor_ingress_value = json.loads(json.dumps(source_value))
        tor_ingress_value["ingress"] = {
            "kind": "tor",
            "onion_address": VALID_ONION,
            "onion_port": 443,
        }
        write_private_json(tor_ingress_config, tor_ingress_value)
        expect_checked_config(
            sync, tor_ingress_config, transport="direct_tcp",
            ingress_transport="tor_onion_service",
            local_device="source", remote_device="receiver",
            label="externally managed Tor ingress configuration check",
        )

        missing_ingress = source_runtime / "linked-peer-missing-ingress.json"
        missing_ingress_value = json.loads(json.dumps(source_value))
        del missing_ingress_value["ingress"]
        write_private_json(missing_ingress, missing_ingress_value)
        expect_config_failure(
            sync, missing_ingress, "v2 missing-ingress configuration",
            message_contains="missing key ingress",
        )

        legacy_with_ingress = source_runtime / "linked-peer-v1-ingress.json"
        legacy_with_ingress_value = json.loads(json.dumps(source_value))
        legacy_with_ingress_value["schema"] = (
            "anonsync.linked-peer-service.v1"
        )
        write_private_json(legacy_with_ingress, legacy_with_ingress_value)
        expect_config_failure(
            sync, legacy_with_ingress, "v1 ingress-expansion configuration",
            message_contains="unknown key ingress",
        )

        private_destination = source_runtime / "i2p-private-destination"
        write_private_bytes(
            private_destination,
            b"persistent-private-destination-for-config-boundary\n",
            "I2P private destination",
        )
        missing_i2p_destination = (
            source_runtime / "linked-peer-i2p-missing-destination.json"
        )
        missing_i2p_destination_value = json.loads(json.dumps(source_value))
        missing_i2p_destination_value["ingress"] = {
            "kind": "i2p",
            "session_id": "anonsync-config-inbound",
        }
        missing_i2p_destination_value["service"][
            "ingress_timeout_seconds"
        ] = 180
        write_private_json(
            missing_i2p_destination, missing_i2p_destination_value
        )
        expect_config_failure(
            sync,
            missing_i2p_destination,
            "I2P ingress missing persistent destination configuration",
            message_contains="missing key private_destination_file",
        )

        transient_destination = source_runtime / "i2p-transient-destination"
        write_private_bytes(
            transient_destination,
            b"TRANSIENT\n",
            "transient I2P destination",
        )
        transient_i2p_ingress = (
            source_runtime / "linked-peer-i2p-transient-destination.json"
        )
        transient_i2p_ingress_value = json.loads(json.dumps(source_value))
        transient_i2p_ingress_value["ingress"] = {
            "kind": "i2p",
            "session_id": "anonsync-config-transient-inbound",
            "private_destination_file": str(transient_destination),
        }
        transient_i2p_ingress_value["service"][
            "ingress_timeout_seconds"
        ] = 180
        write_private_json(
            transient_i2p_ingress, transient_i2p_ingress_value
        )
        expect_config_failure(
            sync,
            transient_i2p_ingress,
            "I2P ingress transient destination configuration",
            message_contains="requires a persisted private destination",
        )

        short_i2p_timeout = (
            source_runtime / "linked-peer-i2p-short-timeout.json"
        )
        short_i2p_timeout_value = json.loads(json.dumps(source_value))
        short_i2p_timeout_value["ingress"] = {
            "kind": "i2p",
            "session_id": "anonsync-config-inbound",
            "private_destination_file": str(private_destination),
        }
        short_i2p_timeout_value["service"][
            "ingress_timeout_seconds"
        ] = 179
        write_private_json(short_i2p_timeout, short_i2p_timeout_value)
        expect_config_failure(
            sync,
            short_i2p_timeout,
            "I2P ingress short-timeout configuration",
            message_contains=(
                "ingress_timeout_seconds must be at least 180 for I2P"
            ),
        )

        shared_i2p_session_base = (
            source_runtime / "linked-peer-i2p-shared-session-base.json"
        )
        shared_i2p_session_base_value = json.loads(json.dumps(source_value))
        shared_i2p_session_base_value["route"] = {
            "kind": "i2p",
            "destination": I2P_PEER,
            "session_id": "anonsync-config-shared-base",
        }
        shared_i2p_session_base_value["ingress"] = {
            "kind": "i2p",
            "session_id": "anonsync-config-shared-base",
            "private_destination_file": str(private_destination),
        }
        shared_i2p_session_base_value["service"]["timeout_seconds"] = 180
        shared_i2p_session_base_value["service"][
            "ingress_timeout_seconds"
        ] = 180
        shared_i2p_session_base_value["service"][
            "cycle_runtime_seconds"
        ] = 1080
        write_private_json(
            shared_i2p_session_base, shared_i2p_session_base_value
        )
        expect_checked_config(
            sync,
            shared_i2p_session_base,
            transport="i2p_sam",
            ingress_transport="i2p_sam_accept",
            local_device="source",
            remote_device="receiver",
            label="I2P shared-session-base configuration check",
        )

        duplicate_i2p_destination = (
            source_runtime / "linked-peer-i2p-duplicate-destination.json"
        )
        duplicate_i2p_destination_value = json.loads(
            json.dumps(shared_i2p_session_base_value)
        )
        duplicate_i2p_destination_value["route"]["session_id"] = (
            "anonsync-config-outbound"
        )
        duplicate_i2p_destination_value["route"][
            "private_destination_file"
        ] = str(private_destination)
        duplicate_i2p_destination_value["ingress"]["session_id"] = (
            "anonsync-config-inbound"
        )
        write_private_json(
            duplicate_i2p_destination, duplicate_i2p_destination_value
        )
        expect_config_failure(
            sync,
            duplicate_i2p_destination,
            "I2P duplicate-destination configuration",
            message_contains="same persistent destination",
        )

        duplicate_runtime = root / "source-duplicate-runtime"
        duplicate_runtime.mkdir(mode=0o700)
        duplicate_port = reserve_port()
        while duplicate_port in {source_port, receiver_port}:
            duplicate_port = reserve_port()
        duplicate_status = duplicate_runtime / "status.sock"
        duplicate_config = duplicate_runtime / "linked-peer.json"
        relocated_manifest = duplicate_runtime / "relocated-deployment.json"
        relocate_deployment_manifest(source_manifest, relocated_manifest)
        duplicate_value = linked_peer_configuration(
            manifest=relocated_manifest,
            certificates=certificates,
            local_device="source",
            remote_device="receiver",
            remote_pin=receiver_pin,
            listen_port=duplicate_port,
            remote_port=receiver_port,
            status_socket=duplicate_status,
        )
        write_private_json(duplicate_config, duplicate_value)
        expect_checked_config(
            sync, duplicate_config, transport="direct_tcp",
            local_device="source", remote_device="receiver",
            label="relocated-manifest linked-peer configuration check",
        )

        unknown = root / "unknown-key.json"
        unknown_value = dict(source_value)
        unknown_value["bureaucracy"] = True
        write_private_json(unknown, unknown_value)
        expect_config_failure(
            sync, unknown, "unknown-key configuration",
            message_contains="unknown key bureaucracy",
        )

        readable = root / "world-readable.json"
        write_private_json(readable, source_value)
        os.chmod(readable, 0o644)
        expect_config_failure(
            sync, readable, "world-readable configuration",
            message_contains="mode 0600",
            error_code="operation_failed",
        )

        base_environment = os.environ.copy()
        base_environment.pop("NOTIFY_SOCKET", None)
        missing_notify_environment = base_environment.copy()
        missing_notify_environment["NOTIFY_SOCKET"] = str(
            root / "missing-systemd-notify.sock"
        )
        missing_notify = subprocess.run(
            [str(sync), "run", "--config", str(source_config)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=missing_notify_environment,
            timeout=5.0,
            check=False,
        )
        if missing_notify.returncode != 1:
            fail(
                "configured but unreachable service manager did not fail startup: "
                f"{missing_notify.returncode}\nstdout:\n{missing_notify.stdout}"
                f"\nstderr:\n{missing_notify.stderr}"
            )
        try:
            missing_notify_value = json.loads(missing_notify.stdout)
        except json.JSONDecodeError as error:
            fail(f"missing service-manager failure was not JSON: {error}")
        if missing_notify_value.get("error_code") != "operation_failed" or (
            "sendto" not in str(missing_notify_value.get("message", ""))
        ):
            fail(
                "missing service-manager failure was not exact: "
                f"{json.dumps(missing_notify_value, sort_keys=True)}"
            )
        if source_status.exists():
            fail("failed Type=notify startup created a status socket")

        notify_path = root / "source-systemd-notify.sock"
        notify_receiver = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        notify_receiver.bind(str(notify_path))
        source_environment = base_environment.copy()
        source_environment["NOTIFY_SOCKET"] = str(notify_path)
        source = subprocess.Popen(
            [str(sync), "run", "--config", str(source_config)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=source_environment,
        )
        receiver = subprocess.Popen(
            [str(sync), "run", "--config", str(receiver_config)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=base_environment,
        )
        try:
            receive_notify_until_ready(
                notify_receiver, source, "config-driven source service"
            )
            notify_receiver.close()
            notify_path.unlink()
            wait_for_service_listener(
                source, source_port, "config-driven source service"
            )
            wait_for_service_listener(
                receiver, receiver_port, "config-driven receiver service"
            )
            initial_source_status = wait_for_status(
                sync, source, source_status, "source", "receiver",
                source_config, "config-driven source service",
            )
            initial_receiver_status = wait_for_status(
                sync, receiver, receiver_status, "receiver", "source",
                receiver_config, "config-driven receiver service",
            )
            if initial_source_status.get("activity") not in {
                "starting", "initial_repair", "peer_service_step",
                "between_steps",
            }:
                fail("source status reported an unknown activity")
            if initial_receiver_status.get("activity") not in {
                "starting", "initial_repair", "peer_service_step",
                "between_steps",
            }:
                fail("receiver status reported an unknown activity")

            expect_singleton_failure(
                sync, duplicate_config,
                "second service for the same source deployment",
            )
            if duplicate_status.exists():
                fail("rejected duplicate service created a status socket")
            expect_deployment_ownership_failure(
                [
                    str(sync), "database-recovery-inspect",
                    "--manifest", str(source_manifest),
                ],
                "offline recovery inspection beside the retained service",
            )
            # once acquires the deployment singleton before parsing route, TLS,
            # or peer options. This deliberately incomplete invocation proves
            # one-shot synchronization cannot race the retained service.
            expect_deployment_ownership_failure(
                [str(sync), "once", "--manifest", str(source_manifest)],
                "one-shot sync beside the retained service",
            )

            # Native-I2P route admission may open the private destination file.
            # A missing file would therefore expose any regression that parsed
            # route authority before claiming the deployment singleton.
            unopened_i2p_private_destination = (
                root / "must-not-open-i2p-private-destination"
            )
            if unopened_i2p_private_destination.exists():
                fail("I2P singleton-order fixture unexpectedly exists")
            expect_deployment_ownership_failure(
                [
                    str(sync), "once", "--manifest", str(source_manifest),
                    "--transport", "i2p",
                    "--i2p-sam-address", "127.0.0.1",
                    "--i2p-sam-port", "7656",
                    "--i2p-destination", "unparsed-destination",
                    "--i2p-private-destination-file",
                    str(unopened_i2p_private_destination),
                    "--timeout-seconds", "180",
                ],
                "one-shot ownership before I2P private route",
            )

            wait_for_tree_convergence(
                source_files, receiver_files,
                "receiver-side/nested/beta.txt",
                "config-driven retained service convergence",
            )
            source_after = run_json(
                [str(sync), "status", "--socket", str(source_status)],
                label="source status after convergence",
            )
            receiver_after = run_json(
                [str(sync), "status", "--socket", str(receiver_status)],
                label="receiver status after convergence",
            )
            if source_after.get("generation", 0) < 1:
                fail("source live status did not advance after a service step")
            if receiver_after.get("generation", 0) < 1:
                fail("receiver live status did not advance after a service step")

            # Ordinary append-only payload retention already preserves exact
            # predecessor bytes, but they were not owner-visible or safely
            # restorable. Change one source file, inspect the bounded causal
            # predecessor inventory through the owner-only action lane, then
            # restore the exact predecessor. The service must publish a new
            # causal successor rather than reactivate the old operation.
            historical_relative_path = "source-side/nested/alpha.txt"
            historical_path = source_files / historical_relative_path
            historical_v1 = b"config-driven source payload\n"
            historical_v2 = b"config-driven source payload revision two\n"
            if historical_path.read_bytes() != historical_v1:
                fail("historical-version fixture did not begin at v1")
            overwrite_regular_file(
                historical_path, historical_v2,
                "historical-version v2 publication",
            )
            wait_for_tree_convergence(
                source_files, receiver_files, historical_relative_path,
                "historical-version v2 convergence",
            )
            if historical_path.read_bytes() != historical_v2 or (
                receiver_files / historical_relative_path
            ).read_bytes() != historical_v2:
                fail("historical-version v2 did not converge exactly")

            history_before = run_json(
                [str(sync), "status", "--socket", str(source_status)],
                label="historical-version baseline status",
            )
            require_payload_operator_status(
                history_before, "historical-version baseline"
            )
            history_before_state = history_before["historical_versions"]
            history_inspection_generation = (
                history_before_state["completed_generation"] + 1
            )
            versions_response = run_json(
                [
                    str(sync), "versions", "--socket", str(source_status),
                    "--path", historical_relative_path,
                    "--limit", "1",
                    "--timeout-milliseconds", "1000",
                ],
                label="owner-only historical-version inspection",
            )
            expected_versions_response = {
                "schema": "anonsync.local-historical-versions.response.v5",
                "command": "versions",
                "terminal_class": "accepted",
                "request_generation": history_inspection_generation,
                "inspection_mode": "exact_payload_availability",
                "maximum_entries": 1,
                "canonical_path": historical_relative_path,
                "start_after_operation_id": None,
                "expected_source_cutpoint": None,
                "server_pid": source.pid,
            }
            if versions_response != expected_versions_response:
                fail(
                    "historical-version inspection acceptance was not exact: "
                    f"{json.dumps(versions_response, sort_keys=True)}"
                )
            inspected_status = wait_for_historical_version_completion(
                sync, source, source_status, history_inspection_generation,
                "inspect", "historical-version inspection",
            )
            inventory = inspected_status["historical_versions"][
                "last_inventory"
            ]
            require_historical_version_inventory(
                inventory, "historical-version inspection"
            )
            expected_initial_history_query = {
                "inspection_mode": "exact_payload_availability",
                "maximum_entries": 1,
                "canonical_path": historical_relative_path,
                "start_after_operation_id": None,
                "expected_source_cutpoint": None,
            }
            if inventory.get("query") != expected_initial_history_query:
                fail(
                    "historical-version inspection changed its exact query: "
                    f"{json.dumps(inventory, sort_keys=True)}"
                )
            if inventory.get("historical_file_operation_count") != 1 or (
                inventory.get("historical_file_operation_count_after_cursor")
                != 1
            ) or inventory.get("truncated") is not False or (
                inventory.get("next_start_after_operation_id") is not None
            ):
                fail(
                    "historical-version first inspection did not prove the "
                    "single path-scoped predecessor exactly: "
                    f"{json.dumps(inventory, sort_keys=True)}"
                )
            historical_v1_digest = hashlib.sha256(historical_v1).hexdigest()
            matching_entries = [
                entry for entry in inventory["entries"]
                if entry["canonical_path"] == historical_relative_path
                and entry["content_sha256"] == historical_v1_digest
                and entry["size_bytes"] == len(historical_v1)
            ]
            if len(matching_entries) != 1:
                fail(
                    "historical-version inspection did not return the exact "
                    f"v1 predecessor: {json.dumps(inventory, sort_keys=True)}"
                )
            historical_entry = matching_entries[0]
            if historical_entry["payload_present"] is not True or (
                historical_entry["restore_ready"] is not True
            ) or historical_entry["visible_head_count"] != 1:
                fail(
                    "historical-version predecessor was not exactly "
                    f"restore-ready: {json.dumps(historical_entry, sort_keys=True)}"
                )
            historical_operation_id = historical_entry["operation_id"]
            replaced_operation_id = historical_entry[
                "current_primary_operation_id"
            ]
            if historical_operation_id == replaced_operation_id:
                fail("historical-version inventory marked its visible head historical")

            restore_generation = history_inspection_generation + 1
            restore_response = run_json(
                [
                    str(sync), "restore", "--socket", str(source_status),
                    "--operation", historical_operation_id,
                    "--expected-current", replaced_operation_id,
                    "--timeout-milliseconds", "1000",
                ],
                label="owner-only exact historical-version restore",
            )
            expected_restore_response = {
                "schema": (
                    "anonsync.local-historical-version-restore.response.v2"
                ),
                "command": "restore",
                "terminal_class": "accepted",
                "request_generation": restore_generation,
                "operation_id": historical_operation_id,
                "expected_current_operation_id": replaced_operation_id,
                "server_pid": source.pid,
            }
            if restore_response != expected_restore_response:
                fail(
                    "historical-version restore acceptance was not exact: "
                    f"{json.dumps(restore_response, sort_keys=True)}"
                )
            restored_status = wait_for_historical_version_completion(
                sync, source, source_status, restore_generation, "restore",
                "historical-version restore",
            )
            restored = restored_status["historical_versions"]["last_restore"]
            require_historical_version_restore(
                restored, "historical-version restore"
            )
            expected_restore_fields = {
                "historical_operation_id": historical_operation_id,
                "replaced_visible_operation_id": replaced_operation_id,
                "canonical_path": historical_relative_path,
                "size_bytes": len(historical_v1),
                "content_sha256": historical_v1_digest,
            }
            for key, wanted in expected_restore_fields.items():
                if restored.get(key) != wanted:
                    fail(
                        f"historical-version restore field {key!r} was "
                        f"{restored.get(key)!r}, expected {wanted!r}: "
                        f"{json.dumps(restored, sort_keys=True)}"
                    )
            wait_for_tree_convergence(
                source_files, receiver_files, historical_relative_path,
                "historical-version restored successor convergence",
            )
            if historical_path.read_bytes() != historical_v1 or (
                receiver_files / historical_relative_path
            ).read_bytes() != historical_v1:
                fail("historical-version restore did not converge exact v1 bytes")

            # The accepted restore was bound to the exact v2 head inspected by
            # the operator. Reusing that intent after the new v1 successor is
            # visible must fail before catalog, rooted-path, or payload access;
            # the same daemon remains available and records the exact stage.
            stale_restore_generation = restore_generation + 1
            stale_restore_response = run_json(
                [
                    str(sync), "restore", "--socket", str(source_status),
                    "--operation", historical_operation_id,
                    "--expected-current", replaced_operation_id,
                    "--timeout-milliseconds", "1000",
                ],
                label="owner-only stale exact-current historical restore",
            )
            expected_stale_restore_response = {
                "schema": (
                    "anonsync.local-historical-version-restore.response.v2"
                ),
                "command": "restore",
                "terminal_class": "accepted",
                "request_generation": stale_restore_generation,
                "operation_id": historical_operation_id,
                "expected_current_operation_id": replaced_operation_id,
                "server_pid": source.pid,
            }
            if stale_restore_response != expected_stale_restore_response:
                fail(
                    "stale exact-current restore acceptance was not exact: "
                    f"{json.dumps(stale_restore_response, sort_keys=True)}"
                )
            stale_restore_status = wait_for_historical_version_source_change(
                sync,
                source,
                source_status,
                stale_restore_generation,
                "restore_current_operation",
                "stale exact-current historical restore",
                expected_action="restore",
            )
            stale_restore_history = stale_restore_status[
                "historical_versions"
            ]
            if (
                stale_restore_history.get("operation_id")
                != historical_operation_id
                or stale_restore_history.get(
                    "expected_current_operation_id"
                )
                != replaced_operation_id
                or "current operation changed"
                not in stale_restore_history.get("last_failure", "")
            ):
                fail(
                    "stale exact-current restore did not retain its exact intent "
                    "and source-change evidence: "
                    f"{json.dumps(stale_restore_history, sort_keys=True)}"
                )
            if source.poll() is not None:
                fail("stale exact-current restore terminated the service")

            # Restoring v1 publishes a new causal successor and leaves both
            # superseded operations active as immutable historical evidence.
            # Exercise exact one-entry cursor pagination so neither predecessor
            # can be stranded behind the bounded first page.
            first_page_generation = stale_restore_generation + 1
            first_page_response = run_json(
                [
                    str(sync), "versions", "--socket", str(source_status),
                    "--path", historical_relative_path,
                    "--limit", "1",
                    "--timeout-milliseconds", "1000",
                ],
                label="owner-only historical-version first page",
            )
            expected_first_page_response = {
                "schema": "anonsync.local-historical-versions.response.v5",
                "command": "versions",
                "terminal_class": "accepted",
                "request_generation": first_page_generation,
                "inspection_mode": "exact_payload_availability",
                "maximum_entries": 1,
                "canonical_path": historical_relative_path,
                "start_after_operation_id": None,
                "expected_source_cutpoint": None,
                "server_pid": source.pid,
            }
            if first_page_response != expected_first_page_response:
                fail(
                    "historical-version first-page acceptance was not exact: "
                    f"{json.dumps(first_page_response, sort_keys=True)}"
                )
            first_page_status = wait_for_historical_version_completion(
                sync, source, source_status, first_page_generation, "inspect",
                "historical-version first page",
            )
            first_page = first_page_status["historical_versions"][
                "last_inventory"
            ]
            require_historical_version_inventory(
                first_page, "historical-version first page"
            )
            expected_first_page_query = {
                "inspection_mode": "exact_payload_availability",
                "maximum_entries": 1,
                "canonical_path": historical_relative_path,
                "start_after_operation_id": None,
                "expected_source_cutpoint": None,
            }
            if first_page.get("query") != expected_first_page_query or (
                first_page.get("historical_file_operation_count") != 2
            ) or first_page.get(
                "historical_file_operation_count_after_cursor"
            ) != 2 or first_page.get("truncated") is not True or len(
                first_page.get("entries", [])
            ) != 1:
                fail(
                    "historical-version first page did not expose the exact "
                    "two-predecessor cursor frontier: "
                    f"{json.dumps(first_page, sort_keys=True)}"
                )
            page_cursor = first_page.get("next_start_after_operation_id")
            if not is_canonical_sha256(page_cursor) or page_cursor != (
                first_page["entries"][0]["operation_id"]
            ):
                fail("historical-version first page omitted its exact tail cursor")
            page_source_cutpoint = first_page.get("source_cutpoint")
            if not is_canonical_historical_source_cutpoint(page_source_cutpoint):
                fail("historical-version first page omitted its exact source cutpoint")

            second_page_generation = first_page_generation + 1
            second_page_response = run_json(
                [
                    str(sync), "versions", "--socket", str(source_status),
                    "--path", historical_relative_path,
                    "--after", page_cursor,
                    "--source-cutpoint", page_source_cutpoint,
                    "--limit", "1",
                    "--timeout-milliseconds", "1000",
                ],
                label="owner-only historical-version second page",
            )
            expected_second_page_response = {
                "schema": "anonsync.local-historical-versions.response.v5",
                "command": "versions",
                "terminal_class": "accepted",
                "request_generation": second_page_generation,
                "inspection_mode": "exact_payload_availability",
                "maximum_entries": 1,
                "canonical_path": historical_relative_path,
                "start_after_operation_id": page_cursor,
                "expected_source_cutpoint": page_source_cutpoint,
                "server_pid": source.pid,
            }
            if second_page_response != expected_second_page_response:
                fail(
                    "historical-version second-page acceptance was not exact: "
                    f"{json.dumps(second_page_response, sort_keys=True)}"
                )
            second_page_status = wait_for_historical_version_completion(
                sync, source, source_status, second_page_generation, "inspect",
                "historical-version second page",
            )
            second_page = second_page_status["historical_versions"][
                "last_inventory"
            ]
            require_historical_version_inventory(
                second_page, "historical-version second page"
            )
            expected_second_page_query = {
                "inspection_mode": "exact_payload_availability",
                "maximum_entries": 1,
                "canonical_path": historical_relative_path,
                "start_after_operation_id": page_cursor,
                "expected_source_cutpoint": page_source_cutpoint,
            }
            if second_page.get("query") != expected_second_page_query or (
                second_page.get("historical_file_operation_count") != 2
            ) or second_page.get(
                "historical_file_operation_count_after_cursor"
            ) != 1 or second_page.get("truncated") is not False or (
                second_page.get("next_start_after_operation_id") is not None
            ) or len(second_page.get("entries", [])) != 1:
                fail(
                    "historical-version second page did not settle the exact "
                    "cursor suffix: "
                    f"{json.dumps(second_page, sort_keys=True)}"
                )
            paged_operation_ids = {
                first_page["entries"][0]["operation_id"],
                second_page["entries"][0]["operation_id"],
            }
            if paged_operation_ids != {
                historical_operation_id,
                replaced_operation_id,
            }:
                fail(
                    "historical-version cursor pages omitted, duplicated, or "
                    "invented predecessor operations: "
                    f"{sorted(paged_operation_ids)!r}"
                )

            # The page cursor still names one valid superseded operation, but
            # another causal successor changes the complete active operation set.
            # Reusing the old source token must fail before payload observation,
            # preserve the same daemon, clear stale result objects, and expose
            # the typed source-change stage through ordinary status.
            unrelated_drift_relative_path = (
                "source-side/source-cutpoint-drift.txt"
            )
            unrelated_drift_bytes = b"unrelated causal source drift\n"
            unrelated_drift_path = source_files / unrelated_drift_relative_path
            if unrelated_drift_path.exists():
                fail("unrelated historical source-drift fixture already existed")
            unrelated_drift_path.write_bytes(unrelated_drift_bytes)
            wait_for_tree_convergence(
                source_files, receiver_files, unrelated_drift_relative_path,
                "historical-version unrelated source-cutpoint convergence",
            )
            if unrelated_drift_path.read_bytes() != unrelated_drift_bytes or (
                receiver_files / unrelated_drift_relative_path
            ).read_bytes() != unrelated_drift_bytes:
                fail("unrelated historical source drift did not converge exactly")

            stale_source_generation = second_page_generation + 1
            stale_source_response = run_json(
                [
                    str(sync), "versions", "--socket", str(source_status),
                    "--path", historical_relative_path,
                    "--after", page_cursor,
                    "--source-cutpoint", page_source_cutpoint,
                    "--limit", "1",
                    "--timeout-milliseconds", "1000",
                ],
                label="owner-only stale historical source cutpoint",
            )
            expected_stale_source_response = {
                "schema": "anonsync.local-historical-versions.response.v5",
                "command": "versions",
                "terminal_class": "accepted",
                "request_generation": stale_source_generation,
                "inspection_mode": "exact_payload_availability",
                "maximum_entries": 1,
                "canonical_path": historical_relative_path,
                "start_after_operation_id": page_cursor,
                "expected_source_cutpoint": page_source_cutpoint,
                "server_pid": source.pid,
            }
            if stale_source_response != expected_stale_source_response:
                fail(
                    "stale historical source acceptance was not exact: "
                    f"{json.dumps(stale_source_response, sort_keys=True)}"
                )
            stale_source_status = wait_for_historical_version_source_change(
                sync, source, source_status, stale_source_generation,
                "operation_set_before_payload_observation",
                "stale historical source cutpoint",
            )
            stale_history = stale_source_status["historical_versions"]
            expected_stale_query = {
                "inspection_mode": "exact_payload_availability",
                "maximum_entries": 1,
                "canonical_path": historical_relative_path,
                "start_after_operation_id": page_cursor,
                "expected_source_cutpoint": page_source_cutpoint,
            }
            if stale_history.get("query") != expected_stale_query or (
                "operation set changed before payload observation"
                not in stale_history.get("last_failure", "")
            ):
                fail(
                    "stale historical source did not preserve exact query and "
                    f"failure evidence: {json.dumps(stale_history, sort_keys=True)}"
                )
            if source.poll() is not None:
                fail("typed historical source drift terminated the service")

            # Causal-metadata inspection is the cheap browsing authority. It
            # uses the same owner action lane and immutable operation-set
            # cutpoint, but it must not claim that retained payload bytes were
            # observed. Every payload-derived field is therefore null rather
            # than false or zero, and its source token is mode-bound.
            metadata_generation = stale_source_generation + 1
            metadata_response = run_json(
                [
                    str(sync), "versions", "--socket", str(source_status),
                    "--inspection-mode", "metadata",
                    "--path", historical_relative_path,
                    "--limit", "1",
                    "--timeout-milliseconds", "1000",
                ],
                label="owner-only causal-metadata historical inspection",
            )
            expected_metadata_response = {
                "schema": "anonsync.local-historical-versions.response.v5",
                "command": "versions",
                "terminal_class": "accepted",
                "request_generation": metadata_generation,
                "inspection_mode": "causal_metadata_only",
                "maximum_entries": 1,
                "canonical_path": historical_relative_path,
                "start_after_operation_id": None,
                "expected_source_cutpoint": None,
                "server_pid": source.pid,
            }
            if metadata_response != expected_metadata_response:
                fail(
                    "causal-metadata historical acceptance was not exact: "
                    f"{json.dumps(metadata_response, sort_keys=True)}"
                )
            metadata_status = wait_for_historical_version_completion(
                sync, source, source_status, metadata_generation, "inspect",
                "causal-metadata historical inspection",
            )
            metadata_inventory = metadata_status["historical_versions"][
                "last_inventory"
            ]
            require_historical_version_inventory(
                metadata_inventory, "causal-metadata historical inspection"
            )
            expected_metadata_query = {
                "inspection_mode": "causal_metadata_only",
                "maximum_entries": 1,
                "canonical_path": historical_relative_path,
                "start_after_operation_id": None,
                "expected_source_cutpoint": None,
            }
            if metadata_inventory.get("query") != expected_metadata_query:
                fail(
                    "causal-metadata historical inspection changed its query: "
                    f"{json.dumps(metadata_inventory, sort_keys=True)}"
                )
            if not metadata_inventory["source_cutpoint"].startswith(
                "v4:metadata:"
            ) or metadata_inventory.get(
                "source_payload_snapshot_digest"
            ) is not None:
                fail(
                    "causal-metadata historical inspection invented payload "
                    "authority or omitted its mode-bound token"
                )
            if len(metadata_inventory.get("entries", [])) != 1 or any(
                metadata_inventory.get(field) is not None
                for field in (
                    "payload_scan_hashed_entries",
                    "payload_scan_hashed_bytes",
                    "payload_scan_reused_entries",
                    "payload_scan_reused_bytes",
                    "payload_present_count",
                    "restore_ready_count",
                )
            ) or any(
                entry.get(field) is not None
                for entry in metadata_inventory["entries"]
                for field in ("payload_present", "restore_ready")
            ):
                fail(
                    "causal-metadata historical inspection fabricated "
                    "payload-derived evidence: "
                    f"{json.dumps(metadata_inventory, sort_keys=True)}"
                )

            # Pinning is durable replica evidence policy, not a payload-store
            # mutation. Prove the complete shipping path: strict owner-only
            # admission, one serialized historical action, durable result
            # reporting, and a subsequent metadata-only inventory whose exact
            # source cutpoint and entry projection both include the pin set.
            pin_operation_id = metadata_inventory["entries"][0]["operation_id"]
            pin_content_sha256 = metadata_inventory["entries"][0][
                "content_sha256"
            ]
            pin_generation = metadata_generation + 1
            pin_response = run_json(
                [
                    str(sync), "version-pin", "--socket", str(source_status),
                    "--operation", pin_operation_id,
                    "--timeout-milliseconds", "1000",
                ],
                label="owner-only historical version pin",
            )
            expected_pin_response = {
                "schema": "anonsync.local-historical-version-pin.response.v1",
                "command": "version-pin",
                "terminal_class": "accepted",
                "request_generation": pin_generation,
                "operation_id": pin_operation_id,
                "server_pid": source.pid,
            }
            if pin_response != expected_pin_response:
                fail(
                    "historical version pin acceptance was not exact: "
                    f"{json.dumps(pin_response, sort_keys=True)}"
                )
            pin_status = wait_for_historical_version_completion(
                sync, source, source_status, pin_generation, "pin",
                "historical version pin",
            )
            pin_update = pin_status["historical_versions"]["last_pin_update"]
            if (
                pin_update.get("disposition") != "pinned"
                or pin_update.get("operation_id") != pin_operation_id
                or pin_update.get("pin_count") != 1
                or not is_canonical_sha256(pin_update.get("pin_set_digest"))
                or pin_status["historical_versions"].get("last_inventory")
                is not None
                or pin_status["historical_versions"].get("last_restore")
                is not None
            ):
                fail(
                    "historical version pin did not publish one exact durable "
                    f"result: {json.dumps(pin_status['historical_versions'], sort_keys=True)}"
                )

            # Compose the complete exact reachability proof with the durable
            # pin set, but stop strictly before any collection authority. The
            # diagnostic planner must classify every physical payload in digest
            # order and explain why the selected predecessor is required.
            retention_plan_generation = pin_generation + 1
            retention_plan_response = run_json(
                [
                    str(sync), "retention-plan", "--socket",
                    str(source_status), "--limit", "1024",
                    "--timeout-milliseconds", "1000",
                ],
                label="owner-only deletion-free retention plan",
            )
            expected_retention_plan_response = {
                "schema": "anonsync.local-retention-plan.response.v6",
                "command": "retention-plan",
                "terminal_class": "accepted",
                "request_generation": retention_plan_generation,
                "maximum_entries": 1024,
                "start_after_content_sha256": None,
                "expected_source_cutpoint": None,
                "server_pid": source.pid,
            }
            if retention_plan_response != expected_retention_plan_response:
                fail(
                    "retention-plan acceptance was not exact: "
                    f"{json.dumps(retention_plan_response, sort_keys=True)}"
                )
            retention_plan_status = wait_for_historical_version_completion(
                sync, source, source_status, retention_plan_generation,
                "retention_plan", "deletion-free retention plan",
            )
            retention_plan = retention_plan_status["historical_versions"][
                "last_retention_plan"
            ]
            require_retention_plan(
                retention_plan, "deletion-free retention plan"
            )
            if (
                retention_plan["query"]
                != {
                    "maximum_entries": 1024,
                    "start_after_content_sha256": None,
                    "expected_source_cutpoint": None,
                }
                or retention_plan["historical_version_pin_count"] != 1
                or retention_plan[
                    "source_historical_version_pin_set_digest"
                ] != pin_update["pin_set_digest"]
                or retention_plan["truncated"] is not False
                or retention_plan["writer_fenced_observation"] is not True
                or retention_plan[
                    "cooperating_new_namespace_activity_excluded_during_observation"
                ] is not True
                or retention_plan["payload_store_transient_namespace_bound"]
                is not True
                or retention_plan["durable_receiver_restart_obligations_bound"]
                is not True
                or retention_plan["same_process_store_live_payload_capabilities_bound"]
                is not True
                or retention_plan[
                    "independently_opened_same_process_store_owner_live_payload_capabilities_bound"
                ] is not True
                or retention_plan["independent_store_owner_live_payload_capabilities_bound"]
                is not False
                or retention_plan["cross_process_live_payload_capabilities_bound"]
                is not False
                or retention_plan["already_copied_response_bytes_bound"]
                is not False
                or retention_plan["active_pass_transient_roots_bound"]
                is not False
                or retention_plan["opened_sender_transient_roots_bound"]
                is not False
                or retention_plan["mutation_batch_transient_roots_bound"]
                is not False
                or retention_plan["external_transient_root_model_complete"]
                is not False
                or any(
                    retention_plan["live_payload_capabilities"][field] != 0
                    for field in (
                        "snapshot_count", "opened_payload_count",
                        "targeted_access_count", "mutation_batch_count",
                        "distinct_opened_payload_root_count",
                        "distinct_opened_payload_root_bytes",
                        "rooted_physical_payload_count",
                        "rooted_physical_payload_bytes",
                        "unreferenced_rooted_payload_count",
                        "unreferenced_rooted_payload_bytes",
                    )
                )
                or retention_plan["live_payload_capabilities"]
                    ["may_reopen_all_current_payloads"] is not False
                or not is_canonical_sha256(
                    retention_plan["source_payload_transient_namespace_digest"]
                )
                or retention_plan["payload_transient_reserved_bytes"]
                < retention_plan["payload_transient_bytes"]
            ):
                fail(
                    "retention plan did not bind the exact pinned source: "
                    f"{json.dumps(retention_plan, sort_keys=True)}"
                )
            pinned_payload_entries = [
                entry for entry in retention_plan["entries"]
                if entry["content_sha256"] == pin_content_sha256
            ]
            if len(pinned_payload_entries) != 1 or (
                pinned_payload_entries[0]["explicit_pin"] is not True
            ) or pinned_payload_entries[0]["disposition"] != (
                "current_or_explicit_pin"
            ) or pinned_payload_entries[0]["payload_use_disposition"] != (
                "not_applicable"
            ):
                fail(
                    "retention plan did not explain the exact pinned payload: "
                    f"{json.dumps(pinned_payload_entries, sort_keys=True)}"
                )
            if retention_plan_status["historical_versions"].get(
                "last_inventory"
            ) is not None or retention_plan_status["historical_versions"].get(
                "last_restore"
            ) is not None or retention_plan_status["historical_versions"].get(
                "last_pin_update"
            ) is not None:
                fail("retention plan retained a result from another action")

            pinned_inspection_generation = retention_plan_generation + 1
            pinned_response = run_json(
                [
                    str(sync), "versions", "--socket", str(source_status),
                    "--inspection-mode", "metadata",
                    "--path", historical_relative_path,
                    "--limit", "1",
                    "--timeout-milliseconds", "1000",
                ],
                label="pinned causal-metadata historical inspection",
            )
            expected_pinned_response = dict(expected_metadata_response)
            expected_pinned_response["request_generation"] = (
                pinned_inspection_generation
            )
            if pinned_response != expected_pinned_response:
                fail(
                    "pinned causal-metadata acceptance was not exact: "
                    f"{json.dumps(pinned_response, sort_keys=True)}"
                )
            pinned_status = wait_for_historical_version_completion(
                sync, source, source_status, pinned_inspection_generation,
                "inspect", "pinned causal-metadata historical inspection",
            )
            pinned_inventory = pinned_status["historical_versions"][
                "last_inventory"
            ]
            if (
                pinned_inventory.get("source_historical_version_pin_set_digest")
                != pin_update["pin_set_digest"]
                or pinned_inventory.get("historical_version_pin_count") != 1
                or len(pinned_inventory.get("entries", [])) != 1
                or pinned_inventory["entries"][0].get("operation_id")
                != pin_operation_id
                or pinned_inventory["entries"][0].get("pinned") is not True
            ):
                fail(
                    "metadata history did not project the durable pin: "
                    f"{json.dumps(pinned_inventory, sort_keys=True)}"
                )

            unpin_generation = pinned_inspection_generation + 1
            unpin_response = run_json(
                [
                    str(sync), "version-unpin", "--socket", str(source_status),
                    "--operation", pin_operation_id,
                    "--timeout-milliseconds", "1000",
                ],
                label="owner-only historical version unpin",
            )
            expected_unpin_response = {
                "schema": "anonsync.local-historical-version-unpin.response.v1",
                "command": "version-unpin",
                "terminal_class": "accepted",
                "request_generation": unpin_generation,
                "operation_id": pin_operation_id,
                "server_pid": source.pid,
            }
            if unpin_response != expected_unpin_response:
                fail(
                    "historical version unpin acceptance was not exact: "
                    f"{json.dumps(unpin_response, sort_keys=True)}"
                )
            unpin_status = wait_for_historical_version_completion(
                sync, source, source_status, unpin_generation, "unpin",
                "historical version unpin",
            )
            unpin_update = unpin_status["historical_versions"][
                "last_pin_update"
            ]
            if (
                unpin_update.get("disposition") != "unpinned"
                or unpin_update.get("operation_id") != pin_operation_id
                or unpin_update.get("pin_count") != 0
                or not is_canonical_sha256(unpin_update.get("pin_set_digest"))
                or unpin_update.get("pin_set_digest")
                == pin_update.get("pin_set_digest")
            ):
                fail(
                    "historical version unpin did not publish the exact "
                    f"successor set: {json.dumps(unpin_update, sort_keys=True)}"
                )

            unpinned_inspection_generation = unpin_generation + 1
            unpinned_response = run_json(
                [
                    str(sync), "versions", "--socket", str(source_status),
                    "--inspection-mode", "metadata",
                    "--path", historical_relative_path,
                    "--limit", "1",
                    "--timeout-milliseconds", "1000",
                ],
                label="unpinned causal-metadata historical inspection",
            )
            expected_unpinned_response = dict(expected_metadata_response)
            expected_unpinned_response["request_generation"] = (
                unpinned_inspection_generation
            )
            if unpinned_response != expected_unpinned_response:
                fail(
                    "unpinned causal-metadata acceptance was not exact: "
                    f"{json.dumps(unpinned_response, sort_keys=True)}"
                )
            metadata_status = wait_for_historical_version_completion(
                sync, source, source_status, unpinned_inspection_generation,
                "inspect", "unpinned causal-metadata historical inspection",
            )
            unpinned_inventory = metadata_status["historical_versions"][
                "last_inventory"
            ]
            if (
                unpinned_inventory.get("source_historical_version_pin_set_digest")
                != unpin_update["pin_set_digest"]
                or unpinned_inventory.get("historical_version_pin_count") != 0
                or len(unpinned_inventory.get("entries", [])) != 1
                or unpinned_inventory["entries"][0].get("operation_id")
                != pin_operation_id
                or unpinned_inventory["entries"][0].get("pinned") is not False
            ):
                fail(
                    "metadata history retained a removed pin: "
                    f"{json.dumps(unpinned_inventory, sort_keys=True)}"
                )

            history_counters = metadata_status.get("counters")
            if not isinstance(history_counters, dict):
                fail("historical-version restore status omitted counters")
            expected_history_counters = {
                "historical_version_requests_observed": 12,
                "historical_version_attempts": 12,
                "historical_version_completions": 12,
                "historical_version_inspections": 6,
                "historical_version_retention_plans": 1,
                "historical_version_restores": 1,
                "historical_version_pins": 1,
                "historical_version_unpins": 1,
                "historical_version_failures": 2,
            }
            for field, wanted in expected_history_counters.items():
                if history_counters.get(field) != wanted:
                    fail(
                        f"historical-version counter {field!r} was "
                        f"{history_counters.get(field)!r}, expected {wanted!r}"
                    )

            # A current-byte mismatch used to escape the peer-service owner,
            # destroy the process, and remove the only live status/control
            # endpoint. Corrupt one exact payload object after convergence and
            # prove the service instead remains alive, publishes a fail-closed
            # fault, performs no ordinary work until a complete reproof, and
            # recovers after the owner explicitly preserves the exact corrupt
            # byte image outside payload authority.
            source_payload_bytes = b"config-driven source payload\n"
            source_payload_digest = hashlib.sha256(
                source_payload_bytes
            ).hexdigest()
            source_payload_path = (
                source_manifest.parent.parent
                / "payload"
                / source_payload_digest
            )
            if source_payload_path.read_bytes() != source_payload_bytes:
                fail("source payload store omitted the converged exact object")
            corrupted_payload_bytes = bytes(
                [source_payload_bytes[0] ^ 0x5A]
            ) + source_payload_bytes[1:]
            corrupted_payload_digest = hashlib.sha256(
                corrupted_payload_bytes
            ).hexdigest()
            source_after_counters = source_after.get("counters")
            if not isinstance(source_after_counters, dict):
                fail("source status omitted counters before lease deferral")
            lease_deferrals_before = source_after_counters.get(
                "payload_store_lease_busy_deferrals"
            )
            if not isinstance(lease_deferrals_before, int):
                fail("source status omitted lease deferral baseline")
            source_recheck_before = source_after.get("payload_recheck")
            if not isinstance(source_recheck_before, dict):
                fail("source status omitted payload recheck baseline")
            if source_recheck_before.get("pending") is not False:
                fail("source unexpectedly began with a pending payload recheck")
            accepted_recheck_generation = 0

            def require_live_lease_deferral() -> None:
                nonlocal accepted_recheck_generation
                accepted_responses: list[dict[str, Any]] = []
                for index in range(2):
                    response = run_json(
                        [
                            str(sync), "recheck", "--socket",
                            str(source_status), "--timeout-milliseconds", "1000",
                        ],
                        label=f"owner-only payload recheck request {index + 1}",
                    )
                    accepted_responses.append(response)
                    expected_generation = accepted_recheck_generation + 1
                    expected_response = {
                        "schema": "anonsync.local-recheck.response.v1",
                        "command": "recheck",
                        "terminal_class": "accepted",
                        "request_generation": expected_generation,
                        "server_pid": source.pid,
                    }
                    if response != expected_response:
                        fail(
                            "payload recheck acceptance was not exact: "
                            f"{json.dumps(response, sort_keys=True)}"
                        )
                    accepted_recheck_generation = expected_generation

                deadline = time.monotonic() + 5.0
                last_status: dict[str, Any] | None = None
                while time.monotonic() < deadline:
                    if source.poll() is not None:
                        stdout, stderr = source.communicate(timeout=1.0)
                        fail(
                            "service exited during a cooperative payload-store "
                            f"lease conflict with {source.returncode}\n"
                            f"stdout:\n{stdout}\nstderr:\n{stderr}"
                        )
                    last_status = run_json(
                        [
                            str(sync), "status", "--socket", str(source_status),
                            "--timeout-milliseconds", "1000",
                        ],
                        label="status during exclusive payload-store lease",
                    )
                    require_payload_operator_status(
                        last_status, "exclusive payload-store lease"
                    )
                    counters = last_status.get("counters")
                    last_step = last_status.get("last_step")
                    recheck = last_status.get("payload_recheck")
                    if (
                        isinstance(counters, dict)
                        and isinstance(recheck, dict)
                        and recheck.get("requested_generation")
                        == accepted_recheck_generation
                        and recheck.get("completed_generation", -1)
                        < accepted_recheck_generation
                        and recheck.get("pending") is True
                        and counters.get("payload_recheck_requests_observed", 0)
                        >= 2
                        and counters.get("payload_recheck_requests_coalesced", 0)
                        >= 1
                        and counters.get("payload_recheck_attempts", 0) >= 1
                        and counters.get(
                            "payload_store_lease_busy_deferrals", -1
                        ) > lease_deferrals_before
                        and isinstance(last_step, dict)
                        and last_step.get("disposition")
                        == "payload_store_lease_busy_deferred"
                        and last_step.get(
                            "payload_store_lease_conflict_observed"
                        )
                        is True
                    ):
                        if last_status.get("pid") != source.pid:
                            fail("lease deferral replaced the service process")
                        if last_status.get("ready") is not True:
                            fail(
                                "cooperative lease contention revoked healthy "
                                "service readiness"
                            )
                        outcome_known = last_step.get("network_outcome_known")
                        if not isinstance(outcome_known, bool):
                            fail("lease deferral omitted network outcome truth")
                        if outcome_known:
                            if last_step.get("role_before") != last_step.get(
                                "role_after"
                            ):
                                fail(
                                    "known local lease deferral changed the "
                                    "network role"
                                )
                        else:
                            role_before = last_step.get("role_before")
                            role_after = last_step.get("role_after")
                            if role_before == "outbound_pull":
                                if role_after != "inbound_serve":
                                    fail(
                                        "unknown outbound outcome did not "
                                        "apply the conservative inbound turn "
                                        "fence: "
                                        f"{json.dumps(last_status, sort_keys=True)}"
                                    )
                            elif role_before == "inbound_serve":
                                if role_after != "inbound_serve":
                                    fail(
                                        "unknown inbound outcome changed the "
                                        "inbound service role: "
                                        f"{json.dumps(last_status, sort_keys=True)}"
                                    )
                            else:
                                fail(
                                    "unknown network outcome reported an "
                                    "invalid role: "
                                    f"{json.dumps(last_status, sort_keys=True)}"
                                )
                        return
                    time.sleep(0.02)
                fail(
                    "service did not expose a bounded payload-store lease "
                    "deferral while the exact exclusive lease was held: "
                    f"{json.dumps(last_status, sort_keys=True)}"
                )

            overwrite_payload_under_exclusive_store_lease(
                source_payload_path,
                corrupted_payload_bytes,
                "payload integrity corruption injection",
                while_lease_held=require_live_lease_deferral,
            )
            faulted_status = wait_for_payload_integrity_state(
                sync,
                source,
                source_status,
                "faulted",
                "config-driven source integrity fault",
            )
            if faulted_status.get("service_state") != "faulted" or (
                faulted_status.get("ready") is not False
            ):
                fail(
                    "payload corruption was not reflected in fail-closed "
                    "service readiness: "
                    f"{json.dumps(faulted_status, sort_keys=True)}"
                )
            faulted_recheck = faulted_status.get("payload_recheck")
            if not isinstance(faulted_recheck, dict) or (
                faulted_recheck.get("requested_generation")
                != accepted_recheck_generation
            ) or faulted_recheck.get("pending") is not True or (
                faulted_recheck.get("completed_generation", -1)
                >= accepted_recheck_generation
            ):
                fail(
                    "detected corruption lost the accepted recheck obligation: "
                    f"{json.dumps(faulted_recheck, sort_keys=True)}"
                )
            if not isinstance(
                faulted_status["payload_scrub"].get("last_report"), dict
            ):
                fail(
                    "payload corruption workflow omitted its prior "
                    "process-observed scrub report"
                )
            active_fault = faulted_status["payload_integrity"].get(
                "active_fault"
            )
            if not isinstance(active_fault, dict):
                fail("faulted source status omitted active payload evidence")
            expected_fault = {
                "expected_content_sha256": source_payload_digest,
                "observed_content_sha256": corrupted_payload_digest,
            }
            for key, wanted in expected_fault.items():
                if active_fault.get(key) != wanted:
                    fail(
                        f"payload fault field {key!r} was "
                        f"{active_fault.get(key)!r}, expected {wanted!r}: "
                        f"{json.dumps(active_fault, sort_keys=True)}"
                    )
            for key in (
                "detection_count",
                "observed_content_change_count",
                "active_age_milliseconds",
                "last_detection_age_milliseconds",
                "retry_delay_milliseconds",
            ):
                if not isinstance(active_fault.get(key), int) or (
                    active_fault[key] < 0
                ):
                    fail(f"payload fault omitted bounded integer field {key}")
            if active_fault["detection_count"] < 1:
                fail("payload fault did not account its first detection")
            fault_counters = faulted_status.get("counters")
            if not isinstance(fault_counters, dict) or (
                fault_counters.get("payload_integrity_faults_observed", 0)
                < 1
            ):
                fail("payload fault status omitted service-owned accounting")
            if fault_counters.get(
                "payload_store_lease_busy_deferrals", -1
            ) <= lease_deferrals_before:
                fail("payload fault status lost cooperative lease accounting")

            # Change the corrupt byte image while the same expected payload is
            # still faulted. A durable witness for the first mismatch must not
            # be falsely attached to this newer exact expected/observed pair.
            second_corrupted_payload_bytes = (
                corrupted_payload_bytes[:1]
                + bytes([source_payload_bytes[1] ^ 0xA5])
                + source_payload_bytes[2:]
            )
            second_corrupted_payload_digest = hashlib.sha256(
                second_corrupted_payload_bytes
            ).hexdigest()
            if second_corrupted_payload_digest == corrupted_payload_digest:
                fail("second corruption injection did not change byte identity")
            overwrite_payload_under_exclusive_store_lease(
                source_payload_path,
                second_corrupted_payload_bytes,
                "payload integrity second corruption injection",
            )
            faulted_status = wait_for_payload_integrity_state(
                sync,
                source,
                source_status,
                "faulted",
                "config-driven source changed integrity fault",
                expected_observed_content_sha256=(
                    second_corrupted_payload_digest
                ),
                minimum_detection_count=2,
                minimum_observed_content_change_count=1,
            )
            active_fault = faulted_status["payload_integrity"].get(
                "active_fault"
            )
            if not isinstance(active_fault, dict):
                fail("changed payload fault omitted active evidence")
            expected_fault = {
                "expected_content_sha256": source_payload_digest,
                "observed_content_sha256": second_corrupted_payload_digest,
            }
            for key, wanted in expected_fault.items():
                if active_fault.get(key) != wanted:
                    fail(
                        f"changed payload fault field {key!r} was "
                        f"{active_fault.get(key)!r}, expected {wanted!r}: "
                        f"{json.dumps(active_fault, sort_keys=True)}"
                    )
            if active_fault.get("failure_persisted") is not False:
                fail(
                    "changed corrupt bytes inherited a durable witness for "
                    "an older observed image"
                )
            if active_fault.get("detection_count", 0) < 2 or (
                active_fault.get("observed_content_change_count", 0) < 1
            ):
                fail(
                    "changed corrupt bytes did not advance exact evidence "
                    "accounting"
                )

            source_payload_before_quarantine = source_payload_path.stat()
            quarantine_response = run_json(
                [
                    str(sync),
                    "quarantine",
                    "--socket",
                    str(source_status),
                    "--expected",
                    source_payload_digest,
                    "--observed",
                    second_corrupted_payload_digest,
                    "--timeout-milliseconds",
                    "1000",
                ],
                label="owner-only exact corrupt payload quarantine",
            )
            expected_quarantine_response = {
                "schema": "anonsync.local-quarantine.response.v1",
                "command": "quarantine",
                "terminal_class": "accepted",
                "request_generation": 1,
                "expected_content_sha256": source_payload_digest,
                "observed_content_sha256": (
                    second_corrupted_payload_digest
                ),
                "server_pid": source.pid,
            }
            if quarantine_response != expected_quarantine_response:
                fail(
                    "payload quarantine acceptance was not exact: "
                    f"{json.dumps(quarantine_response, sort_keys=True)}"
                )
            quarantine_basename = (
                ".anonsync-payload-quarantine-v1-"
                f"{source_payload_digest}-{second_corrupted_payload_digest}"
            )
            quarantine_path = source_payload_path.parent / quarantine_basename

            recovered_status = wait_for_payload_integrity_state(
                sync,
                source,
                source_status,
                "healthy",
                "config-driven source integrity recovery",
            )
            if recovered_status.get("service_state") != "running" or (
                recovered_status.get("ready") is not True
            ):
                fail(
                    "complete current-byte reproof did not restore readiness: "
                    f"{json.dumps(recovered_status, sort_keys=True)}"
                )
            recovered_quarantine = recovered_status.get(
                "payload_quarantine"
            )
            if not isinstance(recovered_quarantine, dict):
                fail("integrity recovery omitted payload quarantine completion")
            expected_quarantine_completion = {
                "requested_generation": 1,
                "started_generation": 1,
                "completed_generation": 1,
                "pending": False,
                "action": "preserve",
                "expected_content_sha256": source_payload_digest,
                "observed_content_sha256": second_corrupted_payload_digest,
            }
            for key, wanted in expected_quarantine_completion.items():
                if recovered_quarantine.get(key) != wanted:
                    fail(
                        f"recovered payload quarantine field {key!r} was "
                        f"{recovered_quarantine.get(key)!r}, expected "
                        f"{wanted!r}: "
                        f"{json.dumps(recovered_quarantine, sort_keys=True)}"
                    )
            quarantine_result = recovered_quarantine.get("last_result")
            require_payload_quarantine_result(
                quarantine_result, "recovered payload quarantine"
            )
            expected_quarantine_result = {
                "action": "preserve",
                "disposition": "quarantined",
                "expected_content_sha256": source_payload_digest,
                "requested_observed_content_sha256": (
                    second_corrupted_payload_digest
                ),
                "current_observed_content_sha256": (
                    second_corrupted_payload_digest
                ),
                "quarantine_basename": quarantine_basename,
                "size_bytes": len(second_corrupted_payload_bytes),
            }
            if quarantine_result != expected_quarantine_result:
                fail(
                    "payload quarantine result was not exact: "
                    f"{json.dumps(quarantine_result, sort_keys=True)}"
                )
            if quarantine_path.read_bytes() != second_corrupted_payload_bytes:
                fail("quarantine did not preserve the exact corrupt byte image")
            quarantine_observation = quarantine_path.stat()
            if (
                quarantine_observation.st_dev
                != source_payload_before_quarantine.st_dev
                or quarantine_observation.st_ino
                != source_payload_before_quarantine.st_ino
                or quarantine_observation.st_nlink != 1
                or stat.S_IMODE(quarantine_observation.st_mode) != 0o600
            ):
                fail(
                    "payload quarantine did not preserve the exact private "
                    "source inode"
                )
            recovered_inventory = recovered_quarantine.get("inventory")
            require_payload_quarantine_inventory(
                recovered_inventory, "recovered payload quarantine"
            )
            expected_recovered_inventory = {
                "observation_known": True,
                "entry_count": 1,
                "total_bytes": len(second_corrupted_payload_bytes),
                "entries": [
                    {
                        "expected_content_sha256": source_payload_digest,
                        "observed_content_sha256": (
                            second_corrupted_payload_digest
                        ),
                        "size_bytes": len(second_corrupted_payload_bytes),
                    }
                ],
            }
            for key, wanted in expected_recovered_inventory.items():
                if recovered_inventory.get(key) != wanted:
                    fail(
                        f"recovered quarantine inventory field {key!r} was "
                        f"{recovered_inventory.get(key)!r}, expected {wanted!r}: "
                        f"{json.dumps(recovered_inventory, sort_keys=True)}"
                    )
            if source_payload_path.read_bytes() != source_payload_bytes:
                fail(
                    "ordinary convergence did not re-admit the expected "
                    "payload after quarantine"
                )
            re_admitted_observation = source_payload_path.stat()
            if (
                re_admitted_observation.st_dev
                == quarantine_observation.st_dev
                and re_admitted_observation.st_ino
                == quarantine_observation.st_ino
            ):
                fail(
                    "re-admitted authoritative payload still aliases the "
                    "quarantined inode"
                )

            recovered_recheck = recovered_status.get("payload_recheck")
            if not isinstance(recovered_recheck, dict):
                fail("integrity recovery omitted payload recheck completion")
            expected_recheck_completion = {
                "requested_generation": accepted_recheck_generation,
                "started_generation": accepted_recheck_generation,
                "completed_generation": accepted_recheck_generation,
                "pending": False,
                "last_snapshot_handoffs": 1,
                "last_convergence_snapshot_observations": 0,
                "last_convergence_mutation_full_scans": 1,
                "last_completion_recovered_integrity_fault": True,
            }
            for key, wanted in expected_recheck_completion.items():
                if recovered_recheck.get(key) != wanted:
                    fail(
                        f"recovered payload recheck field {key!r} was "
                        f"{recovered_recheck.get(key)!r}, expected {wanted!r}: "
                        f"{json.dumps(recovered_recheck, sort_keys=True)}"
                    )
            if recovered_recheck.get("last_hashed_entries", 0) < 1 or (
                recovered_recheck.get("last_hashed_bytes", 0)
                < len(source_payload_bytes)
            ):
                fail(
                    "operator recheck did not report a complete current-byte "
                    f"proof: {json.dumps(recovered_recheck, sort_keys=True)}"
                )
            if faulted_status.get("pid") != source.pid or (
                recovered_status.get("pid") != source.pid
            ):
                fail("payload-integrity recovery replaced the service process")
            recovery_history = recovered_status["payload_integrity"].get(
                "most_recent_recovery"
            )
            if not isinstance(recovery_history, dict):
                fail("integrity recovery erased exact operator evidence")
            for key, wanted in expected_fault.items():
                if recovery_history.get(key) != wanted:
                    fail(
                        f"recovery history field {key!r} was "
                        f"{recovery_history.get(key)!r}, expected {wanted!r}: "
                        f"{json.dumps(recovery_history, sort_keys=True)}"
                    )
            if recovery_history.get("failure_persisted") is not False:
                fail(
                    "recovery history attached stale durable evidence to the "
                    "latest changed corrupt image"
                )
            for key in (
                "detection_count",
                "observed_content_change_count",
                "fault_duration_milliseconds",
                "recovery_age_milliseconds",
            ):
                if not isinstance(recovery_history.get(key), int) or (
                    recovery_history[key] < 0
                ):
                    fail(f"recovery history omitted bounded integer field {key}")
            if recovery_history["detection_count"] < 2:
                fail("recovery history lost repeated detection accounting")
            if recovery_history["observed_content_change_count"] < 1:
                fail("recovery history lost changed-byte-image accounting")

            recovery_counters = recovered_status.get("counters")
            if not isinstance(recovery_counters, dict):
                fail("integrity recovery status omitted counters")
            for field in (
                "payload_integrity_faults_observed",
                "payload_recheck_attempts",
                "payload_recheck_completions",
                "payload_recheck_integrity_recoveries",
            ):
                if recovery_counters.get(field, 0) < 1:
                    fail(f"integrity recovery did not account {field}")
            if recovery_counters.get("payload_recheck_requests_observed", 0) < 2:
                fail("integrity recovery lost accepted recheck accounting")
            if recovery_counters.get("payload_recheck_requests_coalesced", 0) < 1:
                fail("integrity recovery lost recheck coalescing accounting")
            if recovery_counters.get("payload_recheck_snapshot_handoffs", 0) < 1:
                fail("integrity recovery did not account the recheck handoff")
            if recovery_counters.get(
                "payload_recheck_convergence_snapshot_observations",
                -1,
            ) != 0:
                fail(
                    "integrity recovery performed a duplicate complete "
                    "payload-root observation during convergence"
                )
            if recovery_counters.get(
                "payload_recheck_convergence_mutation_full_scans",
                -1,
            ) != 1:
                fail(
                    "quarantine recovery did not expose the one full scan "
                    "required to establish payload mutation authority before "
                    "re-admitting the missing expected object"
                )
            expected_quarantine_counters = {
                "payload_quarantine_requests_observed": 1,
                "payload_quarantine_attempts": 1,
                "payload_quarantine_completions": 1,
                "payload_quarantine_images_preserved": 1,
                "payload_quarantine_images_released": 0,
                "payload_quarantine_observed_content_changes": 0,
            }
            for field, minimum in expected_quarantine_counters.items():
                if recovery_counters.get(field, -1) < minimum:
                    fail(
                        f"integrity recovery did not account {field}: "
                        f"{json.dumps(recovery_counters, sort_keys=True)}"
                    )

            # Exact diagnostic evidence release is deliberately separate from
            # payload restoration. It must not mutate, rename, or rehash the
            # re-admitted authoritative object, and it must not perturb the
            # already completed owner recheck generation.
            re_admitted_before_release = source_payload_path.stat()
            recheck_before_release = dict(recovered_recheck)
            quarantine_release_response = run_json(
                [
                    str(sync),
                    "quarantine-release",
                    "--socket",
                    str(source_status),
                    "--expected",
                    source_payload_digest,
                    "--observed",
                    second_corrupted_payload_digest,
                    "--timeout-milliseconds",
                    "1000",
                ],
                label="owner-only exact quarantine release",
            )
            expected_quarantine_release_response = {
                "schema": "anonsync.local-quarantine-release.response.v1",
                "command": "quarantine-release",
                "terminal_class": "accepted",
                "request_generation": 2,
                "expected_content_sha256": source_payload_digest,
                "observed_content_sha256": second_corrupted_payload_digest,
                "server_pid": source.pid,
            }
            if quarantine_release_response != expected_quarantine_release_response:
                fail(
                    "payload quarantine-release acceptance was not exact: "
                    f"{json.dumps(quarantine_release_response, sort_keys=True)}"
                )
            released_status = wait_for_payload_quarantine_completion(
                sync,
                source,
                source_status,
                2,
                "release",
                "released",
                "config-driven source exact quarantine release",
            )
            if released_status.get("pid") != source.pid or (
                released_status.get("ready") is not True
            ) or released_status["payload_integrity"].get("state") != "healthy":
                fail("quarantine release disturbed service identity or readiness")
            released_quarantine = released_status["payload_quarantine"]
            expected_release_completion = {
                "requested_generation": 2,
                "started_generation": 2,
                "completed_generation": 2,
                "pending": False,
                "action": "release",
                "expected_content_sha256": source_payload_digest,
                "observed_content_sha256": second_corrupted_payload_digest,
            }
            for key, wanted in expected_release_completion.items():
                if released_quarantine.get(key) != wanted:
                    fail(
                        f"released payload quarantine field {key!r} was "
                        f"{released_quarantine.get(key)!r}, expected {wanted!r}: "
                        f"{json.dumps(released_quarantine, sort_keys=True)}"
                    )
            release_result = released_quarantine.get("last_result")
            require_payload_quarantine_result(
                release_result, "released payload quarantine"
            )
            expected_release_result = {
                "action": "release",
                "disposition": "released",
                "expected_content_sha256": source_payload_digest,
                "requested_observed_content_sha256": (
                    second_corrupted_payload_digest
                ),
                "current_observed_content_sha256": (
                    second_corrupted_payload_digest
                ),
                "quarantine_basename": quarantine_basename,
                "size_bytes": len(second_corrupted_payload_bytes),
            }
            if release_result != expected_release_result:
                fail(
                    "payload quarantine-release result was not exact: "
                    f"{json.dumps(release_result, sort_keys=True)}"
                )
            if quarantine_path.exists():
                fail("exact quarantine release left diagnostic bytes retained")
            released_inventory = released_quarantine.get("inventory")
            require_payload_quarantine_inventory(
                released_inventory, "released payload quarantine"
            )
            if (
                released_inventory.get("observation_known") is not True
                or released_inventory.get("entry_count") != 0
                or released_inventory.get("total_bytes") != 0
                or released_inventory.get("entries") != []
            ):
                fail(
                    "exact quarantine release did not publish an exact empty "
                    f"successor inventory: {json.dumps(released_inventory, sort_keys=True)}"
                )
            if source_payload_path.read_bytes() != source_payload_bytes:
                fail("quarantine release changed authoritative payload bytes")
            re_admitted_after_release = source_payload_path.stat()
            if (
                re_admitted_after_release.st_dev
                != re_admitted_before_release.st_dev
                or re_admitted_after_release.st_ino
                != re_admitted_before_release.st_ino
            ):
                fail("quarantine release replaced the authoritative payload inode")
            released_recheck = released_status.get("payload_recheck")
            if not isinstance(released_recheck, dict):
                fail("quarantine release omitted retained recheck state")
            for field in (
                "requested_generation",
                "started_generation",
                "completed_generation",
                "last_hashed_entries",
                "last_hashed_bytes",
                "last_snapshot_handoffs",
                "last_convergence_snapshot_observations",
                "last_convergence_mutation_full_scans",
                "last_completion_recovered_integrity_fault",
            ):
                if released_recheck.get(field) != recheck_before_release.get(field):
                    fail(
                        "quarantine release perturbed completed recheck field "
                        f"{field!r}: before={recheck_before_release.get(field)!r}, "
                        f"after={released_recheck.get(field)!r}"
                    )
            released_counters = released_status.get("counters")
            if not isinstance(released_counters, dict) or (
                released_counters.get("payload_quarantine_images_released", 0) < 1
            ) or released_counters.get("payload_quarantine_images_preserved", 0) < 1:
                fail("quarantine release lost preserve/release accounting")

            # Request the signal-driven peer drain first. Otherwise the
            # locally drained source can close while the receiver starts one
            # final outbound TLS pull, turning a test teardown race into an
            # unrelated unexpected-EOF process failure.
            receiver.send_signal(signal.SIGTERM)
            stop_response = run_json(
                [str(sync), "stop", "--socket", str(source_status)],
                label="owner-only source drain request",
            )
            expected_stop_response = {
                "schema": "anonsync.local-stop.response.v1",
                "command": "stop",
                "terminal_class": "completed",
                "stop_mode": "drain",
                "first_request": True,
                "server_pid": source.pid,
            }
            if stop_response != expected_stop_response:
                fail(
                    "source drain response was not exact: "
                    f"{json.dumps(stop_response, sort_keys=True)}"
                )
            source_terminal = finish_service(
                source, "config-driven source local drain", timeout=15.0
            )
            receiver_terminal = finish_service(
                receiver, "config-driven receiver stop", timeout=15.0
            )
        finally:
            notify_receiver.close()
            try:
                notify_path.unlink()
            except FileNotFoundError:
                pass
            for process in (source, receiver):
                if process.poll() is None:
                    process.kill()
                    process.communicate(timeout=2.0)

        source_notify = source_terminal.get("service_manager_notify")
        if not isinstance(source_notify, dict):
            fail("source terminal omitted service-manager notification state")
        if source_notify.get("configured") is not True or (
            source_notify.get("ready_announced") is not True
        ):
            fail(
                "source terminal did not retain configured READY state: "
                f"{json.dumps(source_notify, sort_keys=True)}"
            )
        if source_notify.get("stopping_announced") is not False or (
            source_notify.get("datagrams_failed", 0) < 1
        ):
            fail(
                "source did not classify post-ready manager loss as diagnostic: "
                f"{json.dumps(source_notify, sort_keys=True)}"
            )
        if source_notify.get("datagrams_sent", 0) < 3:
            fail("source did not send startup and readiness notifications")
        if source_notify.get("datagrams_attempted") != (
            source_notify.get("datagrams_sent", 0)
            + source_notify.get("datagrams_failed", 0)
        ):
            fail("source service-manager datagram accounting is incoherent")

        receiver_notify = receiver_terminal.get("service_manager_notify")
        if not isinstance(receiver_notify, dict) or receiver_notify.get(
            "configured"
        ) is not False or receiver_notify.get("datagrams_attempted") != 0:
            fail(
                "manual service unexpectedly acquired manager notification: "
                f"{json.dumps(receiver_notify, sort_keys=True)}"
            )

        expect_terminal(
            source_terminal,
            local_device="source",
            remote_device="receiver",
            config_path=source_config,
            status_socket=source_status,
            label="config-driven source service",
            stop_reason="local_stop_requested",
            payload_integrity_recovery_expected=True,
        )
        expect_terminal(
            receiver_terminal,
            local_device="receiver",
            remote_device="source",
            config_path=receiver_config,
            status_socket=receiver_status,
            label="config-driven receiver service",
        )
        if source_status.exists() or receiver_status.exists():
            fail("graceful service stop left a status socket behind")
        source_tree = tree_snapshot(source_files)
        receiver_tree = tree_snapshot(receiver_files)
        if (
            source_tree != receiver_tree
            or len(source_tree) != 3
            or "source-side/source-cutpoint-drift.txt" not in source_tree
        ):
            fail(
                "config-driven services did not converge exact trees: "
                f"source={source_tree}, receiver={receiver_tree}"
            )

    print("anonsync linked-peer configuration/status process test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
