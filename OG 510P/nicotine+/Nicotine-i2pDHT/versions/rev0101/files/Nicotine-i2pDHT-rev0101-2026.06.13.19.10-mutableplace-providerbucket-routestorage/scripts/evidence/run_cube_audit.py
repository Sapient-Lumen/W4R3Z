#!/usr/bin/env python3
"""Write the current rev0101 cube audit report for packaging/surface hygiene."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from i2p_dht_lab.cubeaudit import audit_cube
from i2p_dht_lab.foldmap import audit_fold_map
from i2p_dht_lab.foldregistry import audit_fold_registry
from i2p_dht_lab.nativefoldspine import audit_native_fold_spine
from i2p_dht_lab.substratespine import audit_substrate_spine
from i2p_dht_lab.substratereturnfold import audit_substrate_return_fold
from i2p_dht_lab.substratecenturyfold import audit_substrate_century_fold
from i2p_dht_lab.substrateplacementfold import audit_substrate_placement_fold
from i2p_dht_lab.surfaceaudit import audit_surface_pointers
from i2p_dht_lab.surfaceclean import audit_surface_clean
from i2p_dht_lab.surfacefold import audit_surface_fold
from i2p_dht_lab.surfaceindex import audit_surface_index
from i2p_dht_lab.surfaceledger import audit_surface_ledger, entries_for_revision

REVISION = "rev0101"


def _cleanup_transients() -> None:
    for path in ROOT.rglob("__pycache__"):
        shutil.rmtree(path, ignore_errors=True)
    for path in ROOT.rglob(".pytest_cache"):
        shutil.rmtree(path, ignore_errors=True)


def _findings(report: object) -> list[dict[str, object]]:
    return [getattr(finding, "__dict__", dict(finding=finding)) for finding in getattr(report, "findings", ())]


def _snapshot(report: object) -> dict[str, object]:
    return {"status": getattr(report, "status", "pass"), "warning_count": getattr(report, "warning_count", 0), "error_count": getattr(report, "error_count", 0), "findings": _findings(report)}


def main() -> None:
    _cleanup_transients()
    root_name = ROOT.name
    report = audit_cube(ROOT)
    surface = audit_surface_pointers(ROOT, revision=REVISION)
    clean = audit_surface_clean(ROOT, revision=REVISION)
    ledger = audit_surface_ledger(ROOT, entries_for_revision(REVISION))
    legacy_fold = audit_surface_fold(ROOT, revision="rev0054", artifact_stem=root_name)
    index = audit_surface_index(ROOT, revision=REVISION)
    fold_map = audit_fold_map(ROOT, revision=REVISION, artifact_stem=root_name)
    fold_registry = audit_fold_registry(ROOT, revision=REVISION)
    native_spine = audit_native_fold_spine(ROOT, revision="rev0099")
    substrate_spine = audit_substrate_spine(ROOT, revision=REVISION)
    predecessor = audit_substrate_return_fold(ROOT, revision="rev0099")
    predecessor_century = audit_substrate_century_fold(ROOT, revision="rev0100")
    current_fold = audit_substrate_placement_fold(ROOT, revision=REVISION)
    payload = report.as_dict()
    payload.update({
        "revision": REVISION,
        "surface_pointers": _snapshot(surface),
        "surface_clean": _snapshot(clean),
        "surface_ledger": {"status": "pass" if ledger.ok else "fail", "error_count": ledger.error_count, "warning_count": getattr(ledger, "warning_count", 0), "findings": _findings(ledger)},
        "legacy_surface_fold": _snapshot(legacy_fold),
        "surface_index": _snapshot(index),
        "fold_map": _snapshot(fold_map),
        "fold_registry": _snapshot(fold_registry),
        "nativefoldspine_rev0099": _snapshot(native_spine),
        "substratespine": _snapshot(substrate_spine),
        "predecessor_substratereturnfold": _snapshot(predecessor),
        "predecessor_substratecenturyfold": _snapshot(predecessor_century),
        "substrateplacementfold": _snapshot(current_fold),
    })
    failures = []
    for label, obj in (
        ("cube", report), ("surface", surface), ("clean", clean), ("legacy_fold", legacy_fold), ("index", index),
        ("fold_map", fold_map), ("fold_registry", fold_registry), ("native_spine", native_spine), ("substrate_spine", substrate_spine),
        ("predecessor", predecessor), ("predecessor_century", predecessor_century), ("current_fold", current_fold),
    ):
        if getattr(obj, "status", "pass") != "pass" or getattr(obj, "error_count", 0):
            failures.append(label)
    if not ledger.ok:
        failures.append("surface_ledger")
    payload["status"] = "pass" if not failures and not report.error_count else "fail"
    payload["failures"] = failures
    target = ROOT / "artifacts/process/rev0101_cube_audit.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    if payload["status"] != "pass":
        raise SystemExit(f"cube audit failed: {failures}")
    print(f"cube audit pass: wrote {target.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
