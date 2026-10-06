import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "replay-capsule.json"

context = json.loads((ROOT / "context-pack.json").read_text(encoding="utf-8"))
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
innovation = json.loads((ROOT / "innovation-packet.json").read_text(encoding="utf-8"))
frontier = json.loads((ROOT / "frontier-ticket.json").read_text(encoding="utf-8"))
bundle = json.loads((ROOT / "compact-surface-bundle.json").read_text(encoding="utf-8"))

candidate_surfaces = [
    "START_HERE.md",
    "SURFACE-STATUS.json",
    "innovation-packet.json",
    "frontier-ticket.json",
    "compact-surface-bundle.json",
]
for rel in candidate_surfaces:
    if not (ROOT / rel).exists():
        raise SystemExit(f"missing replay-capsule candidate surface: {rel}")

payload = {
    "project": "DelayBasin",
    "revision": context["revision"],
    "surface": "replay-capsule.json",
    "derivative_note": "Derivative bounded replay-capsule aid; canon wins.",
    "packet_sources": [
        "docs/10-method/sufficiency-witnesses-replay-capsules-and-core-only-reentry-trials.md",
        "START_HERE.md",
        "AGENTS.md",
        "docs/00-meta/llm-runbook.md",
        "SURFACE-STATUS.json",
        "REVISION-RECEIPT.json",
        "innovation-packet.json",
        "frontier-ticket.json",
        "compact-surface-bundle.json",
    ],
    "candidate_reduced_packet": {
        "surfaces": candidate_surfaces,
        "selection_rule": "Keep the smallest current replay seed that still names the head, exact delta, live focus, and compact derivative family before canon is reopened.",
        "governing_underliers": [
            "REVISION-RECEIPT.json",
            "docs/20-constitution/open-question-registry.md",
            "docs/00-meta/trajectory-map.md",
            "docs/10-method/sufficiency-witnesses-replay-capsules-and-core-only-reentry-trials.md",
        ],
    },
    "bounded_sufficiency": {
        "core_only_replay_surface": "replay-capsule.json",
        "fixed_context_family": [
            "local checked repo tree only",
            "the named candidate packet surfaces only",
            "ordinary careful next-pass reentry rather than fresh canon import or final proof",
        ],
        "withheld_context_family": [
            "full docs/10-method cold scan",
            "full changelog history scan",
            "older frozen bundles beyond the current citation head",
            "same-session hidden carry not named in the packet",
        ],
        "target_continuation_property": "Recover the current citation head, exact current delta, selected live focus, and compact derivative family well enough to reopen canon for an ordinary careful next revision pass.",
        "tolerated_degradation": "The capsule may lose deeper justification and still count as adequate only if it still points the operator back to the governing receipt, status, and canon surfaces before import, packaging, or canon promotion.",
        "sufficiency_state": "bounded-ordinary-reentry-only",
    },
    "reinflate_route": {
        "reinflate_triggers": [
            "the next pass cannot recover the current exact delta from innovation-packet.json plus REVISION-RECEIPT.json",
            "the next pass cannot tell what live focus or compact family is current without scanning broader canon immediately",
            "a canon import, package claim, or stronger authority move is being attempted from the capsule alone",
        ],
        "fallback_surfaces": [
            "AGENTS.md",
            "docs/00-meta/llm-runbook.md",
            "REVISION-RECEIPT.json",
            "docs/20-constitution/open-question-registry.md",
            "docs/00-meta/trajectory-map.md",
            "docs/10-method/sufficiency-witnesses-replay-capsules-and-core-only-reentry-trials.md",
        ],
        "repair": "reopen underliers and reinflate to the stronger startup and canon surfaces before acting.",
        "quarantine_consequence": "Retire or narrow the capsule if later revisions keep treating it as a proven minimal seed, universal replay prompt, or substitute for receipt-plus-canon reread.",
    },
    "current_projection": {
        "citation_head": status["citation_head"]["surface"],
        "anchor_revision": innovation["anchor"]["previous_revision"],
        "selected_focus_id": frontier["primary_focus"]["id"],
        "compact_family_surface": bundle["surface"],
    },
    "explicit_non_claim": "Not a proven minimal seed, universal replay prompt, or substitute for START_HERE.md, REVISION-RECEIPT.json, SURFACE-STATUS.json, AGENTS.md, or make lint.",
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
