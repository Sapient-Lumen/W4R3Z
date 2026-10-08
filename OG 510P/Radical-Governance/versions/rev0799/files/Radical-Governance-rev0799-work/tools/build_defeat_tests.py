#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc

CURRENT_REV = current_revision()
INPUT = METADATA_DIR / "defeat_tests.json"


def render_markdown(data: dict) -> str:
    lines = [
        "# Defeat tests matrix",
        "",
        f"Generated for `{data['revision']}` from `metadata/defeat_tests.json`.",
        "",
        "## Tests",
        "",
        "| Test | Question | Related notes | Repair if failed |",
        "| --- | --- | --- | --- |",
    ]
    for test in data["tests"]:
        notes = ", ".join(f"`{n}`" for n in test.get("related_notes", []))
        lines.append(f"| `{test['test_id']}` {test['label']} | {test['question']} | {notes} | {test['fail_or_repair']} |")
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
    for test_id, test in sorted(payload.get("tests", {}).items()):
        related = [int(n) for n in test.get("related_notes", [])]
        counts.update(related)
        tests.append({"test_id": test_id, **test, "related_notes": related})
    data = {
        "revision": CURRENT_REV,
        "generated_at_utc": generated_at_utc(),
        "defeat_test_source": str(INPUT.relative_to(ROOT)),
        "source_notes": payload.get("source_notes", []),
        "test_count": len(tests),
        "tests": tests,
        "related_note_counts": {str(k): v for k, v in sorted(counts.items())},
        "use_rule": "Run trigger, lower-form, fiscal/statutory/contract/emergency, waist-capture, handback, and claim-falsifier tests before creating, thickening, consolidating, or retiring a cross-boundary authority. A failed test is a design finding, not clerical noncompliance.",
    }
    (GENERATED / "DEFEAT_TESTS.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (GENERATED / "DEFEAT_TESTS.md").write_text(render_markdown(data), encoding="utf-8")
    print("OK: wrote generated/DEFEAT_TESTS.json and generated/DEFEAT_TESTS.md")


if __name__ == "__main__":
    main()
