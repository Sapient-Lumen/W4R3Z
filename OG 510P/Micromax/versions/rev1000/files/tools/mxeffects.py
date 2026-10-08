#!/usr/bin/env python3
"""Emit the generated Micromax effect/resource contract slice."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from micromax_editor.effect_contracts import (  # noqa: E402
    EFFECT_CONTRACT_HELP_DOC,
    effect_contract_help_markdown,
    effect_resource_contract,
    validate_effect_resource_contract,
)


def _load_audit_payload() -> dict[str, Any]:
    tools_dir = ROOT / "tools"
    if str(tools_dir) not in sys.path:
        sys.path.insert(0, str(tools_dir))
    try:
        import mxaudit  # type: ignore[import-not-found]
    except Exception:
        return {}
    try:
        data = mxaudit.payload(limit=3)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _current_rev(audit_payload: dict[str, Any]) -> int | None:
    value = audit_payload.get("rev")
    return int(value) if isinstance(value, int) else None


def _human(payload: dict[str, Any], *, errors: list[str]) -> str:
    lines = [
        f"Micromax effect/resource contract ({payload.get('schema')})",
        f"Rev: {payload.get('rev')}",
        f"Rows: {payload.get('row_count')}",
        "",
        "High-risk host effects:",
    ]
    for row in payload.get("rows") or []:
        if not isinstance(row, dict):
            continue
        budgets = row.get("budgets") if isinstance(row.get("budgets"), dict) else {}
        budget_bits = ", ".join(f"{key}={budgets[key]}" for key in sorted(budgets))
        cap = row.get("capability_option") or row.get("capability_kind") or "n/a"
        lines.append(
            f"  - {row.get('name')}: {row.get('effect_class')} "
            f"via {cap}; {budget_bits}"
        )
    if errors:
        lines.extend(["", "Contract errors:", *[f"  - {error}" for error in errors]])
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--markdown", action="store_true", help="emit the installed help markdown page")
    parser.add_argument("--write-help-doc", action="store_true", help="write the generated installed help markdown page")
    parser.add_argument("--check-help-doc", action="store_true", help="fail when the installed help markdown page is stale")
    parser.add_argument("--check", action="store_true", help="fail on stale/missing contract facts")
    args = parser.parse_args(argv)

    audit_payload = _load_audit_payload()
    payload = effect_resource_contract(rev=_current_rev(audit_payload), audit_payload=audit_payload)
    errors = validate_effect_resource_contract(payload)
    markdown = effect_contract_help_markdown(payload)
    help_doc_path = ROOT / EFFECT_CONTRACT_HELP_DOC
    if args.write_help_doc:
        help_doc_path.parent.mkdir(parents=True, exist_ok=True)
        help_doc_path.write_text(markdown, encoding="utf-8")
    help_doc_errors: list[str] = []
    if args.check_help_doc:
        current = help_doc_path.read_text(encoding="utf-8") if help_doc_path.exists() else ""
        if current != markdown:
            help_doc_errors.append(f"stale generated help doc: {EFFECT_CONTRACT_HELP_DOC}")
    all_errors = [*errors, *help_doc_errors]
    if args.json:
        emitted = dict(payload)
        emitted["help_doc"] = {
            "path": EFFECT_CONTRACT_HELP_DOC,
            "ok": not help_doc_errors,
            "errors": help_doc_errors,
        }
        emitted["checks"] = {"ok": not all_errors, "errors": all_errors}
        print(json.dumps(emitted, indent=2, sort_keys=True))
    elif args.markdown or args.write_help_doc:
        sys.stdout.write(markdown)
    else:
        sys.stdout.write(_human(payload, errors=all_errors))
    return 1 if (args.check or args.check_help_doc) and all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
