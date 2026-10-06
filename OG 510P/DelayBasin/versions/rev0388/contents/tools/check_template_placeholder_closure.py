import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
FORBIDDEN = [
    "{PREV_FAMILY}",
    "{FAMILY}",
    "{TOKEN}",
    "{ALLOWED}",
    "TODO-REPLACE",
    "PLACEHOLDER-REPLACE",
]
TARGETS = []
TARGETS.extend((ROOT / "docs" / "10-method").glob("pa-governance-retirement*.md"))
for rel in [
    "REVISION-RECEIPT.json",
    "SURFACE-STATUS.json",
    "context-pack.json",
    "innovation-packet.json",
    "frontier-ticket.json",
    "replay-capsule.json",
    "compact-surface-bundle.json",
    "WITNESS-VOCABULARY.json",
    "WITNESS-FAMILY-HANDLES.json",
    "SELF-SUFFICIENCY-LEDGER.json",
]:
    TARGETS.append(ROOT / rel)

violations = []
for path in TARGETS:
    if not path.exists():
        raise SystemExit(f"template placeholder guard target missing: {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    for marker in FORBIDDEN:
        if marker in text:
            violations.append(f"{path.relative_to(ROOT)} contains unresolved marker {marker}")
if violations:
    raise SystemExit("template placeholder closure failed: " + "; ".join(violations[:12]))
print("check_template_placeholder_closure: OK")
