import base64
import gzip
import hashlib
import json
import pathlib
import shutil
import tempfile
from typing import Any, Callable

GOVERNED_LEDGERS = [
    "DATACUBE-TRANSFER-LEDGER.json",
    "FOREIGN-PRESSURE-LEDGER.json",
    "APPLICABILITY-LEDGER.json",
    "RESOLUTION-LEDGER.json",
    "FIREBREAK-LEDGER.json",
    "ASSUMPTION-LEDGER.json",
    "OBLIGATION-LEDGER.json",
    "FOLLOWTHROUGH-QUEUE.json",
    "RETROSPECTIVE-QUEUE.json",
]

REQUIRED_FILES = ["REVISION-RECEIPT.json", "LEDGER-COLDSTORE.json", *GOVERNED_LEDGERS]


class LedgerColdstoreError(ValueError):
    pass


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def pretty_json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def load_json(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def _fail(message: str) -> None:
    raise LedgerColdstoreError(message)


def _revision_number(revision: str) -> int:
    if not isinstance(revision, str) or not revision.startswith("rev"):
        return -1
    try:
        return int(revision[3:])
    except ValueError:
        return -1


def restored_ledger_payload(root: pathlib.Path, ledger: str, cold_payload_rows: dict[str, dict[str, Any]] | None = None) -> dict[str, Any]:
    """Return the hot ledger with compacted rows restored from cold payload rows."""
    data = load_json(root, ledger)
    rows = cold_payload_rows or cold_payload_rows_by_ledger(root).get(ledger, {})
    restored_items = []
    for item in data.get("items", []):
        item_id = item.get("id")
        restored_items.append(rows.get(item_id, item))
    restored = dict(data)
    restored["items"] = restored_items
    return restored


def cold_payload_rows_by_ledger(root: pathlib.Path) -> dict[str, dict[str, dict[str, Any]]]:
    cold = load_json(root, "LEDGER-COLDSTORE.json")
    rows_by_ledger: dict[str, dict[str, dict[str, Any]]] = {}
    for chunk in cold.get("cold_payloads", []) or []:
        ledger = chunk.get("ledger")
        if not isinstance(ledger, str):
            continue
        try:
            raw = gzip.decompress(base64.b64decode(chunk.get("payload", "")))
            payload = json.loads(raw)
        except Exception:
            continue
        rows = payload.get("rows")
        if isinstance(rows, dict):
            rows_by_ledger[ledger] = rows
    return rows_by_ledger


def recompute_coldstore_stats(root: pathlib.Path) -> dict[str, Any]:
    rows_by_ledger = cold_payload_rows_by_ledger(root)
    stats = []
    hot_after = 0
    hot_before = 0
    for ledger in GOVERNED_LEDGERS:
        after = (root / ledger).stat().st_size
        restored = restored_ledger_payload(root, ledger, rows_by_ledger.get(ledger, {}))
        before = len(pretty_json_bytes(restored))
        hot_after += after
        hot_before += before
        stats.append({
            "ledger": ledger,
            "compacted_rows": len(rows_by_ledger.get(ledger, {})),
            "before_bytes": before,
            "after_bytes": after,
            "saved_bytes": before - after,
        })
    coldstore_bytes = (root / "LEDGER-COLDSTORE.json").stat().st_size
    return {
        "stats": stats,
        "hot_ledger_before_bytes": hot_before,
        "hot_ledger_after_bytes": hot_after,
        "coldstore_bytes": coldstore_bytes,
        "net_plaintext_bytes_after_coldstore": hot_after + coldstore_bytes,
        "net_plaintext_saved_bytes": hot_before - (hot_after + coldstore_bytes),
    }


def validate_ledger_coldstore(root: pathlib.Path) -> dict[str, Any]:
    root = pathlib.Path(root)
    coldstore_path = root / "LEDGER-COLDSTORE.json"
    receipt_path = root / "REVISION-RECEIPT.json"
    if not coldstore_path.exists():
        _fail("missing LEDGER-COLDSTORE.json")
    if not receipt_path.exists():
        _fail("missing REVISION-RECEIPT.json")

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    revision = receipt.get("revision")
    cold = json.loads(coldstore_path.read_text(encoding="utf-8"))

    if cold.get("project") != "DelayBasin":
        _fail("LEDGER-COLDSTORE project must be DelayBasin")
    if cold.get("revision") != revision:
        _fail("LEDGER-COLDSTORE revision must match REVISION-RECEIPT")
    if cold.get("encoding") != "gzip+base64+canonical-json":
        _fail("LEDGER-COLDSTORE encoding drifted")
    if "not deletion authority" not in cold.get("non_claim", ""):
        _fail("LEDGER-COLDSTORE must reject deletion authority")
    if cold.get("coldstore_bytes") != coldstore_path.stat().st_size:
        _fail("LEDGER-COLDSTORE coldstore_bytes must equal actual file size")

    chunks = cold.get("cold_payloads")
    if not isinstance(chunks, list) or not chunks:
        _fail("LEDGER-COLDSTORE cold_payloads must be a non-empty list")

    compaction_revision = cold.get("compaction_revision") or cold.get("created_revision") or "rev0356"
    if not isinstance(compaction_revision, str) or _revision_number(compaction_revision) < 0:
        _fail("LEDGER-COLDSTORE compaction_revision must be a revision token")
    if _revision_number(compaction_revision) > _revision_number(str(revision)):
        _fail("LEDGER-COLDSTORE compaction_revision cannot be after current revision")

    ledger_items: dict[str, dict[str, dict[str, Any]]] = {}
    compacted_hot_refs: set[tuple[str, str]] = set()
    tail_keep = cold.get("hot_tail_policy", {}).get("tail_rows_kept_full_per_ledger")
    if not isinstance(tail_keep, int) or tail_keep < 20:
        _fail("LEDGER-COLDSTORE tail policy must keep at least 20 rows hot")

    for ledger in GOVERNED_LEDGERS:
        data = load_json(root, ledger)
        if data.get("revision") != revision:
            _fail(f"{ledger} revision must match current revision")
        items = data.get("items")
        if not isinstance(items, list) or not items:
            _fail(f"{ledger} items must be a non-empty list")
        by_id: dict[str, dict[str, Any]] = {}
        for item in items:
            item_id = item.get("id")
            if not isinstance(item_id, str) or not item_id:
                _fail(f"{ledger} item missing id")
            if item_id in by_id:
                _fail(f"{ledger} duplicate id: {item_id}")
            by_id[item_id] = item
            if item.get("cold_compacted"):
                compacted_hot_refs.add((ledger, item_id))
                expected_ref = f"LEDGER-COLDSTORE.json#{ledger}:{item_id}"
                if item.get("cold_payload_ref") != expected_ref:
                    _fail(f"{ledger}#{item_id} cold_payload_ref mismatch")
                if item.get("cold_compacted_at") != compaction_revision:
                    _fail(f"{ledger}#{item_id} cold_compacted_at must match compaction_revision {compaction_revision}")
                if item.get("origin_revision") == revision or item.get("revision") == revision:
                    _fail(f"current revision row must not be cold-compacted: {ledger}#{item_id}")
        for item in items[-tail_keep:]:
            if item.get("cold_compacted"):
                _fail(f"{ledger} hot tail row was cold-compacted: {item.get('id')}")
        ledger_items[ledger] = by_id

    payload_refs: set[tuple[str, str]] = set()
    rows_by_ledger: dict[str, dict[str, dict[str, Any]]] = {}
    for chunk in chunks:
        ledger = chunk.get("ledger")
        if ledger not in GOVERNED_LEDGERS:
            _fail(f"unknown coldstore ledger: {ledger}")
        encoded = chunk.get("payload")
        if not isinstance(encoded, str) or not encoded:
            _fail(f"{ledger} cold payload missing")
        try:
            raw = gzip.decompress(base64.b64decode(encoded))
        except Exception as exc:
            _fail(f"{ledger} cold payload decode failed: {exc}")
        if hashlib.sha256(raw).hexdigest() != chunk.get("payload_sha256"):
            _fail(f"{ledger} cold payload hash mismatch")
        if len(raw) != chunk.get("payload_byte_count"):
            _fail(f"{ledger} cold payload byte count mismatch")
        payload = json.loads(raw)
        if payload.get("ledger") != ledger:
            _fail(f"{ledger} payload ledger mismatch")
        rows = payload.get("rows")
        if not isinstance(rows, dict) or len(rows) != chunk.get("row_count"):
            _fail(f"{ledger} row_count mismatch")
        rows_by_ledger[ledger] = rows
        row_hashes = chunk.get("row_hashes")
        row_byte_counts = chunk.get("row_byte_counts")
        if set(rows) != set(row_hashes or {}) or set(rows) != set(row_byte_counts or {}):
            _fail(f"{ledger} row hash/byte-count coverage mismatch")
        for item_id, original in rows.items():
            payload_refs.add((ledger, item_id))
            if original.get("id") != item_id:
                _fail(f"{ledger} cold row id mismatch: {item_id}")
            canonical = canonical_bytes(original)
            if hashlib.sha256(canonical).hexdigest() != row_hashes[item_id]:
                _fail(f"{ledger}#{item_id} original row hash mismatch")
            if len(canonical) != row_byte_counts[item_id]:
                _fail(f"{ledger}#{item_id} original row byte count mismatch")
            hot = ledger_items[ledger].get(item_id)
            if hot is None:
                _fail(f"{ledger}#{item_id} missing compacted hot row")
            if not hot.get("cold_compacted"):
                _fail(f"{ledger}#{item_id} cold payload points to non-compacted hot row")
            for key in ("state", "origin_revision", "revision", "witness_surface"):
                if key in original and hot.get(key) != original.get(key):
                    _fail(f"{ledger}#{item_id} routing key drifted after compaction: {key}")

    if payload_refs != compacted_hot_refs:
        missing = sorted(compacted_hot_refs - payload_refs)[:5]
        extra = sorted(payload_refs - compacted_hot_refs)[:5]
        _fail(f"LEDGER-COLDSTORE/hot compacted row mismatch; missing={missing} extra={extra}")
    if cold.get("cold_row_count") != len(payload_refs):
        _fail("LEDGER-COLDSTORE cold_row_count mismatch")
    if len(payload_refs) < 1000:
        _fail("LEDGER-COLDSTORE should cover at least 1000 historical rows")

    stats = cold.get("stats")
    if not isinstance(stats, list) or {row.get("ledger") for row in stats} != set(GOVERNED_LEDGERS):
        _fail("LEDGER-COLDSTORE stats must cover governed ledgers exactly")
    for row in stats:
        ledger = row["ledger"]
        if row.get("after_bytes") != (root / ledger).stat().st_size:
            _fail(f"{ledger} after_bytes stat mismatch")
        if row.get("saved_bytes") != row.get("before_bytes") - row.get("after_bytes"):
            _fail(f"{ledger} saved_bytes arithmetic mismatch")

    hot_after = sum((root / ledger).stat().st_size for ledger in GOVERNED_LEDGERS)
    if cold.get("hot_ledger_after_bytes") != hot_after:
        _fail("LEDGER-COLDSTORE hot_ledger_after_bytes mismatch")
    if cold.get("hot_ledger_before_bytes") != sum(int(row.get("before_bytes", 0) or 0) for row in stats):
        _fail("LEDGER-COLDSTORE hot_ledger_before_bytes mismatch")
    if cold.get("net_plaintext_bytes_after_coldstore") != hot_after + coldstore_path.stat().st_size:
        _fail("LEDGER-COLDSTORE net plaintext arithmetic mismatch")
    if cold.get("net_plaintext_saved_bytes") != cold.get("hot_ledger_before_bytes") - cold.get("net_plaintext_bytes_after_coldstore"):
        _fail("LEDGER-COLDSTORE net plaintext savings arithmetic mismatch")
    if cold.get("net_plaintext_saved_bytes", 0) < 400_000:
        _fail("LEDGER-COLDSTORE net plaintext savings below budget")

    return {
        "cold_row_count": len(payload_refs),
        "governed_ledger_count": len(GOVERNED_LEDGERS),
        "hot_ledger_after_bytes": hot_after,
        "net_plaintext_saved_bytes": cold.get("net_plaintext_saved_bytes"),
        "compaction_revision": compaction_revision,
        "current_revision": revision,
    }


def _copy_required_tree(source: pathlib.Path, destination: pathlib.Path) -> None:
    destination.mkdir(parents=True, exist_ok=True)
    for rel in REQUIRED_FILES:
        shutil.copy2(source / rel, destination / rel)


def _write_json(path: pathlib.Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_coldstore_with_stable_size(root: pathlib.Path, payload: dict[str, Any]) -> None:
    """Write LEDGER-COLDSTORE.json while stabilizing its self-recorded byte count."""
    path = root / "LEDGER-COLDSTORE.json"
    for _ in range(6):
        _write_json(path, payload)
        size = path.stat().st_size
        if payload.get("coldstore_bytes") == size:
            return
        payload["coldstore_bytes"] = size
    _write_json(path, payload)


def _mutate_coldstore(root: pathlib.Path, mutator: Callable[[dict[str, Any]], None]) -> None:
    path = root / "LEDGER-COLDSTORE.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    write_coldstore_with_stable_size(root, payload)


def _mutate_ledger(root: pathlib.Path, ledger: str, mutator: Callable[[dict[str, Any]], None]) -> None:
    path = root / ledger
    payload = json.loads(path.read_text(encoding="utf-8"))
    mutator(payload)
    _write_json(path, payload)


def _first_chunk_and_id(cold: dict[str, Any]) -> tuple[dict[str, Any], str]:
    chunk = cold["cold_payloads"][0]
    first_id = next(iter(chunk["row_hashes"]))
    return chunk, first_id


def _first_compacted_hot_ref(root: pathlib.Path) -> tuple[str, str]:
    for ledger in GOVERNED_LEDGERS:
        data = load_json(root, ledger)
        for item in data.get("items", []):
            if item.get("cold_compacted"):
                return ledger, item["id"]
    raise AssertionError("no compacted hot refs found")


def _mutate_payload_hash(cold: dict[str, Any]) -> None:
    chunk, _ = _first_chunk_and_id(cold)
    raw = gzip.decompress(base64.b64decode(chunk["payload"])) + b"\n"
    chunk["payload"] = base64.b64encode(gzip.compress(raw, mtime=0)).decode("ascii")
    # Keep payload_sha256 stale on purpose.
    chunk["payload_byte_count"] = len(raw)


def _mutate_row_hash(cold: dict[str, Any]) -> None:
    chunk, first_id = _first_chunk_and_id(cold)
    chunk["row_hashes"][first_id] = "0" * 64


def _mutate_payload_row_omission(cold: dict[str, Any]) -> None:
    chunk, first_id = _first_chunk_and_id(cold)
    raw = gzip.decompress(base64.b64decode(chunk["payload"]))
    payload = json.loads(raw)
    payload["rows"].pop(first_id)
    new_raw = canonical_bytes(payload)
    chunk["payload"] = base64.b64encode(gzip.compress(new_raw, mtime=0)).decode("ascii")
    chunk["payload_sha256"] = hashlib.sha256(new_raw).hexdigest()
    chunk["payload_byte_count"] = len(new_raw)
    chunk["row_count"] = len(payload["rows"])
    # Leave row_hashes and row_byte_counts stale so coverage mismatch is exercised.


def _mutate_hot_ref(root: pathlib.Path) -> None:
    ledger, item_id = _first_compacted_hot_ref(root)
    def mutate(data: dict[str, Any]) -> None:
        for item in data["items"]:
            if item.get("id") == item_id:
                item["cold_payload_ref"] = "LEDGER-COLDSTORE.json#wrong-ledger:wrong-id"
                return
    _mutate_ledger(root, ledger, mutate)


def _mutate_current_tail_compaction(root: pathlib.Path) -> None:
    ledger = GOVERNED_LEDGERS[0]
    def mutate(data: dict[str, Any]) -> None:
        item = data["items"][-1]
        item["cold_compacted"] = True
        item["cold_compacted_at"] = load_json(root, "LEDGER-COLDSTORE.json").get("compaction_revision", "rev0356")
        item["cold_payload_ref"] = f"LEDGER-COLDSTORE.json#{ledger}:{item['id']}"
    _mutate_ledger(root, ledger, mutate)


def _mutate_stats(cold: dict[str, Any]) -> None:
    cold["stats"][0]["saved_bytes"] = int(cold["stats"][0]["saved_bytes"]) + 1


def ledger_coldstore_canary_results(root: pathlib.Path) -> list[dict[str, Any]]:
    """Run cheap local mutation canaries for the ledger coldstore contract."""
    root = pathlib.Path(root)
    results: list[dict[str, Any]] = []

    def add(row_id: str, expected: object, observed: object, ok: bool) -> None:
        results.append({
            "id": row_id,
            "expected": expected,
            "observed": observed,
            "status": "pass" if ok else "fail",
        })

    with tempfile.TemporaryDirectory(prefix="delaybasin-ledger-coldstore-canaries-") as tmp:
        base = pathlib.Path(tmp)
        pristine = base / "pristine"
        _copy_required_tree(root, pristine)
        try:
            observed = validate_ledger_coldstore(pristine)
        except LedgerColdstoreError as exc:
            add("ledger-coldstore-valid-baseline", "valid coldstore tree is accepted", str(exc), False)
        else:
            add("ledger-coldstore-valid-baseline", "valid coldstore tree is accepted", observed, observed.get("cold_row_count", 0) >= 1000)

        scenarios: list[dict[str, Any]] = [
            {
                "id": "ledger-coldstore-payload-hash-mutation",
                "expected_failure_contains": "cold payload hash mismatch",
                "mutate": lambda case: _mutate_coldstore(case, _mutate_payload_hash),
            },
            {
                "id": "ledger-coldstore-row-hash-mutation",
                "expected_failure_contains": "original row hash mismatch",
                "mutate": lambda case: _mutate_coldstore(case, _mutate_row_hash),
            },
            {
                "id": "ledger-coldstore-payload-row-omission",
                "expected_failure_contains": "row hash/byte-count coverage mismatch",
                "mutate": lambda case: _mutate_coldstore(case, _mutate_payload_row_omission),
            },
            {
                "id": "ledger-coldstore-hot-ref-mismatch",
                "expected_failure_contains": "cold_payload_ref mismatch",
                "mutate": _mutate_hot_ref,
            },
            {
                "id": "ledger-coldstore-current-tail-compaction",
                "expected_failure_contains": "current revision row must not be cold-compacted",
                "mutate": _mutate_current_tail_compaction,
            },
            {
                "id": "ledger-coldstore-savings-arithmetic-mutation",
                "expected_failure_contains": "saved_bytes arithmetic mismatch",
                "mutate": lambda case: _mutate_coldstore(case, _mutate_stats),
            },
        ]
        for index, scenario in enumerate(scenarios, start=1):
            case = base / f"case-{index}"
            _copy_required_tree(pristine, case)
            scenario["mutate"](case)
            try:
                validate_ledger_coldstore(case)
            except LedgerColdstoreError as exc:
                message = str(exc)
                token = scenario["expected_failure_contains"]
                add(scenario["id"], {"failure_contains": token}, message, token in message)
            else:
                add(scenario["id"], {"failure_contains": scenario["expected_failure_contains"]}, None, False)
    return results
