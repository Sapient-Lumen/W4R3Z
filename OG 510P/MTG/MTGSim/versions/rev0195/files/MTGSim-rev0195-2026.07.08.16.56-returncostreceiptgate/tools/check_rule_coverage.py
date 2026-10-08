#!/usr/bin/env python3
"""Validate MTGSim's rule implementation ledger.

The ledger is intentionally metadata-only: rule identifiers, local implementation status,
and test links. It does not copy Wizards rules text.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from typing import Any

# Reports should use the project/user timezone for readable revision artifacts.
os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
LEDGER = ROOT / "data" / "rules" / "coverage" / "rules_ledger.json"
REPORT_DIR = ROOT / "reports" / "rules"
ALLOWED_STATUSES = {"inventory", "roadmap", "design", "scaffold", "implemented", "tested"}
RULE_ID_RE = re.compile(r"^(Glossary|\d{3}(?:\.\d+[a-z]?)?(?:-\d{3})?|\d{3}-[a-z][a-z0-9]*(?:-[a-z0-9]+)*)$")
# Hyphenated word suffixes are MTGSim synthetic ledger anchors for engine/evidence
# seams that attach to a Comprehensive Rules family without claiming to be literal
# Wizards rule numbers, e.g. 117-replay-bundle-manifest.


@dataclass
class LedgerIssue:
    severity: str
    code: str
    detail: str


def load_json(path: pathlib.Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def append_jsonl(path: pathlib.Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")


def compact_history_record(report: dict[str, Any], report_path: pathlib.Path) -> dict[str, Any]:
    """Append a compact trend row while preserving full detail in report_path."""
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    return {
        "schema": "mtgsim.rule_coverage_history.compact.v1",
        "source_schema": report.get("schema"),
        "created_at_local": report.get("created_at_local"),
        "revision": report.get("revision"),
        "source_effective_date": report.get("source_effective_date"),
        "ledger": report.get("ledger"),
        "report": rel(report_path),
        "summary": summary,
    }


def test_path_exists(test_ref: str) -> bool:
    path_part = test_ref.split("::", 1)[0]
    return (ROOT / path_part).exists()


def symbol_exists(test_ref: str) -> bool:
    if "::" not in test_ref:
        return True
    path_part, symbol = test_ref.split("::", 1)
    path = ROOT / path_part
    if not path.exists():
        return False
    try:
        return symbol in path.read_text(encoding="utf-8", errors="replace")
    except UnicodeDecodeError:
        return True


def check_ledger(root: pathlib.Path = ROOT, ledger_path: pathlib.Path = LEDGER) -> dict[str, Any]:
    started = time.perf_counter()
    issues: list[LedgerIssue] = []
    ledger = load_json(ledger_path)

    if ledger.get("schema") != "mtgsim.rules_ledger.v1":
        issues.append(LedgerIssue("error", "ledger.schema", "unexpected or missing ledger schema"))

    manifest_path = root / ledger.get("source_manifest", "")
    manifest = None
    if not manifest_path.exists():
        issues.append(LedgerIssue("error", "ledger.source_manifest_missing", str(manifest_path)))
    else:
        manifest = load_json(manifest_path)
        source_key = ledger.get("source_key")
        sources = manifest.get("sources", {})
        if source_key not in sources:
            issues.append(LedgerIssue("error", "ledger.source_key_missing", f"{source_key!r} not present in manifest"))
        elif sources[source_key].get("effective_date") != ledger.get("source_effective_date"):
            issues.append(LedgerIssue(
                "error",
                "ledger.effective_date_mismatch",
                f"ledger={ledger.get('source_effective_date')} manifest={sources[source_key].get('effective_date')}",
            ))

    rules = ledger.get("rules", [])
    if not isinstance(rules, list) or not rules:
        issues.append(LedgerIssue("error", "ledger.rules_empty", "rules array is empty or invalid"))
        rules = []

    seen: set[str] = set()
    status_counts: Counter[str] = Counter()
    tests_by_rule: dict[str, list[str]] = {}
    component_to_rules: defaultdict[str, list[str]] = defaultdict(list)

    for index, rule in enumerate(rules):
        prefix = f"rules[{index}]"
        rule_id = str(rule.get("rule_id", ""))
        status = str(rule.get("status", ""))
        tests = rule.get("tests", [])
        component = str(rule.get("component", ""))
        status_counts[status] += 1

        if not RULE_ID_RE.match(rule_id):
            issues.append(LedgerIssue("error", "rule_id.format", f"{prefix} has invalid rule_id={rule_id!r}"))
        if rule_id in seen:
            issues.append(LedgerIssue("error", "rule_id.duplicate", f"duplicate rule_id={rule_id}"))
        seen.add(rule_id)

        if status not in ALLOWED_STATUSES:
            issues.append(LedgerIssue("error", "status.invalid", f"{rule_id} has invalid status={status!r}"))
        if status in {"implemented", "tested", "scaffold"} and not component:
            issues.append(LedgerIssue("error", "component.missing", f"{rule_id} status={status} needs component"))
        if status == "tested" and not tests:
            issues.append(LedgerIssue("error", "tests.missing", f"{rule_id} is tested but has no tests"))
        if tests and not isinstance(tests, list):
            issues.append(LedgerIssue("error", "tests.invalid", f"{rule_id} tests must be a list"))
            tests = []
        for test_ref in tests:
            if not isinstance(test_ref, str):
                issues.append(LedgerIssue("error", "test_ref.invalid", f"{rule_id} has non-string test ref"))
                continue
            if not test_path_exists(test_ref):
                issues.append(LedgerIssue("error", "test_ref.path_missing", f"{rule_id}: {test_ref}"))
            elif not symbol_exists(test_ref):
                issues.append(LedgerIssue("warning", "test_ref.symbol_missing", f"{rule_id}: {test_ref}"))
        tests_by_rule[rule_id] = list(tests)
        if component:
            component_to_rules[component].append(rule_id)

    required_inventory = ["100-123", "200-213", "300-315", "400-408", "500-514", "600-616", "700-733", "800-811", "900-905", "Glossary"]
    for rule_id in required_inventory:
        if rule_id not in seen:
            issues.append(LedgerIssue("error", "inventory.missing_top_level", f"missing top-level inventory bucket {rule_id}"))

    implemented_like = sum(status_counts[s] for s in ("scaffold", "implemented", "tested"))
    tested = status_counts["tested"]
    report = {
        "schema": "mtgsim.rules_coverage_report.v1",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "duration_sec": time.perf_counter() - started,
        "ledger": str(ledger_path.relative_to(root)),
        "revision": ledger.get("revision"),
        "source_effective_date": ledger.get("source_effective_date"),
        "summary": {
            "rules_total": len(rules),
            "statuses": dict(sorted(status_counts.items())),
            "implemented_or_scaffolded": implemented_like,
            "tested": tested,
            "tests_linked": sum(len(v) for v in tests_by_rule.values()),
            "issues": len(issues),
            "errors": sum(1 for issue in issues if issue.severity == "error"),
            "warnings": sum(1 for issue in issues if issue.severity == "warning"),
        },
        "issues": [asdict(issue) for issue in issues],
        "tests_by_rule": tests_by_rule,
        "component_to_rules": dict(component_to_rules),
    }
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=pathlib.Path, default=LEDGER)
    parser.add_argument("--report", type=pathlib.Path, default=REPORT_DIR / "rule_coverage_report_latest.json")
    parser.add_argument("--json", action="store_true", help="Print full JSON report.")
    args = parser.parse_args(argv)

    report = check_ledger(ROOT, args.ledger)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    append_jsonl(REPORT_DIR / "rule_coverage_history.jsonl", compact_history_record(report, args.report))

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        summary = report["summary"]
        print(
            "rule coverage: "
            f"rules={summary['rules_total']} tested={summary['tested']} "
            f"implemented_or_scaffolded={summary['implemented_or_scaffolded']} "
            f"errors={summary['errors']} warnings={summary['warnings']} "
            f"report={args.report.relative_to(ROOT)}"
        )
        for issue in report["issues"][:20]:
            print(f"{issue['severity'].upper()} {issue['code']}: {issue['detail']}")
    return 1 if report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
