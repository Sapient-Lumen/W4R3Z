#!/usr/bin/env python3
"""Generate an audit report for public-fingerprint portable-name warnings."""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
REV = VERSION.removeprefix("v").zfill(4)
PF = ROOT / "tools" / "public_fingerprint_report.py"
CMP = ROOT / "tools" / "compare_public_fingerprints.py"
PACKET = ROOT / "artifacts" / "examples" / "evidence_packet_ed25519_threshold2_minimal"
OUT_JSON = ROOT / "artifacts" / "reports" / f"public-fingerprint-portable-name-surface-audit-rev{REV}.json"
OUT_MD = ROOT / "artifacts" / "reports" / f"public-fingerprint-portable-name-surface-audit-rev{REV}.md"


def helper_profile() -> str:
    text = PF.read_text(encoding="utf-8")
    m = re.search(r'^REPORT_FORMAT_VERSION\s*=\s*["\']([^"\']+)["\']', text, re.M)
    if not m:
        raise SystemExit("could not read public fingerprint helper profile")
    return m.group(1)


def run_json(args: list[str], *, want_rc: int = 0) -> dict:
    proc = subprocess.run([sys.executable, *args], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if proc.returncode != want_rc:
        raise SystemExit(f"command failed rc={proc.returncode} want={want_rc}: {' '.join(args)}\n{proc.stdout}\n{proc.stderr}")
    return json.loads(proc.stdout)


def main() -> int:
    profile = helper_profile()
    with tempfile.TemporaryDirectory(prefix="tes-pubfp-portable-audit-") as td:
        t = Path(td)
        bad = t / "portable-name"
        shutil.copytree(PACKET, bad)
        (bad / "bad:name.txt").write_text("colon route\n", encoding="utf-8")
        (bad / "CON.txt").write_text("reserved device route\n", encoding="utf-8")
        (bad / "notes" / "dir.").mkdir(parents=True, exist_ok=True)
        (bad / "notes" / "dir." / "ok.md").write_text("trailing dot route\n", encoding="utf-8")
        rep = run_json([str(PF), str(bad), "--stable"])
        cmp = run_json([str(CMP), str(PACKET), str(bad), "--json"], want_rc=2)

    warnings = [str(w) for w in rep.get("warnings") or []]
    expected_prefixes = [
        "public_relpath_portable_component_rejected_for_hash:bad:name.txt:windows_reserved_character",
        "public_relpath_portable_component_rejected_for_hash:CON.txt:windows_reserved_device_name",
        "public_relpath_portable_component_rejected_for_hash:notes/dir./ok.md:windows_trailing_space_or_dot",
    ]
    missing = [p for p in expected_prefixes if not any(w.startswith(p) for w in warnings)]
    result = {
        "archive_version": VERSION,
        "public_fingerprint_profile": profile,
        "audit": "public_fingerprint_portable_name_surface",
        "positive_packet": str(PACKET.relative_to(ROOT)),
        "portable_warning_count": len(warnings),
        "expected_warning_prefixes": expected_prefixes,
        "missing_expected_warning_prefixes": missing,
        "compare_status": cmp.get("status"),
        "compare_exit_expected_nonzero": True,
        "failure_count": len(missing) + (0 if cmp.get("status") == "UNSAFE_WARNING" else 1),
        "warnings": warnings,
    }
    OUT_JSON.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    lines = [
        f"# Public fingerprint portable-name surface audit — rev{REV}\n\n",
        "**Track:** Shared\n\n",
        "This generated audit proves that the public-fingerprint helper now treats cross-platform reserved public path components as unsafe comparison routes. Strict policy verification already fails closed when public-fingerprint warnings are present.\n\n",
        f"- Archive version: `{VERSION}`\n",
        f"- Public-fingerprint profile: `{profile}`\n",
        f"- Portable warning count: `{result['portable_warning_count']}`\n",
        f"- Compare status for clean-vs-reserved-name packet: `{result['compare_status']}`\n",
        f"- Failure count: `{result['failure_count']}`\n\n",
        "## Expected warnings\n\n",
    ]
    for prefix in expected_prefixes:
        lines.append(f"- `{prefix}`\n")
    OUT_MD.write_text("".join(lines), encoding="utf-8")
    print(f"WROTE {OUT_JSON.relative_to(ROOT)} failure_count={result['failure_count']}")
    return 0 if result["failure_count"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
