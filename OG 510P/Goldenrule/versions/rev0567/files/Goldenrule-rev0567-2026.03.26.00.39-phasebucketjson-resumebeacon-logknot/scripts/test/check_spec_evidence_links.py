#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    ledger = root / "specs" / "spec_ledger.yaml"
    adr_index = root / "docs" / "adr" / "INDEX.md"
    out = root / "artifacts" / "reports" / "spec_evidence_links.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    entries = json.loads(ledger.read_text(encoding="utf-8"))
    adr_text = adr_index.read_text(encoding="utf-8") if adr_index.exists() else ""

    checked = 0
    missing: list[dict[str, str]] = []

    for e in entries:
        sid = str(e.get("id", ""))
        links = e.get("evidence_links", [])
        if not isinstance(links, list):
            continue
        for raw in links:
            if not isinstance(raw, str) or not raw.strip():
                continue
            checked += 1
            link = raw.strip()
            if link.startswith("ADR-"):
                if link not in adr_text:
                    missing.append({"spec_id": sid, "link": link, "reason": "missing ADR reference"})
                continue
            path = (root / link).resolve()
            if not path.exists():
                missing.append({"spec_id": sid, "link": link, "reason": "missing path"})

    payload = {"checked": checked, "missing": missing, "missing_count": len(missing)}
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if missing:
        for m in missing:
            print(
                f"spec-evidence: missing spec={m['spec_id']} link={m['link']} reason={m['reason']}",
                file=sys.stderr,
            )
        return 1

    print(f"spec-evidence: ok ({checked} links)")
    print(f"spec-evidence: wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
