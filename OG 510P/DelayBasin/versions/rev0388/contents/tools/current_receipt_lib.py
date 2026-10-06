import json
import pathlib
from typing import Any

TAIL_WITNESS_SPECS = [
    ("DATACUBE-TRANSFER-LEDGER.json", "transfer_witness", "current_import_id"),
    ("FOREIGN-PRESSURE-LEDGER.json", "foreign_pressure_witness", "current_pressure_id"),
    ("APPLICABILITY-LEDGER.json", "applicability_witness", None),
    ("RESOLUTION-LEDGER.json", "resolution_witness", None),
    ("FIREBREAK-LEDGER.json", "reasoning_firebreak_witness", None),
    ("ASSUMPTION-LEDGER.json", "assumption_witness", None),
    ("OBLIGATION-LEDGER.json", "obligation_witness", None),
    ("FOLLOWTHROUGH-QUEUE.json", "followthrough_witness", None),
    ("RETROSPECTIVE-QUEUE.json", "retrospective_write_witness", None),
]

NON_CLAIM = "Derivative hot receipt view only; REVISION-RECEIPT.json and source ledgers remain authoritative. This surface is not a receipt replacement, witness court, shrink proof, release notary, or deletion authority."


def load_json(root: pathlib.Path, rel: str) -> dict[str, Any]:
    return json.loads((root / rel).read_text(encoding="utf-8"))


def id_from_witness(witness: dict[str, Any]) -> str | None:
    if isinstance(witness.get("id"), str):
        return witness["id"]
    surface = witness.get("witness_surface")
    if isinstance(surface, str) and "#" in surface:
        return surface.rsplit("#", 1)[1]
    return None


def _small_witness(witness: dict[str, Any], ledger_tail: dict[str, Any], current_key: str | None, receipt: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": id_from_witness(witness),
        "revision": witness.get("revision") or ledger_tail.get("revision"),
        "surface": witness.get("witness_surface") or ledger_tail.get("witness_surface"),
        "state": witness.get("state") or witness.get("closure_state") or witness.get("assumption_state") or witness.get("obligation_state") or witness.get("retrospective_state") or witness.get("firebreak_state") or ledger_tail.get("state"),
        "title": witness.get("title") or ledger_tail.get("title"),
        "origin_revision": witness.get("origin_revision") or ledger_tail.get("origin_revision"),
    }
    if current_key:
        row["receipt_current_key"] = current_key
        row["receipt_current_value"] = receipt.get(current_key)
    return {key: value for key, value in row.items() if value is not None}


def build_current_receipt(root: pathlib.Path) -> dict[str, Any]:
    root = pathlib.Path(root)
    receipt = load_json(root, "REVISION-RECEIPT.json")
    manifest = load_json(root, "RELEASE-MANIFEST.json")
    status = load_json(root, "SURFACE-STATUS.json")

    witnesses: dict[str, Any] = {}
    for ledger, witness_key, current_key in TAIL_WITNESS_SPECS:
        data = load_json(root, ledger)
        tail = data.get("items", [{}])[-1]
        witness = receipt.get(witness_key, {})
        witnesses[witness_key] = {
            "ledger": ledger,
            "ledger_tail_id": tail.get("id"),
            "ledger_tail_revision": tail.get("revision"),
            "receipt": _small_witness(witness if isinstance(witness, dict) else {}, tail, current_key, receipt),
            "tail_matches_receipt": tail.get("id") == id_from_witness(witness if isinstance(witness, dict) else {}),
        }

    return {
        "project": "DelayBasin",
        "revision": receipt.get("revision"),
        "surface": "CURRENT-RECEIPT.json",
        "source_receipt": "REVISION-RECEIPT.json",
        "source_manifest": "RELEASE-MANIFEST.json",
        "source_status": "SURFACE-STATUS.json",
        "source_receipt_coldstore": "RECEIPT-COLDSTORE.json" if (root / "RECEIPT-COLDSTORE.json").exists() else None,
        "derivative_note": "Derivative hot-current view; canon wins.",
        "non_claim": NON_CLAIM,
        "identity": {
            "previous_revision": receipt.get("previous_revision"),
            "bundle": manifest.get("bundle"),
            "stamp": manifest.get("timestamp"),
            "slug": manifest.get("slug"),
            "packaged_release": receipt.get("packaged_release"),
        },
        "question_posture": {
            "resolved_question": receipt.get("resolved_question"),
            "resolution_id": id_from_witness(receipt.get("resolution_witness", {})),
            "next_open_question": receipt.get("next_open_question"),
            "change_summary": receipt.get("change_summary"),
        },
        "currentness": {
            "status_current_head": status.get("current_head"),
            "status_latest_revision": status.get("latest_revision"),
            "status_latest_bundle": status.get("latest_bundle"),
            "receipt_current_import_id": receipt.get("current_import_id"),
            "receipt_current_pressure_id": receipt.get("current_pressure_id"),
        },
        "summary": receipt.get("summary"),
        "hot_current_supports": receipt.get("hot_current_supports"),
        "current_witness_slot": receipt.get("current_witness_slot"),
        "tail_witnesses": witnesses,
        "substance_pointers": [
            "tools/check_ledger_coldstore_mutation_canaries.py",
            "tools/ledger_coldstore_contract_lib.py",
            "tools/check_receipt_coldstore_roundtrip_contract.py",
            "tools/check_receipt_coldstore_mutation_canaries.py",
            "tools/receipt_coldstore_contract_lib.py",
            "RECEIPT-COLDSTORE.json",
            "tools/check_current_receipt_contract.py",
            "CURRENT-RECEIPT.json",
            "CANARY-RUNS.json",
            "ARCHIVE-ECONOMY-AUDIT.json",
        ],
        "guard": "tools/check_current_receipt_contract.py",
    }
