#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc

CURRENT_REV = current_revision()
INPUT = METADATA_DIR / "staff_copilot_tests.json"


def render_markdown(data: dict) -> str:
    lines = [
        "# Staff-copilot tests matrix",
        "",
        f"Generated for `{data['revision']}` from `metadata/staff_copilot_tests.json`.",
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


def main() -> None:
    GENERATED.mkdir(exist_ok=True)
    payload = json.loads(INPUT.read_text(encoding="utf-8"))
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
        "revision": CURRENT_REV,
        "generated_at_utc": generated_at_utc(),
        "staff_copilot_test_source": str(INPUT.relative_to(ROOT)),
        "source_notes": payload.get("source_notes", []),
        "test_count": len(tests),
        "tests": tests,
        "related_note_counts": {str(k): v for k, v in sorted(counts.items())},
        "case_example_index": {k: v for k, v in sorted(case_index.items(), key=lambda item: int(item[0]))},
        "use_rule": "Run staff-copilot tests whenever an internal AI tool used by officials drafts, summarizes, classifies, routes, creates case records, flags vulnerability, prepopulates fields, writes report sections, or otherwise shapes public action without speaking directly to the public. Separate personal productivity from official record creation, record creation from queue or priority effect, and staff assistance from legal or similarly significant decisions.",
    }
    (GENERATED / "STAFF_COPILOT_TESTS.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (GENERATED / "STAFF_COPILOT_TESTS.md").write_text(render_markdown(data), encoding="utf-8")
    print("OK: wrote generated/STAFF_COPILOT_TESTS.json and generated/STAFF_COPILOT_TESTS.md")


if __name__ == "__main__":
    main()
