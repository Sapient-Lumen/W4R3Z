import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
rev = receipt.get("revision")

LEDGER_SPECS = [
    ("FOLLOWTHROUGH-QUEUE.json", "followthrough_witness", "id"),
    ("ASSUMPTION-LEDGER.json", "assumption_witness", "id"),
    ("OBLIGATION-LEDGER.json", "obligation_witness", "id"),
    ("APPLICABILITY-LEDGER.json", "applicability_witness", "id"),
    ("FOREIGN-PRESSURE-LEDGER.json", "foreign_pressure_witness", "id"),
    ("DATACUBE-TRANSFER-LEDGER.json", "transfer_witness", "id"),
    ("RESOLUTION-LEDGER.json", "resolution_witness", "id"),
    ("RETROSPECTIVE-QUEUE.json", "retrospective_write_witness", "id"),
    ("FIREBREAK-LEDGER.json", "reasoning_firebreak_witness", "id"),
]

def id_from_witness(witness: dict, fallback_key: str) -> str | None:
    if witness.get(fallback_key):
        return witness.get(fallback_key)
    surface = witness.get("witness_surface", "")
    if "#" in surface:
        return surface.rsplit("#", 1)[1]
    return None

for filename, witness_key, fallback_key in LEDGER_SPECS:
    items = json.loads((ROOT / filename).read_text(encoding="utf-8")).get("items", [])
    if not items:
        raise SystemExit(f"{filename} has no items")
    latest = items[-1]
    witness = receipt.get(witness_key)
    if not isinstance(witness, dict):
        raise SystemExit(f"receipt missing {witness_key}")
    expected_id = id_from_witness(witness, fallback_key)
    if latest.get("id") != expected_id:
        raise SystemExit(f"{filename} latest id {latest.get('id')} != receipt {witness_key} {expected_id}")
    if latest.get("revision") != rev:
        raise SystemExit(f"{filename} latest revision {latest.get('revision')} != receipt revision {rev}")
    origin = latest.get("origin_revision")
    if origin is not None and origin != rev:
        raise SystemExit(f"{filename} latest origin_revision {origin} != receipt revision {rev}")

if receipt.get("current_pressure_id") != receipt.get("foreign_pressure_witness", {}).get("id"):
    raise SystemExit("receipt current_pressure_id must match foreign_pressure_witness.id")
if receipt.get("current_import_id") != receipt.get("transfer_witness", {}).get("id"):
    raise SystemExit("receipt current_import_id must match transfer_witness.id")
if receipt.get("resolved_question") not in receipt.get("resolution_witness", {}).get("resolved_objects", []):
    raise SystemExit("receipt resolution witness must include resolved_question")

print("check_continuity_tail_alignment: OK")
