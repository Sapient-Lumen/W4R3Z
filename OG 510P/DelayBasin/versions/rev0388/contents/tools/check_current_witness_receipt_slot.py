import json
import pathlib

from witness_vocabulary_lib import load_families

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
handles = json.loads((ROOT / "WITNESS-FAMILY-HANDLES.json").read_text(encoding="utf-8"))
families = load_families()

slot = receipt.get("current_witness_slot")
if not isinstance(slot, dict):
    raise SystemExit("receipt missing current_witness_slot")
required = {"witness_key", "contract_key", "family", "handle", "selected_token", "witness_surface", "contract_surface", "resolved_question", "next_open_question", "guard"}
missing = required - slot.keys()
if missing:
    raise SystemExit("current_witness_slot missing keys: " + ", ".join(sorted(missing)))
if slot.get("guard") != "tools/check_current_witness_receipt_slot.py":
    raise SystemExit("current witness slot guard path mismatch")
if slot.get("resolved_question") != receipt.get("resolved_question") or slot.get("next_open_question") != receipt.get("next_open_question"):
    raise SystemExit("current witness slot question ids must match receipt")
if slot.get("witness_surface") not in receipt.get("canon_additions", []):
    raise SystemExit("current witness slot surface must be a canon addition")
if slot.get("contract_surface") not in receipt.get("canon_additions", []):
    raise SystemExit("current witness slot contract must be a canon addition")
if slot.get("guard") not in receipt.get("canon_additions", []):
    raise SystemExit("current witness slot guard must be a canon addition")

witness_key = slot["witness_key"]
contract_key = slot["contract_key"]
witness = receipt.get(witness_key)
contract = receipt.get(contract_key)
if not isinstance(witness, dict) or not isinstance(contract, dict):
    raise SystemExit("receipt current witness slot keys must point to witness and contract objects")
if witness.get("witness_family") != slot.get("family"):
    raise SystemExit("current witness family mismatch")
if witness.get("witness_family_handle") != slot.get("handle"):
    raise SystemExit("current witness handle mismatch")
if witness.get("selected_token") != slot.get("selected_token"):
    raise SystemExit("current witness selected token mismatch")
if witness.get("witness_surface") != slot.get("witness_surface") or witness.get("contract_surface") != slot.get("contract_surface"):
    raise SystemExit("current witness surfaces mismatch")
if contract.get("checker") != slot.get("contract_surface") or contract.get("doc") != slot.get("witness_surface"):
    raise SystemExit("current witness contract surfaces mismatch")
if contract.get("family") != slot.get("family"):
    raise SystemExit("current witness contract family mismatch")
if contract.get("receipt_slot_guard") != "tools/check_current_witness_receipt_slot.py":
    raise SystemExit("current witness contract must name receipt-slot guard")

family = families.get(slot["family"])
if not isinstance(family, dict):
    raise SystemExit("current witness family missing from vocabulary")
if slot["selected_token"] not in family.get("allowed", []):
    raise SystemExit("current witness selected token not allowed by vocabulary")
expected_surfaces = ["WITNESS-VOCABULARY.json", "REVISION-RECEIPT.json", slot["witness_surface"]]
if family.get("surfaces") != expected_surfaces:
    raise SystemExit("current witness vocabulary surfaces mismatch")
row = next((row for row in handles.get("families", []) if row.get("canonical_family") == slot["family"]), None)
if row is None or row.get("handle") != slot["handle"]:
    raise SystemExit("current witness family handle row mismatch")

print("check_current_witness_receipt_slot: OK")
