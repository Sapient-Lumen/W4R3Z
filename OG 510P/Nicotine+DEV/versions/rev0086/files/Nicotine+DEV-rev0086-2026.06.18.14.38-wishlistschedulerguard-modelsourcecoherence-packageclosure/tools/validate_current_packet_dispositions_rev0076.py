#!/usr/bin/env python3
"""Validate the rev0076 current packet-disposition authority.

The validator intentionally has no third-party dependency. It enforces the
schema properties needed by the cube, path safety, document existence, patch
selection rules, and snapshot equality.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path, PurePosixPath
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REVISION = "rev0076"
SOURCE_REF = "98089ac233aa57786e8dbdc48123f6ac1c4767d8"
LEDGER = Path("data/current_packet_dispositions.json")
SNAPSHOT = Path("data/rev0076_packet_dispositions.json")
SCHEMA = Path("data/current_packet_dispositions.schema.json")
OUTPUT = Path("data/rev0076_packet_disposition_validation.json")
EVIDENCE = Path("evidence/rev0076-packet-disposition-validation.md")
REQUIRED_LEDGER_KEYS = {"authority", "revision", "source_lane", "source_ref", "packets"}
REQUIRED_PACKET_KEYS = {
    "packet_id", "title", "status", "behavior", "impact",
    "security_route", "selected_patch", "current_document",
}
ALLOWED_PACKET_KEYS = REQUIRED_PACKET_KEYS | {"missing_evidence"}
NO_PATCH_STATUS_PREFIXES = ("open-", "retired-")


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True) + "\n"


def safe_document(value: object) -> bool:
    if not isinstance(value, str):
        return False
    pure = PurePosixPath(value)
    return (
        not pure.is_absolute()
        and ".." not in pure.parts
        and pure.parts[:1] == ("docs",)
        and pure.suffix == ".md"
        and "\\" not in value
    )


def validate(root: Path) -> dict[str, Any]:
    checks: list[dict[str, Any]] = []
    errors: list[str] = []

    def add(name: str, passed: bool, detail: object = "") -> None:
        checks.append({"check": name, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{name}: {detail}")

    try:
        ledger = load(root / LEDGER)
        snapshot = load(root / SNAPSHOT)
        schema = load(root / SCHEMA)
    except Exception as exc:
        return {
            "revision": REVISION,
            "status": "fail",
            "checks": [],
            "errors": [f"load: {exc}"],
        }

    add("ledger is object", isinstance(ledger, dict), type(ledger).__name__)
    if not isinstance(ledger, dict):
        return {"revision": REVISION, "status": "fail", "checks": checks, "errors": errors}

    add("ledger keys exact", set(ledger) == REQUIRED_LEDGER_KEYS, sorted(set(ledger) ^ REQUIRED_LEDGER_KEYS))
    add("revision exact", ledger.get("revision") == REVISION, ledger.get("revision"))
    add("source lane exact", ledger.get("source_lane") == "github-branch-3.3.x", ledger.get("source_lane"))
    add("source ref exact", ledger.get("source_ref") == SOURCE_REF, ledger.get("source_ref"))
    add("authority meaningful", isinstance(ledger.get("authority"), str) and len(ledger["authority"]) >= 20)
    add("snapshot parsed equality", ledger == snapshot)
    add("snapshot canonical equality", canonical(ledger) == canonical(snapshot))

    add("schema object", isinstance(schema, dict))
    add("schema revision const", schema.get("properties", {}).get("revision", {}).get("const") == REVISION)
    add("schema source ref const", schema.get("properties", {}).get("source_ref", {}).get("const") == SOURCE_REF)
    add("schema disallows ledger extras", schema.get("additionalProperties") is False)
    packet_schema = schema.get("properties", {}).get("packets", {}).get("items", {})
    add("schema disallows packet extras", packet_schema.get("additionalProperties") is False)
    add("schema packet requirements", set(packet_schema.get("required", [])) == REQUIRED_PACKET_KEYS)

    packets = ledger.get("packets")
    add("packets is nonempty list", isinstance(packets, list) and bool(packets), type(packets).__name__)
    if not isinstance(packets, list):
        packets = []

    ids: list[str] = []
    documents: list[str] = []
    for index, packet in enumerate(packets):
        prefix = f"packet[{index}]"
        add(f"{prefix} object", isinstance(packet, dict), type(packet).__name__)
        if not isinstance(packet, dict):
            continue
        packet_id = packet.get("packet_id")
        add(f"{prefix} required keys", REQUIRED_PACKET_KEYS <= set(packet), sorted(REQUIRED_PACKET_KEYS - set(packet)))
        add(f"{prefix} allowed keys", set(packet) <= ALLOWED_PACKET_KEYS, sorted(set(packet) - ALLOWED_PACKET_KEYS))
        add(f"{prefix} id", isinstance(packet_id, str) and len(packet_id) >= 2, packet_id)
        add(f"{prefix} title", isinstance(packet.get("title"), str) and len(packet["title"]) >= 4)
        status = packet.get("status")
        add(f"{prefix} status format", isinstance(status, str) and re.fullmatch(r"[a-z0-9-]+", status or "") is not None, status)
        for field in ("behavior", "impact", "security_route"):
            add(f"{prefix} {field}", isinstance(packet.get(field), str) and len(packet[field]) >= 3)
        selected = packet.get("selected_patch")
        add(f"{prefix} selected patch type", selected is None or isinstance(selected, str), type(selected).__name__)
        if isinstance(status, str) and status.startswith(NO_PATCH_STATUS_PREFIXES):
            add(f"{prefix} open/retired has no patch", selected is None, selected)
        document = packet.get("current_document")
        add(f"{prefix} safe document path", safe_document(document), document)
        if safe_document(document):
            add(f"{prefix} document exists", (root / str(document)).is_file(), document)
            documents.append(str(document))
        missing = packet.get("missing_evidence")
        if missing is not None:
            add(f"{prefix} missing evidence list", isinstance(missing, list) and all(isinstance(x, str) and len(x) >= 4 for x in missing))
            if isinstance(missing, list):
                add(f"{prefix} missing evidence unique", len(missing) == len(set(missing)))
        if isinstance(packet_id, str):
            ids.append(packet_id)

    add("packet ids unique", len(ids) == len(set(ids)), ids)
    add("current document coverage", len(set(documents)) >= 4, documents)
    add(
        "shared PB document intentional",
        documents.count("docs/PB01-CURRENT-DISPOSITION-REV0074.md") == 2,
        documents,
    )
    by_id = {packet.get("packet_id"): packet for packet in packets if isinstance(packet, dict)}
    add("expected packet set", set(by_id) == {
        "U-123", "PB-01A/U-168", "PB-01B/U-176",
        "SEARCH-RESP-01A/U-163A", "SEARCH-RESP-01B/U-163B",
    }, sorted(by_id))

    buddy = by_id.get("SEARCH-RESP-01B/U-163B", {})
    add("buddy row status", buddy.get("status") == "open-request-epoch-design-research", buddy.get("status"))
    add("buddy row no selected patch", buddy.get("selected_patch") is None, buddy.get("selected_patch"))
    add("buddy row security route", buddy.get("security_route") == "not supported by current evidence", buddy.get("security_route"))
    add("buddy row current document", buddy.get("current_document") == "docs/SEARCH-RESP-01B-CURRENT-DISPOSITION-REV0076.md")
    missing = buddy.get("missing_evidence", [])
    add("buddy row has epoch gap", any("epoch" in item.lower() for item in missing), missing)
    add("buddy row has identity gap", any("identity" in item.lower() for item in missing), missing)
    add("buddy row has impact gap", any("harm" in item.lower() or "impact" in item.lower() for item in missing), missing)

    return {
        "revision": REVISION,
        "status": "pass" if not errors else "fail",
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "packet_count": len(packets),
        "packet_ids": ids,
        "buddy_selected_patch": buddy.get("selected_patch"),
        "buddy_status": buddy.get("status"),
        "checks": checks,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    result = validate(root)
    if args.write_data:
        (root / OUTPUT).write_text(canonical(result), encoding="utf-8")
        lines = [
            "# rev0076 packet-disposition validation",
            "",
            f"Status: **{result['status']}**",
            "",
            "```text",
            f"checks: {result.get('checks_passed', 0)}/{result.get('checks_total', 0)}",
            f"packets: {result.get('packet_count', 0)}",
            f"SEARCH-RESP-01B status: {result.get('buddy_status')}",
            f"SEARCH-RESP-01B selected patch: {result.get('buddy_selected_patch')}",
            "```",
            "",
        ]
        if result["errors"]:
            lines.extend(["## Errors", ""] + [f"- {item}" for item in result["errors"]])
        (root / EVIDENCE).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(canonical(result), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
