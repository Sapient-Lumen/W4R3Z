#!/usr/bin/env python3
"""Guardrail for concrete breakglass session methods and adapter projection posture."""
from __future__ import annotations
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))

def main() -> int:
    errors = []
    grant = load_json("spec/breakglass.grant.schema.json")
    receipt = load_json("spec/breakglass.receipt.schema.json")

    allowed = (((grant.get("properties") or {}).get("scope") or {}).get("properties") or {}).get("allowed_methods") or {}
    allowed_enum = ((allowed.get("items") or {}).get("enum") or [])
    if allowed_enum != ["console", "serial", "ssh"]:
        errors.append("spec/breakglass.grant.schema.json scope.allowed_methods enum must be ['console', 'serial', 'ssh']")
    if "oob" in json.dumps(allowed, sort_keys=True):
        errors.append("spec/breakglass.grant.schema.json must not leave `oob` in the breakglass allowed_methods contract")
    adesc = allowed.get("description") or ""
    for needle in ["Out-of-band approval", "BMC KVM/HTML5 console", "Serial-over-LAN", "install/reset lane"]:
        if needle not in adesc:
            errors.append(f"spec/breakglass.grant.schema.json allowed_methods description missing required token: {needle}")

    method = ((((receipt.get("properties") or {}).get("session") or {}).get("properties") or {}).get("method") or {})
    method_enum = method.get("enum") or []
    if method_enum != ["console", "serial", "ssh"]:
        errors.append("spec/breakglass.receipt.schema.json session.method enum must be ['console', 'serial', 'ssh']")
    if "oob" in json.dumps(method, sort_keys=True):
        errors.append("spec/breakglass.receipt.schema.json must not leave `oob` in the breakglass session.method contract")
    mdesc = method.get("description") or ""
    for needle in ["BMC KVM/HTML5 console", "Serial-over-LAN", "virtual-media-assisted recovery"]:
        if needle not in mdesc:
            errors.append(f"spec/breakglass.receipt.schema.json session.method description missing required token: {needle}")

    for rel in ["spec/examples/breakglass.grant.json", "spec/examples/breakglass.receipt.json", "spec/examples/breakglass.receipt.rejected.json"]:
        txt = (ROOT / rel).read_text(encoding="utf-8")
        if '"oob"' in txt:
            errors.append(f"{rel} must not use deprecated breakglass method value `oob`")

    doc_checks = {
        "adrs/ADR-0296-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md": [
            "`console`", "`serial`", "`ssh`", "`oob` is **not**", "Serial-over-LAN", "virtual-media"
        ],
        "docs/706-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md": [
            "`oob` is no longer", "BMC KVM / HTML5 remote console projects to `console`", "Serial-over-LAN projects to `serial`"
        ],
        "docs/236-breakglass-and-recovery-mode.md": [
            "session methods stay concrete", "BMC KVM/HTML5 console", "virtual-media"
        ],
        "docs/250-breakglass-and-recovery-workflows.md": [
            "OOB approval still works", "project to `console`, `serial`, or `ssh`", "approval transport is not the same thing as session method"
        ],
        "docs/618-breakglass-recording-detail-and-export-posture-by-profile.md": [
            "`console` / `serial` / `ssh`", "not a generic `oob` method"
        ],
        "docs/266-open-questions-and-risk-register.md": [
            "ADR-0296", "`console|serial|ssh` method split"
        ],
        "docs/98-archive-hygiene.md": [
            "check_breakglass_method_boundary.py", "generic `oob` bucket"
        ],
        "docs/99-llm-runbook.md": [
            "docs/706-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md", "tools/check_breakglass_method_boundary.py"
        ],
        "docs/00-index.md": [
            "docs/706-breakglass-session-methods-stay-concrete-and-oob-adapters-project-into-them.md", "tools/check_breakglass_method_boundary.py"
        ],
        "docs/110-juicy-os-lessons.md": [
            "BMC KVM, SOL, and virtual media", "generic `oob` bucket"
        ],
        "docs/32-curated-references.md": [
            "DMTF Redfish `VirtualMedia` schema index", "Intel Serial-over-LAN setup guide", "Supermicro BMC remote-presence feature overview"
        ],
    }
    for rel, needles in doc_checks.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    if errors:
        for err in errors:
            print(f"ERROR: {err}")
        return 1
    print("Breakglass method boundary: OK")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
