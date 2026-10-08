#!/usr/bin/env python3
"""Build a deterministic Bloom-filter false-positive poem artifact.

The artifact is intentionally tiny and self-contained. It demonstrates one
specific non-member query for which every queried bit is already set by other
inserted records. The filter answers ``POSSIBLY PRESENT`` while the exact input
ledger proves the query was never inserted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

SCHEMA = "llmpoetry-bloom-poem-spec-v1"
RECEIPT_SCHEMA = "llmpoetry-bloom-poem-receipt-v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def read_spec(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8"))
    if obj.get("schema") != SCHEMA:
        raise ValueError(f"unexpected Bloom poem schema: {obj.get('schema')!r}")
    return obj


def token_bytes(token: str) -> bytes:
    if not isinstance(token, str) or not token or token.strip() != token:
        raise ValueError(f"invalid token: {token!r}")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in token):
        raise ValueError(f"control character in token: {token!r}")
    return token.encode("utf-8")


def positions(token: str, *, bit_count: int, hash_count: int, domain: str) -> list[int]:
    token_bytes(token)
    if bit_count <= 0 or bit_count % 8:
        raise ValueError("bit_count must be a positive multiple of 8")
    if hash_count <= 0:
        raise ValueError("hash_count must be positive")
    if not domain or any(ord(ch) < 32 for ch in domain):
        raise ValueError("hash domain must be non-empty printable text")
    out: list[int] = []
    for index in range(hash_count):
        payload = f"{domain}|{index}|{token}".encode("utf-8")
        digest = hashlib.sha256(payload).digest()
        out.append(int.from_bytes(digest[:8], "big") % bit_count)
    return out


def set_bit(buf: bytearray, bit: int) -> None:
    buf[bit // 8] |= 1 << (bit % 8)


def get_bit(buf: bytes | bytearray, bit: int) -> bool:
    return bool(buf[bit // 8] & (1 << (bit % 8)))


def expected_surface(records: list[str], query: str, query_positions: list[int], owners: dict[int, list[str]]) -> str:
    lines = ["INSERTED", *records, "", "QUERY", query, ""]
    for bit in query_positions:
        owner_list = owners[bit]
        if len(owner_list) != 1:
            raise ValueError(f"query bit {bit} must have exactly one owner for this poem contract")
        lines.append(f"BIT {bit} | SET BY {owner_list[0]}")
    lines.extend([
        "",
        "FILTER",
        "POSSIBLY PRESENT",
        "",
        "EXACT SET",
        "NOT PRESENT",
        "",
        "All three bits said yes.",
        "No record did.",
    ])
    return "\n".join(lines) + "\n"


def build(spec_path: Path) -> dict[str, Any]:
    spec_path = spec_path.resolve()
    artifact_dir = spec_path.parent
    spec = read_spec(spec_path)

    bit_count = int(spec["bit_count"])
    hash_count = int(spec["hash_count"])
    domain = str(spec["hash_domain"])
    records = list(spec["inserted_records"])
    query = str(spec["query"])
    outputs = dict(spec["outputs"])

    if bit_count % 8 or bit_count < 8:
        raise ValueError("bit_count must be a multiple of 8 and at least 8")
    if hash_count != 3:
        raise ValueError("this poem contract requires exactly three hash probes")
    if len(records) != 3 or len(set(records)) != 3:
        raise ValueError("this poem contract requires exactly three distinct inserted records")
    for token in records:
        token_bytes(token)
    token_bytes(query)
    if query in records:
        raise ValueError("query must not be present in exact inserted records")

    allowed_outputs = {
        "filter": "filter.bin",
        "ledger": "inserted_records.txt",
        "query": "query.txt",
        "surface": "filter_surface.txt",
        "receipt": "BLOOM_RECEIPT.json",
    }
    if outputs != allowed_outputs:
        raise ValueError(f"outputs must equal the fixed local contract: {allowed_outputs}")

    record_positions = {token: positions(token, bit_count=bit_count, hash_count=hash_count, domain=domain) for token in records}
    query_positions = positions(query, bit_count=bit_count, hash_count=hash_count, domain=domain)
    if len(set(query_positions)) != hash_count:
        raise ValueError("query probes must be distinct for this poem contract")

    bits = bytearray(bit_count // 8)
    owners_all: dict[int, list[str]] = {i: [] for i in range(bit_count)}
    for token in records:
        for bit in record_positions[token]:
            set_bit(bits, bit)
            if token not in owners_all[bit]:
                owners_all[bit].append(token)

    if not all(get_bit(bits, bit) for bit in query_positions):
        raise ValueError("spec does not produce the required false positive")

    query_owners = {bit: owners_all[bit] for bit in query_positions}
    if any(len(owner_list) != 1 for owner_list in query_owners.values()):
        raise ValueError("each query bit must be set by exactly one inserted record")
    if len({owner_list[0] for owner_list in query_owners.values()}) != hash_count:
        raise ValueError("each query bit must belong to a different inserted record")
    query_set = set(query_positions)
    if any(len(query_set.intersection(record_positions[token])) != 1 for token in records):
        raise ValueError("each inserted record must contribute exactly one query bit")

    expected = spec.get("expected", {})
    if expected:
        if expected.get("record_positions") != record_positions:
            raise ValueError("computed record positions do not match the committed spec")
        if expected.get("query_positions") != query_positions:
            raise ValueError("computed query positions do not match the committed spec")
        if expected.get("query_bit_owners") != {str(bit): query_owners[bit] for bit in query_positions}:
            raise ValueError("computed query-bit owners do not match the committed spec")
        if expected.get("filter_hex") != bytes(bits).hex():
            raise ValueError("computed filter bytes do not match the committed spec")

    ledger_text = "\n".join(records) + "\n"
    query_text = query + "\n"
    surface_text = expected_surface(records, query, query_positions, query_owners)

    artifact_dir.mkdir(parents=True, exist_ok=True)
    (artifact_dir / outputs["filter"]).write_bytes(bytes(bits))
    (artifact_dir / outputs["ledger"]).write_text(ledger_text, encoding="utf-8")
    (artifact_dir / outputs["query"]).write_text(query_text, encoding="utf-8")
    (artifact_dir / outputs["surface"]).write_text(surface_text, encoding="utf-8")

    artifact_hashes = {
        name: sha256_file(artifact_dir / outputs[name])
        for name in ("filter", "ledger", "query", "surface")
    }
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "revision": spec["revision"],
        "poem_id": spec["poem_id"],
        "draft_id": spec["draft_id"],
        "created_at": spec["created_at"],
        "spec_path": spec.get("spec_path", "poems/P0005/artifact/d001/BLOOM_POEM_SPEC.json"),
        "spec_sha256": sha256_file(spec_path),
        "algorithm": {
            "family": "Bloom filter",
            "bit_count": bit_count,
            "hash_count": hash_count,
            "hash": "SHA-256 domain-separated by probe index; first 8 digest bytes interpreted big-endian; modulo bit_count",
            "hash_domain": domain,
            "bit_numbering": "bit i is byte i//8, mask 1<<(i%8)",
        },
        "inserted_records": records,
        "record_positions": record_positions,
        "query": query,
        "query_positions": query_positions,
        "query_bit_owners": {str(bit): query_owners[bit] for bit in query_positions},
        "filter_hex": bytes(bits).hex(),
        "filter_answer": "POSSIBLY PRESENT",
        "exact_membership": False,
        "false_positive": True,
        "state_contract": {
            "query_not_inserted": True,
            "all_query_bits_set": True,
            "each_query_bit_has_one_distinct_inserted_owner": True,
            "all_inserted_records_test_positive": True,
        },
        "outputs": outputs,
        "artifact_sha256": artifact_hashes,
        "quality_claims": [],
        "non_claim": "This receipt proves one deterministic Bloom-filter false positive and exact-ledger absence only. It is not a literary judgment, real case record, reader response, admission, or evidence of quality.",
    }
    (artifact_dir / outputs["receipt"]).write_text(
        json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "spec",
        nargs="?",
        default="poems/P0005/artifact/d001/BLOOM_POEM_SPEC.json",
    )
    args = parser.parse_args()
    try:
        receipt = build(Path(args.spec))
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1
    print(json.dumps({"ok": True, "receipt": receipt}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
