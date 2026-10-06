import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
innovation = json.loads((ROOT / "innovation-packet.json").read_text(encoding="utf-8")) if (ROOT / "innovation-packet.json").exists() else {}
context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8")) if (ROOT / "context-pack.json").exists() else {}
frontier = json.loads((ROOT / "frontier-ticket.json").read_text(encoding="utf-8")) if (ROOT / "frontier-ticket.json").exists() else {}
registry = (ROOT / "docs/20-constitution/open-question-registry.md").read_text(encoding="utf-8")
changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")

rev = receipt["revision"]
resolved = receipt["resolved_question"]
next_q = receipt["next_open_question"]
method = receipt["current_method_surface"]
summary = receipt["summary"]

for label, payload in [("SURFACE-STATUS", status), ("RELEASE-MANIFEST", manifest), ("innovation-packet", innovation), ("context-pack", context), ("frontier-ticket", frontier)]:
    if payload and payload.get("revision") != rev:
        raise SystemExit(f"{label} revision {payload.get('revision')} != receipt {rev}")
if status.get("latest_bundle") != receipt.get("packaged_bundle_filename"):
    raise SystemExit("SURFACE-STATUS latest_bundle drifted from receipt bundle")
if manifest.get("bundle") != receipt.get("packaged_bundle_filename"):
    raise SystemExit("RELEASE-MANIFEST bundle drifted from receipt bundle")
if method not in receipt.get("canon_additions", []):
    raise SystemExit("current_method_surface is not a canon addition")
for rel in receipt.get("canon_additions", []):
    if not (ROOT / rel).exists():
        raise SystemExit(f"canon addition missing on disk: {rel}")

change_summary = receipt.get("change_summary", "")
for needle in (rev, resolved, next_q, method):
    if needle not in change_summary and needle not in summary:
        raise SystemExit(f"receipt summary/change_summary missing {needle}")

# No stale current-looking nested witness may name an older rev/bundle unless explicitly historical.
def walk(obj, path="root"):
    if isinstance(obj, dict):
        historical = obj.get("historical_witness") is True
        for key, value in obj.items():
            if key in {"current_revision", "expected_revision", "latest_revision"} and isinstance(value, str) and value.startswith("rev") and value != rev and not historical:
                raise SystemExit(f"stale current revision at {path}.{key}: {value}")
            if key in {"latest_bundle", "current_bundle", "packaged_bundle"} and isinstance(value, str) and value.startswith("DelayBasin-rev") and value != receipt.get("packaged_bundle_filename") and not historical:
                raise SystemExit(f"stale current bundle at {path}.{key}: {value}")
            walk(value, f"{path}.{key}")
    elif isinstance(obj, list):
        for i, value in enumerate(obj):
            walk(value, f"{path}[{i}]")
walk(receipt)

if innovation:
    inv = innovation.get("innovation", innovation)
    if inv.get("summary") != summary:
        raise SystemExit("innovation-packet summary drifted from receipt")
    if inv.get("canon_additions") != receipt.get("canon_additions"):
        raise SystemExit("innovation-packet canon additions drifted from receipt")
if context:
    oqs = context.get("open_questions", [])
    if not oqs or oqs[-1].get("id") != next_q:
        raise SystemExit("context-pack open_questions tail drifted from next_open_question")
if frontier:
    focus = frontier.get("primary_focus", {})
    if focus.get("id") != next_q:
        raise SystemExit("frontier-ticket primary focus drifted from next_open_question")

if f"`{resolved}`" not in registry or f"`{next_q}`" not in registry:
    raise SystemExit("open-question registry missing resolved or successor question")
if rev not in changelog.splitlines()[0]:
    raise SystemExit("CHANGELOG first header does not name current revision")
print("check_receipt_delta_coherence: OK")
