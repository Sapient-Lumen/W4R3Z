#!/usr/bin/env python3
"""Check that generated docs are up to date.

Currently checks:
- docs/412-product-profile-matrix.md (generated from spec/examples/product.profiles.json)
- docs/420-context-pack.md and docs/_generated/context_pack.json (generated from CHANGELOG + runbook + risks + profiles)
- docs/414-doc-catalog.md and docs/_generated/doc_catalog.json (generated from docs/)
- docs/415-risk-register-index.md and docs/_generated/risk_register.json (generated from docs/266)
- docs/418-artifact-index.md and docs/_generated/artifact_index.json (generated from spec/ + spec/examples)

r531 refactor note:
  This checker calls generator functions directly instead of spawning one Python
  subprocess per surface.  The old pipe-backed subprocess loop was correct but
  brittle in short interactive runners after the generated surfaces grew.  The
  direct-call path keeps the generated-doc contract identical and avoids a
  release-critical timeout that was not caused by stale output.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import gen_artifact_index  # noqa: E402
import gen_context_pack  # noqa: E402
import gen_doc_catalog  # noqa: E402
import gen_product_profile_matrix  # noqa: E402
import gen_risk_register_index  # noqa: E402

DST_MATRIX = ROOT / "docs" / "412-product-profile-matrix.md"
DST_CONTEXT_MD = ROOT / "docs" / "420-context-pack.md"
DST_CONTEXT_JSON = ROOT / "docs" / "_generated" / "context_pack.json"
DST_CATALOG_MD = ROOT / "docs" / "414-doc-catalog.md"
DST_CATALOG_JSON = ROOT / "docs" / "_generated" / "doc_catalog.json"
DST_RISK_MD = ROOT / "docs" / "415-risk-register-index.md"
DST_RISK_JSON = ROOT / "docs" / "_generated" / "risk_register.json"
DST_ARTIFACT_MD = ROOT / "docs" / "418-artifact-index.md"
DST_ARTIFACT_JSON = ROOT / "docs" / "_generated" / "artifact_index.json"


def _read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""


def _context_payload() -> tuple[str, str]:
    archive_version = gen_context_pack._top_version()
    recent_changes = gen_context_pack._recent_changes()
    must_read = gen_context_pack._extract_must_read(gen_context_pack._read(gen_context_pack.RUNBOOK))
    profiles = gen_context_pack._profiles_summary()
    risks = gen_context_pack._risk_summaries()
    return (
        gen_context_pack.render_markdown(archive_version, recent_changes, must_read, profiles, risks),
        gen_context_pack.render_json(archive_version, recent_changes, must_read, profiles, risks),
    )


def main() -> int:
    stale: list[str] = []

    expected = gen_product_profile_matrix.render()
    if _read(DST_MATRIX) != expected:
        stale.append(str(DST_MATRIX))

    expected_md, expected_json = _context_payload()
    if _read(DST_CONTEXT_MD) != expected_md:
        stale.append(str(DST_CONTEXT_MD))
    if _read(DST_CONTEXT_JSON) != expected_json:
        stale.append(str(DST_CONTEXT_JSON))

    catalog_rows = gen_doc_catalog.collect()
    expected = gen_doc_catalog.emit_md(catalog_rows)
    if _read(DST_CATALOG_MD) != expected:
        stale.append(str(DST_CATALOG_MD))
    expected = gen_doc_catalog.emit_json(catalog_rows)
    if _read(DST_CATALOG_JSON) != expected:
        stale.append(str(DST_CATALOG_JSON))

    risk_rows = gen_risk_register_index.collect()
    expected = gen_risk_register_index.emit_md(risk_rows)
    if _read(DST_RISK_MD) != expected:
        stale.append(str(DST_RISK_MD))
    expected = gen_risk_register_index.emit_json(risk_rows)
    if _read(DST_RISK_JSON) != expected:
        stale.append(str(DST_RISK_JSON))

    artifact_rows = gen_artifact_index.build_rows()
    expected = gen_artifact_index.render_markdown(artifact_rows)
    if _read(DST_ARTIFACT_MD) != expected:
        stale.append(str(DST_ARTIFACT_MD))
    expected = gen_artifact_index.render_json(artifact_rows)
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
