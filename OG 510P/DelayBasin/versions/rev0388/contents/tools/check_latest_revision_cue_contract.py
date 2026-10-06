import json
import pathlib
import re
import sys

from validation_toolchain_lib import build_validation_toolchain

ROOT = pathlib.Path(__file__).resolve().parents[1]
STATUS = ROOT / "SURFACE-STATUS.json"
MANIFEST = ROOT / "RELEASE-MANIFEST.json"
ARCHIVE_INDEX = ROOT / "ARCHIVE_INDEX.md"
CHANGELOG = ROOT / "CHANGELOG.md"

TARGETS = ["START_HERE.md", "README.md", "docs/README.md"]
LATEST_RE = re.compile(r"Latest revision `(?P<revision>rev\d{4})`")


def load_json(path: pathlib.Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # pragma: no cover - lint-time guard
        raise SystemExit(f"could not load {path.relative_to(ROOT)}: {exc}") from exc

status = load_json(STATUS)
manifest = load_json(MANIFEST)
revision = status.get("revision")
bundle = manifest.get("bundle")

if not isinstance(revision, str) or not re.fullmatch(r"rev\d{4}", revision):
    raise SystemExit("SURFACE-STATUS revision must be rev####")
if manifest.get("revision") != revision:
    raise SystemExit("RELEASE-MANIFEST revision must match SURFACE-STATUS revision")
if not isinstance(bundle, str) or not bundle.startswith(f"DelayBasin-{revision}-"):
    raise SystemExit("RELEASE-MANIFEST bundle must name the current revision")

for key in ["latest_revision", "current_head"]:
    if status.get(key) != revision:
        raise SystemExit(f"SURFACE-STATUS {key} must match revision")
for key in ["latest_bundle", "current_bundle", "latest_archive", "frozen_public_surface"]:
    if status.get(key) != bundle:
        raise SystemExit(f"SURFACE-STATUS {key} must match RELEASE-MANIFEST bundle")
if status.get("status_lanes", {}).get("frozen_public_surface") != bundle:
    raise SystemExit("SURFACE-STATUS status_lanes.frozen_public_surface must match RELEASE-MANIFEST bundle")
if status.get("citation_head", {}).get("surface") != bundle:
    raise SystemExit("SURFACE-STATUS citation_head.surface must match RELEASE-MANIFEST bundle")

problems: list[str] = []
for rel in TARGETS:
    path = ROOT / rel
    if not path.exists():
        problems.append(f"missing landing surface: {rel}")
        continue
    text = path.read_text(encoding="utf-8")
    matches = list(LATEST_RE.finditer(text))
    if len(matches) != 1:
        problems.append(f"{rel} must contain exactly one Latest revision cue, found {len(matches)}")
        continue
    cue_rev = matches[0].group("revision")
    if cue_rev != revision:
        problems.append(f"{rel} latest cue names {cue_rev}, expected {revision}")

archive_index_text = ARCHIVE_INDEX.read_text(encoding="utf-8")
changelog_text = CHANGELOG.read_text(encoding="utf-8")
if bundle not in archive_index_text:
    problems.append("ARCHIVE_INDEX.md missing current bundle")
if revision not in changelog_text:
    problems.append("CHANGELOG.md missing current revision")

try:
    toolchain = build_validation_toolchain(ROOT)
except Exception as exc:  # pragma: no cover - lint-time guard
    raise SystemExit(f"could not build validation toolchain: {exc}") from exc
if "check_latest_revision_cue_contract.py" not in toolchain:
    problems.append("validation toolchain is missing check_latest_revision_cue_contract.py")

if problems:
    for problem in problems:
        print(problem)
    sys.exit(1)

print("check_latest_revision_cue_contract: OK")
