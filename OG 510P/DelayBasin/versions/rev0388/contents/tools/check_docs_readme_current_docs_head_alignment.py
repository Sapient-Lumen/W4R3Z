import json
import pathlib
import re

from hot_current_supports_lib import HotCurrentSupportsError, docs_head_cue_items, validate_hot_current_supports

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
expected_rev = receipt.get("revision")
if not isinstance(expected_rev, str) or not re.fullmatch(r"rev\d{4}", expected_rev):
    raise SystemExit("receipt revision must be rev####")

try:
    expected = validate_hot_current_supports(ROOT, receipt)
    match, observed = docs_head_cue_items((ROOT / "docs/README.md").read_text(encoding="utf-8"))
except HotCurrentSupportsError as exc:
    raise SystemExit(str(exc)) from exc

problems: list[str] = []
if match.group("revision") != expected_rev:
    problems.append(f"docs/README.md secondary docs-head cue names {match.group('revision')}, expected {expected_rev}")
if observed != expected:
    problems.append("docs/README.md secondary docs-head current additions differ from receipt hot_current_supports")
if problems:
    raise SystemExit("\n".join(problems))
print("check_docs_readme_current_docs_head_alignment: OK")
