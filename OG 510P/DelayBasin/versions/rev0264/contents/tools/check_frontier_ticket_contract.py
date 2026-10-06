import pathlib

from frontier_ticket_lib import load_json, latest_cooling_retrospective, latest_open_obligation

ROOT = pathlib.Path(__file__).resolve().parents[1]
pack = load_json("frontier-ticket.json")
context = load_json("context-pack.json")
status = load_json("SURFACE-STATUS.json")
obligations = load_json("OBLIGATION-LEDGER.json")["items"]
retros = load_json("RETROSPECTIVE-QUEUE.json")["items"]

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

latest_open_ob = latest_open_obligation(obligations)
latest_cooling_rt = latest_cooling_retrospective(retros)
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
