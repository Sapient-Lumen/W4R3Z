#!/usr/bin/env python3
"""Build a draft-specific SQLite database + WAL poem from a declarative spec.

Three spec generations are supported:

* v1 keeps the historical ``poem_lines`` transition used by P0003-D001/D002.
* v2 allows a relational schema, explicit base/transition SQL, a rendering query,
  and semantic assertions that must differ correctly between the database alone
  and the database/WAL pair.
* v3 adds an exhaustive table-state contract. Every user table must be named;
  the tool snapshots all of its columns and rows in primary-key order and matches
  those canonical states before and after the WAL is applied.

The command has no implicit current target. It builds in temporary storage,
checkpoints the base state, commits the successor state into WAL, copies the
persistent database/WAL pair while the writer remains open, and validates only
disposable read-only copies.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Iterable

SPEC_V1 = "llmpoetry-sqlite-wal-poem-spec-v1"
SPEC_V2 = "llmpoetry-sqlite-wal-poem-spec-v2"
SPEC_V3 = "llmpoetry-sqlite-wal-poem-spec-v3"
RELATIONAL_SCHEMAS = {SPEC_V2, SPEC_V3}
SPEC_SCHEMAS = {SPEC_V1, *RELATIONAL_SCHEMAS}
RECEIPT_SCHEMA = "llmpoetry-sqlite-wal-poem-receipt-v4"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def surface(lines: list[str]) -> str:
    return "\n".join(lines).rstrip() + "\n"


def load_spec(root: Path, rel: str) -> tuple[Path, dict[str, Any]]:
    spec_path = root / rel
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    schema = spec.get("schema")
    if schema not in SPEC_SCHEMAS:
        raise ValueError(f"unsupported spec schema: {schema!r}")
    common = (
        "poem_id", "draft_id", "title", "draft_path", "database_path",
        "wal_path", "receipt_path", "base_surface_path",
        "committed_surface_path", "base_lines", "committed_lines",
    )
    missing = [key for key in common if key not in spec]
    if schema == SPEC_V1 and "transition_mode" not in spec:
        missing.append("transition_mode")
    if schema in RELATIONAL_SCHEMAS:
        for key in ("schema_sql", "base_sql", "transition_sql", "read_query", "semantic_assertions"):
            if key not in spec:
                missing.append(key)
    if schema == SPEC_V3 and "state_contract" not in spec:
        missing.append("state_contract")
    if missing:
        raise ValueError(f"missing spec fields: {sorted(set(missing))}")
    if not isinstance(spec["base_lines"], list) or not isinstance(spec["committed_lines"], list):
        raise ValueError("base_lines and committed_lines must be lists")
    for key in ("schema_sql", "base_sql", "transition_sql"):
        if key in spec and not isinstance(spec[key], list):
            raise ValueError(f"{key} must be a list of SQL statements")
    if "semantic_assertions" in spec and not isinstance(spec["semantic_assertions"], list):
        raise ValueError("semantic_assertions must be a list")
    if "state_contract" in spec and not isinstance(spec["state_contract"], list):
        raise ValueError("state_contract must be a list")
    if schema == SPEC_V3:
        for item in spec["state_contract"]:
            if not isinstance(item, dict) or not str(item.get("table") or "").strip():
                raise ValueError("each v3 state-contract item requires a table")
            if not isinstance(item.get("order_by"), list) or not item["order_by"]:
                raise ValueError("each v3 state-contract item requires a non-empty order_by list")
            if "query" in item:
                raise ValueError("v3 state-contract queries are tool-generated; use table and order_by only")
            if "expected_base" not in item or "expected_committed" not in item:
                raise ValueError("each v3 state-contract item requires expected_base and expected_committed")
    return spec_path, spec


def execute_batch(con: sqlite3.Connection, statements: Iterable[str]) -> None:
    for statement in statements:
        sql = str(statement).strip()
        if sql:
            con.execute(sql)


def apply_line_transition(con: sqlite3.Connection, base: list[str], committed: list[str], mode: str) -> dict[str, Any]:
    updated: list[int] = []
    appended: list[int] = []
    deleted: list[int] = []
    if mode == "legacy_delete_then_insert":
        con.execute("DELETE FROM poem_lines")
        deleted = list(range(1, len(base) + 1))
        con.executemany("INSERT INTO poem_lines(slot,text) VALUES (?,?)", enumerate(committed, 1))
        appended = list(range(1, len(committed) + 1))
    elif mode == "update_then_append":
        if len(committed) < len(base):
            raise ValueError("update_then_append requires committed_lines to be at least as long as base_lines")
        for slot, (before, after) in enumerate(zip(base, committed), 1):
            if before != after:
                con.execute("UPDATE poem_lines SET text=? WHERE slot=?", (after, slot))
                updated.append(slot)
        for slot in range(len(base) + 1, len(committed) + 1):
            con.execute("INSERT INTO poem_lines(slot,text) VALUES (?,?)", (slot, committed[slot - 1]))
            appended.append(slot)
    else:
        raise ValueError(f"unsupported transition_mode: {mode!r}")
    return {
        "mode": mode,
        "updated_slots": updated,
        "appended_slots": appended,
        "deleted_slots": deleted,
        "updated_count": len(updated),
        "appended_count": len(appended),
        "deleted_count": len(deleted),
    }


def query_rows(con: sqlite3.Connection, query: str) -> list[list[Any]]:
    return [list(row) for row in con.execute(query)]


def assertion_results(con: sqlite3.Connection, assertions: list[dict[str, Any]]) -> dict[str, list[list[Any]]]:
    results: dict[str, list[list[Any]]] = {}
    for assertion in assertions:
        name = str(assertion.get("name") or "").strip()
        query = str(assertion.get("query") or "").strip()
        if not name or not query:
            raise ValueError("each semantic assertion requires name and query")
        if name in results:
            raise ValueError(f"duplicate semantic assertion name: {name}")
        results[name] = query_rows(con, query)
    return results


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def canonical_table_query(con: sqlite3.Connection, table: str, order_by: list[str]) -> str:
    """Build a full-row query whose ordering is exactly the table primary key."""
    xinfo = list(con.execute(f"PRAGMA table_xinfo({quote_identifier(table)})"))
    if not xinfo:
        raise ValueError(f"state-contract table does not exist: {table!r}")
    # Hidden virtual-table implementation columns (hidden=1) are not part of
    # SELECT *; generated columns (hidden=2/3) are visible and are included.
    columns = [str(row[1]) for row in xinfo if int(row[6]) != 1]
    primary_key = [str(row[1]) for row in sorted((r for r in xinfo if int(r[5]) > 0), key=lambda r: int(r[5]))]
    if not primary_key:
        raise ValueError(f"v3 state-contract table requires a primary key: {table!r}")
    if order_by != primary_key:
        raise ValueError(
            f"state-contract order_by must equal primary-key order for {table!r}: "
            f"declared={order_by!r} primary_key={primary_key!r}"
        )
    selected = ", ".join(quote_identifier(c) for c in columns)
    ordering = ", ".join(quote_identifier(c) for c in order_by)
    return f"SELECT {selected} FROM {quote_identifier(table)} ORDER BY {ordering}"


def contract_results(
    con: sqlite3.Connection,
    contract: list[dict[str, Any]],
) -> tuple[dict[str, list[list[Any]]], dict[str, str]]:
    results: dict[str, list[list[Any]]] = {}
    queries: dict[str, str] = {}
    for item in contract:
        table = str(item.get("table") or "").strip()
        order_by = [str(x) for x in item.get("order_by", [])]
        if not table or not order_by:
            raise ValueError("each state-contract item requires table and non-empty order_by")
        if table in results:
            raise ValueError(f"duplicate state-contract table: {table}")
        query = canonical_table_query(con, table, order_by)
        results[table] = query_rows(con, query)
        queries[table] = query
    return results, queries


def read_snapshot(
    db_path: Path,
    wal_path: Path | None,
    query: str,
    assertions: list[dict[str, Any]],
    state_contract: list[dict[str, Any]],
) -> tuple[list[str], dict[str, list[list[Any]]], dict[str, list[list[Any]]], dict[str, str], dict[str, bool], str]:
    """Read disposable copies and report whether copied persistent bytes changed."""
    with tempfile.TemporaryDirectory(prefix="llmpoetry-wal-read-") as td:
        td_path = Path(td)
        temp_db = td_path / db_path.name
        shutil.copy2(db_path, temp_db)
        temp_wal = Path(str(temp_db) + "-wal")
        if wal_path is not None:
            shutil.copy2(wal_path, temp_wal)
        db_before = sha256_file(temp_db)
        wal_before = sha256_file(temp_wal) if temp_wal.exists() else None
        uri = f"file:{temp_db}?mode=ro" if wal_path is not None else f"file:{temp_db}?mode=ro&immutable=1"
        con = sqlite3.connect(uri, uri=True)
        try:
            con.execute("PRAGMA query_only=ON")
            rows = [str(row[0]) for row in con.execute(query)]
            semantics = assertion_results(con, assertions)
            contracted_state, contract_queries = contract_results(con, state_contract)
            integrity_check = str(con.execute("PRAGMA integrity_check").fetchone()[0])
        finally:
            con.close()
        db_unchanged = sha256_file(temp_db) == db_before
        wal_unchanged = (wal_before is None and not temp_wal.exists()) or (
            wal_before is not None and temp_wal.exists() and sha256_file(temp_wal) == wal_before
        )
        return rows, semantics, contracted_state, contract_queries, {
            "database_unchanged": db_unchanged,
            "wal_unchanged": wal_unchanged,
        }, integrity_check


def verify_semantics(
    assertions: list[dict[str, Any]],
    base_results: dict[str, list[list[Any]]],
    committed_results: dict[str, list[list[Any]]],
) -> list[dict[str, Any]]:
    verified: list[dict[str, Any]] = []
    for assertion in assertions:
        name = str(assertion["name"])
        expected_base = assertion.get("expected_base")
        expected_committed = assertion.get("expected_committed")
        observed_base = base_results[name]
        observed_committed = committed_results[name]
        if observed_base != expected_base:
            raise RuntimeError(f"semantic assertion {name!r} base mismatch: {observed_base!r} != {expected_base!r}")
        if observed_committed != expected_committed:
            raise RuntimeError(
                f"semantic assertion {name!r} committed mismatch: {observed_committed!r} != {expected_committed!r}"
            )
        verified.append({
            "name": name,
            "query": assertion["query"],
            "expected_base": expected_base,
            "expected_committed": expected_committed,
            "observed_base": observed_base,
            "observed_committed": observed_committed,
        })
    return verified


def verify_state_contract(
    contract: list[dict[str, Any]],
    base_results: dict[str, list[list[Any]]],
    committed_results: dict[str, list[list[Any]]],
    queries: dict[str, str],
) -> tuple[list[dict[str, Any]], dict[str, list[str]]]:
    verified: list[dict[str, Any]] = []
    changed: list[str] = []
    unchanged: list[str] = []
    for item in contract:
        table = str(item["table"])
        observed_base = base_results[table]
        observed_committed = committed_results[table]
        expected_base = item.get("expected_base")
        expected_committed = item.get("expected_committed")
        if observed_base != expected_base:
            raise RuntimeError(f"state contract {table!r} base mismatch: {observed_base!r} != {expected_base!r}")
        if observed_committed != expected_committed:
            raise RuntimeError(
                f"state contract {table!r} committed mismatch: {observed_committed!r} != {expected_committed!r}"
            )
        (changed if observed_base != observed_committed else unchanged).append(table)
        verified.append({
            "table": table,
            "query": queries[table],
            "expected_base": expected_base,
            "expected_committed": expected_committed,
            "observed_base": observed_base,
            "observed_committed": observed_committed,
        })
    return verified, {"changed_tables": changed, "unchanged_tables": unchanged}


def build(root: Path, spec_rel: str, revision: str, turn: int, created_at: str) -> dict[str, Any]:
    spec_path, spec = load_spec(root, spec_rel)
    spec_schema = str(spec["schema"])
    if spec_schema in RELATIONAL_SCHEMAS and sqlite3.sqlite_version_info < (3, 31, 0):
        raise RuntimeError(
            f"relational WAL specs with generated columns require SQLite >= 3.31.0; runtime={sqlite3.sqlite_version}"
        )
    base = [str(x) for x in spec["base_lines"]]
    committed = [str(x) for x in spec["committed_lines"]]
    query = str(spec.get("read_query") or "SELECT text FROM poem_lines ORDER BY slot")
    assertions = list(spec.get("semantic_assertions") or [])
    state_contract = list(spec.get("state_contract") or [])

    final_db = root / spec["database_path"]
    final_wal = root / spec["wal_path"]
    final_receipt = root / spec["receipt_path"]
    base_surface = root / spec["base_surface_path"]
    committed_surface = root / spec["committed_surface_path"]
    for path in (final_db, final_wal, final_receipt, base_surface, committed_surface):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.unlink(missing_ok=True)

    with tempfile.TemporaryDirectory(prefix="llmpoetry-wal-build-") as td:
        work_db = Path(td) / final_db.name
        con = sqlite3.connect(work_db)
        try:
            con.execute("PRAGMA page_size=4096")
            journal_mode = con.execute("PRAGMA journal_mode=WAL").fetchone()[0]
            con.execute("PRAGMA wal_autocheckpoint=0")
            con.execute("PRAGMA foreign_keys=ON")
            con.execute("PRAGMA application_id=1280068944")
            con.execute(f"PRAGMA user_version={int(spec.get('user_version', 1))}")

            if spec_schema == SPEC_V1:
                con.execute("CREATE TABLE poem_lines(slot INTEGER PRIMARY KEY, text TEXT NOT NULL)")
                con.executemany("INSERT INTO poem_lines(slot,text) VALUES (?,?)", enumerate(base, 1))
            else:
                execute_batch(con, spec["schema_sql"])
                execute_batch(con, spec["base_sql"])

            con.commit()
            checkpoint = con.execute("PRAGMA wal_checkpoint(TRUNCATE)").fetchone()
            main_hash_before = sha256_file(work_db)
            main_size_before = work_db.stat().st_size
            changes_before = con.total_changes

            if spec_schema == SPEC_V1:
                logical_transition = apply_line_transition(con, base, committed, str(spec["transition_mode"]))
            else:
                execute_batch(con, spec["transition_sql"])
                logical_transition = {
                    "mode": "relational_sql",
                    "statement_count": len(spec["transition_sql"]),
                    "declared": spec.get("transition_summary", {}),
                }
            con.commit()
            logical_transition["sqlite_total_changes"] = con.total_changes - changes_before

            work_wal = Path(str(work_db) + "-wal")
            if not work_wal.exists() or work_wal.stat().st_size <= 32:
                raise RuntimeError("committed WAL sidecar was not produced")
            main_hash_after = sha256_file(work_db)
            if main_hash_after != main_hash_before:
                raise RuntimeError("main database changed before checkpoint; WAL invariant failed")
            shutil.copy2(work_db, final_db)
            shutil.copy2(work_wal, final_wal)
            page_size = int(con.execute("PRAGMA page_size").fetchone()[0])
            schema_objects = [
                {"type": row[0], "name": row[1], "table": row[2]}
                for row in con.execute(
                    "SELECT type,name,tbl_name FROM sqlite_schema "
                    "WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"
                )
            ]
        finally:
            con.close()

    observed_base, semantic_base, state_base, base_contract_queries, base_read_integrity, base_integrity_check = read_snapshot(
        final_db, None, query, assertions, state_contract
    )
    observed_committed, semantic_committed, state_committed, committed_contract_queries, pair_read_integrity, pair_integrity_check = read_snapshot(
        final_db, final_wal, query, assertions, state_contract
    )
    if observed_base != base:
        raise RuntimeError(f"base reading mismatch: {observed_base!r}")
    if observed_committed != committed:
        raise RuntimeError(f"committed reading mismatch: {observed_committed!r}")
    if not all(base_read_integrity.values()) or not all(pair_read_integrity.values()):
        raise RuntimeError("read-only disposable validation changed persistent copied bytes")
    if base_integrity_check != "ok" or pair_integrity_check != "ok":
        raise RuntimeError(f"integrity_check failed: base={base_integrity_check!r} pair={pair_integrity_check!r}")
    verified_assertions = verify_semantics(assertions, semantic_base, semantic_committed)
    if base_contract_queries != committed_contract_queries:
        raise RuntimeError("state-contract canonical queries changed between base and committed states")
    user_tables = sorted(x["name"] for x in schema_objects if x["type"] == "table")
    contract_tables = sorted(str(x.get("table") or "") for x in state_contract)
    if spec_schema == SPEC_V3 and contract_tables != user_tables:
        raise RuntimeError(
            f"state contract must cover every user table exactly: contract={contract_tables!r} schema={user_tables!r}"
        )
    verified_contract, state_delta_summary = verify_state_contract(
        state_contract, state_base, state_committed, base_contract_queries
    )

    base_surface.write_text(surface(base), encoding="utf-8")
    committed_surface.write_text(surface(committed), encoding="utf-8")
    wal_bytes = final_wal.read_bytes()
    frame_size = page_size + 24
    frame_count = (len(wal_bytes) - 32) // frame_size if len(wal_bytes) >= 32 else 0

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "spec_schema": spec_schema,
        "spec_path": spec_rel,
        "spec_sha256": sha256_file(spec_path),
        "poem_id": spec["poem_id"],
        "draft_id": spec["draft_id"],
        "title": spec["title"],
        "revision": revision,
        "turn": turn,
        "created_at": created_at,
        "sqlite_runtime_version": sqlite3.sqlite_version,
        "runtime_compatibility": {
            "minimum_for_generated_columns": "3.31.0" if spec_schema in RELATIONAL_SCHEMAS else None,
            "generated_columns_supported": spec_schema not in RELATIONAL_SCHEMAS or sqlite3.sqlite_version_info >= (3, 31, 0),
            "wal_reset_race_note": "SQLite documents a rare concurrent write/checkpoint WAL-reset race in affected runtimes; this build profile uses one connection and performs no checkpoint during the committed transition.",
        },
        "execution_profile": {
            "database_connections_during_build": 1,
            "concurrent_writers": 0,
            "checkpoint_during_committed_transition": False,
            "wal_autocheckpoint": 0,
            "wal_reset_race_trigger_exercised": False,
        },
        "journal_mode": journal_mode,
        "wal_autocheckpoint": 0,
        "foreign_keys": True,
        "checkpoint_before_commit": list(checkpoint),
        "page_size": page_size,
        "main_database": spec["database_path"],
        "wal_sidecar": spec["wal_path"],
        "base_surface": spec["base_surface_path"],
        "committed_surface": spec["committed_surface_path"],
        "draft_path": spec["draft_path"],
        "shared_memory_sidecar_packaged": False,
        "shared_memory_reason": "SQLite documents -shm as non-persistent and recreatable from the WAL.",
        "main_sha256_before_commit": main_hash_before,
        "main_sha256_after_commit": main_hash_after,
        "main_bytes_unchanged_before_checkpoint": main_hash_before == main_hash_after,
        "main_size_bytes": main_size_before,
        "wal_sha256": sha256_file(final_wal),
        "wal_size_bytes": final_wal.stat().st_size,
        "wal_header_magic_hex": wal_bytes[:4].hex(),
        "wal_frame_count": frame_count,
        "base_surface_sha256": sha256_file(base_surface),
        "committed_surface_sha256": sha256_file(committed_surface),
        "base_line_count": len(base),
        "committed_line_count": len(committed),
        "base_lines": base,
        "committed_lines": committed,
        "read_query": query,
        "storage_mode": "relational_sql" if spec_schema in RELATIONAL_SCHEMAS else "poem_lines",
        "schema_objects": schema_objects,
        "logical_transition": logical_transition,
        "semantic_assertions": verified_assertions,
        "state_contract": verified_contract,
        "state_delta_summary": state_delta_summary,
        "state_contract_exhaustive": spec_schema != SPEC_V3 or contract_tables == user_tables,
        "integrity_check": {"base_copy": base_integrity_check, "paired_copy": pair_integrity_check},
        "read_only_validation": {
            "base_copy": base_read_integrity,
            "paired_copy": pair_read_integrity,
            "originals_opened_by_checker": False,
        },
        "formal_claim": spec.get(
            "formal_claim",
            "The database/WAL pair yields a committed reading that differs from the unchanged base database reading.",
        ),
        "destructive_reader_warning": "Inspect disposable copies. Ordinary writable connections can checkpoint or remove a WAL sidecar.",
        "quality_claims": [],
        "non_claim": spec.get(
            "non_claim",
            "This receipt verifies storage-state behavior and byte invariants only; it does not judge poetic quality or external uptake.",
        ),
    }
    final_receipt.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--spec", required=True, help="root-relative WAL poem spec; no implicit current draft")
    ap.add_argument("--revision", required=True)
    ap.add_argument("--turn", required=True, type=int)
    ap.add_argument("--created-at", required=True)
    args = ap.parse_args()
    receipt = build(Path(args.root), args.spec, args.revision, args.turn, args.created_at)
    print(json.dumps({
        "ok": True,
        "draft_id": receipt["draft_id"],
        "wal_frames": receipt["wal_frame_count"],
        "storage_mode": receipt["storage_mode"],
        "transition": receipt["logical_transition"],
        "semantic_assertions": len(receipt["semantic_assertions"]),
        "state_contract_tables": len(receipt.get("state_contract", [])),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
