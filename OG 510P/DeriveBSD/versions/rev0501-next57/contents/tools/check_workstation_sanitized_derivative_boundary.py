#!/usr/bin/env python3
"""Guardrail for workstation sanitized-inspection-derivative posture."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

DOCS = {
    "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md": [
        "sanitized inspection derivatives stay inspection-shaped and disposable-first",
        "sanitizer success is not implicit trust-promotion",
        "document_viewing",
        "content.working-copy.plan",
    ],
    "adrs/ADR-0244-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md": [
        "sanitized inspection derivatives remain inspection-shaped by default",
        "Ordinary viewing of sanitized inspection derivatives stays disposable-first",
        "sanitizer success is not implicit trust-promotion",
    ],
    "docs/267-sanitization-portal-and-disposable-sandboxes.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "inspection-shaped",
    ],
    "docs/410-desktop-viability-checklist.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitized inspection derivatives",
        "disposable-first",
    ],
    "docs/457-workstation-host-ui-and-appvm-boundary.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitized inspection derivatives",
        "disposable-first",
    ],
    "docs/484-origin-label-authority-and-anti-laundering-boundary.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitizer success",
    ],
    "docs/605-workstation-file-open-import-and-bounded-document-roles.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitized inspection derivatives",
    ],
    "docs/606-workstation-imported-foreign-documents-stay-view-first.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitized inspection derivative",
        "disposable-first",
    ],
    "docs/607-workstation-working-copy-receipts-and-edit-route-joins.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitized-inspection-derivative",
        "ambient persistent viewing or trust promotion",
    ],
    "docs/653-workstation-imported-foreign-document-viewing-stays-disposable-first.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitized inspection derivatives stay inspection-shaped",
    ],
    "docs/179-portals-and-powerbox.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitized inspection derivatives",
    ],
    "docs/199-intent-routing-and-plumbing.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitized inspection derivatives",
        "policy-pinned",
    ],
    "docs/541-workstation-role-slot-bindings-as-typed-state-boundary.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitized inspection derivative",
    ],
    "docs/266-open-questions-and-risk-register.md": [
        "ADR-0244",
        "sanitized inspection derivatives",
    ],
    "docs/99-llm-runbook.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "check_workstation_sanitized_derivative_boundary.py",
    ],
    "docs/98-archive-hygiene.md": [
        "check_workstation_sanitized_derivative_boundary.py",
        "sanitized-inspection-derivative boundary",
    ],
    "docs/110-juicy-os-lessons.md": [
        "Sanitized inspection derivatives should stay inspection-shaped until explicit promotion",
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
    ],
    "README.md": [
        "docs/654-workstation-sanitized-inspection-derivatives-stay-inspection-shaped-and-disposable-first.md",
        "sanitized inspection derivatives",
        "implicit trust-promotion",
    ],
}


def main() -> int:
    errors: list[str] = []
    for rel, needles in DOCS.items():
        text = (ROOT / rel).read_text(encoding="utf-8")
        for needle in needles:
            if needle not in text:
                errors.append(f"{rel} missing required token: {needle}")

    wc_plan = json.loads((ROOT / "spec" / "examples" / "content.working-copy.plan.json").read_text(encoding="utf-8"))
    if (wc_plan.get("source") or {}).get("source_class") != "sanitized-inspection-derivative":
        errors.append("spec/examples/content.working-copy.plan.json must keep source.source_class=sanitized-inspection-derivative")

    wc_receipt = json.loads((ROOT / "spec" / "examples" / "content.working-copy.receipt.json").read_text(encoding="utf-8"))
    if (wc_receipt.get("source") or {}).get("source_class") != "sanitized-inspection-derivative":
        errors.append("spec/examples/content.working-copy.receipt.json must keep source.source_class=sanitized-inspection-derivative")

    view_req = json.loads((ROOT / "spec" / "examples" / "intent.request.document-view.sanitized-inspection.json").read_text(encoding="utf-8"))
    if "import_receipt_digest" not in (view_req.get("context") or {}):
        errors.append("spec/examples/intent.request.document-view.sanitized-inspection.json missing context.import_receipt_digest")

    view_route = json.loads((ROOT / "spec" / "examples" / "intent.route.receipt.document-view.sanitized-inspection.json").read_text(encoding="utf-8"))
    if view_route.get("resolution_mode") != "policy-pinned":
        errors.append("spec/examples/intent.route.receipt.document-view.sanitized-inspection.json must use resolution_mode=policy-pinned")
    if "disposable" not in ((view_route.get("handler") or {}).get("service_name") or ""):
        errors.append("spec/examples/intent.route.receipt.document-view.sanitized-inspection.json handler.service_name must stay disposable-shaped")
    if "import_receipt_digest" not in view_route:
        errors.append("spec/examples/intent.route.receipt.document-view.sanitized-inspection.json missing import_receipt_digest")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Workstation sanitized-inspection-derivative boundary: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
