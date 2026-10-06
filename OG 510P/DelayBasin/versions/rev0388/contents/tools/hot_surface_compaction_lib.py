import base64
import gzip
import hashlib
import json
import pathlib
import re
from typing import Any

WORD_RE = re.compile(r"[A-Za-z0-9_]+(?:[-'][A-Za-z0-9_]+)*")
REQUIRED_POLICY_PHRASES = [
    "not a deletion court",
    "semantic substitutes",
    "Full pre-compaction text is retained losslessly",
]
TARGET_COUNT = 4


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def word_count(text: str) -> int:
    return len(WORD_RE.findall(text))


def load_json(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_receipt(root: pathlib.Path) -> dict[str, Any]:
    receipt_path = root / "HOT-SURFACE-COMPACTION.json"
    if not receipt_path.exists():
        raise SystemExit("missing HOT-SURFACE-COMPACTION.json")
    return load_json(receipt_path)


def source_entry_text(source_entry: dict[str, Any], rel: str) -> str:
    """Return the retained original text from either legacy plain-text or cold encoded rows."""
    if isinstance(source_entry.get("text"), str):
        return source_entry["text"]
    if source_entry.get("encoding") == "gzip+base64" and isinstance(source_entry.get("encoded_text"), str):
        try:
            raw = base64.b64decode(source_entry["encoded_text"].encode("ascii"), validate=True)
            text = gzip.decompress(raw).decode("utf-8")
        except Exception as exc:
            raise SystemExit(f"hot-surface source bundle cannot decode cold original for {rel}: {exc}") from exc
        declared = source_entry.get("sha256")
        if declared and declared != sha256_text(text):
            raise SystemExit(f"hot-surface cold original sha256 drifted for {rel}")
        return text
    raise SystemExit(f"source bundle missing original text for {rel}")


def load_source_bundle(root: pathlib.Path, receipt: dict[str, Any] | None = None) -> dict[str, Any]:
    receipt = receipt or load_receipt(root)
    source_rel = receipt.get("source_bundle")
    source = root / str(source_rel)
    if not source.exists():
        raise SystemExit(f"missing hot-surface source bundle: {source_rel}")
    source_bytes = source.read_bytes()
    if receipt.get("source_bundle_sha256") != sha256_bytes(source_bytes):
        raise SystemExit("hot-surface source bundle sha256 drifted")
    try:
        payload = json.loads(source_bytes.decode("utf-8"))
    except Exception as exc:
        raise SystemExit(f"hot-surface source bundle is not valid JSON: {exc}") from exc
    if payload.get("state") != "pre-compaction-hot-surface-sources":
        raise SystemExit("hot-surface source bundle state drifted")
    if payload.get("encoding") not in {None, "plain-text", "mixed", "gzip+base64"}:
        raise SystemExit("hot-surface source bundle encoding drifted")
    return payload


def target_checks(current_text: str, original_text: str) -> dict[str, int | str]:
    return {
        "original_sha256": sha256_text(original_text),
        "compacted_sha256": sha256_text(current_text),
        "original_bytes": len(original_text.encode("utf-8")),
        "compacted_bytes": len(current_text.encode("utf-8")),
        "original_words": word_count(original_text),
        "compacted_words": word_count(current_text),
    }


def verify_compaction_receipt(root: pathlib.Path) -> dict[str, Any]:
    receipt = load_receipt(root)
    current_revision = load_json(root / "REVISION-RECEIPT.json").get("revision")
    if receipt.get("revision") != current_revision:
        raise SystemExit("HOT-SURFACE-COMPACTION revision drifted")
    for phrase in REQUIRED_POLICY_PHRASES:
        haystacks = [receipt.get("non_claim", ""), receipt.get("policy", "")]
        if not any(phrase in haystack for haystack in haystacks):
            raise SystemExit(f"HOT-SURFACE-COMPACTION missing policy/non-claim phrase: {phrase}")
    payload = load_source_bundle(root, receipt)
    rows = receipt.get("targets")
    if not isinstance(rows, list) or len(rows) != TARGET_COUNT:
        raise SystemExit(f"HOT-SURFACE-COMPACTION must record exactly {TARGET_COUNT} target surfaces")
    total_original_words = 0
    total_compacted_words = 0
    total_original_bytes = 0
    total_compacted_bytes = 0
    for row in rows:
        rel = row.get("path")
        current = root / str(rel)
        if not current.exists():
            raise SystemExit(f"compacted target missing: {rel}")
        current_text = current.read_text(encoding="utf-8")
        source_entry = payload.get("targets", {}).get(rel)
        if not isinstance(source_entry, dict):
            raise SystemExit(f"source bundle missing original text for {rel}")
        original_text = source_entry_text(source_entry, rel)
        checks = target_checks(current_text, original_text)
        for key, expected in checks.items():
            if row.get(key) != expected:
                raise SystemExit(f"{rel} {key} drifted: {row.get(key)!r} != {expected!r}")
        if "Hot-surface compaction note" not in current_text:
            raise SystemExit(f"{rel} missing compaction note")
        if row["compacted_words"] >= row["original_words"]:
            raise SystemExit(f"{rel} did not reduce markdown words")
        if "HOT-SURFACE-COMPACTION-ORIGINALS.json" not in current_text:
            raise SystemExit(f"{rel} missing source-bundle pointer")
        total_original_words += int(row["original_words"])
        total_compacted_words += int(row["compacted_words"])
        total_original_bytes += int(row["original_bytes"])
        total_compacted_bytes += int(row["compacted_bytes"])
    totals = receipt.get("totals", {})
    expected_totals = {
        "original_markdown_words": total_original_words,
        "compacted_markdown_words": total_compacted_words,
        "word_delta": total_compacted_words - total_original_words,
        "original_bytes": total_original_bytes,
        "compacted_bytes": total_compacted_bytes,
        "byte_delta": total_compacted_bytes - total_original_bytes,
    }
    for key, expected in expected_totals.items():
        if totals.get(key) != expected:
            raise SystemExit(f"hot-surface totals drifted for {key}: {totals.get(key)!r} != {expected!r}")
    if totals.get("compacted_markdown_words", 0) >= totals.get("original_markdown_words", 0):
        raise SystemExit("hot-surface compaction did not reduce total markdown words")
    return {"receipt": receipt, "source_bundle": payload}


def restore_originals_to(root: pathlib.Path, destination: pathlib.Path) -> list[dict[str, int | str]]:
    verified = verify_compaction_receipt(root)
    payload = verified["source_bundle"]
    receipt = verified["receipt"]
    records: list[dict[str, int | str]] = []
    for row in receipt["targets"]:
        rel = row["path"]
        text = source_entry_text(payload["targets"][rel], rel)
        out = destination / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text, encoding="utf-8")
        data = out.read_bytes()
        record = {
            "path": rel,
            "sha256": sha256_bytes(data),
            "bytes": len(data),
            "words": word_count(text),
        }
        if record["sha256"] != row["original_sha256"]:
            raise SystemExit(f"restored original sha256 mismatch for {rel}")
        if record["bytes"] != row["original_bytes"]:
            raise SystemExit(f"restored original byte count mismatch for {rel}")
        if record["words"] != row["original_words"]:
            raise SystemExit(f"restored original word count mismatch for {rel}")
        records.append(record)
    return records
