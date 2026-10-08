#!/usr/bin/env python3
"""Release-gate drift firewall for voter-facing public-answer surface registry."""

from __future__ import annotations

from _shared.registry import read_csv, split_semicolon

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "artifacts" / "tables" / "voter-facing-public-answer-surfaces.csv"
REQUIRED_HEADER = [
    "doc_id",
    "surface_slug",
    "family_bucket",
    "canonical_question",
    "action_window",
    "doc_path",
    "template_path",
    "checklist_path",
    "control_tags",
]
ALLOWED_BUCKETS = {
    "locate_schedule",
    "eligibility_prerequisites",
    "ballot_path",
    "problem_escalation",
}
ALLOWED_CONTROL_TAGS = {
    "special_case_high_risk",
}


def main() -> int:
    errors: list[str] = []
    if not REG.exists():
        print(f"ERROR: missing registry {REG}")
        return 2

    table = read_csv(REG)
    header = [c.strip() for c in table.headers]
    if header != REQUIRED_HEADER:
        errors.append(f"header mismatch: got {header} want {REQUIRED_HEADER}")

    seen_doc_ids: set[int] = set()
    seen_slugs: set[str] = set()
    doc_ids: list[int] = []

    for i, row in enumerate(table.rows, start=2):
        if not any(row.values()):
            continue

        doc_id_s = row.get("doc_id", "")
        slug = row.get("surface_slug", "")
        bucket = row.get("family_bucket", "")
        question = row.get("canonical_question", "")
        action_window = row.get("action_window", "")
        doc_path = row.get("doc_path", "")
        template_path = row.get("template_path", "")
        checklist_path = row.get("checklist_path", "")
        control_tags = row.get("control_tags", "")

        try:
            doc_id = int(doc_id_s)
        except ValueError:
            errors.append(f"L{i}: doc_id must be an integer: {doc_id_s!r}")
            continue

        doc_ids.append(doc_id)
        if doc_id in seen_doc_ids:
            errors.append(f"L{i}: duplicate doc_id: {doc_id}")
        seen_doc_ids.add(doc_id)

        if not slug:
            errors.append(f"L{i}: empty surface_slug")
        elif slug in seen_slugs:
            errors.append(f"L{i}: duplicate surface_slug: {slug}")
        seen_slugs.add(slug)

        if bucket not in ALLOWED_BUCKETS:
            errors.append(f"L{i}: invalid family_bucket for {slug or doc_id}: {bucket!r}")

        if not question.endswith("?"):
            errors.append(f"L{i}: canonical_question must end with '?': {question!r}")

        if not action_window:
            errors.append(f"L{i}: empty action_window for {slug or doc_id}")

        if not doc_path.startswith("docs/"):
            errors.append(f"L{i}: doc_path must start with docs/: {doc_path}")
        if f"docs/{doc_id}-" not in doc_path:
            errors.append(f"L{i}: doc_path does not match doc_id {doc_id}: {doc_path}")

        for label, rel in [
            ("doc_path", doc_path),
            ("template_path", template_path),
            ("checklist_path", checklist_path),
        ]:
            if not rel:
                errors.append(f"L{i}: empty {label} for {slug or doc_id}")
                continue
            if not (ROOT / rel).exists():
                errors.append(f"L{i}: missing {label}: {rel}")

        unknown_tags = sorted(set(split_semicolon(control_tags)) - ALLOWED_CONTROL_TAGS)
        if unknown_tags:
            errors.append(
                f"L{i}: unknown control_tags for {slug or doc_id}: {', '.join(unknown_tags)}"
            )

    if doc_ids != sorted(doc_ids):
        errors.append("registry rows are not sorted by doc_id ascending")

    if errors:
        for e in errors:
            print("ERROR:", e)
        return 2

    print("PASS: voter-facing public-answer surface registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
