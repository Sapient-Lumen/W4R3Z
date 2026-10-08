#!/usr/bin/env python3
"""SQLite history store for MTGSim harness/build/test/coverage metrics.

This database is an optimization aid, not a source of truth. JSON/JUnit reports remain
plain files; SQLite makes trend queries cheap and allows future dashboards without
requiring a server process.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sqlite3
import time
from typing import Any

os.environ.setdefault("TZ", "America/New_York")
if hasattr(time, "tzset"):
    time.tzset()

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "reports" / "metrics" / "mtgsim_metrics.sqlite"
SCHEMA_VERSION = 1


def rel(path: pathlib.Path) -> str:
    try:
        return path.resolve().relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def connect(db_path: pathlib.Path = DEFAULT_DB) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA foreign_keys=ON")
    ensure_schema(conn)
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            kind TEXT NOT NULL,
            created_at_local TEXT NOT NULL,
            action TEXT,
            mode TEXT,
            status TEXT NOT NULL,
            duration_sec REAL NOT NULL,
            report_path TEXT,
            payload_json TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS steps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            duration_sec REAL NOT NULL,
            returncode INTEGER,
            command_json TEXT,
            metrics_json TEXT
        );

        CREATE TABLE IF NOT EXISTS test_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            repeat_index INTEGER NOT NULL,
            status TEXT NOT NULL,
            duration_sec REAL NOT NULL,
            returncode INTEGER,
            tags_json TEXT,
            rules_json TEXT,
            message TEXT
        );

        CREATE TABLE IF NOT EXISTS rule_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
            ledger_revision TEXT,
            full_rules_conservative_pct REAL,
            ledger_weighted_pct REAL,
            tested_rows INTEGER,
            total_rows INTEGER
        );

        CREATE INDEX IF NOT EXISTS idx_runs_kind_created ON runs(kind, created_at_local);
        CREATE INDEX IF NOT EXISTS idx_steps_run ON steps(run_id);
        CREATE INDEX IF NOT EXISTS idx_test_cases_run_status ON test_cases(run_id, status);
        CREATE INDEX IF NOT EXISTS idx_rule_progress_run ON rule_progress(run_id);
        """
    )
    conn.execute("INSERT OR REPLACE INTO meta(key, value) VALUES('schema_version', ?)", (str(SCHEMA_VERSION),))
    conn.commit()


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True)


def compact_payload_for_db(kind: str, report: dict[str, Any]) -> dict[str, Any]:
    """Store trend payloads in SQLite and leave full detail in named reports.

    The metrics database is an optimization aid. Keeping complete harness, rule,
    and audit reports in both JSON files and SQLite bloats the shared datacube and
    can make package audits warn about the audit trail itself.
    """
    config = report.get("config", {}) if isinstance(report.get("config"), dict) else {}
    summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
    payload: dict[str, Any] = {
        "schema": "mtgsim.metrics_payload.compact.v1",
        "source_schema": report.get("schema"),
        "kind": kind,
        "created_at_local": report.get("created_at_local") or report.get("started_at_local"),
        "status": report.get("status") or "passed",
        "duration_sec": report.get("duration_sec"),
        "summary": summary,
    }
    if config:
        payload["config"] = {
            "mode": config.get("mode"),
            "jobs": config.get("jobs"),
            "parallelism": config.get("parallelism"),
            "target": config.get("target"),
        }
    if isinstance(report.get("results"), list):
        payload["result_count"] = len(report.get("results", []))
    if isinstance(report.get("issues"), list):
        payload["issue_count"] = len(report.get("issues", []))
    return payload


def insert_run(conn: sqlite3.Connection,
               *,
               kind: str,
               report: dict[str, Any],
               report_path: pathlib.Path | None = None,
               action: str | None = None,
               mode: str | None = None) -> int:
    created = str(report.get("created_at_local") or report.get("started_at_local") or time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    status = str(report.get("status") or "passed")
    duration = float(report.get("duration_sec") or 0.0)
    config = report.get("config", {}) if isinstance(report.get("config"), dict) else {}
    action = action if action is not None else str(report.get("action") or config.get("target") or "")
    mode = mode if mode is not None else str(config.get("mode") or "")
    cursor = conn.execute(
        """
        INSERT INTO runs(kind, created_at_local, action, mode, status, duration_sec, report_path, payload_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (kind, created, action, mode, status, duration, rel(report_path) if report_path else None, _json(compact_payload_for_db(kind, report))),
    )
    return int(cursor.lastrowid)


def record_harness_report(report: dict[str, Any], report_path: pathlib.Path | None = None) -> int:
    with connect() as conn:
        run_id = insert_run(conn, kind="harness", report=report, report_path=report_path)
        for step in report.get("steps", []):
            conn.execute(
                """
                INSERT INTO steps(run_id, name, status, duration_sec, returncode, command_json, metrics_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    str(step.get("name", "")),
                    str(step.get("status", "")),
                    float(step.get("duration_sec") or 0.0),
                    step.get("returncode"),
                    _json(step.get("command", [])),
                    _json(step.get("metrics", {})),
                ),
            )
        conn.commit()
        return run_id


def record_build_report(report: dict[str, Any], report_path: pathlib.Path | None = None) -> int:
    with connect() as conn:
        run_id = insert_run(conn, kind="build", report=report, report_path=report_path)
        for action in report.get("actions", []):
            conn.execute(
                """
                INSERT INTO steps(run_id, name, status, duration_sec, returncode, command_json, metrics_json)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    str(action.get("name", "")),
                    str(action.get("status", "")),
                    float(action.get("duration_sec") or 0.0),
                    action.get("returncode"),
                    _json(action.get("command", [])),
                    _json({"skipped": bool(action.get("skipped", False))}),
                ),
            )
        conn.commit()
        return run_id


def record_cpp_test_report(report: dict[str, Any], report_path: pathlib.Path | None = None) -> int:
    with connect() as conn:
        run_id = insert_run(conn, kind="cpp_tests", report=report, report_path=report_path)
        for result in report.get("results", []):
            conn.execute(
                """
                INSERT INTO test_cases(run_id, name, repeat_index, status, duration_sec, returncode, tags_json, rules_json, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    str(result.get("name", "")),
                    int(result.get("repeat_index") or 0),
                    str(result.get("status", "")),
                    float(result.get("duration_sec") or 0.0),
                    result.get("returncode"),
                    _json(result.get("tags", [])),
                    _json(result.get("rules", [])),
                    str(result.get("message", "")),
                ),
            )
        conn.commit()
        return run_id



def record_scenario_report(report: dict[str, Any], report_path: pathlib.Path | None = None) -> int:
    with connect() as conn:
        run_id = insert_run(conn, kind="scenarios", report=report, report_path=report_path)
        for result in report.get("results", []):
            conn.execute(
                """
                INSERT INTO test_cases(run_id, name, repeat_index, status, duration_sec, returncode, tags_json, rules_json, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    str(result.get("name", "")),
                    0,
                    str(result.get("status", "")),
                    float(result.get("duration_sec") or 0.0),
                    result.get("returncode"),
                    _json(["scenario"]),
                    _json([]),
                    str(result.get("message", "")),
                ),
            )
        conn.commit()
        return run_id


def record_fuzz_report(report: dict[str, Any], report_path: pathlib.Path | None = None) -> int:
    with connect() as conn:
        run_id = insert_run(conn, kind="fuzz", report=report, report_path=report_path)
        for result in report.get("results", []):
            conn.execute(
                """
                INSERT INTO test_cases(run_id, name, repeat_index, status, duration_sec, returncode, tags_json, rules_json, message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    run_id,
                    str(result.get("name", "")),
                    0,
                    str(result.get("status", "")),
                    float(result.get("duration_sec") or 0.0),
                    result.get("returncode"),
                    _json(["fuzz", "actions", "invariants"]),
                    _json(["115", "117", "120", "405", "601", "608", "704"]),
                    str(result.get("message", "")),
                ),
            )
        conn.commit()
        return run_id

def record_rules_progress(report: dict[str, Any], report_path: pathlib.Path | None = None) -> int:
    with connect() as conn:
        run_id = insert_run(conn, kind="rule_progress", report=report, report_path=report_path)
        summary = report.get("summary", {}) if isinstance(report.get("summary"), dict) else {}
        conn.execute(
            """
            INSERT INTO rule_progress(run_id, ledger_revision, full_rules_conservative_pct, ledger_weighted_pct, tested_rows, total_rows)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                run_id,
                str(report.get("ledger_revision", "")),
                float(summary.get("full_rules_conservative_pct") or 0.0),
                float(summary.get("ledger_weighted_pct") or 0.0),
                int(summary.get("tested_rows") or 0),
                int(summary.get("total_rows") or 0),
            ),
        )
        conn.commit()
        return run_id



def case_duration_estimates(db_path: pathlib.Path = DEFAULT_DB, *, min_samples: int = 1) -> dict[str, float]:
    """Return average observed duration per C++ case for shard balancing.

    Missing or corrupt databases intentionally produce an empty map so test
    execution never depends on historical metrics.
    """
    if not db_path.exists():
        return {}
    try:
        with connect(db_path) as conn:
            rows = conn.execute(
                """
                SELECT name, COUNT(*) AS samples, AVG(duration_sec) AS avg_duration_sec
                FROM test_cases
                WHERE status='passed'
                GROUP BY name
                HAVING COUNT(*) >= ?
                """,
                (min_samples,),
            )
            return {str(row["name"]): float(row["avg_duration_sec"] or 0.0) for row in rows}
    except sqlite3.DatabaseError:
        return {}

def summarize(db_path: pathlib.Path = DEFAULT_DB) -> dict[str, Any]:
    with connect(db_path) as conn:
        runs = [dict(row) for row in conn.execute(
            """
            SELECT kind, COUNT(*) AS count, MAX(created_at_local) AS latest, 
                   SUM(CASE WHEN status='passed' THEN 1 ELSE 0 END) AS passed,
                   SUM(CASE WHEN status!='passed' THEN 1 ELSE 0 END) AS not_passed,
                   ROUND(AVG(duration_sec), 6) AS avg_duration_sec
            FROM runs
            GROUP BY kind
            ORDER BY kind
            """
        )]
        slow_steps = [dict(row) for row in conn.execute(
            """
            SELECT name, COUNT(*) AS samples, ROUND(AVG(duration_sec), 6) AS avg_duration_sec, ROUND(MAX(duration_sec), 6) AS max_duration_sec
            FROM steps
            GROUP BY name
            ORDER BY max_duration_sec DESC
            LIMIT 20
            """
        )]
        slow_cases = [dict(row) for row in conn.execute(
            """
            SELECT name, COUNT(*) AS samples, ROUND(AVG(duration_sec), 6) AS avg_duration_sec, ROUND(MAX(duration_sec), 6) AS max_duration_sec
            FROM test_cases
            GROUP BY name
            ORDER BY max_duration_sec DESC
            LIMIT 20
            """
        )]
    return {
        "schema": "mtgsim.metrics_summary.v1",
        "created_at_local": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "database": rel(db_path),
        "runs": runs,
        "slow_steps": slow_steps,
        "slow_cases": slow_cases,
    }


def load_report(path: pathlib.Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "ingest-harness", "ingest-build", "ingest-cpp-tests", "ingest-scenarios", "ingest-fuzz", "ingest-rules-progress", "summary"])
    parser.add_argument("--db", type=pathlib.Path, default=DEFAULT_DB)
    parser.add_argument("--report", type=pathlib.Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.action == "init":
        with connect(args.db):
            pass
        print(f"initialized {rel(args.db)}")
        return 0

    if args.action == "summary":
        result = summarize(args.db)
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"metrics database: {result['database']}")
            for run in result["runs"]:
                print(f"  {run['kind']}: count={run['count']} passed={run['passed']} not_passed={run['not_passed']} avg={run['avg_duration_sec']}s latest={run['latest']}")
        return 0

    if args.report is None:
        raise SystemExit("--report is required for ingest actions")
    report = load_report(args.report)
    if args.action == "ingest-harness":
        run_id = record_harness_report(report, args.report)
    elif args.action == "ingest-build":
        run_id = record_build_report(report, args.report)
    elif args.action == "ingest-cpp-tests":
        run_id = record_cpp_test_report(report, args.report)
    elif args.action == "ingest-scenarios":
        run_id = record_scenario_report(report, args.report)
    elif args.action == "ingest-fuzz":
        run_id = record_fuzz_report(report, args.report)
    elif args.action == "ingest-rules-progress":
        run_id = record_rules_progress(report, args.report)
    else:
        raise AssertionError(args.action)
    print(f"ingested {rel(args.report)} as run_id={run_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
