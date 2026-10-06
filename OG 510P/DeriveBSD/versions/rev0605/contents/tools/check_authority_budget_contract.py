#!/usr/bin/env python3
"""Guardrail for the authority-budget policy / check / exception boundary.

This checker keeps DeriveBSD's generic authority-budget lane narrow and wired:
- `authority.budget` remains the authoritative component-runtime least-authority object
- `authority.budget.check` remains evidence-only
- `authority.exception` remains a field-scoped, timeboxed authoritative waiver
- the canonical example stays bound to the v0 dimensions and digest joins
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from cube_digest_lib import canonical_digest, load_json_strict_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
V0_DIMS = {"filesystem", "network", "devices", "trust", "observability"}


def load_json(rel: str) -> dict:
    return load_json_strict_text((ROOT / rel).read_text(encoding="utf-8"))


def digest(obj: dict) -> str:
    return canonical_digest(obj)


def main() -> int:
    errors: list[str] = []

    budget_schema = load_json("spec/authority.budget.schema.json")
    dims = set(((budget_schema.get("properties") or {}).get("dimensions") or {}).get("properties", {}).keys())
    if dims != V0_DIMS:
        errors.append(f"spec/authority.budget.schema.json dimensions must be exactly {sorted(V0_DIMS)}")
    if ((budget_schema.get("properties") or {}).get("dimensions") or {}).get("additionalProperties") is not False:
        errors.append("spec/authority.budget.schema.json dimensions must reject additionalProperties")

    check_schema = load_json("spec/authority.budget.check.schema.json")
    check_props = check_schema.get("properties") or {}
    if check_props.get("authority_semantics", {}).get("const") != "authority-budget-check-evidence-only":
        errors.append("spec/authority.budget.check.schema.json authority_semantics const must be authority-budget-check-evidence-only")
    if "authority_semantics" not in (check_schema.get("required") or []):
        errors.append("spec/authority.budget.check.schema.json missing required authority_semantics")

    budget = load_json("spec/examples/authority.budget.json")
    check = load_json("spec/examples/authority.budget.check.json")
    exc = load_json("spec/examples/authority.exception.json")

    budget_d = digest(budget)
    check_d = digest(check)

    if set((budget.get("dimensions") or {}).keys()) != V0_DIMS:
        errors.append("spec/examples/authority.budget.json dimensions must use the exact v0 dimension set")

    if check.get("budget_digest") != budget_d:
        errors.append("spec/examples/authority.budget.check.json budget_digest != computed digest of spec/examples/authority.budget.json")
    if exc.get("budget_digest") != budget_d:
        errors.append("spec/examples/authority.exception.json budget_digest != computed digest of spec/examples/authority.budget.json")
    if exc.get("check_digest") != check_d:
        errors.append("spec/examples/authority.exception.json check_digest != computed digest of spec/examples/authority.budget.check.json")

    if check.get("authority_semantics") != "authority-budget-check-evidence-only":
        errors.append("spec/examples/authority.budget.check.json authority_semantics must be authority-budget-check-evidence-only")
    if check.get("scope") != budget.get("scope"):
        errors.append("spec/examples/authority.budget.check.json scope must match spec/examples/authority.budget.json scope")
    if check.get("inputs") != budget.get("derived_from"):
        errors.append("spec/examples/authority.budget.check.json inputs must match spec/examples/authority.budget.json derived_from")
    if (exc.get("scope") or {}).get("subject") != budget.get("scope"):
        errors.append("spec/examples/authority.exception.json scope.subject must match spec/examples/authority.budget.json scope")

    deltas = check.get("deltas") or []
    if not deltas:
        errors.append("spec/examples/authority.budget.check.json must have at least one delta in the canonical example")
    else:
        delta_keys = {(d.get("dimension"), d.get("field"), d.get("classification")) for d in deltas}
        exc_scope = exc.get("scope") or {}
        exc_key = (exc_scope.get("dimension"), exc_scope.get("field"), exc_scope.get("classification"))
        if exc_key not in delta_keys:
            errors.append("spec/examples/authority.exception.json must waive a field that appears in spec/examples/authority.budget.check.json deltas")
        observed = None
        for d in deltas:
            if (d.get("dimension"), d.get("field"), d.get("classification")) == exc_key:
                observed = d.get("observed")
                break
        if observed is not None and exc_scope.get("allowed_value") != observed:
            errors.append("spec/examples/authority.exception.json scope.allowed_value must match the observed value for the waived delta in the canonical example")

    if not str(exc.get("expires_at", "")).endswith("Z"):
        errors.append("spec/examples/authority.exception.json expires_at must be an RFC3339 UTC timestamp in the canonical example")

    doc_checks = {
        "docs/298-authority-budgets-and-permission-drift-alarms.md": ["`authority.budget`", "`authority.budget.check`", "`authority.exception`", "component-runtime", "field-scoped"],
        "docs/297-component-descriptors-and-compiled-runtime-manifests.md": ["`authority.budget`", "`authority.budget.check`"],
        "docs/229-evidence-spine-overview.md": ["`authority.budget`", "`authority.budget.check`", "evidence-only"],
        "docs/494-authority-budget-policy-check-and-exception-boundary.md": ["`authority.budget`", "`authority.budget.check`", "`authority.exception`", "component-runtime", "timeboxed"],
        "adrs/ADR-0084-authority-budgets-and-exception-boundary.md": ["authority.budget", "authority.budget.check", "authority.exception", "filesystem", "observability"],
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

    print("Authority budget contract: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
