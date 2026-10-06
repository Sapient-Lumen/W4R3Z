import base64
import gzip
import hashlib
import json
import pathlib
import shutil
import tempfile
from collections import OrderedDict
from typing import Any, Callable

REQUIRED_FILES = ["REVISION-RECEIPT.json", "RECEIPT-COLDSTORE.json"]
SURFACE = "RECEIPT-COLDSTORE.json"
ENCODING = "gzip+base64+canonical-json"
MIN_COLD_KEYS = 100
MIN_NET_SAVED_BYTES = 40_000

# These are live-current receipt controls or compatibility aliases.  They may be
# small, stale, or annoying, but they must not be hidden in the receipt coldstore
# because future operators need to know when a current-looking field exists.
FORBIDDEN_COLD_KEYS = {
    "project",
    "revision",
    "previous_revision",
    "summary",
    "move_classes",
    "canon_additions",
    "hot_current_supports",
    "canonical_additions",
    "artifacts_touched",
    "changed_surfaces",
    "quarantine_additions",
    "refs_used",
    "checks_passed",
    "touched_surfaces",
    "packaged_release",
    "packaged_bundle_filename",
    "stamp",
    "slug",
    "bundle",
    "created_at",
    "summary_highlight",
    "codename",
    "resolved_question",
    "next_open_question",
    "current_import_id",
    "current_pressure_id",
    "current_resolution_id",
    "current_assumption_id",
    "current_followthrough_id",
    "current_obligation_id",
    "current_applicability_id",
    "current_retrospective_id",
    "current_firebreak_id",
    "current_self_sufficiency_id",
    "current_transfer_id",
    "current_receipt_witness",
    "receipt_coldstore_ref",
}

LIVE_WITNESS_KEYS = {
    "basis_witness",
    "scope_witness",
    "authorship_witness",
    "status_witness",
    "reentry_cue_witness",
    "retrospective_write_witness",
    "followthrough_witness",
    "assumption_witness",
    "obligation_witness",
    "applicability_witness",
    "foreign_pressure_witness",
    "transfer_witness",
    "resolution_witness",
    "reasoning_firebreak_witness",
    "vocabulary_witness",
    "counterfactual_shadow",
    "receipt_freshness_witness",
    "question_posture_witness",
    "latest_revision_cue_witness",
    "currentness_cue_witness",
    "package_identity_witness",
    "lint_idempotence_witness",
    "schema_conformance_witness",
    "schema_coverage_witness",
    "basis_provenance_witness",
    "self_sufficiency_witness",
    "self_sufficiency_tail_witness",
    "release_hardening_witness",
    "canary_evidence_witness",
    "path_alias_witness",
    "alias_retention_witness",
    "archive_economy_witness",
    "current_witness_slot",
}

ALLOWED_HISTORICAL_KEY_PATTERNS = ("_witness", "_witness_contract", "_meta")


class ReceiptColdstoreError(ValueError):
    pass


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def pretty_json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def ordered_pretty_json_bytes(value: dict[str, Any], key_order: list[str]) -> bytes:
    ordered: OrderedDict[str, Any] = OrderedDict()
    for key in key_order:
        if key in value:
            ordered[key] = value[key]
    for key in value:
        if key not in ordered:
            ordered[key] = value[key]
    return pretty_json_bytes(ordered)


def load_json(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def _fail(message: str) -> None:
    raise ReceiptColdstoreError(message)


def _decode_payload(chunk: dict[str, Any]) -> dict[str, Any]:
    encoded = chunk.get("payload")
    if not isinstance(encoded, str) or not encoded:
        _fail("receipt cold payload missing")
    try:
        raw = gzip.decompress(base64.b64decode(encoded))
    except Exception as exc:
        _fail(f"receipt cold payload decode failed: {exc}")
    if hashlib.sha256(raw).hexdigest() != chunk.get("payload_sha256"):
        _fail("receipt cold payload hash mismatch")
    if len(raw) != chunk.get("payload_byte_count"):
        _fail("receipt cold payload byte count mismatch")
    payload = json.loads(raw)
    if not isinstance(payload, dict):
        _fail("receipt cold payload must decode to an object")
    return payload


def _is_allowed_historical_key(key: str) -> bool:
    return (
        key not in FORBIDDEN_COLD_KEYS
        and key not in LIVE_WITNESS_KEYS
        and key.startswith("current_") is False
        and any(token in key for token in ALLOWED_HISTORICAL_KEY_PATTERNS)
    )


def decode_receipt_coldstore(root: pathlib.Path) -> tuple[dict[str, Any], dict[str, Any]]:
    cold = load_json(root, SURFACE)
    chunk = cold.get("cold_payload")
    if not isinstance(chunk, dict):
        _fail("RECEIPT-COLDSTORE cold_payload must be an object")
    return cold, _decode_payload(chunk)


def restored_receipt(root: pathlib.Path) -> dict[str, Any]:
    receipt = load_json(root, "REVISION-RECEIPT.json")
    _cold, payload = decode_receipt_coldstore(root)
    keys = payload.get("keys")
    if not isinstance(keys, dict):
        _fail("receipt cold payload keys must be an object")
    restored = dict(receipt)
    for key, value in keys.items():
        if key in restored:
            _fail(f"cold receipt key still present in hot receipt: {key}")
        restored[key] = value
    return restored


def recompute_receipt_coldstore_stats(root: pathlib.Path) -> dict[str, Any]:
    cold, payload = decode_receipt_coldstore(root)
    restored = restored_receipt(root)
    order = payload.get("receipt_key_order")
    if not isinstance(order, list):
        order = list(restored)
    hot_after = (root / "REVISION-RECEIPT.json").stat().st_size
    hot_before = len(ordered_pretty_json_bytes(restored, [str(item) for item in order]))
    cold_bytes = (root / SURFACE).stat().st_size
    return {
        "hot_receipt_before_bytes": hot_before,
        "hot_receipt_after_bytes": hot_after,
        "coldstore_bytes": cold_bytes,
        "net_plaintext_bytes_after_coldstore": hot_after + cold_bytes,
        "net_plaintext_saved_bytes": hot_before - (hot_after + cold_bytes),
        "cold_key_count": len(payload.get("keys", {}) if isinstance(payload.get("keys"), dict) else {}),
    }


def validate_receipt_coldstore(root: pathlib.Path) -> dict[str, Any]:
    root = pathlib.Path(root)
    for rel in REQUIRED_FILES:
        if not (root / rel).exists():
            _fail(f"missing {rel}")
    receipt = load_json(root, "REVISION-RECEIPT.json")
    cold = load_json(root, SURFACE)
    revision = receipt.get("revision")

    if cold.get("project") != "DelayBasin":
        _fail("RECEIPT-COLDSTORE project must be DelayBasin")
    if cold.get("revision") != revision:
        _fail("RECEIPT-COLDSTORE revision must match REVISION-RECEIPT")
    if cold.get("encoding") != ENCODING:
        _fail("RECEIPT-COLDSTORE encoding drifted")
    non_claim = cold.get("non_claim", "")
    for token in ["not deletion authority", "not a receipt replacement", "not a witness court"]:
        if token not in non_claim:
            _fail(f"RECEIPT-COLDSTORE non_claim missing {token}")

    ref = receipt.get("receipt_coldstore_ref")
    if not isinstance(ref, dict):
        _fail("hot receipt missing receipt_coldstore_ref")
    expected_ref = {
        "surface": SURFACE,
        "contract": "tools/check_receipt_coldstore_roundtrip_contract.py",
        "mutation_checker": "tools/check_receipt_coldstore_mutation_canaries.py",
    }
    for key, expected in expected_ref.items():
        if ref.get(key) != expected:
            _fail(f"receipt_coldstore_ref.{key} drifted")

    chunk = cold.get("cold_payload")
    if not isinstance(chunk, dict):
        _fail("RECEIPT-COLDSTORE cold_payload must be an object")
    payload = _decode_payload(chunk)
    if payload.get("source_receipt") != "REVISION-RECEIPT.json":
        _fail("receipt cold payload source_receipt mismatch")
    if payload.get("revision") != revision:
        _fail("receipt cold payload revision mismatch")
    keys = payload.get("keys")
    if not isinstance(keys, dict) or not keys:
        _fail("receipt cold payload keys must be non-empty object")
    if len(keys) < MIN_COLD_KEYS:
        _fail(f"receipt coldstore covers too few keys: {len(keys)}")
    if cold.get("cold_key_count") != len(keys) or ref.get("cold_key_count") != len(keys):
        _fail("receipt cold key count mismatch")

    order = payload.get("receipt_key_order")
    if not isinstance(order, list) or not all(isinstance(key, str) for key in order):
        _fail("receipt cold payload receipt_key_order must be a string list")
    if len(order) != len(set(order)):
        _fail("receipt_key_order has duplicate keys")
    if set(order) != set(receipt) | set(keys):
        _fail("receipt_key_order must cover hot and cold receipt keys exactly")

    key_hashes = chunk.get("key_hashes")
    key_byte_counts = chunk.get("key_byte_counts")
    if set(keys) != set(key_hashes or {}) or set(keys) != set(key_byte_counts or {}):
        _fail("receipt coldstore key hash/byte-count coverage mismatch")
    for key, value in keys.items():
        if key in receipt:
            _fail(f"cold receipt key still present in hot receipt: {key}")
        if not _is_allowed_historical_key(key):
            _fail(f"disallowed current or non-historical receipt key in coldstore: {key}")
        canonical = canonical_bytes(value)
        if hashlib.sha256(canonical).hexdigest() != key_hashes[key]:
            _fail(f"receipt cold key hash mismatch: {key}")
        if len(canonical) != key_byte_counts[key]:
            _fail(f"receipt cold key byte count mismatch: {key}")

    restored = dict(receipt)
    restored.update(keys)
    restored_bytes = ordered_pretty_json_bytes(restored, order)
    if hashlib.sha256(canonical_bytes(restored)).hexdigest() != cold.get("restored_receipt_canonical_sha256"):
        _fail("restored receipt canonical hash mismatch")
    if hashlib.sha256(restored_bytes).hexdigest() != cold.get("restored_receipt_pretty_sha256"):
        _fail("restored receipt pretty hash mismatch")
    if len(restored_bytes) != cold.get("hot_receipt_before_bytes"):
        _fail("restored receipt pretty byte count mismatch")

    if cold.get("hot_receipt_after_bytes") != (root / "REVISION-RECEIPT.json").stat().st_size:
        _fail("hot receipt after byte count mismatch")
    if cold.get("coldstore_bytes") != (root / SURFACE).stat().st_size:
        _fail("receipt coldstore byte count mismatch")
    if cold.get("net_plaintext_bytes_after_coldstore") != cold.get("hot_receipt_after_bytes") + cold.get("coldstore_bytes"):
        _fail("receipt coldstore net plaintext arithmetic mismatch")
    if cold.get("net_plaintext_saved_bytes") != cold.get("hot_receipt_before_bytes") - cold.get("net_plaintext_bytes_after_coldstore"):
        _fail("receipt coldstore savings arithmetic mismatch")
    if int(cold.get("net_plaintext_saved_bytes", 0) or 0) < MIN_NET_SAVED_BYTES:
        _fail("receipt coldstore net savings below budget")
    if cold.get("compaction_revision") != "rev0358":
        _fail("receipt coldstore compaction_revision must be rev0358")
    if cold.get("last_validated_revision") != revision:
        _fail("receipt coldstore last_validated_revision must match current revision")

    return {
        "cold_key_count": len(keys),
        "hot_receipt_before_bytes": cold.get("hot_receipt_before_bytes"),
        "hot_receipt_after_bytes": cold.get("hot_receipt_after_bytes"),
        "coldstore_bytes": cold.get("coldstore_bytes"),
        "net_plaintext_saved_bytes": cold.get("net_plaintext_saved_bytes"),
        "current_revision": revision,
    }


def _copy_required_tree(source: pathlib.Path, destination: pathlib.Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for rel in REQUIRED_FILES:
        shutil.copy2(source / rel, destination / rel)


def _write_json(path: pathlib.Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_coldstore_with_stable_size(root: pathlib.Path, payload: dict[str, Any]) -> None:
    path = root / SURFACE
    for _ in range(8):
        _write_json(path, payload)
        size = path.stat().st_size
        if payload.get("coldstore_bytes") == size:
            return
        payload["coldstore_bytes"] = size
        payload["net_plaintext_bytes_after_coldstore"] = int(payload.get("hot_receipt_after_bytes", 0) or 0) + size
        payload["net_plaintext_saved_bytes"] = int(payload.get("hot_receipt_before_bytes", 0) or 0) - int(payload.get("net_plaintext_bytes_after_coldstore", 0) or 0)
    _write_json(path, payload)


def _mutate_coldstore(root: pathlib.Path, mutator: Callable[[dict[str, Any]], None]) -> None:
    path = root / SURFACE
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    write_coldstore_with_stable_size(root, payload)


def _rewrite_chunk(cold: dict[str, Any], payload: dict[str, Any]) -> None:
    raw = canonical_bytes(payload)
    chunk = cold["cold_payload"]
    chunk["payload"] = base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")
    chunk["payload_sha256"] = hashlib.sha256(raw).hexdigest()
    chunk["payload_byte_count"] = len(raw)
    keys = payload["keys"]
    chunk["key_hashes"] = {key: hashlib.sha256(canonical_bytes(value)).hexdigest() for key, value in keys.items()}
    chunk["key_byte_counts"] = {key: len(canonical_bytes(value)) for key, value in keys.items()}
    cold["cold_key_count"] = len(keys)


def _first_cold_key(cold: dict[str, Any]) -> str:
    return next(iter(cold["cold_payload"]["key_hashes"]))


def _mutate_payload_hash(cold: dict[str, Any]) -> None:
    chunk = cold["cold_payload"]
    raw = gzip.decompress(base64.b64decode(chunk["payload"])) + b"\n"
    chunk["payload"] = base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")
    chunk["payload_byte_count"] = len(raw)
    # Leave payload_sha256 stale on purpose.


def _mutate_key_hash(cold: dict[str, Any]) -> None:
    cold["cold_payload"]["key_hashes"][_first_cold_key(cold)] = "0" * 64


def _mutate_payload_key_omission(cold: dict[str, Any]) -> None:
    payload = _decode_payload(cold["cold_payload"])
    first = next(iter(payload["keys"]))
    payload["keys"].pop(first)
    _rewrite_chunk(cold, payload)
    # Leave the stored count stale so coverage/count validation fails.
    cold["cold_key_count"] += 1


def _mutate_hot_overlap(root: pathlib.Path) -> None:
    cold = load_json(root, SURFACE)
    key = _first_cold_key(cold)
    payload = _decode_payload(cold["cold_payload"])
    receipt = load_json(root, "REVISION-RECEIPT.json")
    receipt[key] = payload["keys"][key]
    _write_json(root / "REVISION-RECEIPT.json", receipt)


def _mutate_disallowed_current_key(root: pathlib.Path) -> None:
    cold = load_json(root, SURFACE)
    payload = _decode_payload(cold["cold_payload"])
    receipt = load_json(root, "REVISION-RECEIPT.json")
    payload["keys"]["current_import_id"] = receipt.get("current_import_id")
    if "current_import_id" not in payload["receipt_key_order"]:
        payload["receipt_key_order"].append("current_import_id")
    # Remove from hot receipt so the validator reaches the current-key rejection.
    receipt.pop("current_import_id", None)
    ref = receipt.get("receipt_coldstore_ref")
    if isinstance(ref, dict):
        ref["cold_key_count"] = len(payload["keys"])
    _write_json(root / "REVISION-RECEIPT.json", receipt)
    _rewrite_chunk(cold, payload)
    write_coldstore_with_stable_size(root, cold)


def _mutate_savings(cold: dict[str, Any]) -> None:
    cold["net_plaintext_saved_bytes"] = int(cold["net_plaintext_saved_bytes"]) + 1


def receipt_coldstore_canary_results(root: pathlib.Path) -> list[dict[str, Any]]:
    root = pathlib.Path(root)
    results: list[dict[str, Any]] = []

    def add(row_id: str, expected: object, observed: object, ok: bool) -> None:
        results.append({"id": row_id, "expected": expected, "observed": observed, "status": "pass" if ok else "fail"})

    with tempfile.TemporaryDirectory(prefix="delaybasin-receipt-coldstore-canaries-") as tmp:
        base = pathlib.Path(tmp)
        pristine = base / "pristine"
        _copy_required_tree(root, pristine)
        try:
            observed = validate_receipt_coldstore(pristine)
        except ReceiptColdstoreError as exc:
            add("receipt-coldstore-valid-baseline", "valid receipt coldstore tree is accepted", str(exc), False)
        else:
            add("receipt-coldstore-valid-baseline", "valid receipt coldstore tree is accepted", observed, observed.get("cold_key_count", 0) >= MIN_COLD_KEYS)

        scenarios: list[dict[str, Any]] = [
            {"id": "receipt-coldstore-payload-hash-mutation", "expected_failure_contains": "payload hash mismatch", "mutate": lambda case: _mutate_coldstore(case, _mutate_payload_hash)},
            {"id": "receipt-coldstore-key-hash-mutation", "expected_failure_contains": "cold key hash mismatch", "mutate": lambda case: _mutate_coldstore(case, _mutate_key_hash)},
            {"id": "receipt-coldstore-payload-key-omission", "expected_failure_contains": "cold key count mismatch", "mutate": lambda case: _mutate_coldstore(case, _mutate_payload_key_omission)},
            {"id": "receipt-coldstore-hot-overlap", "expected_failure_contains": "still present in hot receipt", "mutate": _mutate_hot_overlap},
            {"id": "receipt-coldstore-current-key-compaction", "expected_failure_contains": "disallowed current or non-historical receipt key", "mutate": _mutate_disallowed_current_key},
            {"id": "receipt-coldstore-savings-arithmetic-mutation", "expected_failure_contains": "savings arithmetic mismatch", "mutate": lambda case: _mutate_coldstore(case, _mutate_savings)},
        ]
        for index, scenario in enumerate(scenarios, start=1):
            case = base / f"case-{index}"
            _copy_required_tree(pristine, case)
            scenario["mutate"](case)
            try:
                validate_receipt_coldstore(case)
            except ReceiptColdstoreError as exc:
                message = str(exc)
                token = scenario["expected_failure_contains"]
                add(scenario["id"], {"failure_contains": token}, message, token in message)
            else:
                add(scenario["id"], {"failure_contains": scenario["expected_failure_contains"]}, None, False)
    return results
