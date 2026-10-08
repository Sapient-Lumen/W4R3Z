#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc

CURRENT_REV = current_revision()
INPUT = METADATA_DIR / "transition_receipt_tests.json"


def render_markdown(data: dict) -> str:
    lines = [
        "# Transition-receipt tests matrix",
        "",
        f"Generated for `{data['revision']}` from `metadata/transition_receipt_tests.json`.",
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
        "transition_receipt_test_source": str(INPUT.relative_to(ROOT)),
        "source_notes": payload.get("source_notes", []),
        "test_count": len(tests),
        "tests": tests,
        "related_note_counts": {str(k): v for k, v in sorted(counts.items())},
        "case_example_index": {k: v for k, v in sorted(case_index.items(), key=lambda item: int(item[0]))},
        "use_rule": "Run transition-receipt tests whenever a public tool, platform, pilot, authority, supplier arrangement, emergency measure, database, AI system, or coordination body is ended, converted, absorbed, migrated, paused, made optional, relaunched, renewed, or replaced. Separate terminal status from successor ownership, defect learning, affected-user tail, record preservation, data closeout, procurement / contract closeout, costs, residual dependency, and relaunch gates.",
    }
    (GENERATED / "TRANSITION_RECEIPT_TESTS.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (GENERATED / "TRANSITION_RECEIPT_TESTS.md").write_text(render_markdown(data), encoding="utf-8")
    print("OK: wrote generated/TRANSITION_RECEIPT_TESTS.json and generated/TRANSITION_RECEIPT_TESTS.md")


if __name__ == "__main__":
    main()
