#!/usr/bin/env python3
"""Generate a deterministic artifact index (schema → kind → examples).

This is an 'amnesia resistor' for the archive: it gives humans/LLMs a single place
to look up the canonical schema for a given artifact kind and find its example(s).

Outputs:
  - Markdown (stdout): docs/418-artifact-index.md content
  - JSON (stdout with --json): docs/_generated/artifact_index.json content

Write outputs to the repo:
  python3 tools/gen_artifact_index.py --write

Notes:
  - deterministic output (no timestamps)
  - repo-relative paths only
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "spec"
EXAMPLES = SPEC / "examples"
DOCS = ROOT / "docs"
CHANGELOG = ROOT / "CHANGELOG.md"

OUT_MD = DOCS / "418-artifact-index.md"
OUT_JSON = DOCS / "_generated" / "artifact_index.json"


@dataclass(frozen=True)
class ArtifactRow:
    kind: str
    category: str
    schema: str
    examples: list[str]
    title: str


def _read_json(p: Path) -> Any:
    return json.loads(p.read_text(encoding="utf-8"))


def _top_version() -> str:
    import re
    txt = CHANGELOG.read_text(encoding="utf-8")
    m = re.search(r"^##\s+(\S+)\s*$", txt, re.MULTILINE)
    return m.group(1) if m else "<generated>"


def _kind_from_schema(schema: dict[str, Any]) -> str | None:
    # Prefer root `properties.kind` singleton (const or single-value enum).
    if schema.get("type") == "object":
        props = schema.get("properties", {})
        k = props.get("kind")
        if isinstance(k, dict):
            if "const" in k:
                return str(k["const"])
            if "enum" in k and isinstance(k["enum"], list) and len(k["enum"]) == 1:
                return str(k["enum"][0])

    # Fall back: search for any nested `kind` singleton.
    def walk(node: Any) -> str | None:
        if isinstance(node, dict):
            if "kind" in node and isinstance(node["kind"], dict):
                kk = node["kind"]
                if "const" in kk:
                    return str(kk["const"])
                if "enum" in kk and isinstance(kk["enum"], list) and len(kk["enum"]) == 1:
                    return str(kk["enum"][0])
            for v in node.values():
                r = walk(v)
                if r:
                    return r
        elif isinstance(node, list):
            for v in node:
                r = walk(v)
                if r:
                    return r
        return None

    return walk(schema)


def _category_from_name(name: str) -> str:
    # Keep it simple and stable: categorize based on filename suffixes.
    for suf in [
        ".plan.schema.json",
        ".receipt.schema.json",
        ".event.schema.json",
        ".report.schema.json",
        ".registry.schema.json",
        ".diff.schema.json",
    ]:
        if name.endswith(suf):
            return suf.split(".")[1]  # plan/receipt/event/report/registry/diff
    return "schema"


def build_rows() -> list[ArtifactRow]:
    rows: list[ArtifactRow] = []
    for schema_path in sorted(SPEC.glob("*.schema.json")):
        obj = _read_json(schema_path)
        title = str(obj.get("title", "")).strip()
        kind = _kind_from_schema(obj) or schema_path.name.replace(".schema.json", "")
        category = _category_from_name(schema_path.name)

        ex_base = schema_path.name.replace(".schema.json", ".json")
        ex_path = EXAMPLES / ex_base
        examples: list[str] = []
        if ex_path.exists():
            examples.append(str(ex_path.relative_to(ROOT).as_posix()))

        rows.append(
            ArtifactRow(
                kind=kind,
                category=category,
                schema=str(schema_path.relative_to(ROOT).as_posix()),
                examples=examples,
                title=title,
            )
        )

    # Deterministic ordering: category, then kind, then schema path.
    rows.sort(key=lambda r: (r.category, r.kind, r.schema))
    return rows


def render_json(rows: list[ArtifactRow]) -> str:
    payload = {
        "version": 1,
        "artifacts": [asdict(r) for r in rows],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def render_markdown(rows: list[ArtifactRow]) -> str:
    cats: dict[str, int] = {}
    for r in rows:
        cats[r.category] = cats.get(r.category, 0) + 1
    cat_lines = "\n".join([f"- **{k}**: {cats[k]}" for k in sorted(cats.keys())])

    lines: list[str] = []
    lines.append("# Artifact index (generated)")
    lines.append("")
    lines.append("**Tier:** A")
    lines.append("**Profiles:** A, B, C, D")
    lines.append("**Pillars:** operability, reproducibility")
    lines.append("")
    lines.append("This page is generated from `spec/` (schemas) and `spec/examples/`.")
    lines.append("It is an *amnesia resistor*: a stable lookup from `kind` → schema → example.")
    lines.append("")
    lines.append("**Counts by category:**")
    lines.append(cat_lines)
    lines.append("")
    lines.append("Full machine-readable index: `docs/_generated/artifact_index.json`.")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    lines.append("| kind | category | schema | example | title |")
    lines.append("|---|---|---|---|---|")
    for r in rows:
        ex = r.examples[0] if r.examples else ""
        lines.append(
            f"| `{r.kind}` | {r.category} | `{r.schema}` | `{ex}` | {r.title} |"
        )
    lines.append("")
    lines.append(f"Last updated: {_top_version()}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true", help="emit JSON index")
    ap.add_argument("--write", action="store_true", help="write outputs to repo")
    args = ap.parse_args()

    rows = build_rows()

    if args.json:
        out = render_json(rows)
        if args.write:
            OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
            OUT_JSON.write_text(out, encoding="utf-8")
        print(out, end="")
        return 0

    out = render_markdown(rows)
    if args.write:
        OUT_MD.write_text(out, encoding="utf-8")
        # Keep the machine-readable index in sync: `--write` refreshes both outputs.
        jout = render_json(rows)
        OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
        OUT_JSON.write_text(jout, encoding="utf-8")
    print(out, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
