#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc

INPUT = METADATA_DIR / "route_redirect_ledger.json"
OUT_JSON = GENERATED / "ROUTE_REDIRECT_LEDGER.json"
OUT_MD = GENERATED / "ROUTE_REDIRECT_LEDGER.md"


def render_markdown(data: dict) -> str:
    lines = [
        "# Route redirect ledger",
        "",
        f"Generated for `{data['revision']}` from `metadata/route_redirect_ledger.json`.",
        "",
        "## Holding",
        "",
        data.get("holding", ""),
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "| --- | ---: |",
        f"| Ledgers | {data['ledger_count']} |",
        f"| Redirect rows | {data['redirect_row_count']} |",
        f"| Rows mapped but not retired | {data['status_counts'].get('mapped_not_retired', 0)} |",
        f"| Deletion-authorized ledgers | {data['deletion_authorized_count']} |",
        f"| Reader-visible surface links | {data.get('reader_surface_count', 0)} |",
        "",
        "## Ledgers",
        "",
        "| Ledger | Source | Successor | Rows | Deletion authorized | Reader redirect | Reader surfaces | Final review | Final status |",
        "| --- | --- | --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for ledger in data.get("ledgers", []):
        final_review = f"note `{ledger.get('final_preservation_review_note')}`" if ledger.get("final_preservation_review_note") else "—"
        final_status = ledger.get("final_preservation_review_status", "—")
        lines.append(
            f"| `{ledger['ledger_id']}` | `{ledger['source_note']}` | `{ledger['successor_note']}` | {ledger['redirect_row_count']} | {ledger['deletion_authorization']} | {ledger.get('reader_redirect_status', '—')} | {len(ledger.get('reader_redirect_surfaces', []))} | {final_review} | {final_status} |"
        )
    lines.extend([
        "",
        "## Reader-visible routes",
        "",
        "| Ledger | Surface | Purpose |",
        "| --- | --- | --- |",
    ])
    for ledger in data.get("ledgers", []):
        for surface in ledger.get("reader_redirect_surfaces", []):
            if isinstance(surface, dict):
                lines.append(f"| `{ledger['ledger_id']}` | `{surface.get('surface', '')}` | {surface.get('purpose', '')} |")
            else:
                lines.append(f"| `{ledger['ledger_id']}` | `{surface}` | — |")
    lines.extend([
        "",
        "## Redirect rows",
        "",
        "| Ledger | Element | Successor section | Tests | Source keys | Applied examples | Status |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row in data.get("redirect_rows", []):
        tests = ", ".join(f"`{t}`" for t in row.get("test_ids", [])) or "—"
        keys = ", ".join(f"`{k}`" for k in row.get("source_keys", [])[:5])
        if len(row.get("source_keys", [])) > 5:
            keys += ", …"
        examples = ", ".join(f"`{n}`" for n in row.get("applied_examples", [])) or "—"
        lines.append(
            f"| `{row['ledger_id']}` | `{row['element_id']}` {row.get('protected_element', '')} | {row.get('successor_section', '')} | {tests} | {keys} | {examples} | {row.get('status', '')} |"
        )
    lines.extend(["", "## Unresolved before retirement", ""])
    for ledger in data.get("ledgers", []):
        lines.append(f"### `{ledger['ledger_id']}`")
        for item in ledger.get("unresolved_before_retirement", []):
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
    ledgers = []
    redirect_rows = []
    status_counts: Counter[str] = Counter()
    deletion_authorized_count = 0
    for ledger_id, ledger in sorted(payload.get("ledgers", {}).items()):
        rows = ledger.get("redirect_rows", [])
        if ledger.get("deletion_authorization") is True:
            deletion_authorized_count += 1
        ledgers.append({"ledger_id": ledger_id, **{k: v for k, v in ledger.items() if k != "redirect_rows"}, "redirect_row_count": len(rows)})
        for row in rows:
            status_counts[row.get("status", "unknown")] += 1
            redirect_rows.append({"ledger_id": ledger_id, "source_note": ledger.get("source_note"), "successor_note": ledger.get("successor_note"), **row})
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        "generated_from": ["metadata/route_redirect_ledger.json"],
        "holding": payload.get("holding", ""),
        "ledger_count": len(ledgers),
        "redirect_row_count": len(redirect_rows),
        "deletion_authorized_count": deletion_authorized_count,
        "reader_surface_count": sum(len(ledger.get('reader_redirect_surfaces', [])) for ledger in ledgers),
        "status_counts": dict(sorted(status_counts.items())),
        "ledgers": ledgers,
        "redirect_rows": redirect_rows,
    }
    OUT_JSON.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(data), encoding="utf-8")
    print("OK: wrote generated/ROUTE_REDIRECT_LEDGER.json and generated/ROUTE_REDIRECT_LEDGER.md")


if __name__ == "__main__":
    main()
