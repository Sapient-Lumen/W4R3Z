#!/usr/bin/env python3
"""Validate the request-owner Search Again policy and reject semantic drift."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import canonical_json, derive_revision, safe_relative, write_csv, write_json  # noqa: E402

CONTRACT_PATH = Path("data/current_search_action_contract.json")
CANDIDATE_PATH = Path("data/current_candidate_artifact_contract.json")
LEDGER_PATH = Path("data/current_packet_dispositions.json")


def validate_contract(root: Path, contract: dict[str, Any]) -> tuple[list[dict[str, str]], list[str]]:
    revision = derive_revision(root)
    rows: list[dict[str, str]] = []
    errors: list[str] = []

    def add(check: str, passed: bool, detail: object = "") -> None:
        rows.append({"check": check, "status": "pass" if passed else "fail", "detail": str(detail)})
        if not passed:
            errors.append(f"{check}: {detail}")

    add("contract version", contract.get("version") == 1, contract.get("version"))
    add("contract revision", contract.get("revision") == revision, contract.get("revision"))
    cases = contract.get("cases")
    add("cases list", isinstance(cases, list) and len(cases) == 3, type(cases).__name__)
    cases = cases if isinstance(cases, list) else []
    by_id = {
        item.get("case_id"): item
        for item in cases
        if isinstance(item, dict) and isinstance(item.get("case_id"), str)
    }
    add("case IDs exact", set(by_id) == {
        "ordinary-page", "manual-wishlist-page", "persistent-wishlist-inbox"
    }, sorted(by_id))
    add("case IDs unique", len(by_id) == len(cases), len(by_id))

    required_fields = {
        "case_id", "request_class", "gui_modes", "packet_id", "action_visibility",
        "action_semantics", "wire_epoch", "stable_page_identity",
        "clear_result_derived_state", "preserve_seen_history", "manual_alternative",
    }
    for index, case in enumerate(cases):
        add(f"case {index} mapping", isinstance(case, dict))
        if not isinstance(case, dict):
            continue
        add(f"case {index} fields", set(case) == required_fields, sorted(set(case) ^ required_fields))
        add(f"case {index} GUI modes", isinstance(case.get("gui_modes"), list) and bool(case.get("gui_modes")))
        add(f"case {index} page identity", case.get("stable_page_identity") is True)

    ordinary = by_id.get("ordinary-page", {})
    manual = by_id.get("manual-wishlist-page", {})
    persistent = by_id.get("persistent-wishlist-inbox", {})
    for label, case in (("ordinary", ordinary), ("manual", manual)):
        add(f"{label} owner", case.get("request_class") == "SearchRequest", case.get("request_class"))
        add(f"{label} action visible", case.get("action_visibility") == "visible", case.get("action_visibility"))
        add(f"{label} replacement refresh", case.get("action_semantics") == "replacement-refresh", case.get("action_semantics"))
        add(f"{label} fresh token", case.get("wire_epoch") == "fresh-token", case.get("wire_epoch"))
        add(f"{label} clears result state", case.get("clear_result_derived_state") is True)
    add("ordinary modes", set(ordinary.get("gui_modes", [])) == {"global", "rooms", "buddies", "user"}, ordinary.get("gui_modes"))
    add("manual wishlist mode", manual.get("gui_modes") == ["wishlist"], manual.get("gui_modes"))

    add("persistent owner", persistent.get("request_class") == "WishSearchRequest", persistent.get("request_class"))
    add("persistent action hidden", persistent.get("action_visibility") == "hidden", persistent.get("action_visibility"))
    add("persistent action absent", persistent.get("action_semantics") == "absent-from-result-page", persistent.get("action_semantics"))
    add("persistent scheduler owns epoch", persistent.get("wire_epoch") == "scheduler-owned-unchanged", persistent.get("wire_epoch"))
    add("persistent result state not cleared", persistent.get("clear_result_derived_state") is False)
    add("persistent seen history preserved", persistent.get("preserve_seen_history") is True)
    add("persistent manual alternative", persistent.get("manual_alternative") == "wishlist-dialog-search-for-item", persistent.get("manual_alternative"))

    cap = contract.get("cap_boundary")
    add("cap boundary mapping", isinstance(cap, dict))
    if isinstance(cap, dict):
        add("cap boundary packet", cap.get("packet_id") == "WISHLIST-CAP-01", cap.get("packet_id"))
        add("cap boundary remains unselected", cap.get("selected_policy") is None, cap.get("selected_policy"))
        add("cap boundary status", cap.get("status") == "open-subscription-cap-lifecycle-research", cap.get("status"))
        add("cap behavior explained", isinstance(cap.get("current_behavior"), str) and len(cap["current_behavior"]) > 60)

    try:
        candidate = json.loads((root / CANDIDATE_PATH).read_text(encoding="utf-8"))
        ledger = json.loads((root / LEDGER_PATH).read_text(encoding="utf-8"))
    except Exception as exc:
        add("authority inputs readable", False, exc)
        return rows, errors
    add("authority inputs readable", True)
    candidate_id = contract.get("candidate_artifact_id")
    artifacts = {
        item.get("artifact_id"): item
        for item in candidate.get("artifacts", []) if isinstance(item, dict)
    }
    add("candidate ID is current", candidate_id == candidate.get("current_candidate_id"), candidate_id)
    add("candidate artifact exists", candidate_id in artifacts, candidate_id)
    artifact = artifacts.get(candidate_id, {})
    patch_value = artifact.get("path")
    add("candidate path safe", isinstance(patch_value, str) and safe_relative(patch_value), patch_value)
    patch_text = ""
    if isinstance(patch_value, str) and safe_relative(patch_value):
        patch_path = root / patch_value
        add("candidate path exists", patch_path.is_file() and not patch_path.is_symlink(), patch_value)
        if patch_path.is_file():
            patch_text = patch_path.read_text(encoding="utf-8")
    add("candidate classifies WishSearchRequest", "not isinstance(search, WishSearchRequest)" in patch_text)
    add("candidate persistent repeat fails closed", "search is None or isinstance(search, WishSearchRequest)" in patch_text)
    add("candidate hides disabled menu item", '("=" + _("Search _Again")' in patch_text)
    add("candidate guards callback", "if not core.search.can_repeat_search(self.token):" in patch_text)
    add("candidate does not clear seen users", "ignored_users.clear" not in patch_text)

    packets = {
        item.get("packet_id"): item
        for item in ledger.get("packets", []) if isinstance(item, dict)
    }
    for case_id, case in by_id.items():
        packet_id = case.get("packet_id")
        add(f"ledger packet for {case_id}", packet_id in packets, packet_id)
        if packet_id in packets:
            add(f"packet remains unselected: {packet_id}", packets[packet_id].get("selected_patch") is None)
    cap_id = cap.get("packet_id") if isinstance(cap, dict) else None
    add("ledger cap packet", cap_id in packets, cap_id)
    if cap_id in packets:
        add("cap ledger status", packets[cap_id].get("status") == cap.get("status"), packets[cap_id].get("status"))

    return rows, errors


def mutation_checks(root: Path, contract: dict[str, Any]) -> list[dict[str, str]]:
    mutations: list[tuple[str, dict[str, Any]]] = []

    def mutate_case(name: str, case_id: str, field: str, value: object) -> None:
        mutant = copy.deepcopy(contract)
        for case in mutant["cases"]:
            if case["case_id"] == case_id:
                case[field] = value
        mutations.append((name, mutant))

    wrong_revision = copy.deepcopy(contract)
    wrong_revision["revision"] = "rev0000"
    mutations.append(("wrong revision", wrong_revision))
    mutate_case("persistent action visible", "persistent-wishlist-inbox", "action_visibility", "visible")
    mutate_case("persistent refresh invented", "persistent-wishlist-inbox", "action_semantics", "replacement-refresh")
    mutate_case("persistent seen reset", "persistent-wishlist-inbox", "preserve_seen_history", False)
    mutate_case("ordinary same-token retry", "ordinary-page", "wire_epoch", "same-token")
    mutate_case("manual page lacks stable identity", "manual-wishlist-page", "stable_page_identity", False)
    missing_cap = copy.deepcopy(contract)
    missing_cap["cap_boundary"]["packet_id"] = ""
    mutations.append(("missing cap packet", missing_cap))
    wrong_artifact = copy.deepcopy(contract)
    wrong_artifact["candidate_artifact_id"] = "missing"
    mutations.append(("wrong candidate", wrong_artifact))

    rows: list[dict[str, str]] = []
    for name, mutant in mutations:
        _checks, errors = validate_contract(root, mutant)
        rows.append({
            "mutation": name,
            "status": "pass" if errors else "fail",
            "detail": f"rejected with {len(errors)} error(s)" if errors else "mutation was accepted",
        })
    return rows


def audit(root: Path) -> dict[str, Any]:
    contract = json.loads((root / CONTRACT_PATH).read_text(encoding="utf-8"))
    checks, errors = validate_contract(root, contract)
    mutations = mutation_checks(root, contract)
    if any(row["status"] != "pass" for row in mutations):
        errors.append("one or more policy mutations were accepted")
    return {
        "revision": derive_revision(root),
        "status": "pass" if not errors else "fail",
        "contract": CONTRACT_PATH.as_posix(),
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "mutation_checks_passed": sum(row["status"] == "pass" for row in mutations),
        "mutation_checks_total": len(mutations),
        "checks": checks,
        "mutations": mutations,
        "errors": errors,
    }


def write_outputs(root: Path, result: dict[str, Any]) -> None:
    revision = result["revision"]
    write_json(root / f"data/{revision}_search_action_policy_audit.json", result)
    write_csv(root / f"data/{revision}_search_action_policy_checks.csv", result["checks"],
              fields=("check", "status", "detail"))
    write_csv(root / f"data/{revision}_search_action_policy_mutations.csv", result["mutations"],
              fields=("mutation", "status", "detail"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write-data", action="store_true")
    args = parser.parse_args()
    result = audit(args.root.resolve())
    if args.write_data:
        write_outputs(args.root.resolve(), result)
    print(canonical_json({key: value for key, value in result.items() if key not in {"checks", "mutations"}}), end="")
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
