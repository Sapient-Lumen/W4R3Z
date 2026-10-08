#!/usr/bin/env python3
"""Validate every declared SQLite database/WAL poem without opening originals.

Historical v1 line-table artifacts and v2 relational artifacts are validated on
disposable read-only copies. V3 relational artifacts additionally declare an
exhaustive state contract covering every user table in both persistent states.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sqlite3
import sys
import tempfile
from pathlib import Path
from typing import Any

SPEC_V1 = "llmpoetry-sqlite-wal-poem-spec-v1"
SPEC_V2 = "llmpoetry-sqlite-wal-poem-spec-v2"
SPEC_V3 = "llmpoetry-sqlite-wal-poem-spec-v3"
RELATIONAL_SCHEMAS = {SPEC_V2, SPEC_V3}
SPEC_SCHEMAS = {SPEC_V1, *RELATIONAL_SCHEMAS}
RECEIPT_SCHEMAS = {
    "llmpoetry-sqlite-wal-poem-receipt-v1",
    "llmpoetry-sqlite-wal-poem-receipt-v2",
    "llmpoetry-sqlite-wal-poem-receipt-v3",
    "llmpoetry-sqlite-wal-poem-receipt-v4",
}


def add(checks: list[dict], name: str, ok: bool, detail: object = "") -> None:
    checks.append({"name": name, "ok": bool(ok), "detail": "" if detail is None else str(detail)})


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def surface(lines: list[str]) -> str:
    return "\n".join(lines).rstrip() + "\n"


def poem_body(raw: str) -> str:
    if "## Poem" not in raw or "## Disclosure" not in raw:
        return ""
    return raw.split("## Poem", 1)[1].split("## Disclosure", 1)[0].strip("\n") + "\n"


def query_rows(con: sqlite3.Connection, query: str) -> list[list[Any]]:
    return [list(row) for row in con.execute(query)]


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def canonical_table_query(con: sqlite3.Connection, table: str, order_by: list[str]) -> str:
    xinfo = list(con.execute(f"PRAGMA table_xinfo({quote_identifier(table)})"))
    if not xinfo:
        raise ValueError(f"state-contract table does not exist: {table!r}")
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
    state_contract: list[dict[str, Any]],
) -> tuple[dict[str, list[list[Any]]], dict[str, str]]:
    results: dict[str, list[list[Any]]] = {}
    queries: dict[str, str] = {}
    for item in state_contract:
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


def read_state(
    db_path: Path,
    wal_path: Path | None,
    query: str,
    assertions: list[dict[str, Any]],
    state_contract: list[dict[str, Any]],
) -> tuple[list[str], dict[str, list[list[Any]]], dict[str, list[list[Any]]], dict[str, str], dict[str, bool], str, list[dict[str, str]]]:
    with tempfile.TemporaryDirectory(prefix="llmpoetry-wal-check-") as td:
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
            semantics = {
                str(a["name"]): query_rows(con, str(a["query"]))
                for a in assertions
            }
            contracted_state, contract_queries = contract_results(con, state_contract)
            integrity = str(con.execute("PRAGMA integrity_check").fetchone()[0])
            schema_objects = [
                {"type": str(row[0]), "name": str(row[1]), "table": str(row[2])}
                for row in con.execute(
                    "SELECT type,name,tbl_name FROM sqlite_schema "
                    "WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"
                )
            ]
        finally:
            con.close()
        byte_integrity = {
            "database_unchanged": sha256_file(temp_db) == db_before,
            "wal_unchanged": (wal_before is None and not temp_wal.exists()) or (
                wal_before is not None and temp_wal.exists() and sha256_file(temp_wal) == wal_before
            ),
        }
        return rows, semantics, contracted_state, contract_queries, byte_integrity, integrity, schema_objects


def discover_specs(root: Path) -> list[Path]:
    return sorted(root.glob("poems/P[0-9][0-9][0-9][0-9]/artifact/**/WAL_POEM_SPEC*.json"))


def check_spec(root: Path, spec_path: Path, state: dict[str, Any]) -> list[dict]:
    checks: list[dict] = []
    rel_spec = spec_path.relative_to(root).as_posix()
    prefix = f"wal_poem:{rel_spec}:"
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except Exception as exc:
        add(checks, prefix + "spec_json", False, exc)
        return checks
    spec_schema = spec.get("schema")
    add(checks, prefix + "spec_schema", spec_schema in SPEC_SCHEMAS, spec_schema)
    common = (
        "poem_id", "draft_id", "draft_path", "database_path", "wal_path",
        "receipt_path", "base_surface_path", "committed_surface_path",
        "base_lines", "committed_lines",
    )
    required = list(common)
    if spec_schema == SPEC_V1:
        required.append("transition_mode")
    elif spec_schema in RELATIONAL_SCHEMAS:
        required.extend(("schema_sql", "base_sql", "transition_sql", "read_query", "semantic_assertions"))
        if spec_schema == SPEC_V3:
            required.append("state_contract")
    missing = [k for k in required if k not in spec]
    add(checks, prefix + "spec_required_keys", not missing, missing)
    if missing or spec_schema not in SPEC_SCHEMAS:
        return checks

    paths = {key: root / spec[key] for key in (
        "draft_path", "database_path", "wal_path", "receipt_path",
        "base_surface_path", "committed_surface_path",
    )}
    for key, path in paths.items():
        add(checks, prefix + f"path_exists:{key}", path.exists(), path.relative_to(root) if path.exists() else path)
    if not all(path.exists() for path in paths.values()):
        return checks

    try:
        receipt = json.loads(paths["receipt_path"].read_text(encoding="utf-8"))
    except Exception as exc:
        add(checks, prefix + "receipt_json", False, exc)
        return checks
    draft_id = str(spec["draft_id"])
    is_current = draft_id == state.get("current_head")
    add(checks, prefix + "receipt_schema", receipt.get("schema") in RECEIPT_SCHEMAS, receipt.get("schema"))
    add(checks, prefix + "receipt_identity", receipt.get("draft_id") == draft_id and receipt.get("poem_id") == spec.get("poem_id"), receipt.get("draft_id"))
    add(checks, prefix + "receipt_paths", receipt.get("main_database") == spec["database_path"] and receipt.get("wal_sidecar") == spec["wal_path"], f"{receipt.get('main_database')} {receipt.get('wal_sidecar')}")
    if receipt.get("schema") in {"llmpoetry-sqlite-wal-poem-receipt-v2", "llmpoetry-sqlite-wal-poem-receipt-v3", "llmpoetry-sqlite-wal-poem-receipt-v4"}:
        add(checks, prefix + "receipt_spec_path", receipt.get("spec_path") == rel_spec, receipt.get("spec_path"))
        add(checks, prefix + "receipt_spec_hash", receipt.get("spec_sha256") == sha256_file(spec_path), receipt.get("spec_sha256"))
    if receipt.get("schema") in {"llmpoetry-sqlite-wal-poem-receipt-v3", "llmpoetry-sqlite-wal-poem-receipt-v4"}:
        add(checks, prefix + "receipt_spec_schema", receipt.get("spec_schema") == spec_schema, receipt.get("spec_schema"))
        expected_mode = "relational_sql" if spec_schema in RELATIONAL_SCHEMAS else "poem_lines"
        add(checks, prefix + "receipt_storage_mode", receipt.get("storage_mode") == expected_mode, receipt.get("storage_mode"))
        if spec_schema in RELATIONAL_SCHEMAS:
            compat = receipt.get("runtime_compatibility") or {}
            profile = receipt.get("execution_profile") or {}
            add(checks, prefix + "generated_columns_runtime_supported", sqlite3.sqlite_version_info >= (3, 31, 0) and compat.get("generated_columns_supported") is True, {"runtime": sqlite3.sqlite_version, "receipt": compat})
            add(checks, prefix + "single_connection_no_checkpoint_race_profile", profile.get("database_connections_during_build") == 1 and profile.get("concurrent_writers") == 0 and profile.get("checkpoint_during_committed_transition") is False and profile.get("wal_autocheckpoint") == 0 and profile.get("wal_reset_race_trigger_exercised") is False, profile)
    current_review = None
    current_review_rel = state.get("current_judgment") if is_current else None
    if isinstance(current_review_rel, str) and (root / current_review_rel).exists():
        try:
            current_review = json.loads((root / current_review_rel).read_text(encoding="utf-8"))
        except Exception:
            current_review = None
    if is_current and isinstance(current_review, dict):
        # Later-turn review freezes the creation-time artifact.  Its receipt should
        # remain tied to the reviewed target revision, not be rewritten to the cube's
        # current routing revision.
        target_revision = current_review.get("target_created_revision") or current_review.get("reviewed_revision")
        add(checks, prefix + "current_review_targets_artifact", current_review.get("draft_id") == draft_id and target_revision == receipt.get("revision") == spec.get("revision"), {"target": target_revision, "receipt": receipt.get("revision"), "spec": spec.get("revision")})
        add(checks, prefix + "current_review_is_later_turn", int(current_review.get("created_turn", 0)) > int(receipt.get("turn", 0)), {"review": current_review.get("created_turn"), "artifact": receipt.get("turn")})
    else:
        add(checks, prefix + "current_receipt_revision", not is_current or receipt.get("revision") == state.get("revision"), receipt.get("revision"))
    add(checks, prefix + "main_hash", sha256_file(paths["database_path"]) == receipt.get("main_sha256_before_commit") == receipt.get("main_sha256_after_commit"), receipt.get("main_sha256_after_commit"))
    add(checks, prefix + "wal_hash", sha256_file(paths["wal_path"]) == receipt.get("wal_sha256"), receipt.get("wal_sha256"))
    add(checks, prefix + "surface_hashes", sha256_file(paths["base_surface_path"]) == receipt.get("base_surface_sha256") and sha256_file(paths["committed_surface_path"]) == receipt.get("committed_surface_sha256"), "base/committed")
    add(checks, prefix + "main_unchanged", receipt.get("main_bytes_unchanged_before_checkpoint") is True, receipt.get("main_bytes_unchanged_before_checkpoint"))
    add(checks, prefix + "wal_nonempty", paths["wal_path"].stat().st_size > 32 and int(receipt.get("wal_frame_count", 0)) >= 1, paths["wal_path"].stat().st_size)
    add(checks, prefix + "quality_claims_empty", receipt.get("quality_claims") == [], receipt.get("quality_claims"))

    assertions = list(spec.get("semantic_assertions") or [])
    assertion_names = [str(a.get("name") or "") for a in assertions]
    add(checks, prefix + "assertion_names_valid", len(assertion_names) == len(set(assertion_names)) and all(assertion_names), assertion_names)
    state_contract = list(spec.get("state_contract") or [])
    contract_tables = [str(item.get("table") or "") for item in state_contract]
    contract_orders = [item.get("order_by") for item in state_contract]
    contract_shape_ok = (
        len(contract_tables) == len(set(contract_tables))
        and all(contract_tables)
        and all(isinstance(order, list) and order and all(isinstance(x, str) and x for x in order) for order in contract_orders)
        and all("query" not in item for item in state_contract)
        and all("expected_base" in item and "expected_committed" in item for item in state_contract)
    )
    add(checks, prefix + "state_contract_keys_valid", contract_shape_ok if spec_schema == SPEC_V3 else not state_contract, contract_tables)
    query = str(spec.get("read_query") or "SELECT text FROM poem_lines ORDER BY slot")
    try:
        observed_base, semantic_base, state_base, base_contract_queries, base_integrity, base_integrity_check, base_schema = read_state(
            paths["database_path"], None, query, assertions, state_contract
        )
        observed_committed, semantic_committed, state_committed, committed_contract_queries, pair_integrity, pair_integrity_check, pair_schema = read_state(
            paths["database_path"], paths["wal_path"], query, assertions, state_contract
        )
    except Exception as exc:
        add(checks, prefix + "read_states", False, exc)
        return checks

    expected_base = [str(x) for x in spec["base_lines"]]
    expected_committed = [str(x) for x in spec["committed_lines"]]
    add(checks, prefix + "base_read", observed_base == expected_base == receipt.get("base_lines"), observed_base)
    add(checks, prefix + "paired_read", observed_committed == expected_committed == receipt.get("committed_lines"), observed_committed)
    add(checks, prefix + "sidecar_changes_reading", observed_base != observed_committed, f"base={len(observed_base)} committed={len(observed_committed)}")
    add(checks, prefix + "read_only_copy_integrity", all(base_integrity.values()) and all(pair_integrity.values()), {"base": base_integrity, "pair": pair_integrity})
    add(checks, prefix + "sqlite_integrity_check", base_integrity_check == "ok" and pair_integrity_check == "ok", f"base={base_integrity_check} pair={pair_integrity_check}")
    add(checks, prefix + "schema_stable_across_wal", base_schema == pair_schema, {"base": base_schema, "pair": pair_schema})
    if receipt.get("schema") in {"llmpoetry-sqlite-wal-poem-receipt-v3", "llmpoetry-sqlite-wal-poem-receipt-v4"}:
        add(checks, prefix + "receipt_schema_objects", receipt.get("schema_objects") == base_schema, receipt.get("schema_objects"))

    semantic_ok = True
    semantic_detail: list[dict[str, Any]] = []
    for assertion in assertions:
        name = str(assertion["name"])
        expected_a = assertion.get("expected_base")
        expected_b = assertion.get("expected_committed")
        observed_a = semantic_base.get(name)
        observed_b = semantic_committed.get(name)
        ok_a = observed_a == expected_a
        ok_b = observed_b == expected_b
        semantic_ok = semantic_ok and ok_a and ok_b
        semantic_detail.append({"name": name, "base": observed_a, "committed": observed_b, "base_ok": ok_a, "committed_ok": ok_b})
    add(checks, prefix + "semantic_assertions", semantic_ok, semantic_detail)
    if spec_schema in RELATIONAL_SCHEMAS:
        add(checks, prefix + "relational_assertions_present", bool(assertions), len(assertions))
        object_types = {x["type"] for x in base_schema}
        add(checks, prefix + "relational_schema_has_table_and_view", {"table", "view"}.issubset(object_types), base_schema)
    if receipt.get("schema") in {"llmpoetry-sqlite-wal-poem-receipt-v3", "llmpoetry-sqlite-wal-poem-receipt-v4"}:
        receipt_assertions = receipt.get("semantic_assertions") or []
        add(checks, prefix + "receipt_semantic_assertions", len(receipt_assertions) == len(assertions) and all(
            r.get("observed_base") == semantic_base.get(r.get("name")) and r.get("observed_committed") == semantic_committed.get(r.get("name"))
            for r in receipt_assertions
        ), receipt_assertions)

    if spec_schema == SPEC_V3:
        add(checks, prefix + "state_contract_query_stability", base_contract_queries == committed_contract_queries, {"base": base_contract_queries, "committed": committed_contract_queries})
        user_tables = sorted(x["name"] for x in base_schema if x["type"] == "table")
        add(checks, prefix + "state_contract_exhaustive", sorted(contract_tables) == user_tables, {"contract": sorted(contract_tables), "schema": user_tables})
        contract_ok = True
        contract_detail: list[dict[str, Any]] = []
        for item in state_contract:
            table = str(item["table"])
            observed_a = state_base.get(table)
            observed_b = state_committed.get(table)
            expected_a = item.get("expected_base")
            expected_b = item.get("expected_committed")
            ok_a = observed_a == expected_a
            ok_b = observed_b == expected_b
            contract_ok = contract_ok and ok_a and ok_b
            contract_detail.append({"table": table, "base": observed_a, "committed": observed_b, "base_ok": ok_a, "committed_ok": ok_b})
        add(checks, prefix + "state_contract_matches", contract_ok, contract_detail)
        if receipt.get("schema") == "llmpoetry-sqlite-wal-poem-receipt-v4":
            receipt_contract = receipt.get("state_contract") or []
            add(checks, prefix + "receipt_state_contract", len(receipt_contract) == len(state_contract) and all(
                r.get("query") == base_contract_queries.get(r.get("table"))
                and r.get("observed_base") == state_base.get(r.get("table"))
                and r.get("observed_committed") == state_committed.get(r.get("table"))
                for r in receipt_contract
            ), receipt_contract)
            changed = [table for table in contract_tables if state_base.get(table) != state_committed.get(table)]
            unchanged = [table for table in contract_tables if state_base.get(table) == state_committed.get(table)]
            add(checks, prefix + "receipt_state_delta_summary", receipt.get("state_delta_summary") == {"changed_tables": changed, "unchanged_tables": unchanged} and receipt.get("state_contract_exhaustive") is True, receipt.get("state_delta_summary"))

    add(checks, prefix + "base_surface", paths["base_surface_path"].read_text(encoding="utf-8") == surface(observed_base), spec["base_surface_path"])
    committed_text = surface(observed_committed)
    add(checks, prefix + "committed_surface", paths["committed_surface_path"].read_text(encoding="utf-8") == committed_text, spec["committed_surface_path"])
    raw_draft = paths["draft_path"].read_text(encoding="utf-8")
    add(checks, prefix + "draft_body", poem_body(raw_draft) == committed_text, spec["draft_path"])
    add(checks, prefix + "disclosure_pair", Path(spec["database_path"]).name in raw_draft and Path(spec["wal_path"]).name in raw_draft and "machine-drafted" in raw_draft, spec["draft_path"])

    if is_current:
        suffix = draft_id.rsplit("D", 1)[-1]
        judgment_dir = root / f"poems/{spec['poem_id']}/judgments"
        current_reviews = [p for p in judgment_dir.glob(f"cold_review_*_on_D{suffix}.json")]
        if current_reviews:
            review_paths = {p.relative_to(root).as_posix() for p in current_reviews}
            add(checks, prefix + "current_later_turn_review_routed", isinstance(current_review_rel, str) and current_review_rel in review_paths and isinstance(current_review, dict), sorted(review_paths))
            add(checks, prefix + "current_review_firewall", isinstance(current_review, dict) and current_review.get("firewall_ok") is True and int(current_review.get("created_turn", 0)) > int(current_review.get("target_created_turn", 0)), current_review_rel)
            add(checks, prefix + "current_frozen_lineage_declared", (state.get("current_posture") or {}).get("lineage_frozen") is True, state.get("current_posture"))
        else:
            add(checks, prefix + "current_same_turn_unjudged", "same-turn unjudged" in raw_draft, current_reviews)
    else:
        add(checks, prefix + "historical_not_required_same_turn", True, draft_id)
    return checks


def run(root: Path) -> list[dict]:
    checks: list[dict] = []
    state_path = root / "STATE.json"
    if not state_path.exists():
        add(checks, "wal_poem_state_exists", False, state_path)
        return checks
    state = json.loads(state_path.read_text(encoding="utf-8"))
    specs = discover_specs(root)
    add(checks, "wal_poem_specs_present", bool(specs), len(specs))
    current_head = state.get("current_head")
    declared_ids: list[str] = []
    for spec_path in specs:
        try:
            declared_ids.append(json.loads(spec_path.read_text(encoding="utf-8")).get("draft_id"))
        except Exception:
            pass
        checks.extend(check_spec(root, spec_path, state))
    current_family_has_wal = any(str(current_head).startswith(str(did).split("-D", 1)[0] + "-D") for did in declared_ids if did)
    add(
        checks,
        "wal_poem_current_head_declared_or_other_artifact_family",
        (current_head in declared_ids) if current_family_has_wal else True,
        f"head={current_head} specs={declared_ids}",
    )
    shm_files = [p.relative_to(root).as_posix() for p in root.glob("poems/**/**/*-shm") if p.is_file()]
    add(checks, "wal_poem_no_packaged_shm", not shm_files, shm_files)
    return checks


def main(root: str = ".") -> int:
    checks = run(Path(root))
    ok = all(c.get("ok") for c in checks)
    print(json.dumps({"ok": ok, "check_count": len(checks), "checks": checks, "failed": [c for c in checks if not c.get("ok")]}, indent=2, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "."))
