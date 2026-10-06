import json
import pathlib

from currentness_cue_audit_lib import build_currentness_cue_audit, render_currentness_cue_audit_md

ROOT = pathlib.Path(__file__).resolve().parents[1]
payload = build_currentness_cue_audit(ROOT)
(ROOT / "CURRENTNESS-CUE-AUDIT.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
(ROOT / "docs/00-meta/currentness-cue-audit.md").write_text(render_currentness_cue_audit_md(payload), encoding="utf-8")
print("wrote CURRENTNESS-CUE-AUDIT.json")
print("wrote docs/00-meta/currentness-cue-audit.md")
