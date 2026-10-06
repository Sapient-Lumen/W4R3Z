import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
protocol = json.loads((ROOT / "CANARY-PROTOCOL.json").read_text(encoding="utf-8"))
if protocol.get("project") != "DelayBasin" or protocol.get("revision") != receipt.get("revision"):
    raise SystemExit("CANARY-PROTOCOL project/revision drifted")
if protocol.get("surface") != "CANARY-PROTOCOL.json":
    raise SystemExit("CANARY-PROTOCOL self id drifted")
if "review court" not in protocol.get("non_claim", ""):
    raise SystemExit("CANARY-PROTOCOL must deny review-court authority")
if len(protocol.get("packet_classes", [])) < 4:
    raise SystemExit("CANARY-PROTOCOL must include null/landing/compact/full packet classes")
for key in ["required_questions", "negative_canaries", "admissible_conclusions", "forbidden_conclusions"]:
    if len(protocol.get(key, [])) < 4:
        raise SystemExit(f"CANARY-PROTOCOL {key} is too thin")
for bad in ["continuation authority", "canonical status for derivative packets", "proof of minimality", "standing review governance"]:
    if bad not in protocol.get("forbidden_conclusions", []):
        raise SystemExit(f"CANARY-PROTOCOL missing forbidden conclusion {bad}")
print("check_canary_protocol_contract: OK")
