#!/usr/bin/env python3
from __future__ import annotations

import json
from collections import Counter

from archive_meta import GENERATED, METADATA_DIR, ROOT, current_revision, generated_at_utc

CURRENT_REV = current_revision()
INPUT = METADATA_DIR / "symbolic_authority_tests.json"


def render_markdown(data: dict) -> str:
    lines = [
        "# Symbolic authority tests matrix",
        "",
        f"Generated for `{data['revision']}` from `metadata/symbolic_authority_tests.json`.",
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
        "symbolic_authority_test_source": str(INPUT.relative_to(ROOT)),
        "source_notes": payload.get("source_notes", []),
        "test_count": len(tests),
        "tests": tests,
        "related_note_counts": {str(k): v for k, v in sorted(counts.items())},
        "case_example_index": {k: v for k, v in sorted(case_index.items(), key=lambda item: int(item[0]))},
        "use_rule": "Run symbolic-authority tests whenever a visible authority, partnership, board, JPA, commission, secretariat, hub, or department is credited, blamed, abolished, absorbed, or rechartered for a public outcome whose legal, fiscal, land, data, contract, workforce, or remedy levers sit across multiple principals. The core discipline is to separate mission, mandate, means, record, recourse, attribution, and transition receipt before issuing a success, failure, or repair holding.",
    }
    (GENERATED / "SYMBOLIC_AUTHORITY_TESTS.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (GENERATED / "SYMBOLIC_AUTHORITY_TESTS.md").write_text(render_markdown(data), encoding="utf-8")
    print("OK: wrote generated/SYMBOLIC_AUTHORITY_TESTS.json and generated/SYMBOLIC_AUTHORITY_TESTS.md")


if __name__ == "__main__":
    main()
