#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def rows(root: Path) -> list[dict[str, object]]:
    src = root / "specs" / "claim_classes.yaml"
    data = json.loads(src.read_text(encoding="utf-8"))
    out = []
    for row in data:
        out.append(
            {
                "id": row["id"],
                "title": row["title"],
                "evidence_class": row["evidence_class"],
                "strict_gate_required": bool(row["strict_gate_required"]),
                "required_checks": row["required_checks"],
                "required_artifacts": row["required_artifacts"],
            }
        )
    return out


def render(rows_: list[dict[str, object]]) -> str:
    lines = [
        "# Claim Matrix",
        "",
        "Generated from `specs/claim_classes.yaml`.",
        "",
        f"- total_claim_classes: {len(rows_)}",
        "",
        "| id | title | evidence_class | strict_gate_required | required_checks |",
        "|---|---|---|---|---|",
    ]
    for r in rows_:
        checks = "<br>".join(r["required_checks"])
        lines.append(
            f"| `{r['id']}` | {r['title']} | `{r['evidence_class']}` | {'yes' if r['strict_gate_required'] else 'no'} | {checks} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    data = rows(root)

    out_json = root / "artifacts" / "reports" / "claim_matrix.json"
    out_md = root / "docs" / "CLAIM_MATRIX.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps({"claims": data}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = render(data)

    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"claim-matrix: wrote {out_md}")
        print(f"claim-matrix: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("claim-matrix: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"claim-matrix: ok ({len(data)} claim classes)")
    print(f"claim-matrix: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
