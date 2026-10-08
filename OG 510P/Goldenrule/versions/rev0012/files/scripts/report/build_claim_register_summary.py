#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def rows(root: Path) -> list[dict[str, object]]:
    claims = json.loads((root / "specs" / "claim_register.yaml").read_text(encoding="utf-8"))
    classes = json.loads((root / "specs" / "claim_classes.yaml").read_text(encoding="utf-8"))
    strict = {str(c["id"]): bool(c["strict_gate_required"]) for c in classes}

    out = []
    for c in claims:
        out.append(
            {
                "id": c["id"],
                "claim_class_id": c["claim_class_id"],
                "status": c["status"],
                "strict_gate_required": strict.get(str(c["claim_class_id"]), False),
                "owner": c["owner"],
                "summary": c["summary"],
                "evidence_link_count": len(c.get("evidence_links", [])),
            }
        )
    return sorted(out, key=lambda r: str(r["id"]))


def render(rows_: list[dict[str, object]]) -> str:
    lines = [
        "# Claim Register",
        "",
        "Generated from `specs/claim_register.yaml`.",
        "",
        f"- total_claims: {len(rows_)}",
        "",
        "| id | class | status | strict_gate_required | owner | evidence_links | summary |",
        "|---|---|---|---|---|---:|---|",
    ]
    for r in rows_:
        lines.append(
            "| `{}` | `{}` | `{}` | {} | `{}` | {} | {} |".format(
                r["id"],
                r["claim_class_id"],
                r["status"],
                "yes" if r["strict_gate_required"] else "no",
                r["owner"],
                r["evidence_link_count"],
                r["summary"],
            )
        )
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    write = "--write" in sys.argv
    root = Path(__file__).resolve().parents[2]
    data = rows(root)

    out_json = root / "artifacts" / "reports" / "claim_register_summary.json"
    out_md = root / "docs" / "CLAIM_REGISTER.md"
    out_json.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(json.dumps({"claims": data}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = render(data)

    if write or not out_md.exists():
        out_md.write_text(expected, encoding="utf-8")
        print(f"claim-register: wrote {out_md}")
        print(f"claim-register: wrote {out_json}")
        return 0

    current = out_md.read_text(encoding="utf-8")
    if current != expected:
        print("claim-register: drift detected; run with --write", file=sys.stderr)
        return 1

    print(f"claim-register: ok ({len(data)} claims)")
    print(f"claim-register: wrote {out_json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
