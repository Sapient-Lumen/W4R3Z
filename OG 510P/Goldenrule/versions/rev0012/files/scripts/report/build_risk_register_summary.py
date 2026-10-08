#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def rows(root: Path) -> list[dict[str, object]]:
    raw = json.loads((root / "specs" / "risk_register.yaml").read_text(encoding="utf-8"))
    out = []
    for r in raw:
        out.append(
            {
                "id": r["id"],
                "status": r["status"],
                "domain": r["domain"],
                "severity": r["severity"],
                "likelihood": r["likelihood"],
                "owner": r["owner"],
                "review_date": r["review_date"],
                "summary": r["summary"],
            }
        )
    return sorted(out, key=lambda r: str(r["id"]))


def render(rows_: list[dict[str, object]]) -> str:
    lines = [
        "# Risk Register",
        "",
        "Generated from `specs/risk_register.yaml`.",
        "",
        f"- total_risks: {len(rows_)}",
        "",
        "| id | status | domain | severity | likelihood | owner | review_date | summary |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows_:
        lines.append(
            "| `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | `{}` | {} |".format(
                r["id"],
                r["status"],
                r["domain"],
                r["severity"],
                r["likelihood"],
                r["owner"],
                r["review_date"],
                r["summary"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    data = rows(root)

    out_json = root / "artifacts" / "reports" / "risk_register_summary.json"
    out_md = root / "docs" / "RISK_REGISTER.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps({"risks": data}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = render(data)

    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"risk-register: wrote {out_md}")
        print(f"risk-register: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("risk-register: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"risk-register: ok ({len(data)} risks)")
    print(f"risk-register: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
