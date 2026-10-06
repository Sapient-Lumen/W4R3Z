#!/usr/bin/env python3
"""Check that generated docs are up to date.

Currently checks:
- docs/412-product-profile-matrix.md (generated from spec/examples/product.profiles.json)
- docs/420-context-pack.md and docs/_generated/context_pack.json (generated from CHANGELOG + runbook + risks + profiles)
- docs/414-doc-catalog.md and docs/_generated/doc_catalog.json (generated from docs/)
- docs/415-risk-register-index.md and docs/_generated/risk_register.json (generated from docs/266)
- docs/418-artifact-index.md and docs/_generated/artifact_index.json (generated from spec/ + spec/examples)

Usage:
  python3 tools/check_generated_docs.py

Exit codes:
  0: OK
  1: At least one generated doc is stale
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GEN_MATRIX = ROOT / "tools" / "gen_product_profile_matrix.py"
DST_MATRIX = ROOT / "docs" / "412-product-profile-matrix.md"

GEN_CONTEXT = ROOT / "tools" / "gen_context_pack.py"
DST_CONTEXT_MD = ROOT / "docs" / "420-context-pack.md"
DST_CONTEXT_JSON = ROOT / "docs" / "_generated" / "context_pack.json"

GEN_CATALOG = ROOT / "tools" / "gen_doc_catalog.py"
DST_CATALOG_MD = ROOT / "docs" / "414-doc-catalog.md"
DST_CATALOG_JSON = ROOT / "docs" / "_generated" / "doc_catalog.json"

GEN_RISK = ROOT / "tools" / "gen_risk_register_index.py"
DST_RISK_MD = ROOT / "docs" / "415-risk-register-index.md"
DST_RISK_JSON = ROOT / "docs" / "_generated" / "risk_register.json"

GEN_ARTIFACT = ROOT / "tools" / "gen_artifact_index.py"
DST_ARTIFACT_MD = ROOT / "docs" / "418-artifact-index.md"
DST_ARTIFACT_JSON = ROOT / "docs" / "_generated" / "artifact_index.json"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def _run(cmd: list[str]) -> tuple[int, str, str]:
    p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return int(p.returncode), p.stdout, p.stderr


def _expect_stdout(gen: Path, args: list[str] | None = None) -> str:
    cmd = [sys.executable, str(gen)]
    if args:
        cmd.extend(args)
    rc, out, err = _run(cmd)
    if rc != 0:
        print("Failed to run generator:", gen)
        sys.stdout.write(out)
        sys.stderr.write(err)
        raise RuntimeError(str(gen))
    return out


def main() -> int:
    stale: list[str] = []

    # 412: product profile matrix (md)
    expected = _expect_stdout(GEN_MATRIX)
    if _read(DST_MATRIX) != expected:
        stale.append(str(DST_MATRIX))

    # 420: context pack (md + json)
    expected = _expect_stdout(GEN_CONTEXT)
    if _read(DST_CONTEXT_MD) != expected:
        stale.append(str(DST_CONTEXT_MD))
    expected = _expect_stdout(GEN_CONTEXT, ["--json"])
    if _read(DST_CONTEXT_JSON) != expected:
        stale.append(str(DST_CONTEXT_JSON))

    # 414: doc catalog (md + json)
    expected = _expect_stdout(GEN_CATALOG)
    if _read(DST_CATALOG_MD) != expected:
        stale.append(str(DST_CATALOG_MD))
    expected = _expect_stdout(GEN_CATALOG, ["--json"])
    if _read(DST_CATALOG_JSON) != expected:
        stale.append(str(DST_CATALOG_JSON))

    # 415: risk register index (md + json)
    expected = _expect_stdout(GEN_RISK)
    if _read(DST_RISK_MD) != expected:
        stale.append(str(DST_RISK_MD))
    expected = _expect_stdout(GEN_RISK, ["--json"])
    if _read(DST_RISK_JSON) != expected:
        stale.append(str(DST_RISK_JSON))

    # 418: artifact index (md + json)
    expected = _expect_stdout(GEN_ARTIFACT)
    if _read(DST_ARTIFACT_MD) != expected:
        stale.append(str(DST_ARTIFACT_MD))
    expected = _expect_stdout(GEN_ARTIFACT, ["--json"])
    if _read(DST_ARTIFACT_JSON) != expected:
        stale.append(str(DST_ARTIFACT_JSON))

    if stale:
        print("Generated doc mismatch (stale outputs):")
        for p in stale:
            print(f"- {p}")
        print("\nFix:")
        print("- python3 tools/gen_product_profile_matrix.py --write")
        print("- python3 tools/gen_context_pack.py --write")
        print("- python3 tools/gen_doc_catalog.py --write")
        print("- python3 tools/gen_risk_register_index.py --write")
        print("- python3 tools/gen_artifact_index.py --write")
        return 1

    print("Generated docs check OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
