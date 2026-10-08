#!/usr/bin/env python3
"""Validate all LLMPoetry Bloom-filter false-positive poem artifacts."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

from build_bloom_false_positive_poem import build as build_artifact


def add(checks: list[dict[str, Any]], name: str, ok: bool, detail: Any = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": detail})


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_positions(token: str, bit_count: int, hash_count: int, domain: str) -> list[int]:
    out = []
    for index in range(hash_count):
        payload = f"{domain}|{index}|{token}".encode("utf-8")
        out.append(int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") % bit_count)
    return out


def bit_is_set(data: bytes, bit: int) -> bool:
    return bool(data[bit // 8] & (1 << (bit % 8)))


def expected_surface(records: list[str], query: str, query_positions: list[int], owners: dict[int, list[str]]) -> str:
    lines = ["INSERTED", *records, "", "QUERY", query, ""]
    for bit in query_positions:
        owner = owners[bit][0] if len(owners.get(bit, [])) == 1 else "<INVALID>"
        lines.append(f"BIT {bit} | SET BY {owner}")
    lines.extend(["", "FILTER", "POSSIBLY PRESENT", "", "EXACT SET", "NOT PRESENT", "", "All three bits said yes.", "No record did."])
    return "\n".join(lines) + "\n"


def check_one(root: Path, spec_path: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    rel = spec_path.relative_to(root).as_posix()
    artifact = spec_path.parent
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        add(checks, f"bloom_spec_parse:{rel}", True)
    except Exception as exc:
        add(checks, f"bloom_spec_parse:{rel}", False, str(exc))
        return checks

    add(checks, f"bloom_spec_schema:{rel}", spec.get("schema") == "llmpoetry-bloom-poem-spec-v1", spec.get("schema"))
    bit_count = int(spec.get("bit_count", 0) or 0)
    hash_count = int(spec.get("hash_count", 0) or 0)
    domain = str(spec.get("hash_domain", ""))
    records = list(spec.get("inserted_records", []))
    query = str(spec.get("query", ""))
    outputs = dict(spec.get("outputs", {}))
    expected_outputs = {"filter": "filter.bin", "ledger": "inserted_records.txt", "query": "query.txt", "surface": "filter_surface.txt", "receipt": "BLOOM_RECEIPT.json"}
    add(checks, f"bloom_bit_count:{rel}", bit_count == 32, bit_count)
    add(checks, f"bloom_hash_count:{rel}", hash_count == 3, hash_count)
    add(checks, f"bloom_three_records:{rel}", len(records) == 3 and len(set(records)) == 3, records)
    add(checks, f"bloom_query_absent_exact:{rel}", bool(query) and query not in records, query)
    add(checks, f"bloom_fixed_outputs:{rel}", outputs == expected_outputs, outputs)

    missing = [name for name in expected_outputs.values() if not (artifact / name).is_file()]
    add(checks, f"bloom_outputs_exist:{rel}", not missing, missing)
    if missing:
        return checks

    filter_bytes = (artifact / outputs["filter"]).read_bytes()
    add(checks, f"bloom_filter_length:{rel}", len(filter_bytes) == bit_count // 8, len(filter_bytes))
    record_positions = {token: independent_positions(token, bit_count, hash_count, domain) for token in records}
    query_positions = independent_positions(query, bit_count, hash_count, domain)
    add(checks, f"bloom_query_probes_distinct:{rel}", len(set(query_positions)) == hash_count, query_positions)
    add(checks, f"bloom_inserted_no_false_negatives:{rel}", all(all(bit_is_set(filter_bytes, b) for b in record_positions[token]) for token in records), record_positions)
    add(checks, f"bloom_query_all_bits_set:{rel}", all(bit_is_set(filter_bytes, b) for b in query_positions), query_positions)

    owners_all: dict[int, list[str]] = {i: [] for i in range(bit_count)}
    rebuilt = bytearray(bit_count // 8)
    for token in records:
        for bit in record_positions[token]:
            rebuilt[bit // 8] |= 1 << (bit % 8)
            if token not in owners_all[bit]:
                owners_all[bit].append(token)
    add(checks, f"bloom_filter_exact_rebuild:{rel}", bytes(rebuilt) == filter_bytes, {"expected": bytes(rebuilt).hex(), "actual": filter_bytes.hex()})
    owners = {bit: owners_all[bit] for bit in query_positions}
    add(checks, f"bloom_one_owner_per_query_bit:{rel}", all(len(v) == 1 for v in owners.values()), owners)
    add(checks, f"bloom_distinct_owner_per_query_bit:{rel}", len({v[0] for v in owners.values() if len(v) == 1}) == hash_count, owners)
    add(checks, f"bloom_each_record_contributes_one_query_bit:{rel}", all(len(set(query_positions).intersection(record_positions[t])) == 1 for t in records), record_positions)

    ledger = (artifact / outputs["ledger"]).read_text(encoding="utf-8")
    query_text = (artifact / outputs["query"]).read_text(encoding="utf-8")
    surface = (artifact / outputs["surface"]).read_text(encoding="utf-8")
    add(checks, f"bloom_ledger_exact:{rel}", ledger == "\n".join(records) + "\n", ledger)
    add(checks, f"bloom_query_file_exact:{rel}", query_text == query + "\n", query_text)
    add(checks, f"bloom_surface_exact:{rel}", surface == expected_surface(records, query, query_positions, owners), surface)

    try:
        receipt = json.loads((artifact / outputs["receipt"]).read_text(encoding="utf-8"))
        add(checks, f"bloom_receipt_parse:{rel}", True)
    except Exception as exc:
        add(checks, f"bloom_receipt_parse:{rel}", False, str(exc))
        return checks
    add(checks, f"bloom_receipt_schema:{rel}", receipt.get("schema") == "llmpoetry-bloom-poem-receipt-v1", receipt.get("schema"))
    add(checks, f"bloom_receipt_spec_hash:{rel}", receipt.get("spec_sha256") == sha256_file(spec_path), receipt.get("spec_sha256"))
    add(checks, f"bloom_receipt_positions:{rel}", receipt.get("query_positions") == query_positions, receipt.get("query_positions"))
    add(checks, f"bloom_receipt_record_positions:{rel}", receipt.get("record_positions") == record_positions, receipt.get("record_positions"))
    add(checks, f"bloom_receipt_filter_hex:{rel}", receipt.get("filter_hex") == filter_bytes.hex(), receipt.get("filter_hex"))
    add(checks, f"bloom_receipt_false_positive:{rel}", receipt.get("false_positive") is True and receipt.get("exact_membership") is False and receipt.get("filter_answer") == "POSSIBLY PRESENT", {k: receipt.get(k) for k in ("false_positive", "exact_membership", "filter_answer")})
    for key in ("filter", "ledger", "query", "surface"):
        add(checks, f"bloom_receipt_hash:{rel}:{key}", receipt.get("artifact_sha256", {}).get(key) == sha256_file(artifact / outputs[key]), receipt.get("artifact_sha256", {}).get(key))

    # Prove that the declared spec alone deterministically rebuilds every output.
    with tempfile.TemporaryDirectory(prefix="llmpoetry-bloom-rebuild-") as td:
        temp_artifact = Path(td) / "artifact"
        temp_artifact.mkdir(parents=True)
        temp_spec = temp_artifact / "BLOOM_POEM_SPEC.json"
        shutil.copyfile(spec_path, temp_spec)
        try:
            build_artifact(temp_spec)
            rebuild_ok = all((temp_artifact / name).read_bytes() == (artifact / name).read_bytes() for name in expected_outputs.values())
            add(checks, f"bloom_deterministic_rebuild:{rel}", rebuild_ok)
        except Exception as exc:
            add(checks, f"bloom_deterministic_rebuild:{rel}", False, str(exc))

    # Small fail-closed mutation checks exercise the builder's semantic boundaries.
    for label, mutate in (
        ("query_inserted", lambda s: s.__setitem__("query", s["inserted_records"][0])),
        ("duplicate_record", lambda s: s.__setitem__("inserted_records", [s["inserted_records"][0]] * 3)),
        ("bad_bit_count", lambda s: s.__setitem__("bit_count", 31)),
    ):
        with tempfile.TemporaryDirectory(prefix=f"llmpoetry-bloom-{label}-") as td:
            bad = json.loads(json.dumps(spec))
            mutate(bad)
            bad_path = Path(td) / "BLOOM_POEM_SPEC.json"
            bad_path.write_text(json.dumps(bad, indent=2) + "\n", encoding="utf-8")
            rejected = False
            try:
                build_artifact(bad_path)
            except Exception:
                rejected = True
            add(checks, f"bloom_rejects_{label}:{rel}", rejected)
    return checks


def run(root: Path) -> list[dict[str, Any]]:
    root = root.resolve()
    checks: list[dict[str, Any]] = []
    specs = sorted(root.glob("poems/P*/artifact/d*/BLOOM_POEM_SPEC.json"))
    add(checks, "bloom_specs_present", bool(specs), [p.relative_to(root).as_posix() for p in specs])
    for spec in specs:
        checks.extend(check_one(root, spec))
    return checks


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    checks = run(Path(args.root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "check_count": len(checks), "failed": [c for c in checks if not c.get("ok")], "checks": checks}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
