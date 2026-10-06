import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
ledger = json.loads((ROOT / "SELF-SUFFICIENCY-LEDGER.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))
context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
frontier = json.loads((ROOT / "frontier-ticket.json").read_text(encoding="utf-8"))
items = ledger.get("items", [])
if not items:
    raise SystemExit("self-sufficiency ledger has no items")
latest = items[-1]
rev = receipt.get("revision")
if ledger.get("revision") != rev:
    raise SystemExit("self-sufficiency ledger revision mismatch")
if latest.get("revision") != rev:
    raise SystemExit("latest self-sufficiency item revision mismatch")
if latest.get("summary") != receipt.get("summary"):
    raise SystemExit("latest self-sufficiency summary must match receipt summary")
if receipt.get("resolved_question") not in latest.get("question_set", []):
    raise SystemExit("latest self-sufficiency question set must name resolved question")
if receipt.get("next_open_question") not in latest.get("question_set", []):
    raise SystemExit("latest self-sufficiency question set must name next open question")
focus = frontier.get("primary_focus", {}).get("id")
context_focus = context.get("open_questions", [{}])[-1].get("id")
if latest.get("frontier_id") != focus or latest.get("frontier_id") != context_focus:
    raise SystemExit("latest self-sufficiency frontier id must match compact surfaces")
canon = set(receipt.get("canon_additions", []))
for test in latest.get("packet_tests", []):
    surfaces = test.get("surfaces", [])
    if not surfaces:
        if test.get("id") == "baseline-no-archive":
            continue
        raise SystemExit(f"self-sufficiency test {test.get('id')} has no surfaces")
    for rel in surfaces:
        base = rel.split('#', 1)[0]
        if base and not (ROOT / base).exists():
            raise SystemExit(f"self-sufficiency test references missing surface: {rel}")
if not any(any(surface in canon for surface in test.get("surfaces", [])) for test in latest.get("packet_tests", [])):
    raise SystemExit("latest self-sufficiency tests must cover at least one current canon addition")
print("check_self_sufficiency_tail_alignment: OK")
