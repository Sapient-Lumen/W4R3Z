#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc


def render_test_matrix_markdown(data: dict, *, title: str, metadata_filename: str) -> str:
    lines = [
        f"# {title}",
        "",
        f"Generated for `{data['revision']}` from `metadata/{metadata_filename}`.",
        "",
        "## Tests",
        "",
        "| Test | Question | Related notes | Repair if failed |",
        "| --- | --- | --- | --- |",
    ]
    for test in data["tests"]:
        notes = ", ".join(f"`{n}`" for n in test.get("related_notes", []))
        lines.append(f"| `{test['test_id']}` {test['label']} | {test['question']} | {notes} | {test['fail_or_repair']} |")
    lines.extend(["", "## Case examples", "", "| Case | Tests activated |", "| --- | --- |"])
    for case, tests in data.get("case_example_index", {}).items():
        lines.append(f"| `{case}` | {', '.join(f'`{t}`' for t in tests)} |")
    lines.extend(["", "## Related-note recurrence", "", "| Note | Count |", "| --- | ---: |"])
    for note, count in data.get("related_note_counts", {}).items():
        lines.append(f"| `{note}` | {count} |")
    lines.extend(["", "## Use rule", "", data.get("use_rule", ""), ""])
    return "\n".join(lines)


def build_test_matrix(
    *,
    metadata_filename: str,
    output_stem: str,
    title: str,
    source_field: str,
    use_rule: str,
) -> dict:
    """Build the common metadata -> generated test-matrix shape used by recent dockets."""
    GENERATED.mkdir(exist_ok=True)
    input_path = METADATA_DIR / metadata_filename
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    tests = []
    counts: Counter[int] = Counter()
    case_index: dict[str, list[str]] = {}
    for test_id, test in sorted(payload.get("tests", {}).items()):
        related = [int(n) for n in test.get("related_notes", [])]
        counts.update(related)
        examples = [int(n) for n in test.get("case_examples", [])]
        for ex in examples:
            case_index.setdefault(str(ex), []).append(test_id)
        tests.append({"test_id": test_id, **test, "related_notes": related, "case_examples": examples})
    data = {
        "revision": current_revision(),
        "generated_at_utc": generated_at_utc(),
        source_field: str(input_path.relative_to(ROOT)),
        "source_notes": payload.get("source_notes", []),
        "test_count": len(tests),
        "tests": tests,
        "related_note_counts": {str(k): v for k, v in sorted(counts.items())},
        "case_example_index": {k: v for k, v in sorted(case_index.items(), key=lambda item: int(item[0]))},
        "use_rule": use_rule,
    }
    json_path = GENERATED / f"{output_stem}.json"
    md_path = GENERATED / f"{output_stem}.md"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(render_test_matrix_markdown(data, title=title, metadata_filename=metadata_filename), encoding="utf-8")
    print(f"OK: wrote {json_path.relative_to(ROOT)} and {md_path.relative_to(ROOT)}")
    return data
