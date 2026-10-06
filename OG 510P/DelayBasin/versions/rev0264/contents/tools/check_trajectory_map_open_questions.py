import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
registry = (ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8")
trajectory = (ROOT / "docs/00-meta/trajectory-map.md").read_text(encoding="utf-8")
ids = sorted(set(re.findall(r"OQ-\d{4}", registry)))
missing = [oid for oid in ids[-4:] if oid not in trajectory]
if missing:
    print("trajectory-map missing recent open questions:", ", ".join(missing))
    sys.exit(1)
print("check_trajectory_map_open_questions: OK")
