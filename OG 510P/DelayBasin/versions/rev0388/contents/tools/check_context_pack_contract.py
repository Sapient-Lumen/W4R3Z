import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))

required_top = {"project", "revision", "must_read", "open_questions", "frontier_ticket", "innovation_packet", "current_posture", "operator_warnings", "reentry_contract", "core_lexicon", "move_registry", "recovery", "revision_receipt", "typed_reentry", "commands"}
missing = required_top - set(pack)
if missing:
    raise SystemExit(f"context-pack missing keys: {sorted(missing)}")

questions = pack["open_questions"]
if not isinstance(questions, list) or not questions:
    raise SystemExit("open_questions must be a non-empty list")
for idx, item in enumerate(questions):
    if not isinstance(item, dict):
        raise SystemExit(f"open_questions[{idx}] must be an object")
    for key in ["id", "source", "selection_source", "text"]:
        if key not in item:
            raise SystemExit(f"open_questions[{idx}] missing {key}")
    if not item["id"].startswith("OQ-"):
        raise SystemExit(f"open_questions[{idx}] id must start with OQ-")
    for key in ["source", "selection_source"]:
        if not (ROOT / item[key]).exists():
            raise SystemExit(f"open_questions[{idx}] {key} missing: {item[key]}")
    if "?" not in item["text"]:
        raise SystemExit(f"open_questions[{idx}] text missing question mark")
print("check_context_pack_contract: open_questions OK")

frontier = pack["frontier_ticket"]
for key in ["surface", "selected_focus_id"]:
    if key not in frontier:
        raise SystemExit(f"frontier_ticket missing {key}")
if frontier["surface"] != "frontier-ticket.json":
    raise SystemExit("frontier_ticket surface must be frontier-ticket.json")
if frontier["selected_focus_id"] != questions[-1]["id"]:
    raise SystemExit("frontier_ticket selected_focus_id must match last open question")
print("check_context_pack_contract: frontier_ticket OK")

innovation = pack["innovation_packet"]
for key in ["surface", "anchor_revision"]:
    if key not in innovation:
        raise SystemExit(f"innovation_packet missing {key}")
if innovation["surface"] != "innovation-packet.json":
    raise SystemExit("innovation_packet surface must be innovation-packet.json")
if not innovation["anchor_revision"].startswith("rev"):
    raise SystemExit("innovation_packet anchor_revision must look like rev####")
if not (ROOT / innovation["surface"]).exists():
    raise SystemExit("innovation_packet surface missing: " + innovation["surface"])
print("check_context_pack_contract: innovation_packet OK")

tr = pack["typed_reentry"]
for key in ["workflow_surface", "state_surfaces", "check_surface", "quarantine_surface", "admission_moves"]:
    if key not in tr:
        raise SystemExit(f"typed_reentry missing {key}")

workflow = ROOT / tr["workflow_surface"]
if not workflow.exists():
    raise SystemExit(f"workflow surface missing: {workflow}")

for rel in tr["state_surfaces"]:
    if not (ROOT / rel).exists():
        raise SystemExit(f"state surface missing: {rel}")

if tr["check_surface"] != "make lint":
    raise SystemExit("typed_reentry.check_surface must be 'make lint'")

if not (ROOT / tr["quarantine_surface"]).exists():
    raise SystemExit(f"quarantine surface missing: {tr['quarantine_surface']}")

print("check_context_pack_contract: OK")


reentry = pack.get("reentry_contract")
if not reentry:
    raise SystemExit("context-pack missing reentry_contract")
for key in ["surface", "conformance", "profile_id"]:
    if key not in reentry:
        raise SystemExit(f"reentry_contract missing {key}")
if reentry["profile_id"] != "careful-revision-pass":
    raise SystemExit("context-pack reentry_contract.profile_id must be careful-revision-pass")
for key in ["surface", "conformance"]:
    if not (ROOT / reentry[key]).exists():
        raise SystemExit(f"reentry_contract surface missing: {reentry[key]}")

print("check_context_pack_contract: reentry_contract OK")

cl = pack["core_lexicon"]
for key in ["registry", "certified", "provisional"]:
    if key not in cl:
        raise SystemExit(f"core_lexicon missing {key}")
if not (ROOT / cl["registry"]).exists():
    raise SystemExit(f"core_lexicon registry missing: {cl['registry']}")

mr = pack["move_registry"]
for key in ["registry", "certified"]:
    if key not in mr:
        raise SystemExit(f"move_registry missing {key}")
if not (ROOT / mr["registry"]).exists():
    raise SystemExit(f"move_registry registry missing: {mr['registry']}")
if not mr["certified"]:
    raise SystemExit("move_registry certified list empty")


recovery = pack["recovery"]
for key in ["surface", "move"]:
    if key not in recovery:
        raise SystemExit(f"recovery missing {key}")
if not (ROOT / recovery["surface"]).exists():
    raise SystemExit(f"recovery surface missing: {recovery['surface']}")
if recovery["move"] not in mr["certified"]:
    raise SystemExit(f"recovery move not certified: {recovery['move']}")

print("check_context_pack_contract: recovery OK")


receipt = pack.get("revision_receipt")
if not receipt:
    raise SystemExit("context-pack missing revision_receipt")
for key in ["surface", "contract", "move"]:
    if key not in receipt:
        raise SystemExit(f"revision_receipt missing {key}")
if not (ROOT / receipt["surface"]).exists():
    raise SystemExit(f"revision_receipt surface missing: {receipt['surface']}")
if not (ROOT / receipt["contract"]).exists():
    raise SystemExit(f"revision_receipt contract missing: {receipt['contract']}")
if receipt["move"] not in mr["certified"]:
    raise SystemExit(f"revision_receipt move not certified: {receipt['move']}")

print("check_context_pack_contract: revision_receipt OK")


cp = pack["current_posture"]
for key in ["operational_head", "citation_head", "decision_state", "execution_state", "public_state", "state_class"]:
    if key not in cp:
        raise SystemExit(f"current_posture missing {key}")

warnings = pack["operator_warnings"]
if not isinstance(warnings, list) or not warnings:
    raise SystemExit("operator_warnings must be a non-empty list")
for idx, item in enumerate(warnings):
    if not isinstance(item, dict):
        raise SystemExit(f"operator_warnings[{idx}] must be an object")
    for key in ["id", "source", "text"]:
        if key not in item:
            raise SystemExit(f"operator_warnings[{idx}] missing {key}")
    if not (ROOT / item["source"]).exists():
        raise SystemExit(f"operator_warnings[{idx}] source missing: {item['source']}")
    if not item["id"].startswith("OW-"):
        raise SystemExit(f"operator_warnings[{idx}] id must start with OW-")

print("check_context_pack_contract: posture/warnings OK")
