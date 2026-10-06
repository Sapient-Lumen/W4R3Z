import json
import pathlib

from hot_current_supports_lib import (
    LANDING_SURFACES,
    MAX_HOT_CURRENT_SUPPORTS,
    HotCurrentSupportsError,
    docs_head_cue_items,
    latest_cue_items,
    validate_hot_current_supports,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))

try:
    expected = validate_hot_current_supports(ROOT, receipt)
    for rel in LANDING_SURFACES:
        text = (ROOT / rel).read_text(encoding="utf-8")
        match, observed = latest_cue_items(text, rel)
        if observed != expected:
            raise HotCurrentSupportsError(f"{rel} current additions must exactly equal hot_current_supports in receipt order")
        if match.group("revision") != receipt.get("revision"):
            raise HotCurrentSupportsError(f"{rel} latest cue revision mismatch")
        if match.group("bundle") != manifest.get("bundle"):
            raise HotCurrentSupportsError(f"{rel} latest cue bundle mismatch")
    docs_match, docs_observed = docs_head_cue_items((ROOT / "docs/README.md").read_text(encoding="utf-8"))
    if docs_observed != expected:
        raise HotCurrentSupportsError("docs/README.md packaged-docs cue must exactly equal hot_current_supports")
    if docs_match.group("revision") != receipt.get("revision") or docs_match.group("bundle") != manifest.get("bundle"):
        raise HotCurrentSupportsError("docs/README.md packaged-docs cue identity mismatch")
except HotCurrentSupportsError as exc:
    raise SystemExit(f"hot current supports contract failed: {exc}") from exc

print(f"check_hot_current_supports_contract: OK ({len(expected)}/{MAX_HOT_CURRENT_SUPPORTS})")
