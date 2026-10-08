#!/usr/bin/env python3
"""Compact negative replay checks for source-role and authority-boundary lint.

The archive lint validates the live tree.  This script mutates representative
rows in memory and confirms the dangerous mutations are detected.  It is kept
small on purpose: the goal is not another registry, but proof that the new typed
controls fail closed for the leakage classes that motivated rev0346-rev0350.
"""
from __future__ import annotations

import copy
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from typing import Any
from source_role_event_utils import source_event_failures_for_row, walk_rev_note_keys
from source_role_credit_cap_policy import evaluate_source_role_credit_cap

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]


def load(rel: str) -> Any:
    return json.loads((ROOT / rel).read_text())


IGNORE_DIR_NAMES = {"__pycache__", ".pytest_cache", ".mypy_cache"}


def ignored_release_path(path: Path) -> bool:
    rel = path.relative_to(ROOT)
    if path.name.endswith(".zip"):
        return True
    return any(part in IGNORE_DIR_NAMES for part in rel.parts)


def copy_release_tree(tmpdir: str) -> Path:
    """Build a lightweight symlink mirror for mutation tests.

    Negative replay needs full-tree reads but only rewrites a few selected files.
    Copying the whole archive for every case is wasteful in cloudtainers, while
    hard-linking is unsafe because writes can alter the source inode.  This mirror
    creates real directories and symlinked files, then the write helper below
    materializes a private copy before any mutation.
    """
    tmp_root = Path(tmpdir) / "cube"
    tmp_root.mkdir(parents=True, exist_ok=True)
    for path in sorted(ROOT.rglob("*")):
        if ignored_release_path(path):
            continue
        rel = path.relative_to(ROOT)
        target = tmp_root / rel
        if path.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif path.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            target.symlink_to(path)
    return tmp_root


def ensure_private_file(path: Path) -> None:
    if not path.is_symlink():
        return
    data = path.read_bytes()
    path.unlink()
    path.write_bytes(data)


def write_text_private(path: Path, text: str) -> None:
    ensure_private_file(path)
    path.write_text(text)


def authority_boundary_failures(row: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    row_id = row.get("language_permission_id") or row.get("credit_id") or "<row>"
    events = row.get("authority_boundary_events", []) or []
    if not isinstance(events, list):
        return [f"{row_id}: authority_boundary_events not list"]
    for event in events:
        if not isinstance(event, dict):
            failures.append(f"{row_id}: non-object authority_boundary_event")
            continue
        eid = event.get("event_id", "<event>")
        etype = event.get("authority_boundary_event_type")
        if not str(eid).startswith("ABE-"):
            failures.append(f"{row_id}/{eid}: malformed event id")
        if etype == "current_vs_conditional_claim_language_normalization":
            if event.get("current_authority_state") != row.get("current_authority_state"):
                failures.append(f"{row_id}/{eid}: current_authority_state drift")
            if event.get("conditional_authority_ceiling") != row.get("conditional_authority_ceiling"):
                failures.append(f"{row_id}/{eid}: conditional_authority_ceiling drift")
            if not event.get("ceiling_spend_rule"):
                failures.append(f"{row_id}/{eid}: missing ceiling_spend_rule")
        elif etype == "current_vs_conditional_credit_normalization":
            if event.get("current_credit_state") != row.get("current_credit_state"):
                failures.append(f"{row_id}/{eid}: current_credit_state drift")
            if event.get("conditional_authority_ceiling") != row.get("conditional_authority_ceiling"):
                failures.append(f"{row_id}/{eid}: conditional_authority_ceiling drift")
            if not event.get("conditional_trigger"):
                failures.append(f"{row_id}/{eid}: missing conditional_trigger")
        else:
            failures.append(f"{row_id}/{eid}: unknown authority boundary event type {etype}")
    return failures


def first_row_with_source_event(disposition: str) -> dict[str, Any]:
    for path in sorted(ROOT.glob("*-LEDGER.json")):
        data = load(path.name)
        if not isinstance(data, dict):
            continue
        for rows in data.values():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                for event in row.get("source_role_events", []) or []:
                    if isinstance(event, dict) and event.get("source_ref_disposition") == disposition:
                        return copy.deepcopy(row)
    raise RuntimeError(f"no source_role_event row found for disposition {disposition}")


def require_detected(case: str, failures: list[str]) -> None:
    if not failures:
        raise AssertionError(f"negative replay did not fail closed: {case}")


def frontier_freshness_event_replay_failures_after_mutation() -> list[str]:
    """Mutate a copied typed event and require the freshness replay to catch it."""
    from frontier_source_freshness import evaluate_frontier_source_freshness

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = copy_release_tree(tmpdir)
        assertions = json.loads((tmp_root / "FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json").read_text())
        for assertion in assertions.get("assertion_rows", []):
            if not assertion.get("typed_event_replay_policy"):
                continue
            target_refs = set(assertion.get("source_refs_must_exist", []) or [])
            for spec in assertion.get("required_row_refs", []):
                required_refs = set(spec.get("source_refs_must_include", []) or []) & target_refs
                if not required_refs:
                    continue
                ledger_path = tmp_root / spec["ledger_file"]
                ledger = json.loads(ledger_path.read_text())
                rows = ledger.get(spec["row_collection"], [])
                row = next((item for item in rows if isinstance(item, dict) and item.get(spec["id_field"]) == spec["row_id"]), None)
                if not row:
                    continue
                for event in row.get("source_role_events", []) or []:
                    if not isinstance(event, dict):
                        continue
                    if event.get("source_role") != assertion["typed_event_replay_policy"].get("source_role"):
                        continue
                    event_refs = set(event.get("source_refs", []) or [])
                    victim_refs = sorted(required_refs & event_refs)
                    if not victim_refs:
                        continue
                    event["source_refs"] = [ref for ref in event.get("source_refs", []) if ref != victim_refs[0]]
                    write_text_private(ledger_path, json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
                    return evaluate_frontier_source_freshness(tmp_root).get("failures", [])
        raise RuntimeError("no typed frontier event replay row found for negative mutation")


def frontier_freshness_row_scoped_replay_failures_after_mutation() -> list[str]:
    """Mutate a copied mixed-role event and require row-scoped replay to catch it."""
    from frontier_source_freshness import evaluate_frontier_source_freshness

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = copy_release_tree(tmpdir)
        assertions = json.loads((tmp_root / "FRONTIER-SOURCE-FRESHNESS-ASSERTIONS.json").read_text())
        assertion = next(
            (
                item
                for item in assertions.get("assertion_rows", [])
                if item.get("assertion_id") == "FSF-0022-COSMO-DESI-LYA-EUCLID-SOURCE-STAGING"
            ),
            None,
        )
        if not assertion:
            raise RuntimeError("FSF-0022 mixed-role assertion missing")
        for policy in assertion.get("typed_event_replay_policies", []) or []:
            dispositions = set(policy.get("include_dispositions", []) or [])
            for row_spec in policy.get("applies_to_rows", []) or []:
                required_refs = set(row_spec.get("source_refs", []) or [])
                if not required_refs:
                    continue
                ledger_path = tmp_root / row_spec["ledger_file"]
                ledger = json.loads(ledger_path.read_text())
                for rows in ledger.values():
                    if not isinstance(rows, list):
                        continue
                    row = next(
                        (
                            item
                            for item in rows
                            if isinstance(item, dict)
                            and any(
                                key.endswith("_id") or key == "route_id"
                                for key, value in item.items()
                                if value == row_spec["row_id"]
                            )
                        ),
                        None,
                    )
                    if not row:
                        continue
                    for event in row.get("source_role_events", []) or []:
                        if not isinstance(event, dict):
                            continue
                        if event.get("source_role") != policy.get("source_role"):
                            continue
                        if event.get("source_ref_disposition") not in dispositions:
                            continue
                        victim_refs = sorted(required_refs & set(event.get("source_refs", []) or []))
                        if not victim_refs:
                            continue
                        event["source_refs"] = [ref for ref in event.get("source_refs", []) if ref != victim_refs[0]]
                        write_text_private(ledger_path, json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
                        return evaluate_frontier_source_freshness(tmp_root).get("failures", [])
        raise RuntimeError("no row-scoped mixed-role frontier event found for negative mutation")


def frontier_watchlist_zero_placement_failures_after_mutation() -> list[str]:
    """Inject a watchlist ref into a route-bearing row and require freshness to fail."""
    from frontier_source_freshness import evaluate_frontier_source_freshness

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = copy_release_tree(tmpdir)
        ledger_path = tmp_root / "CANDIDATE-ROUTE-STATE-LEDGER.json"
        ledger = json.loads(ledger_path.read_text())
        row = next(row for row in ledger["route_rows"] if row.get("route_id") == "R-OQ0057-COSMO-DARK-ENERGY-BAO")
        row.setdefault("source_refs", []).append("REF-0627")
        write_text_private(ledger_path, json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
        return evaluate_frontier_source_freshness(tmp_root).get("failures", [])





def source_snapshot_local_payload_hash_failures_after_mutation() -> list[str]:
    """Mutate a retained local payload and require source-snapshot custody to fail."""
    from source_snapshot_manifest import evaluate_source_snapshot_manifest

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = copy_release_tree(tmpdir)
        manifest = json.loads((tmp_root / "SOURCE-SNAPSHOT-MANIFEST.json").read_text())
        for row in manifest.get("snapshot_rows", []) or []:
            records = row.get("local_payload_records", []) or []
            if not records:
                continue
            victim_path = tmp_root / records[0]["local_path"]
            write_text_private(victim_path, victim_path.read_text() + "# drift injected by negative replay\n")
            return evaluate_source_snapshot_manifest(tmp_root).get("failures", [])
        raise RuntimeError("no retained local payload record found for source-snapshot mutation")


def source_snapshot_version_identity_failures_after_mutation() -> list[str]:
    """Remove exact-version identity from a versioned public record and require failure."""
    from source_snapshot_manifest import evaluate_source_snapshot_manifest

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = copy_release_tree(tmpdir)
        manifest_path = tmp_root / "SOURCE-SNAPSHOT-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        for row in manifest.get("snapshot_rows", []) or []:
            if "zenodo.org/records/" not in str(row.get("payload_locator", "")):
                continue
            row.pop("payload_record_identity", None)
            write_text_private(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
            return evaluate_source_snapshot_manifest(tmp_root).get("failures", [])
        raise RuntimeError("no versioned public-record payload found for source-snapshot mutation")


def source_snapshot_checksum_manifest_format_failures_after_mutation() -> list[str]:
    """Keep file hash metadata coherent but corrupt checksum-manifest syntax."""
    from source_snapshot_manifest import evaluate_source_snapshot_manifest

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = copy_release_tree(tmpdir)
        manifest_path = tmp_root / "SOURCE-SNAPSHOT-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        for row in manifest.get("snapshot_rows", []) or []:
            for record in row.get("local_payload_records", []) or []:
                if record.get("record_type") != "checksum_manifest":
                    continue
                payload_path = tmp_root / record["local_path"]
                lines = payload_path.read_text().splitlines()
                if not lines:
                    continue
                lines[0] = "not-a-sha256 " + lines[0].split(maxsplit=1)[-1]
                write_text_private(payload_path, "\n".join(lines) + "\n")
                data = payload_path.read_bytes()
                # Keep the generic local payload hash/size/count checks green;
                # this negative replay is specifically for checksum-manifest parsing.
                record["sha256"] = hashlib.sha256(data).hexdigest()
                record["byte_size"] = len(data)
                record["line_count"] = len(data.decode("utf-8").splitlines())
                write_text_private(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
                return evaluate_source_snapshot_manifest(tmp_root).get("failures", [])
        raise RuntimeError("no checksum-manifest local payload record found for source-snapshot mutation")



def source_snapshot_known_malformed_manifest_line_failures_after_mutation() -> list[str]:
    """Keep generic hashes coherent but mutate a declared upstream malformed manifest line."""
    from source_snapshot_manifest import evaluate_source_snapshot_manifest

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = copy_release_tree(tmpdir)
        manifest_path = tmp_root / "SOURCE-SNAPSHOT-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        for row in manifest.get("snapshot_rows", []) or []:
            for record in row.get("local_payload_records", []) or []:
                known = record.get("checksum_manifest_known_malformed_lines", []) or []
                if not known:
                    continue
                line_number = int(known[0]["line_number"])
                payload_path = tmp_root / record["local_path"]
                lines = payload_path.read_text().splitlines()
                if line_number < 1 or line_number > len(lines):
                    raise RuntimeError("declared malformed checksum line is outside local payload")
                old_line = lines[line_number - 1]
                replacement_tail = "0" if not old_line.endswith("0") else "1"
                lines[line_number - 1] = old_line[:-1] + replacement_tail
                write_text_private(payload_path, "\n".join(lines) + "\n")
                data = payload_path.read_bytes()
                # Keep generic local file metadata and upstream component-md5 replay coherent;
                # this negative replay is specifically for declared-anomaly content drift.
                record["sha256"] = hashlib.sha256(data).hexdigest()
                record["byte_size"] = len(data)
                record["line_count"] = len(data.decode("utf-8").splitlines())
                source_component = record.get("source_component_name")
                for component in row.get("payload_component_checksums", []) or []:
                    if component.get("component_name") == source_component and component.get("checksum_algorithm") == "md5":
                        component["checksum"] = hashlib.md5(data).hexdigest()
                write_text_private(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
                return evaluate_source_snapshot_manifest(tmp_root).get("failures", [])
        raise RuntimeError("no declared malformed checksum-manifest line found for source-snapshot mutation")



def source_snapshot_inventory_checksum_failures_after_mutation() -> list[str]:
    """Mutate an inventory checksum and require source-snapshot lint to fail."""
    from source_snapshot_manifest import evaluate_source_snapshot_manifest

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = copy_release_tree(tmpdir)
        manifest_path = tmp_root / "SOURCE-SNAPSHOT-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        for row in manifest.get("snapshot_rows", []) or []:
            if not isinstance(row, dict):
                continue
            for record in row.get("payload_inventory_records", []) or []:
                if not isinstance(record, dict):
                    continue
                algorithm = record.get("checksum_algorithm")
                checksum = record.get("checksum")
                if algorithm == "md5" and checksum:
                    record["checksum"] = "0" * 31
                    write_text_private(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
                    return evaluate_source_snapshot_manifest(tmp_root).get("failures", [])
                if algorithm == "sha256" and checksum:
                    record["checksum"] = "0" * 63
                    write_text_private(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
                    return evaluate_source_snapshot_manifest(tmp_root).get("failures", [])
        raise RuntimeError("no payload inventory checksum found for source-snapshot mutation")


def source_snapshot_inventory_control_json_failures_after_mutation() -> list[str]:
    """Keep local file metadata coherent but corrupt retained inventory-control semantics."""
    from source_snapshot_manifest import evaluate_source_snapshot_manifest

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = copy_release_tree(tmpdir)
        manifest_path = tmp_root / "SOURCE-SNAPSHOT-MANIFEST.json"
        manifest = json.loads(manifest_path.read_text())
        for row in manifest.get("snapshot_rows", []) or []:
            for record in row.get("local_payload_records", []) or []:
                if record.get("record_type") != "inventory_control_json":
                    continue
                payload_path = tmp_root / record["local_path"]
                payload = json.loads(payload_path.read_text())
                entries = payload.get("entries", [])
                if not entries:
                    continue
                entries[0]["route_credit_cap"] = "S1"
                write_text_private(payload_path, json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
                data = payload_path.read_bytes()
                # Keep generic retained-file metadata coherent; this replay is for semantic inventory drift.
                record["sha256"] = hashlib.sha256(data).hexdigest()
                record["byte_size"] = len(data)
                record["line_count"] = len(data.decode("utf-8").splitlines())
                write_text_private(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
                return evaluate_source_snapshot_manifest(tmp_root).get("failures", [])
        raise RuntimeError("no inventory_control_json local payload record found for source-snapshot mutation")

def source_role_credit_cap_failures_after_mutation() -> list[str]:
    """Mutate retained acquired-support cap semantics and require policy to fail."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = copy_release_tree(tmpdir)
        for ledger_path in sorted(tmp_root.glob("*-LEDGER.json")):
            ledger = json.loads(ledger_path.read_text())
            if not isinstance(ledger, dict):
                continue
            mutated = False
            for rows in ledger.values():
                if not isinstance(rows, list):
                    continue
                for row in rows:
                    if not isinstance(row, dict):
                        continue
                    for event in row.get("source_role_events", []) or []:
                        if isinstance(event, dict) and event.get("source_ref_disposition") == "retained_as_acquired_support":
                            event["credit_cap"] = "S0"
                            mutated = True
                            break
                    if mutated:
                        break
                if mutated:
                    break
            if mutated:
                write_text_private(ledger_path, json.dumps(ledger, indent=2, ensure_ascii=False) + "\n")
                return evaluate_source_role_credit_cap(tmp_root).get("failures", [])
        raise RuntimeError("no retained acquired-support event found for credit-cap mutation")

def main() -> int:
    live_rev_note_failures: list[str] = []
    for path in sorted(ROOT.glob("*.json")):
        try:
            live_rev_note_failures.extend(f"{path.name}:{item}" for item in walk_rev_note_keys(load(path.name)))
        except Exception:
            continue
    if live_rev_note_failures:
        print("SOURCE-ROLE NEGATIVE REPLAY PRECONDITION FAILED: live rev-note keys remain")
        for item in live_rev_note_failures[:20]:
            print(f"- {item}")
        return 1

    retained_row = first_row_with_source_event("retained_on_denominator_row_only")
    retained_event = next(event for event in retained_row["source_role_events"] if event.get("source_ref_disposition") == "retained_on_denominator_row_only")
    retained_row["source_refs"] = [ref for ref in retained_row.get("source_refs", []) if ref != retained_event["source_refs"][0]]
    require_detected("retained denominator source ref removed from row source_refs", source_event_failures_for_row(retained_row))

    acquired_row = first_row_with_source_event("retained_as_acquired_support")
    acquired_event = next(event for event in acquired_row["source_role_events"] if event.get("source_ref_disposition") == "retained_as_acquired_support")
    acquired_row["source_refs"] = [ref for ref in acquired_row.get("source_refs", []) if ref != acquired_event["source_refs"][0]]
    require_detected("retained acquired-support source ref removed from row source_refs", source_event_failures_for_row(acquired_row))

    forecast_row = first_row_with_source_event("retained_as_forecast_runway")
    forecast_event = next(event for event in forecast_row["source_role_events"] if event.get("source_ref_disposition") == "retained_as_forecast_runway")
    forecast_row["source_refs"] = [ref for ref in forecast_row.get("source_refs", []) if ref != forecast_event["source_refs"][0]]
    require_detected("retained forecast-runway source ref removed from row source_refs", source_event_failures_for_row(forecast_row))

    status_row = first_row_with_source_event("retained_as_operational_status")
    status_event = next(event for event in status_row["source_role_events"] if event.get("source_ref_disposition") == "retained_as_operational_status")
    status_row["source_refs"] = [ref for ref in status_row.get("source_refs", []) if ref != status_event["source_refs"][0]]
    require_detected("retained operational-status source ref removed from row source_refs", source_event_failures_for_row(status_row))

    forbidden_row = first_row_with_source_event("forbidden_on_metadata_wrapper")
    forbidden_event = next(event for event in forbidden_row["source_role_events"] if event.get("source_ref_disposition") == "forbidden_on_metadata_wrapper")
    forbidden_row.setdefault("source_refs", []).append(forbidden_event["source_refs"][0])
    require_detected("forbidden metadata-wrapper source ref injected into row source_refs", source_event_failures_for_row(forbidden_row))

    bad_role_row = first_row_with_source_event("route_local_handoff_only")
    bad_role_row["source_role_events"][0]["source_role"] = "candidate_support"
    require_detected("unknown source_role accepted", source_event_failures_for_row(bad_role_row))

    bad_cap_row = first_row_with_source_event("retained_on_denominator_row_only")
    bad_cap_row["source_role_events"][0]["credit_cap"] = "S2"
    require_detected("non-S0 source-custody credit cap accepted", source_event_failures_for_row(bad_cap_row))

    require_detected("frontier freshness accepted row refs after typed source_role_event ref removal", frontier_freshness_event_replay_failures_after_mutation())

    require_detected("mixed-role frontier freshness accepted row refs after row-scoped source_role_event ref removal", frontier_freshness_row_scoped_replay_failures_after_mutation())

    require_detected("watchlist frontier source accepted a route-bearing placement", frontier_watchlist_zero_placement_failures_after_mutation())

    require_detected("retained acquired-support no-new-credit boundary accepted S0 mutation", source_role_credit_cap_failures_after_mutation())

    require_detected("source snapshot local payload hash drift accepted", source_snapshot_local_payload_hash_failures_after_mutation())

    require_detected("source snapshot versioned public record accepted without exact identity", source_snapshot_version_identity_failures_after_mutation())

    require_detected("source snapshot checksum manifest syntax accepted after coherent hash mutation", source_snapshot_checksum_manifest_format_failures_after_mutation())

    require_detected("source snapshot declared malformed manifest line accepted after coherent hash mutation", source_snapshot_known_malformed_manifest_line_failures_after_mutation())

    require_detected("source snapshot payload inventory checksum accepted after mutation", source_snapshot_inventory_checksum_failures_after_mutation())

    require_detected("source snapshot retained inventory-control JSON semantic drift accepted after coherent hash mutation", source_snapshot_inventory_control_json_failures_after_mutation())

    fake_rev_note_row = {"row_id": "NEGATIVE-REPLAY", "rev0999_fake_note": "should fail"}
    require_detected("revXXXX note key accepted", walk_rev_note_keys(fake_rev_note_row))

    claim_rows = load("CLAIM-LANGUAGE-PERMISSION-LEDGER.json")["permission_rows"]
    authority_row = copy.deepcopy(next(row for row in claim_rows if row.get("authority_boundary_events")))
    authority_row["authority_boundary_events"][0]["current_authority_state"] = "S5"
    require_detected("authority boundary current-state drift accepted", authority_boundary_failures(authority_row))

    print("SOURCE-ROLE NEGATIVE REPLAY TESTS OK cases=19")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
