#!/usr/bin/env python3
"""Probe native validation capabilities and bind packet claims to reality.

This audit prevents the cube from silently relabeling source/model evidence as
native GTK validation. Capability presence is only a prerequisite; it is never
counted as a completed integration test.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from cube_runtime import canonical_json, derive_revision, run_bounded, write_csv, write_json  # noqa: E402

CONTRACT = Path("data/current_environment_capability_contract.json")
LEDGER = Path("data/current_packet_dispositions.json")

IMPORT_COMMANDS = {
    "python-gi": "import gi; print('gi')",
    "gtk3": "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk; print(Gtk.get_major_version())",
    "gtk4": "import gi; gi.require_version('Gtk', '4.0'); from gi.repository import Gtk; print(Gtk.get_major_version())",
    "gio": "import gi; from gi.repository import Gio; print(Gio.Application.__name__)",
}


def load_json(path: Path) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def probe_capability(spec: dict[str, Any]) -> dict[str, Any]:
    capability_id = spec["capability_id"]
    kind = spec["kind"]
    available = False
    detail = ""
    if kind == "python-import":
        result = run_bounded(
            [sys.executable, "-I", "-c", IMPORT_COMMANDS[capability_id]],
            cwd=ROOT,
            timeout=20,
        )
        available = result.returncode == 0
        detail = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else f"returncode={result.returncode}"
    elif kind == "command":
        available = shutil.which(spec["command"]) is not None
        detail = spec["command"] if available else "not found"
    elif kind == "platform":
        available = sys.platform == spec["platform"]
        detail = sys.platform
    else:
        raise ValueError(f"unknown capability kind: {kind}")
    return {
        "capability_id": capability_id,
        "kind": kind,
        "available": available,
        "status": "observed",
        "detail": detail[:300],
    }


def run() -> dict[str, Any]:
    contract = load_json(CONTRACT)
    ledger = load_json(LEDGER)
    revision = derive_revision(ROOT)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, passed: bool, detail: Any = "") -> None:
        checks.append({"check_id": check_id, "status": "pass" if passed else "fail", "detail": detail})

    add("contract revision", contract.get("revision") == revision, contract.get("revision"))
    capability_rows = [probe_capability(spec) for spec in contract.get("capabilities", [])]
    capability_map = {row["capability_id"]: row["available"] for row in capability_rows}
    add("capability IDs unique", len(capability_map) == len(capability_rows), len(capability_rows))
    add("all capabilities observed", all(row["status"] == "observed" for row in capability_rows), len(capability_rows))

    packets = {packet["packet_id"]: packet for packet in ledger.get("packets", [])}
    boundary_rows: list[dict[str, Any]] = []
    for boundary in contract.get("packet_boundaries", []):
        packet_id = boundary["packet_id"]
        packet = packets.get(packet_id)
        required = boundary.get("required_capabilities", [])
        native_ready = all(capability_map.get(item, False) for item in required)
        missing_text = " ".join(packet.get("missing_evidence", [])) if packet else ""
        terms = boundary.get("required_missing_evidence_terms_when_unavailable", [])
        terms_present = all(term in missing_text for term in terms) if not native_ready else True
        selected_ok = not boundary.get("selected_patch_must_be_null") or (packet and packet.get("selected_patch") is None)
        passed = packet is not None and terms_present and selected_ok
        boundary_rows.append({
            "packet_id": packet_id,
            "required_capabilities": ",".join(required),
            "native_prerequisites_available": native_ready,
            "missing_evidence_terms_present": terms_present,
            "selected_patch_null": selected_ok,
            "status": "pass" if passed else "fail",
        })
        add(f"packet boundary {packet_id}", passed, boundary_rows[-1])

    native_gtk_ready = capability_map.get("gtk3", False) and capability_map.get("gtk4", False)
    result = {
        "revision": revision,
        "status": "pass" if all(row["status"] == "pass" for row in checks) else "fail",
        "platform": sys.platform,
        "capabilities": capability_rows,
        "native_gtk3_and_gtk4_prerequisites_available": native_gtk_ready,
        "native_win32_prerequisite_available": capability_map.get("win32-native", False),
        "interpretation": {
            "native_ui_validated": False,
            "reason": (
                "required GTK runtimes are unavailable in this environment"
                if not native_gtk_ready
                else "capabilities are present, but no native UI scenario has been executed by this audit"
            ),
            "model_and_source_evidence_only": True,
        },
        "checks_passed": sum(row["status"] == "pass" for row in checks),
        "checks_total": len(checks),
        "checks": checks,
        "packet_boundaries": boundary_rows,
    }
    write_csv(ROOT / f"data/{revision}_environment_capabilities.csv", capability_rows,
              fields=("capability_id", "kind", "available", "status", "detail"))
    write_csv(ROOT / f"data/{revision}_environment_packet_boundaries.csv", boundary_rows,
              fields=("packet_id", "required_capabilities", "native_prerequisites_available",
                      "missing_evidence_terms_present", "selected_patch_null", "status"))
    write_json(ROOT / f"data/{revision}_environment_capability_audit.json", result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-data", action="store_true", help="retained for current-tool CLI consistency")
    parser.parse_args()
    try:
        result = run()
    except Exception as exc:
        result = {"status": "fail", "errors": [f"{type(exc).__name__}: {exc}"]}
    print(canonical_json(result), end="")
    return 0 if result.get("status") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
