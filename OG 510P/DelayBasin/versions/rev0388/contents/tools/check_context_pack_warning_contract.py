import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
pack = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))

cp = pack["current_posture"]
if cp["operational_head"] != status["operational_head"]["surface"]:
    raise SystemExit("context-pack current_posture.operational_head disagrees with SURFACE-STATUS")
if cp["citation_head"] != status["citation_head"]["surface"]:
    raise SystemExit("context-pack current_posture.citation_head disagrees with SURFACE-STATUS")
if cp["citation_head"] != manifest["bundle"]:
    raise SystemExit("context-pack current_posture.citation_head must match RELEASE-MANIFEST bundle")
if cp["decision_state"] != status["status_lanes"]["decision_state"]:
    raise SystemExit("context-pack decision_state disagrees with SURFACE-STATUS")
if cp["execution_state"] != status["status_lanes"]["execution_state"]:
    raise SystemExit("context-pack execution_state disagrees with SURFACE-STATUS")
if cp["public_state"] != status["status_lanes"]["public_state"]:
    raise SystemExit("context-pack public_state disagrees with SURFACE-STATUS")
if cp["state_class"] != status["state_class"]:
    raise SystemExit("context-pack state_class disagrees with SURFACE-STATUS")

expected = [
    {
        "id": "OW-0001",
        "source": "docs/10-method/derivative-operator-contracts-low-entropy-reentry-wrappers-and-non-canon-read-first-surfaces.md",
        "text": "Derivative aids; canon wins",
    },
    {
        "id": "OW-0002",
        "source": "SURFACE-STATUS.json",
        "text": "Working tree is not citation head.",
    },
    {
        "id": "OW-0003",
        "source": "DATACUBE-TRANSFER-LEDGER.json",
        "text": "Check transfer ledger before peer import.",
    },
    {
        "id": "OW-0004",
        "source": "WITNESS-VOCABULARY.json",
        "text": "Use exact governed tokens.",
    },
]
if pack["operator_warnings"] != expected:
    raise SystemExit("context-pack operator_warnings drifted from admitted compact warning rows")

for item in pack["operator_warnings"]:
    if not (ROOT / item["source"]).exists():
        raise SystemExit(f"context-pack operator_warning source missing: {item['source']}")

print("check_context_pack_warning_contract: OK")
