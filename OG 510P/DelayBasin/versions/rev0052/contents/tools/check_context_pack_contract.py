import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))

required_top = {"project", "revision", "must_read", "open_questions", "core_lexicon", "move_registry", "recovery", "revision_receipt", "typed_reentry", "commands"}
missing = required_top - set(pack)
if missing:
    raise SystemExit(f"context-pack missing keys: {sorted(missing)}")

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
