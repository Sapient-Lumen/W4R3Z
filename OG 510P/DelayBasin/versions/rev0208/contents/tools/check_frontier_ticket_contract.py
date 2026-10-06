import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "frontier-ticket.json").read_text(encoding="utf-8"))
context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
obligations = json.loads((ROOT / "OBLIGATION-LEDGER.json").read_text(encoding="utf-8"))["items"]
retros = json.loads((ROOT / "RETROSPECTIVE-QUEUE.json").read_text(encoding="utf-8"))["items"]

required = {"project", "revision", "derivative_note", "selection_policy", "current_posture", "primary_focus", "background_checks", "reentry_anchors"}
missing = required - set(pack)
if missing:
    raise SystemExit(f"frontier-ticket missing keys: {sorted(missing)}")
if pack["project"] != "DelayBasin":
    raise SystemExit("frontier-ticket project mismatch")
if pack["revision"] != context["revision"]:
    raise SystemExit("frontier-ticket revision must match context-pack")
if pack["derivative_note"] != "Derivative frontier aid; canon wins.":
    raise SystemExit("frontier-ticket derivative_note drift")

sp = pack["selection_policy"]
for key in ["primary_focus_rule", "background_rule", "source_surfaces"]:
    if key not in sp:
        raise SystemExit(f"frontier-ticket selection_policy missing {key}")
for rel in sp["source_surfaces"]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"frontier-ticket selection_policy source missing: {rel}")

cp = pack["current_posture"]
ctx_cp = context["current_posture"]
for key in ["operational_head", "citation_head", "decision_state", "execution_state", "public_state", "state_class"]:
    if cp.get(key) != ctx_cp.get(key):
        raise SystemExit(f"frontier-ticket current_posture mismatch on {key}")

pf = pack["primary_focus"]
ctx_focus = context["open_questions"][-1]
for key in ["id", "source", "selection_source", "text"]:
    if pf.get(key) != ctx_focus.get(key):
        raise SystemExit(f"frontier-ticket primary_focus mismatch on {key}")
expected_gov = f"{ctx_focus['source']}#{ctx_focus['id'].lower()}"
if pf.get("governing_surface") != expected_gov:
    raise SystemExit("frontier-ticket governing_surface mismatch")
if not (ROOT / pf["source"]).exists() or not (ROOT / pf["selection_source"]).exists():
    raise SystemExit("frontier-ticket primary_focus surfaces missing")

latest_open_ob = next((item for item in reversed(obligations) if item.get("state") == "open" or item.get("obligation_state") == "open"), None)
latest_cooling_rt = next((item for item in reversed(retros) if item.get("state") == "cooling"), None)
if latest_open_ob is None or latest_cooling_rt is None:
    raise SystemExit("frontier-ticket background rows unavailable")
background = pack["background_checks"]
ob = background.get("latest_obligation")
rt = background.get("latest_retrospective")
if ob.get("id") != latest_open_ob["id"]:
    raise SystemExit("frontier-ticket latest obligation mismatch")
if rt.get("id") != latest_cooling_rt["id"]:
    raise SystemExit("frontier-ticket latest retrospective mismatch")

anchors = pack["reentry_anchors"]
for key in ["startup_surface", "wrapper_surface", "runbook_surface", "compact_packet", "status_surface"]:
    if key not in anchors:
        raise SystemExit(f"frontier-ticket reentry_anchors missing {key}")
    if not (ROOT / anchors[key]).exists():
        raise SystemExit(f"frontier-ticket anchor missing: {anchors[key]}")
if anchors["compact_packet"] != "context-pack.json" or anchors["status_surface"] != "SURFACE-STATUS.json":
    raise SystemExit("frontier-ticket anchor drift")

print("check_frontier_ticket_contract: OK")
