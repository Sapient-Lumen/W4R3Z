#!/usr/bin/env python3
"""scripts/check_example_packet_readmes.py

Release-gate drift firewall: shipped example evidence packets must include a
small human note.

Why:
- Example packets are part of the public interface for implementers.
- Without a short README, the purpose/scope of an example tends to drift
  (especially when filenames are content-addressed).

Policy:
- stdlib-only
- bounded: requires a `README.txt` in each `artifacts/examples/evidence_packet_*`
  directory and enforces a small size cap.
- actionable: each README must include a one-line verifier command.
- coherent: README must agree with the packet's envelope kind(s) + schema(s).

Notes on coherence rules (intentionally simple):
- If the packet contains exactly one envelope, README must contain:
  - `Example evidence packet for <kind>.`
  - `- Payload: <payload_schema>`
- If the packet contains multiple envelopes, README must contain:
  - `Example evidence packet bundle.`
  - `- Envelopes: <kind1>; <kind2>; ...` (kinds must appear as substrings)
  - `- Payload schemas: <schema1>; <schema2>; ...` (schemas must appear)

These conventions keep READMEs small while preventing "example rot".
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "artifacts" / "examples"

# Keep READMEs intentionally small to avoid archive bloat.
MAX_BYTES = 1024


def find_packets() -> list[Path]:
    out: list[Path] = []
    if not EXAMPLES.exists():
        return out
    for p in sorted(EXAMPLES.iterdir()):
        if p.is_dir() and p.name.startswith("evidence_packet_"):
            if (p / "manifest.json").exists() and (p / "envelopes").exists() and (p / "objects").exists():
                out.append(p)
    return out


def read_envelope_meta(packet_dir: Path) -> tuple[list[str], list[str]]:
    env_dir = packet_dir / "envelopes"
    kinds: list[str] = []
    schemas: list[str] = []
    for ep in sorted(env_dir.glob("*.json")):
        try:
            obj = json.loads(ep.read_text(encoding="utf-8"))
        except Exception:
            continue
        k = obj.get("kind")
        s = obj.get("payload_schema")
        if isinstance(k, str):
            kinds.append(k)
        if isinstance(s, str):
            schemas.append(s)
    return kinds, schemas


def main() -> int:
    failures: list[str] = []
    for p in find_packets():
        rp = p / "README.txt"
        if not rp.exists():
            failures.append(f"missing README.txt in {p.relative_to(ROOT)}")
            continue

        try:
            b = rp.read_bytes()
        except Exception as e:
            failures.append(f"unreadable README.txt in {p.relative_to(ROOT)}: {e}")
            continue

        if not b.strip():
            failures.append(f"empty README.txt in {p.relative_to(ROOT)}")
        if len(b) > MAX_BYTES:
            failures.append(
                f"README.txt too large in {p.relative_to(ROOT)}: {len(b)} bytes (cap {MAX_BYTES})"
            )

        t = b.decode("utf-8", errors="replace")

        # Actionability: require a stable verification hint.
        if "tools/observer_verify_packet.py" not in t:
            failures.append(f"README.txt missing verifier command in {p.relative_to(ROOT)}")
        verify_lines = [ln.strip() for ln in t.splitlines() if ln.strip().startswith("Verify:")]
        if len(verify_lines) != 1:
            failures.append(
                f"README.txt must include exactly one 'Verify:' line in {p.relative_to(ROOT)} (found {len(verify_lines)})"
            )
        else:
            # Require the command to verify THIS packet directory (no absolute paths).
            m = re.match(r"^Verify:\s*python3\s+tools/observer_verify_packet\.py\s+(.+)$", verify_lines[0])
            if not m:
                failures.append(
                    f"Verify line must be: 'Verify: python3 tools/observer_verify_packet.py artifacts/examples/<packet>' in {p.relative_to(ROOT)}"
                )
            else:
                target = m.group(1).strip()
                if target.startswith("/"):
                    failures.append(f"Verify path must be relative (no leading /) in {p.relative_to(ROOT)}")
                expected = f"artifacts/examples/{p.name}"
                if target != expected:
                    failures.append(
                        f"Verify path mismatch in {p.relative_to(ROOT)}: got '{target}', expected '{expected}'"
                    )
                if not (ROOT / target).exists():
                    failures.append(f"Verify path does not exist in {p.relative_to(ROOT)}: {target}")

        # Coherence: README must reflect envelope kind(s) and schema(s).
        kinds, schemas = read_envelope_meta(p)
        kinds_u = sorted(set(kinds))
        schemas_u = sorted(set(schemas))

        # Determine whether this is a single-envelope packet.
        env_count = len(list((p / "envelopes").glob("*.json")))
        if env_count == 1 and kinds_u and schemas_u:
            # First non-empty line must declare the kind.
            first = next((ln.strip() for ln in t.splitlines() if ln.strip()), "")
            want = f"Example evidence packet for {kinds_u[0]}."
            if first != want:
                failures.append(
                    f"README first line must be '{want}' in {p.relative_to(ROOT)} (got '{first}')"
                )
            # Must contain payload schema line.
            if f"- Payload: {schemas_u[0]}" not in t:
                failures.append(
                    f"README must include '- Payload: {schemas_u[0]}' in {p.relative_to(ROOT)}"
                )
        else:
            # Multi-envelope bundle rules.
            first = next((ln.strip() for ln in t.splitlines() if ln.strip()), "")
            if first != "Example evidence packet bundle.":
                failures.append(
                    f"README first line must be 'Example evidence packet bundle.' in {p.relative_to(ROOT)} (got '{first}')"
                )
            if "- Envelopes:" not in t:
                failures.append(f"README bundle must include '- Envelopes:' in {p.relative_to(ROOT)}")
            if "- Payload schemas:" not in t:
                failures.append(f"README bundle must include '- Payload schemas:' in {p.relative_to(ROOT)}")
            for k in kinds_u:
                if k not in t:
                    failures.append(f"README bundle missing envelope kind '{k}' in {p.relative_to(ROOT)}")
            for s in schemas_u:
                if s not in t:
                    failures.append(f"README bundle missing payload schema '{s}' in {p.relative_to(ROOT)}")

    if failures:
        for f in failures:
            print("ERROR:", f, file=sys.stderr)
        return 2

    print(f"PASS: example packet README.txt present + coherent + actionable (cap {MAX_BYTES} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
