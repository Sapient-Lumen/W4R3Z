import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
out = ROOT / "frontier-ticket.json"

context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
obligations = json.loads((ROOT / "OBLIGATION-LEDGER.json").read_text(encoding="utf-8"))["items"]
retros = json.loads((ROOT / "RETROSPECTIVE-QUEUE.json").read_text(encoding="utf-8"))["items"]

focus = context["open_questions"][-1]
latest_open_ob = next(
    (item for item in reversed(obligations) if item.get("state") == "open" or item.get("obligation_state") == "open"),
    None,
)
latest_cooling_rt = next((item for item in reversed(retros) if item.get("state") == "cooling"), None)
if latest_open_ob is None:
    raise SystemExit("no open obligation row found")
if latest_cooling_rt is None:
    raise SystemExit("no cooling retrospective row found")

status_lanes = status["status_lanes"]
pack = {
    "project": "DelayBasin",
    "revision": context["revision"],
    "derivative_note": "Derivative frontier aid; canon wins.",
    "selection_policy": {
        "primary_focus_rule": "select the last source-backed unresolved hot open question already projected into context-pack.json",
        "background_rule": "carry the latest open obligation and latest cooling retrospective as compact continuity checks",
        "source_surfaces": [
            "context-pack.json",
            "docs/20-constitution/open-question-registry.md",
            "docs/00-meta/trajectory-map.md",
            "OBLIGATION-LEDGER.json",
            "RETROSPECTIVE-QUEUE.json",
        ],
    },
    "current_posture": {
        "operational_head": status["operational_head"]["surface"],
        "citation_head": status["citation_head"]["surface"],
        "decision_state": status_lanes["decision_state"],
        "execution_state": status_lanes["execution_state"],
        "public_state": status_lanes["public_state"],
        "state_class": status["state_class"],
    },
    "primary_focus": {
        "id": focus["id"],
        "source": focus["source"],
        "selection_source": focus["selection_source"],
        "text": focus["text"],
        "governing_surface": f"{focus['source']}#{focus['id'].lower()}",
    },
    "background_checks": {
        "latest_obligation": {
            "id": latest_open_ob["id"],
            "surface": f"OBLIGATION-LEDGER.json#{latest_open_ob['id']}",
            "title": latest_open_ob["title"],
            "discharge": latest_open_ob["discharge"],
        },
        "latest_retrospective": {
            "id": latest_cooling_rt["id"],
            "surface": f"RETROSPECTIVE-QUEUE.json#{latest_cooling_rt['id']}",
            "title": latest_cooling_rt["title"],
            "discharge": latest_cooling_rt["discharge"],
        },
    },
    "reentry_anchors": {
        "startup_surface": "START_HERE.md",
        "wrapper_surface": "AGENTS.md",
        "runbook_surface": "docs/00-meta/llm-runbook.md",
        "compact_packet": "context-pack.json",
        "status_surface": "SURFACE-STATUS.json",
    },
}
out.write_text(json.dumps(pack, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
print(f"wrote {out}")
