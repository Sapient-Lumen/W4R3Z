#!/usr/bin/env python3
"""Guardrail for disposable-first viewing of imported foreign documents."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md": [
        "disposable-first",
        "persistent viewer",
        "policy-pinned",
        "fail closed",
    ],
    "adrs/ADR-0243-workstation-imported-foreign-document-viewing-stays-disposable-first.md": [
        "disposable-first",
        "persistent `document_viewing`",
        "fail closed",
    ],
    "docs/605-workstation-file-open-import-and-bounded-document-roles.md": [
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
        "disposable-first",
    ],
    "docs/606-workstation-imported-foreign-documents-stay-view-first.md": [
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
        "disposable-first",
        "persistent viewer fallback",
    ],
    "docs/179-portals-and-powerbox.md": [
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
        "disposable-first",
    ],
    "docs/199-intent-routing-and-plumbing.md": [
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
        "policy-pinned",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
        "disposable-first",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
        "disposable-first",
    ],
    "docs/540-workstation-role-bound-intent-targets-and-chooser-floor.md": [
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
        "policy-pinned",
    ],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": [
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
        "persistent `document_viewing` target",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0243",
        "disposable-first",
    ],
    "docs/99-llm-runbook.md": [
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
        "check_workstation_document_viewing_posture.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_document_viewing_posture.py",
        "disposable-first viewing posture",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Imported foreign document viewing should stay disposable-first",
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
    ],
    "README.md": [
        "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md",
        "disposable-first",
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    binding = json.loads((ROOT / "spec" / "examples" / "intent.role.binding.json").read_text(encoding="utf-8"))
    targets = binding["bindings"]["document_viewing"]["enrolled_targets"]
    if not any(t.get("target_kind") == "disposable-template" for t in targets):
        errors.append("spec/examples/intent.role.binding.json missing disposable-template document_viewing target")

    view_req = json.loads((ROOT / "spec" / "examples" / "intent.request.document-view.json").read_text(encoding="utf-8"))
    if "import_receipt_digest" not in (view_req.get("context") or {}):
        errors.append("spec/examples/intent.request.document-view.json missing context.import_receipt_digest")

    view_route = json.loads((ROOT / "spec" / "examples" / "intent.route.receipt.document-view.json").read_text(encoding="utf-8"))
    if view_route.get("resolution_mode") != "policy-pinned":
        errors.append("spec/examples/intent.route.receipt.document-view.json must use resolution_mode=policy-pinned")
    if "disposable" not in ((view_route.get("handler") or {}).get("service_name") or ""):
        errors.append("spec/examples/intent.route.receipt.document-view.json handler.service_name must stay disposable-shaped")
    if "import_receipt_digest" not in view_route:
        errors.append("spec/examples/intent.route.receipt.document-view.json missing import_receipt_digest")

    for name in ["content.import.document-view.plan.json", "content.import.document-view.receipt.json"]:
        obj = json.loads((ROOT / "spec" / "examples" / name).read_text(encoding="utf-8"))
        execution = obj.get("execution") or {}
        if execution != {"isolation": "microvm", "network": "none", "lifetime": "disposable"}:
            errors.append(f"spec/examples/{name} execution must stay microvm/none/disposable")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Workstation imported-document viewing posture: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
