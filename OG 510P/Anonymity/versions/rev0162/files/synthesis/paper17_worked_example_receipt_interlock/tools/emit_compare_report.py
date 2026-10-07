#!/usr/bin/env python3
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(name: str):
    with open(ART / name, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    compare_profile = load("example_compare_profile.json")
    compare_walkthrough = load("example_compare_walkthrough.json")
    change_control = load("example_change_control.json")
    support_manifest = load("support_manifest.json")
    artifact_inventory = load("example_artifact_inventory.json")
    report = {
        "report_id": "worked-example-compare-report-v1",
        "claim_id": compare_walkthrough["claim_id"],
        "base_release_id": compare_walkthrough["base_release_id"],
        "release_id": compare_walkthrough["base_release_id"],
        "successor_release_id": compare_walkthrough["successor_fields"]["release_id"],
        "compare_profile_id": compare_profile["compare_profile_id"],
        "support_manifest_id": support_manifest["manifest_id"],
        "artifact_inventory_id": artifact_inventory["inventory_id"],
        "note_version": artifact_inventory.get("note_version"),
        "classification": compare_walkthrough["classification_result"],
        "required_action": compare_walkthrough["required_action"],
        "user_fast_diff": {
            "base": compare_walkthrough["base_fields"]["user_fast_diff"],
            "successor": compare_walkthrough["successor_fields"]["user_fast_diff"],
            "first_fields": compare_profile["diff_views"]["user_fast_diff"],
            "first_alarm": compare_walkthrough["user_first_alarm"],
        },
        "auditor_fast_diff": {
            "base": compare_walkthrough["base_fields"]["auditor_fast_diff"],
            "successor": compare_walkthrough["successor_fields"]["auditor_fast_diff"],
            "first_fields": compare_profile["diff_views"]["auditor_fast_diff"],
            "first_alarm": compare_walkthrough["auditor_first_alarm"],
            "guard_reference": change_control["interface_guard"],
        },
        "stable_guard_fields": compare_walkthrough["successor_fields"]["auditor_fast_diff"],
        "observed_diffs": compare_walkthrough["observed_diffs"],
        "note": "Maintenance compare report generated from the compare profile, compare walk-through, and change-control adjunct. It is not a new receipt or UVI primitive.",
    }
    out = ART / "example_compare_report.json"
    payload = json.dumps(report, indent=2, sort_keys=True) + "\n"
    out.write_text(payload, encoding="utf-8")
    digest = sha256_bytes(payload.encode("utf-8"))

    files = support_manifest.get("files", [])
    found = False
    for entry in files:
        if entry.get("path") == "example_compare_report.json":
            entry["sha256"] = digest
            found = True
            break
    if not found:
        files.append({"path": "example_compare_report.json", "sha256": digest})
    support_manifest["files"] = sorted(files, key=lambda x: x["path"])
    (ART / "support_manifest.json").write_text(json.dumps(support_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
