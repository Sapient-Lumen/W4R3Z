#!/usr/bin/env python3
"""Validate compact source-snapshot custody rows for public frontier refs.

The manifest is intentionally small.  It records public locators and custody
roles for source refs whose payloads are not vendored into the archive, then
checks that every placement is backed by a typed source-role event and an
explicit no-promotion cap.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from source_role_event_utils import (
    CREDIT_CAP_VALUES,
    RETAINED_SOURCE_REF_DISPOSITIONS,
    SOURCE_REF_DISPOSITIONS,
    SOURCE_ROLE_VALUES,
    iter_source_role_events,
)

sys.dont_write_bytecode = True

MANIFEST_FILE = "SOURCE-SNAPSHOT-MANIFEST.json"
GENERATED_AUDIT = "docs/30-program/source-snapshot-manifest-audit.generated.md"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CHECKSUM_RE = {
    "md5": re.compile(r"^[0-9a-f]{32}$"),
    "sha256": re.compile(r"^[0-9a-f]{64}$"),
}
UPSTREAM_CHECKSUM_STATES = {
    "no-upstream-checksum-recorded",
    "upstream-md5-components-recorded",
    "upstream-md5-manifest-retained",
    "upstream-sha256-manifest-retained",
    "upstream-file-inventory-no-checksum",
    "watchlist-zero-placement-no-payload",
}
LOCAL_PAYLOAD_STATES = {
    "not-retained",
    "not-retained-bulky-external",
    "not-retained-watchlist",
    "retained-small-text-sha256",
    "retained-checksum-manifest-sha256",
    "retained-inventory-control-sha256",
}
RECORD_IDENTITY_MODES = {
    "exact-versioned-record",
    "versioned-record-plus-latest-pointer",
    "single-public-locator",
}
MAX_RETAINED_SMALL_TEXT_BYTES = 64 * 1024
MAX_RETAINED_CHECKSUM_MANIFEST_BYTES = 2 * 1024 * 1024
MAX_RETAINED_INVENTORY_CONTROL_BYTES = 256 * 1024
LOCAL_PAYLOAD_RECORD_TYPES = {
    "source_payload_text",
    "checksum_manifest",
    "inventory_control_json",
}



def load_json(root: Path, rel: str) -> Any:
    return json.loads((root / rel).read_text())


def bibliography_ref_ids(root: Path) -> set[str]:
    text = (root / "docs/00-meta/bibliography.md").read_text()
    return set(re.findall(r"`(REF-\d{4})`", text)) | set(re.findall(r"^(REF-\d{4})", text, flags=re.MULTILINE))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def freshness_snapshot_receipts(root: Path) -> set[tuple[str, str, str]]:
    """Return (freshness_assertion_id, receipt_id, source_ref) receipt triples."""
    path = root / "FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json"
    if not path.exists():
        return set()
    data = load_json(root, "FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json")
    receipts: set[tuple[str, str, str]] = set()
    for assertion in data.get("assertion_rows", []) or []:
        if not isinstance(assertion, dict):
            continue
        aid = str(assertion.get("assertion_id", ""))
        for receipt in assertion.get("source_snapshot_receipts", []) or []:
            if not isinstance(receipt, dict):
                continue
            receipts.add((aid, str(receipt.get("receipt_id", "")), str(receipt.get("source_ref", ""))))
    return receipts


def route_source_ref_count(root: Path, source_ref: str) -> int:
    """Count route-head appearances of a ref in retained refs or source-role events."""
    path = root / "CANDIDATE-ROUTE-STATE-LEDGER.json"
    if not path.exists() or not source_ref:
        return 0
    data = load_json(root, "CANDIDATE-ROUTE-STATE-LEDGER.json")
    count = 0
    for row in data.get("route_rows", []) or []:
        if not isinstance(row, dict):
            continue
        if source_ref in (row.get("source_refs") or []):
            count += 1
        for event in iter_source_role_events(row):
            if source_ref in (event.get("source_refs") or []):
                count += 1
    return count


def _safe_local_payload_path(root: Path, local_path: str) -> Path | None:
    candidate = Path(local_path)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    return root / candidate


def validate_payload_record_identity(row: dict[str, Any], sid: str, failures: list[str]) -> None:
    """Validate exact-version identity for mutable public-record systems."""
    payload_locator = str(row.get("payload_locator", ""))
    identity = row.get("payload_record_identity")
    requires_identity = "zenodo.org/records/" in payload_locator
    if not requires_identity and identity in (None, {}):
        return
    if not isinstance(identity, dict):
        failures.append(f"{sid}: payload_record_identity must be an object for versioned public records")
        return

    mode = str(identity.get("identity_mode", ""))
    if mode not in RECORD_IDENTITY_MODES:
        failures.append(f"{sid}: unknown payload_record_identity.identity_mode `{mode}`")
    captured_locator = str(identity.get("captured_record_locator", ""))
    if requires_identity and captured_locator != payload_locator:
        failures.append(f"{sid}: captured_record_locator must match payload_locator for exact-version custody")
    if "/latest" in captured_locator:
        failures.append(f"{sid}: captured_record_locator must not be a latest-version redirect")
    if not str(identity.get("captured_version", "")).strip():
        failures.append(f"{sid}: payload_record_identity missing captured_version")
    captured_record_id = str(identity.get("captured_record_id", ""))
    match = re.search(r"/records/(\d+)(?:$|[/?#])", captured_locator)
    if match and captured_record_id and captured_record_id != match.group(1):
        failures.append(f"{sid}: captured_record_id `{captured_record_id}` does not match captured_record_locator `{match.group(1)}`")
    elif requires_identity and not captured_record_id:
        failures.append(f"{sid}: payload_record_identity missing captured_record_id")
    captured_doi = str(identity.get("captured_doi", ""))
    if requires_identity and not captured_doi:
        failures.append(f"{sid}: payload_record_identity missing captured_doi")
    if captured_doi:
        if not re.match(r"^10\.5281/zenodo\.\d+$", captured_doi):
            failures.append(f"{sid}: malformed captured_doi `{captured_doi}`")
        elif captured_record_id and not captured_doi.endswith(f".{captured_record_id}"):
            failures.append(f"{sid}: captured_doi `{captured_doi}` does not match captured_record_id `{captured_record_id}`")
    concept_doi = str(identity.get("concept_doi", ""))
    if concept_doi and not re.match(r"^10\.5281/zenodo\.\d+$", concept_doi):
        failures.append(f"{sid}: malformed concept_doi `{concept_doi}`")
    for key in ["captured_record_locator_sha256", "latest_record_locator_sha256", "latest_resolved_record_locator_sha256"]:
        locator_key = key.replace("_sha256", "")
        locator_value = str(identity.get(locator_key, ""))
        hash_value = str(identity.get(key, ""))
        if hash_value and locator_value and hash_value != sha256_text(locator_value):
            failures.append(f"{sid}: payload_record_identity {key} does not match `{locator_key}`")
    if mode == "versioned-record-plus-latest-pointer":
        for key in ["latest_record_locator", "latest_resolved_record_locator", "latest_relation_note"]:
            if not str(identity.get(key, "")).strip():
                failures.append(f"{sid}: versioned-record-plus-latest-pointer missing `{key}`")
        latest_locator = str(identity.get("latest_record_locator", ""))
        if latest_locator and "/latest" not in latest_locator:
            failures.append(f"{sid}: latest_record_locator should be an explicit latest-version pointer")


def validate_inventory_control_json(
    data: bytes,
    record: dict[str, Any],
    row: dict[str, Any],
    sid: str,
    local_path: str,
    failures: list[str],
) -> int:
    """Validate retained compact inventory-control JSON for bulky public products."""
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        failures.append(f"{sid}: inventory_control_json local payload is not UTF-8 text `{local_path}`")
        return 0
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        failures.append(f"{sid}: inventory_control_json local payload is not valid JSON `{local_path}`: {exc}")
        return 0
    if not isinstance(payload, dict):
        failures.append(f"{sid}: inventory_control_json local payload must be a JSON object `{local_path}`")
        return 0
    required = [
        "control_record_type",
        "inventory_id",
        "schema_version",
        "source_ref",
        "captured_at",
        "source_pages",
        "entries",
        "entry_count",
        "entry_category_counts",
        "non_promotion_disposition",
    ]
    for key in required:
        if key not in payload or payload.get(key) in ("", None, []):
            failures.append(f"{sid}: inventory_control_json missing `{key}` in `{local_path}`")
    if payload.get("control_record_type") != "source_inventory_control":
        failures.append(f"{sid}: inventory_control_json control_record_type must be source_inventory_control in `{local_path}`")
    if str(payload.get("source_ref", "")) != str(row.get("source_ref", "")):
        failures.append(f"{sid}: inventory_control_json source_ref drift in `{local_path}`")
    captured_at = str(payload.get("captured_at", ""))
    if captured_at and not DATE_RE.match(captured_at):
        failures.append(f"{sid}: inventory_control_json captured_at must be YYYY-MM-DD in `{local_path}`")
    source_pages = payload.get("source_pages", {})
    if not isinstance(source_pages, dict):
        failures.append(f"{sid}: inventory_control_json source_pages must be an object in `{local_path}`")
        source_pages = {}
    else:
        for page_key, page_locator in source_pages.items():
            if not str(page_key).strip():
                failures.append(f"{sid}: inventory_control_json source_pages has blank key in `{local_path}`")
            if not str(page_locator).startswith(("http://", "https://", "doi:", "NERSC:")):
                failures.append(f"{sid}: inventory_control_json source_pages `{page_key}` is not an external locator in `{local_path}`")
    entries = payload.get("entries", [])
    if not isinstance(entries, list):
        failures.append(f"{sid}: inventory_control_json entries must be a list in `{local_path}`")
        entries = []
    try:
        declared_count = int(payload.get("entry_count", -1))
    except Exception:
        declared_count = -1
    if declared_count != len(entries):
        failures.append(f"{sid}: inventory_control_json entry_count drift in `{local_path}`")
    if "inventory_entry_count" in record and int(record.get("inventory_entry_count", -1)) != len(entries):
        failures.append(f"{sid}: local payload inventory_entry_count drift for `{local_path}`")
    category_counts: Counter[str] = Counter()
    seen_entry_ids: set[str] = set()
    entry_component_names: set[str] = set()
    allowed_retention = {"external-not-vendored", "retained-local-control-only"}
    for entry in entries:
        if not isinstance(entry, dict):
            failures.append(f"{sid}: inventory_control_json entries must contain objects in `{local_path}`")
            continue
        for key in ["entry_id", "category", "component_name", "source_page", "payload_retention", "route_credit_cap"]:
            if not str(entry.get(key, "")).strip():
                failures.append(f"{sid}: inventory_control_json entry missing `{key}` in `{local_path}`")
        entry_id = str(entry.get("entry_id", ""))
        if entry_id in seen_entry_ids:
            failures.append(f"{sid}: duplicate inventory_control_json entry_id `{entry_id}` in `{local_path}`")
        seen_entry_ids.add(entry_id)
        category = str(entry.get("category", ""))
        if category:
            category_counts[category] += 1
        component_name = str(entry.get("component_name", ""))
        if component_name:
            entry_component_names.add(component_name)
        source_page = str(entry.get("source_page", ""))
        if source_page and not (source_page in source_pages or source_page.startswith(("http://", "https://", "doi:", "NERSC:"))):
            failures.append(f"{sid}: inventory_control_json entry source_page `{source_page}` is not a known source_pages key or locator in `{local_path}`")
        retention = str(entry.get("payload_retention", ""))
        if retention and retention not in allowed_retention:
            failures.append(f"{sid}: inventory_control_json entry `{entry_id}` has unknown payload_retention `{retention}` in `{local_path}`")
        cap = str(entry.get("route_credit_cap", ""))
        if cap != str(row.get("maximum_route_credit_cap", "")):
            failures.append(f"{sid}: inventory_control_json entry `{entry_id}` route_credit_cap drift in `{local_path}`")
    declared_categories = payload.get("entry_category_counts")
    if not isinstance(declared_categories, dict):
        failures.append(f"{sid}: inventory_control_json entry_category_counts must be an object in `{local_path}`")
    else:
        normalized = {str(k): int(v) for k, v in declared_categories.items()}
        if normalized != dict(sorted(category_counts.items())):
            failures.append(f"{sid}: inventory_control_json entry_category_counts drift in `{local_path}`")
    record_categories = record.get("inventory_category_counts")
    if record_categories is not None:
        if not isinstance(record_categories, dict):
            failures.append(f"{sid}: local payload inventory_category_counts must be an object for `{local_path}`")
        else:
            normalized_record = {str(k): int(v) for k, v in record_categories.items()}
            if normalized_record != dict(sorted(category_counts.items())):
                failures.append(f"{sid}: local payload inventory_category_counts drift for `{local_path}`")
    for inventory_record in row.get("payload_inventory_records", []) or []:
        if not isinstance(inventory_record, dict):
            continue
        component_name = str(inventory_record.get("component_name", ""))
        if component_name and component_name not in entry_component_names:
            failures.append(f"{sid}: payload_inventory_records component `{component_name}` is absent from retained inventory_control_json `{local_path}`")
    return len(entries)


def validate_local_payload_records(root: Path, row: dict[str, Any], sid: str, failures: list[str], checksum_records: list[dict[str, Any]] | None = None) -> tuple[int, int, int, int, int, int, int]:
    records = row.get("local_payload_records", []) or []
    local_state = str(row.get("local_payload_state", ""))
    if not isinstance(records, list):
        failures.append(f"{sid}: local_payload_records must be a list when present")
        return 0, 0, 0, 0, 0, 0, 0
    if local_state in {"retained-small-text-sha256", "retained-checksum-manifest-sha256", "retained-inventory-control-sha256"} and not records:
        failures.append(f"{sid}: {local_state} requires local_payload_records")
    if local_state.startswith("not-retained") and records:
        failures.append(f"{sid}: not-retained local_payload_state must not carry local_payload_records")
    component_checksums: dict[str, list[dict[str, Any]]] = {}
    for checksum_record in checksum_records or []:
        if isinstance(checksum_record, dict):
            component_checksums.setdefault(str(checksum_record.get("component_name", "")), []).append(checksum_record)
    record_count = 0
    byte_total = 0
    seen_paths: set[str] = set()
    checksum_manifest_count = 0
    checksum_manifest_entry_total = 0
    checksum_manifest_malformed_total = 0
    inventory_control_count = 0
    inventory_control_entry_total = 0
    for record in records:
        if not isinstance(record, dict):
            failures.append(f"{sid}: local_payload_records entries must be objects")
            continue
        record_count += 1
        for key in ["local_path", "sha256", "source_component_name", "source_locator", "custody_note"]:
            if not str(record.get(key, "")).strip():
                failures.append(f"{sid}: local payload record missing `{key}`")
        record_type = str(record.get("record_type", "source_payload_text"))
        if record_type not in LOCAL_PAYLOAD_RECORD_TYPES:
            failures.append(f"{sid}: unknown local payload record_type `{record_type}`")
        local_path = str(record.get("local_path", ""))
        if local_path in seen_paths:
            failures.append(f"{sid}: duplicate local payload path `{local_path}`")
        seen_paths.add(local_path)
        if not local_path.startswith("payload-snapshots/"):
            failures.append(f"{sid}: local payload path must live under payload-snapshots/: `{local_path}`")
        payload_path = _safe_local_payload_path(root, local_path)
        if payload_path is None:
            failures.append(f"{sid}: unsafe local payload path `{local_path}`")
            continue
        if not payload_path.exists() or not payload_path.is_file():
            failures.append(f"{sid}: local payload file missing `{local_path}`")
            continue
        data = payload_path.read_bytes()
        byte_total += len(data)
        declared = str(record.get("sha256", ""))
        if declared and not CHECKSUM_RE["sha256"].match(declared):
            failures.append(f"{sid}: malformed local payload sha256 `{declared}`")
        actual = hashlib.sha256(data).hexdigest()
        if declared and declared != actual:
            failures.append(f"{sid}: local payload sha256 drift for `{local_path}`")
        for component_checksum in component_checksums.get(str(record.get("source_component_name", "")), []):
            algorithm = str(component_checksum.get("checksum_algorithm", ""))
            expected_checksum = str(component_checksum.get("checksum", ""))
            if algorithm not in CHECKSUM_RE or not expected_checksum:
                continue
            h = hashlib.new(algorithm)
            h.update(data)
            if h.hexdigest() != expected_checksum:
                failures.append(f"{sid}: local payload `{local_path}` does not match upstream {algorithm} component checksum for `{record.get('source_component_name', '')}`")
        if record_type == "checksum_manifest":
            byte_cap = MAX_RETAINED_CHECKSUM_MANIFEST_BYTES
        elif record_type == "inventory_control_json":
            byte_cap = MAX_RETAINED_INVENTORY_CONTROL_BYTES
        else:
            byte_cap = MAX_RETAINED_SMALL_TEXT_BYTES
        if len(data) > byte_cap:
            failures.append(f"{sid}: retained local payload exceeds {record_type} cap `{local_path}` ({len(data)} bytes)")
        if "byte_size" in record and int(record.get("byte_size", -1)) != len(data):
            failures.append(f"{sid}: local payload byte_size drift for `{local_path}`")
        if "line_count" in record:
            actual_lines = len(data.decode("utf-8").splitlines())
            if int(record.get("line_count", -1)) != actual_lines:
                failures.append(f"{sid}: local payload line_count drift for `{local_path}`")
        if record_type == "inventory_control_json":
            inventory_control_count += 1
            if local_state != "retained-inventory-control-sha256":
                failures.append(f"{sid}: inventory_control_json local payload requires retained-inventory-control-sha256 local_payload_state")
            inventory_control_entry_total += validate_inventory_control_json(data, record, row, sid, local_path, failures)
        if record_type == "checksum_manifest":
            checksum_manifest_count += 1
            algorithm = str(record.get("checksum_algorithm", ""))
            pattern = CHECKSUM_RE.get(algorithm)
            if pattern is None:
                failures.append(f"{sid}: checksum_manifest local payload has unknown checksum_algorithm `{algorithm}`")
                pattern = CHECKSUM_RE["sha256"]
            root_counts: Counter[str] = Counter()
            entry_count = 0
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                failures.append(f"{sid}: checksum_manifest local payload is not UTF-8 text `{local_path}`")
                text = ""
            known_malformed = record.get("checksum_manifest_known_malformed_lines", []) or []
            if not isinstance(known_malformed, list):
                failures.append(f"{sid}: checksum_manifest_known_malformed_lines must be a list for `{local_path}`")
                known_malformed = []
            known_by_line: dict[int, dict[str, Any]] = {}
            for item in known_malformed:
                if not isinstance(item, dict):
                    failures.append(f"{sid}: checksum_manifest_known_malformed_lines entries must be objects for `{local_path}`")
                    continue
                try:
                    line_number = int(item.get("line_number", -1))
                except Exception:
                    line_number = -1
                if line_number <= 0:
                    failures.append(f"{sid}: known malformed checksum line has invalid line_number in `{local_path}`")
                    continue
                if line_number in known_by_line:
                    failures.append(f"{sid}: duplicate known malformed checksum line {line_number} in `{local_path}`")
                known_by_line[line_number] = item
                declared_line_hash = str(item.get("content_sha256", ""))
                if declared_line_hash and not CHECKSUM_RE["sha256"].match(declared_line_hash):
                    failures.append(f"{sid}: known malformed checksum line {line_number} has malformed content_sha256 in `{local_path}`")
                if not str(item.get("reason", "")).strip():
                    failures.append(f"{sid}: known malformed checksum line {line_number} missing reason in `{local_path}`")
            encountered_malformed: set[int] = set()
            malformed_count = 0
            extension_counts: Counter[str] = Counter()
            for line_no, line in enumerate(text.splitlines(), 1):
                if not line.strip():
                    continue
                parts = line.split(maxsplit=1)
                if len(parts) != 2 or not pattern.match(parts[0]):
                    malformed_count += 1
                    declared = known_by_line.get(line_no)
                    if declared is None:
                        failures.append(f"{sid}: malformed checksum manifest line {line_no} in `{local_path}`")
                    else:
                        encountered_malformed.add(line_no)
                        actual_line_hash = hashlib.sha256(line.encode("utf-8")).hexdigest()
                        declared_line_hash = str(declared.get("content_sha256", ""))
                        if declared_line_hash != actual_line_hash:
                            failures.append(f"{sid}: known malformed checksum line {line_no} content drift in `{local_path}`")
                    continue
                component_path = Path(parts[1])
                if component_path.is_absolute() or ".." in component_path.parts:
                    failures.append(f"{sid}: unsafe checksum manifest component path on line {line_no} in `{local_path}`")
                    continue
                root_counts[component_path.parts[0] if component_path.parts else "<empty>"] += 1
                extension_counts[component_path.suffix or "<none>"] += 1
                entry_count += 1
            missing_known = sorted(set(known_by_line) - encountered_malformed)
            if missing_known:
                failures.append(f"{sid}: declared known malformed checksum lines not encountered in `{local_path}`: {missing_known}")
            if "checksum_manifest_known_malformed_line_count" in record and int(record.get("checksum_manifest_known_malformed_line_count", -1)) != malformed_count:
                failures.append(f"{sid}: checksum_manifest_known_malformed_line_count drift for `{local_path}`")
            checksum_manifest_malformed_total += malformed_count
            checksum_manifest_entry_total += entry_count
            if "checksum_manifest_entry_count" in record and int(record.get("checksum_manifest_entry_count", -1)) != entry_count:
                failures.append(f"{sid}: checksum_manifest_entry_count drift for `{local_path}`")
            declared_roots = record.get("checksum_manifest_path_roots")
            if declared_roots is not None:
                if not isinstance(declared_roots, dict):
                    failures.append(f"{sid}: checksum_manifest_path_roots must be an object for `{local_path}`")
                else:
                    normalized = {str(k): int(v) for k, v in declared_roots.items()}
                    if normalized != dict(sorted(root_counts.items())):
                        failures.append(f"{sid}: checksum_manifest_path_roots drift for `{local_path}`")
            declared_extensions = record.get("checksum_manifest_extension_counts")
            if declared_extensions is not None:
                if not isinstance(declared_extensions, dict):
                    failures.append(f"{sid}: checksum_manifest_extension_counts must be an object for `{local_path}`")
                else:
                    normalized_extensions = {str(k): int(v) for k, v in declared_extensions.items()}
                    if normalized_extensions != dict(sorted(extension_counts.items())):
                        failures.append(f"{sid}: checksum_manifest_extension_counts drift for `{local_path}`")
    if local_state == "retained-checksum-manifest-sha256" and checksum_manifest_count == 0:
        failures.append(f"{sid}: retained-checksum-manifest-sha256 requires a checksum_manifest local payload record")
    if local_state == "retained-inventory-control-sha256" and inventory_control_count == 0:
        failures.append(f"{sid}: retained-inventory-control-sha256 requires an inventory_control_json local payload record")
    if inventory_control_count and local_state != "retained-inventory-control-sha256":
        failures.append(f"{sid}: inventory_control_json local payload records require retained-inventory-control-sha256 local_payload_state")
    return record_count, byte_total, checksum_manifest_count, checksum_manifest_entry_total, checksum_manifest_malformed_total, inventory_control_count, inventory_control_entry_total


def validate_payload_custody(root: Path, row: dict[str, Any], sid: str, failures: list[str]) -> tuple[int, int, int, int, int, int, int]:
    checksum_state = str(row.get("upstream_checksum_state", ""))
    local_state = str(row.get("local_payload_state", ""))
    if checksum_state and checksum_state not in UPSTREAM_CHECKSUM_STATES:
        failures.append(f"{sid}: unknown upstream_checksum_state `{checksum_state}`")
    if local_state and local_state not in LOCAL_PAYLOAD_STATES:
        failures.append(f"{sid}: unknown local_payload_state `{local_state}`")
    retained_manifest_states = {"upstream-sha256-manifest-retained", "upstream-md5-manifest-retained"}
    if checksum_state in retained_manifest_states and local_state != "retained-checksum-manifest-sha256":
        failures.append(f"{sid}: {checksum_state} requires retained-checksum-manifest-sha256 local_payload_state")
    if local_state == "retained-checksum-manifest-sha256" and checksum_state not in retained_manifest_states:
        failures.append(f"{sid}: retained-checksum-manifest-sha256 requires a retained upstream checksum-manifest state")
    if local_state == "retained-inventory-control-sha256" and checksum_state != "upstream-file-inventory-no-checksum":
        failures.append(f"{sid}: retained-inventory-control-sha256 requires upstream-file-inventory-no-checksum")
    if checksum_state == "upstream-file-inventory-no-checksum" and local_state == "not-retained":
        failures.append(f"{sid}: upstream-file-inventory-no-checksum should declare a retained inventory control or explicit non-retained external inventory state")
    payload_locator = row.get("payload_locator")
    if payload_locator not in (None, "") and not str(payload_locator).startswith(("http://", "https://", "doi:", "NERSC:", "ESA:")):
        failures.append(f"{sid}: payload_locator should be an external locator or explicit non-URL custody token")

    validate_payload_record_identity(row, sid, failures)

    checksum_records = row.get("payload_component_checksums", []) or []
    if not isinstance(checksum_records, list):
        failures.append(f"{sid}: payload_component_checksums must be a list when present")
        checksum_records = []
    for record in checksum_records:
        if not isinstance(record, dict):
            failures.append(f"{sid}: payload_component_checksums entries must be objects")
            continue
        for key in ["component_name", "checksum_algorithm", "checksum"]:
            if key not in record or not str(record.get(key, "")).strip():
                failures.append(f"{sid}: payload checksum record missing `{key}`")
        algorithm = str(record.get("checksum_algorithm", ""))
        checksum = str(record.get("checksum", ""))
        pattern = CHECKSUM_RE.get(algorithm)
        if pattern is None:
            failures.append(f"{sid}: unknown checksum algorithm `{algorithm}`")
        elif checksum and not pattern.match(checksum):
            failures.append(f"{sid}: malformed {algorithm} checksum `{checksum}`")
        source_locator = str(record.get("source_locator", record.get("record_locator", "")))
        record_id = str(record.get("record_id", ""))
        locator_match = re.search(r"zenodo\.org/records/(\d+)", source_locator)
        if locator_match and record_id and record_id != locator_match.group(1):
            failures.append(f"{sid}: payload checksum record_id `{record_id}` does not match source_locator `{locator_match.group(1)}`")
        doi = str(record.get("doi", ""))
        if doi:
            if not re.match(r"^10\.5281/zenodo\.\d+$", doi):
                failures.append(f"{sid}: malformed payload checksum DOI `{doi}`")
            elif record_id and not doi.endswith(f".{record_id}"):
                failures.append(f"{sid}: payload checksum DOI `{doi}` does not match record_id `{record_id}`")
    if checksum_state == "upstream-md5-components-recorded" and not checksum_records:
        failures.append(f"{sid}: upstream-md5-components-recorded requires payload_component_checksums")

    inventory_records = row.get("payload_inventory_records", []) or []
    if not isinstance(inventory_records, list):
        failures.append(f"{sid}: payload_inventory_records must be a list when present")
        inventory_records = []
    for record in inventory_records:
        if not isinstance(record, dict):
            failures.append(f"{sid}: payload_inventory_records entries must be objects")
            continue
        if not str(record.get("component_name", "")).strip():
            failures.append(f"{sid}: payload inventory record missing `component_name`")
        algorithm = str(record.get("checksum_algorithm", ""))
        checksum = str(record.get("checksum", ""))
        if bool(algorithm) != bool(checksum):
            failures.append(f"{sid}: payload inventory checksum must include both algorithm and checksum for `{record.get('component_name', '')}`")
        if algorithm or checksum:
            pattern = CHECKSUM_RE.get(algorithm)
            if pattern is None:
                failures.append(f"{sid}: unknown payload inventory checksum algorithm `{algorithm}`")
            elif not pattern.match(checksum):
                failures.append(f"{sid}: malformed payload inventory {algorithm} checksum `{checksum}`")
        source_locator = str(record.get("record_locator", record.get("source_locator", "")))
        record_id = str(record.get("record_id", ""))
        locator_match = re.search(r"zenodo\.org/records/(\d+)", source_locator)
        if locator_match and record_id and record_id != locator_match.group(1):
            failures.append(f"{sid}: payload inventory record_id `{record_id}` does not match locator `{locator_match.group(1)}`")
        doi = str(record.get("doi", ""))
        if doi:
            if not re.match(r"^10\.5281/zenodo\.\d+$", doi):
                failures.append(f"{sid}: malformed payload inventory DOI `{doi}`")
            elif record_id and not doi.endswith(f".{record_id}"):
                failures.append(f"{sid}: payload inventory DOI `{doi}` does not match record_id `{record_id}`")
    if checksum_state == "upstream-file-inventory-no-checksum" and not inventory_records:
        failures.append(f"{sid}: upstream-file-inventory-no-checksum requires payload_inventory_records")

    return validate_local_payload_records(root, row, sid, failures, checksum_records)


def find_row(root: Path, placement: dict[str, Any], failures: list[str], *, snapshot_id: str) -> dict[str, Any] | None:
    ledger_file = str(placement.get("ledger_file", ""))
    collection = str(placement.get("row_collection", ""))
    id_field = str(placement.get("id_field", ""))
    row_id = str(placement.get("row_id", ""))
    if not all([ledger_file, collection, id_field, row_id]):
        failures.append(f"{snapshot_id}: placement is missing ledger_file/row_collection/id_field/row_id")
        return None
    path = root / ledger_file
    if not path.exists():
        failures.append(f"{snapshot_id}: placement ledger does not exist: {ledger_file}")
        return None
    data = load_json(root, ledger_file)
    rows = data.get(collection)
    if not isinstance(rows, list):
        failures.append(f"{snapshot_id}: placement collection missing or not a list: {ledger_file}:{collection}")
        return None
    row = next((item for item in rows if isinstance(item, dict) and item.get(id_field) == row_id), None)
    if row is None:
        failures.append(f"{snapshot_id}: placement row not found: {ledger_file}:{row_id}")
    return row


def placement_event_covers(row: dict[str, Any], source_ref: str, source_role: str, disposition: str, cap: str) -> bool:
    for event in iter_source_role_events(row):
        if event.get("source_role") != source_role:
            continue
        if event.get("source_ref_disposition") != disposition:
            continue
        if event.get("credit_cap") != cap:
            continue
        if source_ref in (event.get("source_refs") or []):
            return True
    return False


def evaluate_source_snapshot_manifest(root: Path) -> dict[str, Any]:
    failures: list[str] = []
    path = root / MANIFEST_FILE
    if not path.exists():
        return {
            "manifest_file": MANIFEST_FILE,
            "revision": "<missing>",
            "snapshot_rows": [],
            "row_count": 0,
            "placement_count": 0,
            "zero_placement_count": 0,
            "role_counts": {},
            "cap_counts": {},
            "disposition_counts": {},
            "checksum_state_counts": {},
            "local_payload_state_counts": {},
                "local_payload_record_count": 0,
                "local_payload_byte_total": 0,
                "checksum_manifest_record_count": 0,
                "checksum_manifest_entry_total": 0,
                "checksum_manifest_malformed_total": 0,
                "payload_component_checksum_count": 0,
                "inventory_checksum_count": 0,
                "inventory_control_record_count": 0,
                "inventory_control_entry_total": 0,
            "failures": [f"missing source snapshot manifest: {MANIFEST_FILE}"],
        }

    data = load_json(root, MANIFEST_FILE)
    release = load_json(root, "RELEASE-MANIFEST.json")
    known_refs = bibliography_ref_ids(root)

    if data.get("revision") != release.get("revision"):
        failures.append("SOURCE-SNAPSHOT-MANIFEST revision drifted from RELEASE-MANIFEST")

    rows = data.get("snapshot_rows", [])
    if not isinstance(rows, list):
        failures.append("SOURCE-SNAPSHOT-MANIFEST snapshot_rows must be a list")
        rows = []

    required = [
        "snapshot_id",
        "source_ref",
        "retrieved_at",
        "locator",
        "locator_sha256",
        "payload_hash_status",
        "payload_custody_state",
        "upstream_checksum_state",
        "local_payload_state",
        "source_role",
        "maximum_route_credit_cap",
        "source_custody_role",
        "license_or_terms",
        "row_placements",
        "non_promotion_disposition",
    ]
    seen_snapshots: set[str] = set()
    seen_refs: set[str] = set()
    role_counts: Counter[str] = Counter()
    cap_counts: Counter[str] = Counter()
    disposition_counts: Counter[str] = Counter()
    placement_count = 0
    zero_placement_count = 0
    placement_refs: Counter[str] = Counter()
    checksum_state_counts: Counter[str] = Counter()
    local_payload_state_counts: Counter[str] = Counter()
    known_snapshot_receipts = freshness_snapshot_receipts(root)
    local_payload_record_count = 0
    local_payload_byte_total = 0
    checksum_manifest_record_count = 0
    checksum_manifest_entry_total = 0
    checksum_manifest_malformed_total = 0
    payload_component_checksum_count = 0
    inventory_checksum_count = 0
    inventory_control_record_count = 0
    inventory_control_entry_total = 0

    for row in rows:
        if not isinstance(row, dict):
            failures.append("SOURCE-SNAPSHOT-MANIFEST snapshot row must be an object")
            continue
        sid = str(row.get("snapshot_id", "<missing-snapshot-id>"))
        source_ref = str(row.get("source_ref", ""))
        for key in required:
            missing = key not in row or row.get(key) in ("", None)
            if key != "row_placements" and row.get(key) == []:
                missing = True
            if missing:
                failures.append(f"{sid}: missing required field `{key}`")
        if sid in seen_snapshots:
            failures.append(f"duplicate snapshot_id `{sid}`")
        seen_snapshots.add(sid)
        if source_ref in seen_refs:
            failures.append(f"duplicate source_ref snapshot `{source_ref}`")
        if source_ref:
            seen_refs.add(source_ref)
        if source_ref and source_ref not in known_refs:
            failures.append(f"{sid}: source_ref `{source_ref}` is absent from bibliography")

        retrieved_at = str(row.get("retrieved_at", ""))
        if retrieved_at and not DATE_RE.match(retrieved_at):
            failures.append(f"{sid}: retrieved_at must be YYYY-MM-DD")
        locator = str(row.get("locator", ""))
        locator_hash = str(row.get("locator_sha256", ""))
        if locator and locator_hash and locator_hash != sha256_text(locator):
            failures.append(f"{sid}: locator_sha256 does not match the locator string")
        payload_hash_status = str(row.get("payload_hash_status", ""))
        if "locator-only" in payload_hash_status and row.get("payload_sha256") not in (None, ""):
            failures.append(f"{sid}: locator-only payload_hash_status must not carry payload_sha256")
        local_count, local_bytes, checksum_manifest_count, checksum_manifest_entries, checksum_manifest_malformed, inventory_control_count, inventory_control_entries = validate_payload_custody(root, row, sid, failures)
        local_payload_record_count += local_count
        local_payload_byte_total += local_bytes
        checksum_manifest_record_count += checksum_manifest_count
        checksum_manifest_entry_total += checksum_manifest_entries
        checksum_manifest_malformed_total += checksum_manifest_malformed
        inventory_control_record_count += inventory_control_count
        inventory_control_entry_total += inventory_control_entries
        payload_component_checksum_count += sum(
            1
            for record in (row.get("payload_component_checksums", []) or [])
            if isinstance(record, dict) and record.get("checksum_algorithm") and record.get("checksum")
        )
        inventory_checksum_count += sum(
            1
            for record in (row.get("payload_inventory_records", []) or [])
            if isinstance(record, dict) and record.get("checksum_algorithm") and record.get("checksum")
        )
        checksum_state_counts[str(row.get("upstream_checksum_state", ""))] += 1
        local_payload_state_counts[str(row.get("local_payload_state", ""))] += 1

        source_role = str(row.get("source_role", ""))
        cap = str(row.get("maximum_route_credit_cap", ""))
        if source_role not in SOURCE_ROLE_VALUES:
            failures.append(f"{sid}: unknown source_role `{source_role}`")
        if cap not in CREDIT_CAP_VALUES:
            failures.append(f"{sid}: unknown maximum_route_credit_cap `{cap}`")
        if source_role in {"denominator_pressure", "forecast_runway", "operational_status", "metadata_wrapper"} and cap != "S0":
            failures.append(f"{sid}: source-custody snapshot role `{source_role}` must be S0-capped")
        role_counts[source_role] += 1
        cap_counts[cap] += 1

        placements = row.get("row_placements", [])
        if not isinstance(placements, list):
            failures.append(f"{sid}: row_placements must be a list")
            placements = []
        if not placements:
            zero_receipt = row.get("zero_route_placement_receipt")
            if not isinstance(zero_receipt, dict):
                failures.append(f"{sid}: row_placements must be non-empty unless zero_route_placement_receipt is present")
                continue
            receipt_tuple = (
                str(zero_receipt.get("freshness_assertion_id", "")),
                str(zero_receipt.get("receipt_id", "")),
                source_ref,
            )
            if receipt_tuple not in known_snapshot_receipts:
                failures.append(f"{sid}: zero_route_placement_receipt is not backed by a frontier source snapshot receipt")
            if int(zero_receipt.get("allowed_route_placements", -1)) != 0:
                failures.append(f"{sid}: zero_route_placement_receipt.allowed_route_placements must be 0")
            route_count = route_source_ref_count(root, source_ref)
            if route_count != 0:
                failures.append(f"{sid}: zero-placement source ref `{source_ref}` appears on route rows/events {route_count} time(s)")
            zero_placement_count += 1
            continue
        for placement in placements:
            placement_count += 1
            if not isinstance(placement, dict):
                failures.append(f"{sid}: placement must be an object")
                continue
            disposition = str(placement.get("source_ref_disposition", ""))
            placement_cap = str(placement.get("credit_cap", cap))
            placement_role = str(placement.get("source_role", source_role))
            disposition_counts[disposition] += 1
            placement_refs[source_ref] += 1
            if disposition not in SOURCE_REF_DISPOSITIONS:
                failures.append(f"{sid}: placement has unknown source_ref_disposition `{disposition}`")
            if placement_role not in SOURCE_ROLE_VALUES:
                failures.append(f"{sid}: placement has unknown source_role `{placement_role}`")
            if placement_cap not in CREDIT_CAP_VALUES:
                failures.append(f"{sid}: placement has unknown credit_cap `{placement_cap}`")
            row_obj = find_row(root, placement, failures, snapshot_id=sid)
            if row_obj is None:
                continue
            row_refs = set(row_obj.get("source_refs", []) or [])
            if disposition in RETAINED_SOURCE_REF_DISPOSITIONS and source_ref not in row_refs:
                failures.append(f"{sid}: retained placement {placement.get('ledger_file')}:{placement.get('row_id')} lacks `{source_ref}` in source_refs")
            if disposition == "route_local_handoff_only" and source_ref in row_refs:
                failures.append(f"{sid}: route-local handoff placement should not also retain `{source_ref}` in row source_refs")
            if placement.get("requires_source_role_event", True):
                if not placement_event_covers(row_obj, source_ref, placement_role, disposition, placement_cap):
                    failures.append(
                        f"{sid}: placement {placement.get('ledger_file')}:{placement.get('row_id')} lacks matching source_role_event for `{source_ref}` / `{placement_role}` / `{disposition}` / `{placement_cap}`"
                    )

    return {
        "manifest_file": MANIFEST_FILE,
        "revision": data.get("revision", "<missing>"),
        "schema_version": data.get("schema_version", "<missing>"),
        "row_count": len(rows),
        "placement_count": placement_count,
        "zero_placement_count": zero_placement_count,
        "role_counts": dict(sorted(role_counts.items())),
        "cap_counts": dict(sorted(cap_counts.items())),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "checksum_state_counts": dict(sorted(checksum_state_counts.items())),
        "local_payload_state_counts": dict(sorted(local_payload_state_counts.items())),
        "local_payload_record_count": local_payload_record_count,
        "local_payload_byte_total": local_payload_byte_total,
        "checksum_manifest_record_count": checksum_manifest_record_count,
        "checksum_manifest_entry_total": checksum_manifest_entry_total,
        "checksum_manifest_malformed_total": checksum_manifest_malformed_total,
        "payload_component_checksum_count": payload_component_checksum_count,
        "inventory_checksum_count": inventory_checksum_count,
        "inventory_control_record_count": inventory_control_record_count,
        "inventory_control_entry_total": inventory_control_entry_total,
        "placement_refs": dict(sorted(placement_refs.items())),
        "snapshot_rows": rows,
        "failures": failures,
    }


def write_source_snapshot_manifest_audit(root: Path) -> None:
    result = evaluate_source_snapshot_manifest(root)
    lines = [
        "# Source snapshot manifest audit (generated)",
        "",
        f"Generated from `{MANIFEST_FILE}` plus the bibliography and source-carrying ledgers. Do not edit directly; run `make index` after changing source snapshot rows or source-role placements.",
        "",
        f"- Snapshot manifest revision: `{result.get('revision', '<missing>')}`",
        f"- Snapshot manifest rows: `{result.get('row_count', 0)}`",
        f"- Snapshot row placements: `{result.get('placement_count', 0)}`",
        f"- Zero-placement snapshot receipts: `{result.get('zero_placement_count', 0)}`",
        f"- Local retained payload files: `{result.get('local_payload_record_count', 0)}`",
        f"- Local retained payload bytes: `{result.get('local_payload_byte_total', 0)}`",
        f"- Local checksum-manifest files: `{result.get('checksum_manifest_record_count', 0)}`",
        f"- Local checksum-manifest entries: `{result.get('checksum_manifest_entry_total', 0)}`",
        f"- Known malformed checksum-manifest lines: `{result.get('checksum_manifest_malformed_total', 0)}`",
        f"- Payload component checksum records: `{result.get('payload_component_checksum_count', 0)}`",
        f"- Payload inventory checksum records: `{result.get('inventory_checksum_count', 0)}`",
        f"- Local inventory-control files: `{result.get('inventory_control_record_count', 0)}`",
        f"- Local inventory-control entries: `{result.get('inventory_control_entry_total', 0)}`",
        f"- Snapshot failures: `{len(result.get('failures', []))}`",
        "",
        "## Snapshot role counts",
        "",
    ]
    for role, count in result.get("role_counts", {}).items():
        lines.append(f"- `{role}`: `{count}`")
    lines += ["", "## Credit-cap counts", ""]
    for cap, count in result.get("cap_counts", {}).items():
        lines.append(f"- `{cap}`: `{count}`")
    lines += ["", "## Placement disposition counts", ""]
    for disposition, count in result.get("disposition_counts", {}).items():
        lines.append(f"- `{disposition}`: `{count}`")
    lines += ["", "## Upstream checksum states", ""]
    for state, count in result.get("checksum_state_counts", {}).items():
        lines.append(f"- `{state}`: `{count}`")
    lines += ["", "## Local payload states", ""]
    for state, count in result.get("local_payload_state_counts", {}).items():
        lines.append(f"- `{state}`: `{count}`")
    lines += [
        "",
        "## Snapshot rows",
        "",
        "| Source ref | Snapshot id | Role | Max cap | Placements | Payload hash status | Checksum state | Local payload | Local files |",
        "|---|---|---|---|---:|---|---|---|---:|",
    ]
    for row in result.get("snapshot_rows", []):
        if not isinstance(row, dict):
            continue
        source_ref = str(row.get("source_ref", ""))
        lines.append(
            f"| `{source_ref}` | `{row.get('snapshot_id', '')}` | `{row.get('source_role', '')}` | `{row.get('maximum_route_credit_cap', '')}` | `{result.get('placement_refs', {}).get(source_ref, 0)}` | {str(row.get('payload_hash_status', '')).replace('|', '/')} | {str(row.get('upstream_checksum_state', '')).replace('|', '/')} | {str(row.get('local_payload_state', '')).replace('|', '/')} | `{len(row.get('local_payload_records', []) or [])}` |"
        )
    lines += ["", "## Failures", ""]
    if result.get("failures"):
        lines.extend(f"- {failure}" for failure in result["failures"])
    else:
        lines.append("None.")
    lines += [
        "",
        "## Non-promotion rule",
        "",
        "Source-snapshot rows are custody pointers and replay hooks. A locator/hash record cannot promote a route, upgrade evidence-unit credit, or substitute for a named acquired public data product; every source-custody role in this manifest is capped by the row's declared maximum route-credit cap.",
        "",
    ]
    (root / GENERATED_AUDIT).write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    write_source_snapshot_manifest_audit(root)
    outcome = evaluate_source_snapshot_manifest(root)
    if outcome["failures"]:
        print("SOURCE SNAPSHOT MANIFEST FAILED")
        for failure in outcome["failures"]:
            print(f"- {failure}")
        raise SystemExit(1)
    print("SOURCE SNAPSHOT MANIFEST OK")
