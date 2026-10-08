#!/usr/bin/env python3
"""Audit the revision-neutral packet-authority engine and its mutations."""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = ROOT / "tools/validate_current_packet_dispositions.py"
OUTPUT_JSON = Path("data/rev0077_authority_engine_audit.json")
OUTPUT_CSV = Path("data/rev0077_authority_engine_mutations.csv")
EVIDENCE = Path("evidence/rev0077-authority-engine-audit.md")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def import_validator():
    spec = importlib.util.spec_from_file_location("current_packet_validator", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot import generic validator")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields: list[str] = []
    for row in rows:
        for field in row:
            if field not in fields:
                fields.append(field)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()

    validator = import_validator()
    ledger = load(root / "data/current_packet_dispositions.json")
    snapshot = load(root / "data/rev0077_packet_dispositions.json")
    schema = load(root / "data/current_packet_dispositions.schema.json")
    contract = load(root / "data/current_packet_disposition_contract.json")
    baseline = validator.validate(root)

    mutations: list[tuple[str, str, Callable[[Any, Any, Any, Any], None]]] = []

    def duplicate_id(l, s, c, sc):
        l["packets"].append(deepcopy(l["packets"][0]))
        s.clear(); s.update(deepcopy(l))

    def missing_document(l, s, c, sc):
        packet = l["packets"][0]
        packet["current_document"] = "docs/THIS-DOCUMENT-DOES-NOT-EXIST.md"
        c["packet_constraints"][packet["packet_id"]]["current_document"] = packet["current_document"]
        s.clear(); s.update(deepcopy(l))

    def patch_on_open(l, s, c, sc):
        packet = next(item for item in l["packets"] if item["status"].startswith("open-"))
        packet["selected_patch"] = "maintainer_artifacts/search-again-01/master-search-again-self-token.patch"
        c["packet_constraints"][packet["packet_id"]]["selected_patch"] = packet["selected_patch"]
        s.clear(); s.update(deepcopy(l))

    def snapshot_divergence(l, s, c, sc):
        s["authority"] = s["authority"] + " mutated"

    def contract_divergence(l, s, c, sc):
        packet_id = c["required_packet_ids"][0]
        c["packet_constraints"][packet_id]["status"] = "impossible-contract-status"

    def revision_mismatch(l, s, c, sc):
        l["revision"] = "rev9999"
        s.clear(); s.update(deepcopy(l))

    def hardcoded_schema(l, s, c, sc):
        sc["properties"]["revision"]["const"] = "rev9999"

    mutations.extend([
        ("duplicate-packet-id", "packet ids unique", duplicate_id),
        ("missing-current-document", "current document exists", missing_document),
        ("patch-selected-on-open-packet", "open/retired has no patch", patch_on_open),
        ("snapshot-divergence", "snapshot parsed equality", snapshot_divergence),
        ("contract-divergence", "contract", contract_divergence),
        ("revision-mismatch", "revision matches REVISION.txt", revision_mismatch),
        ("hardcoded-schema-revision", "schema has no revision const", hardcoded_schema),
    ])

    mutation_rows: list[dict[str, Any]] = []
    for name, target, mutate in mutations:
        l = deepcopy(ledger)
        s = deepcopy(snapshot)
        c = deepcopy(contract)
        sc = deepcopy(schema)
        mutate(l, s, c, sc)
        result = validator.validate(
            root,
            ledger_data=l,
            snapshot_data=s,
            contract_data=c,
            schema_data=sc,
        )
        target_seen = any(target in error for error in result.get("errors", []))
        mutation_rows.append({
            "mutation": name,
            "expected_status": "fail",
            "actual_status": result.get("status"),
            "target_invariant": target,
            "target_seen": target_seen,
            "rejected_as_expected": result.get("status") == "fail" and target_seen,
            "error_count": len(result.get("errors", [])),
        })

    validator_source = VALIDATOR_PATH.read_text(encoding="utf-8")
    packet_ids = contract["required_packet_ids"]
    leaked_packet_ids = [packet_id for packet_id in packet_ids if packet_id in validator_source]
    concrete_revisions = sorted(set(re.findall(r"rev[0-9]{4}", validator_source)))
    historical_validators = sorted((root / "tools").glob("validate_current_packet_dispositions_rev*.py"))
    archived_schema = root / "docs/archive/rev0076-status-authority/current_packet_dispositions.schema.rev0076.json"

    checks = {
        "baseline_pass": baseline.get("status") == "pass",
        "all_mutations_rejected": all(row["rejected_as_expected"] for row in mutation_rows),
        "generic_validator_has_no_packet_ids": not leaked_packet_ids,
        "generic_validator_has_no_concrete_revision": not concrete_revisions,
        "revision_neutral_schema": "const" not in schema["properties"]["revision"] and "const" not in schema["properties"]["source_ref"],
        "historical_schema_archived": archived_schema.is_file(),
        "data_contract_covers_ledger": set(contract["required_packet_ids"]) == {row["packet_id"] for row in ledger["packets"]},
    }
    errors = [name for name, passed in checks.items() if not passed]
    result = {
        "revision": "rev0077",
        "status": "pass" if not errors else "fail",
        "checks": checks,
        "errors": errors,
        "baseline_validation": {
            "status": baseline.get("status"),
            "checks_passed": baseline.get("checks_passed"),
            "checks_total": baseline.get("checks_total"),
            "packet_count": baseline.get("packet_count"),
        },
        "mutation_results": mutation_rows,
        "mutations_rejected": sum(bool(row["rejected_as_expected"]) for row in mutation_rows),
        "mutations_total": len(mutation_rows),
        "generic_validator_bytes": VALIDATOR_PATH.stat().st_size,
        "historical_hardcoded_validators": [path.name for path in historical_validators],
        "historical_hardcoded_validator_bytes": sum(path.stat().st_size for path in historical_validators),
        "leaked_packet_ids": leaked_packet_ids,
        "concrete_revision_literals": concrete_revisions,
    }

    if args.write_data:
        (root / OUTPUT_JSON).write_text(canonical(result), encoding="utf-8")
        write_csv(root / OUTPUT_CSV, mutation_rows)
        lines = [
            "# rev0077 authority-engine audit",
            "",
            f"Status: **{result['status']}**",
            "",
            "```text",
            f"baseline validation: {result['baseline_validation']['checks_passed']}/{result['baseline_validation']['checks_total']}",
            f"mutation rejections: {result['mutations_rejected']}/{result['mutations_total']}",
            f"packet IDs embedded in generic validator: {len(leaked_packet_ids)}",
            f"concrete revisions embedded in generic validator: {len(concrete_revisions)}",
            f"historical hard-coded validators retained: {len(historical_validators)}",
            "```",
            "",
            "The old revision-specific validator and schema remain historical evidence. Current policy is data-driven by the contract; current mechanism is the stable generic validator.",
            "",
        ]
        if errors:
            lines.extend(["## Errors", ""] + [f"- {item}" for item in errors])
        (root / EVIDENCE).write_text("\n".join(lines), encoding="utf-8")

    print(canonical(result), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
