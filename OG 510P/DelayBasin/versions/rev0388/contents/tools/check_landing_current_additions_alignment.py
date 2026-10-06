import json
import pathlib
import sys

from hot_current_supports_lib import LANDING_SURFACES, HotCurrentSupportsError, latest_cue_items, validate_hot_current_supports

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))

try:
    expected = validate_hot_current_supports(ROOT, receipt)
except HotCurrentSupportsError as exc:
    raise SystemExit(str(exc)) from exc

problems: list[str] = []
for rel in LANDING_SURFACES:
    path = ROOT / rel
    if not path.exists():
        problems.append(f"missing landing surface: {rel}")
        continue
    try:
        _, observed = latest_cue_items(path.read_text(encoding="utf-8"), rel)
    except HotCurrentSupportsError as exc:
        problems.append(str(exc))
        continue
    if observed != expected:
        problems.append(f"{rel} current additions differ from receipt hot_current_supports")

if problems:
    for problem in problems:
        print(problem)
    sys.exit(1)

print("check_landing_current_additions_alignment: OK")
