#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LEDGER_PATH = ROOT / "specs" / "spec_ledger.yaml"
SCHEMA_PATH = ROOT / "schemas" / "spec_ledger.schema.json"

ALLOWED_TYPES = {"gap", "question", "assumption"}
ALLOWED_STATUS = {"open", "mitigated", "resolved", "retired"}
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(msg: str) -> None:
    print(f"spec-ledger: {msg}", file=sys.stderr)
    raise SystemExit(1)


def parse_json_yaml(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"parse error in {path}: {exc}")


def require_date(label: str, value: str) -> None:
    if not DATE_RE.match(value):
        fail(f"{label} must be YYYY-MM-DD: {value}")
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError:
        fail(f"{label} invalid date: {value}")


def main() -> int:
    if not LEDGER_PATH.exists():
        fail(f"missing {LEDGER_PATH}")
    if not SCHEMA_PATH.exists():
        fail(f"missing {SCHEMA_PATH}")

    _schema = parse_json_yaml(SCHEMA_PATH)
    entries = parse_json_yaml(LEDGER_PATH)

    if not isinstance(entries, list) or not entries:
        fail("ledger must be non-empty list (JSON/YAML)")

    ids = set()
    gap_ids = set()
    question_links = {}

    required = {
        "id",
        "type",
        "status",
        "summary",
        "owner",
        "exit_criteria",
        "evidence_links",
        "created",
        "last_updated",
        "target_resolution",
    }

    for idx, e in enumerate(entries):
        if not isinstance(e, dict):
            fail(f"entry[{idx}] must be object")

        missing = required - set(e)
        if missing:
            fail(f"entry[{idx}] missing keys: {sorted(missing)}")

        eid = str(e["id"])
        if eid in ids:
            fail(f"duplicate id: {eid}")
        ids.add(eid)

        etype = e["type"]
        if etype not in ALLOWED_TYPES:
            fail(f"entry {eid}: invalid type {etype}")

        status = e["status"]
        if status not in ALLOWED_STATUS:
            fail(f"entry {eid}: invalid status {status}")

        for key in ["created", "last_updated", "target_resolution"]:
            require_date(f"entry {eid}.{key}", str(e[key]))

        if not isinstance(e["evidence_links"], list):
            fail(f"entry {eid}.evidence_links must be list")

        if etype == "gap":
            gap_ids.add(eid)
            if status in {"open", "mitigated"}:
                if not str(e.get("owner", "")).strip():
                    fail(f"entry {eid}: unresolved gap needs owner")
                if not str(e.get("exit_criteria", "")).strip():
                    fail(f"entry {eid}: unresolved gap needs exit_criteria")

        if etype == "question":
            related = str(e.get("related_gap", "")).strip()
            if not related:
                fail(f"entry {eid}: question needs related_gap")
            question_links.setdefault(related, 0)
            question_links[related] += 1

        if etype == "assumption":
            linked_gap = str(e.get("linked_gap", "")).strip()
            if not linked_gap:
                fail(f"entry {eid}: assumption needs linked_gap")

    for e in entries:
        if e["type"] == "assumption":
            linked = str(e["linked_gap"])
            if linked not in gap_ids:
                fail(f"entry {e['id']}: linked_gap missing: {linked}")
        if e["type"] == "question":
            related = str(e["related_gap"])
            if related not in gap_ids:
                fail(f"entry {e['id']}: related_gap missing: {related}")

    for e in entries:
        if e["type"] == "gap" and e["status"] in {"open", "mitigated"}:
            if question_links.get(e["id"], 0) < 1:
                fail(f"entry {e['id']}: unresolved gap requires at least one open question")

    print(f"spec-ledger: ok ({len(entries)} entries)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
