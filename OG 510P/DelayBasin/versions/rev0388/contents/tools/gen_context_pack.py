import json
import pathlib
import re

from open_question_selection_lib import select_context_open_questions
from ledger_debt_policy_lib import LEDGER_DEBT_POLICIES, live_debt_snapshot

ROOT = pathlib.Path(__file__).resolve().parents[1]
out = ROOT / "context-pack.json"




def parse_lexicon(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    certified = []
    provisional = []
    current = None
    for raw in text.splitlines():
        m = re.match(r"- `(?P<id>LX-\d{4})` — `(?P<term>[^`]+)`", raw.strip())
        if m:
            current = {"id": m.group("id"), "term": m.group("term"), "class": None}
            continue
        if current is not None and raw.strip().startswith("- Class:"):
            current["class"] = raw.split(":", 1)[1].strip()
            target = certified if current["class"] == "certified-core" else provisional
            target.append({"id": current["id"], "term": current["term"]})
            current = None
    return certified, provisional


def parse_moves(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    certified = []
    current = None
    for raw in text.splitlines():
        m = re.match(r"- `(?P<id>MV-\d{4})` — `(?P<term>[^`]+)`", raw.strip())
        if m:
            current = {"id": m.group("id"), "class": None}
            continue
        if current is not None and raw.strip().startswith("- Class:"):
            current["class"] = raw.split(":", 1)[1].strip()
            if current["class"] == "certified-move":
                certified.append(current["id"])
            current = None
    return certified


def parse_decay_watch(path: pathlib.Path):
    text = path.read_text(encoding="utf-8")
    entries = []
    current = None
    for raw in text.splitlines():
        m = re.match(r"- `(?P<id>DW-\d{4})` — `(?P<label>[^`]+)`", raw.strip())
        if m:
            if current:
                entries.append(current)
            current = {"id": m.group("id"), "label": m.group("label"), "horizon": None, "review_status": None}
            continue
        if current is not None and raw.strip().startswith("- Review horizon:"):
            current["horizon"] = raw.split(":", 1)[1].strip()
        if current is not None and raw.strip().startswith("- Review status:"):
            current["review_status"] = raw.split(":", 1)[1].strip().split(";", 1)[0]
    if current:
        entries.append(current)
    return entries


def month_key(value: str):
    m = re.match(r"(\d{4})-(\d{2})", value)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2))


def overdue_decay(entries, created_at: str):
    current = month_key(created_at)
    if current is None:
        return []
    out = []
    for entry in entries:
        horizon = month_key(entry.get("horizon") or "")
        if horizon is not None and horizon < current:
            enriched = dict(entry)
            enriched["overdue_as_of"] = created_at[:7]
            out.append(enriched)
    return out


def queue_health(root: pathlib.Path, current_revision: str):
    snapshots = {}
    totals = {}
    latest_ids = {}
    for rel, policy in LEDGER_DEBT_POLICIES.items():
        items = json.loads((root / rel).read_text(encoding="utf-8"))["items"]
        snapshots[rel] = live_debt_snapshot(items, policy, current_revision)
        totals[rel] = len(items)
        latest_ids[rel] = items[-1].get("id") if items else None

    # Keep the context pack backward-compatible and within its hard byte budget.
    # Rich four-ledger budget/headroom evidence belongs in ARCHIVE-ECONOMY-AUDIT.
    followthrough = snapshots["FOLLOWTHROUGH-QUEUE.json"]
    assumptions = snapshots["ASSUMPTION-LEDGER.json"]
    obligations = snapshots["OBLIGATION-LEDGER.json"]
    return {
        "followthrough_total": totals["FOLLOWTHROUGH-QUEUE.json"],
        "followthrough_queued": followthrough["live_count"],
        "latest_followthrough_id": latest_ids["FOLLOWTHROUGH-QUEUE.json"],
        "oldest_queued_followthrough_id": followthrough["oldest_live_id"],
        "assumptions_total": totals["ASSUMPTION-LEDGER.json"],
        "assumptions_active": assumptions["live_count"],
        "latest_assumption_id": latest_ids["ASSUMPTION-LEDGER.json"],
        "oldest_active_assumption_id": assumptions["oldest_live_id"],
        "obligations_total": totals["OBLIGATION-LEDGER.json"],
        "obligations_open": obligations["live_count"],
        "latest_obligation_id": latest_ids["OBLIGATION-LEDGER.json"],
        "oldest_open_obligation_id": obligations["oldest_live_id"],
    }


changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
rev = re.search(r"(rev\d{4})", changelog).group(1)

start_here = (ROOT / "START_HERE.md").read_text(encoding="utf-8")
must_read = []
for line in start_here.splitlines():
    m = re.match(r"\d+\. `([^`]+)`", line.strip())
    if m:
        must_read.append(m.group(1))
if not must_read:
    raise SystemExit("could not derive must_read from START_HERE.md")
for rel in must_read:
    if not (ROOT / rel).exists():
        raise SystemExit(f"must_read path missing: {rel}")

required_must_read = [
    "docs/10-method/witness-vocabularies-state-families-and-comparability-budgets.md",
    "docs/10-method/transfer-ledgers-adopted-non-takes-and-repeat-argument-brakes.md",
    "docs/10-method/operational-heads-citation-heads-and-frozen-public-surfaces.md",
    "docs/10-method/gate-classes-future-trigger-kinds-and-bounded-reopen-rules.md",
]
must_read = [rel for rel in required_must_read if rel in must_read]

open_questions = select_context_open_questions(ROOT)

certified, provisional = parse_lexicon(ROOT / "docs/20-constitution/core-lexicon-registry.md")
certified_moves = parse_moves(ROOT / "docs/20-constitution/move-registry.md")
decay_watch = parse_decay_watch(ROOT / "docs/20-constitution/decay-watch-registry.md")
status = json.loads((ROOT / "SURFACE-STATUS.json").read_text(encoding="utf-8"))
manifest = json.loads((ROOT / "RELEASE-MANIFEST.json").read_text(encoding="utf-8"))
receipt = json.loads((ROOT / "REVISION-RECEIPT.json").read_text(encoding="utf-8"))

pack = {
    "project": "DelayBasin",
    "revision": rev,
    "must_read": must_read,
    "open_questions": open_questions,
    "frontier_ticket": {
        "surface": "frontier-ticket.json",
        "selected_focus_id": open_questions[-1]["id"],
    },
    "innovation_packet": {
        "surface": "innovation-packet.json",
        "anchor_revision": receipt["previous_revision"],
    },
    "validation": {
        "surface": "VALIDATION-INDEX.json",
        "guide": "docs/00-meta/validation-index.md",
        "toolchain_manifest": "VALIDATION-TOOLCHAIN-MANIFEST.json",
        "toolchain_guide": "docs/00-meta/validation-toolchain.md",
    },
    "replay_capsule": {
        "surface": "replay-capsule.json"
    },
    "current_posture": {
        "operational_head": status["operational_head"]["surface"],
        "citation_head": status["citation_head"]["surface"],
        "decision_state": status["status_lanes"]["decision_state"],
        "execution_state": status["status_lanes"]["execution_state"],
        "public_state": status["status_lanes"]["public_state"],
        "state_class": status["state_class"],
    },
    "operator_warnings": [
        {"id": "OW-0001", "source": "docs/10-method/derivative-operator-contracts-low-entropy-reentry-wrappers-and-non-canon-read-first-surfaces.md", "text": "Derivative aids; canon wins"},
        {"id": "OW-0002", "source": "SURFACE-STATUS.json", "text": "Working tree is not citation head."},
        {"id": "OW-0003", "source": "DATACUBE-TRANSFER-LEDGER.json", "text": "Check transfer ledger before peer import."},
        {"id": "OW-0004", "source": "WITNESS-VOCABULARY.json", "text": "Use exact governed tokens."}
    ],
    "reentry_contract": {
        "surface": "REENTRY-CONTRACT.json",
        "conformance": "REENTRY-SURFACE-CONFORMANCE.json",
        "profile_id": "careful-revision-pass",
    },
    "core_lexicon": {
        "registry": "docs/20-constitution/core-lexicon-registry.md",
        "certified": certified,
        "provisional": provisional,
    },
    "move_registry": {
        "registry": "docs/20-constitution/move-registry.md",
        "certified": certified_moves,
    },
    "promotion_surface": "docs/20-constitution/promotion-contract-registry.md",
    "decay_surface": "docs/20-constitution/decay-watch-registry.md",
    "decay_watch": decay_watch[-1:],
    "decay_watch_overdue": [{"id": entry["id"], "review_status": entry.get("review_status")} for entry in overdue_decay(decay_watch, receipt["created_at"])],
    "queue_health": queue_health(ROOT, receipt["revision"]),
    "self_sufficiency_ledger": {"surface": "SELF-SUFFICIENCY-LEDGER.json"},
    "witness_family_handles": {"surface": "WITNESS-FAMILY-HANDLES.json"},
    "recovery": {
        "surface": "docs/20-constitution/recovery-kernel.md",
        "move": "MV-0010"
    },
    "revision_receipt": {
        "surface": "REVISION-RECEIPT.json",
        "contract": "docs/20-constitution/revision-receipt-contract.md",
        "move": "MV-0011"
    },
    "compact_surface_bundle": {
        "surface": "compact-surface-bundle.json"
    },
    "typed_reentry": {
        "workflow_surface": "docs/50-promptcraft/prompt-pairs.md",
        "state_surfaces": [
            "START_HERE.md",
            "SURFACE-STATUS.json",
            "RELEASE-MANIFEST.json",
            "context-pack.json",
            "innovation-packet.json",
            "frontier-ticket.json",
            "replay-capsule.json",
            "compact-surface-bundle.json",
            "VALIDATION-INDEX.json",
            "docs/00-meta/validation-index.md",
            "VALIDATION-TOOLCHAIN-MANIFEST.json",
            "docs/00-meta/validation-toolchain.md",
            "LINT-IDEMPOTENCE-AUDIT.json",
            "docs/00-meta/lint-idempotence-audit.md",
            "CURRENTNESS-CUE-AUDIT.json",
            "docs/00-meta/currentness-cue-audit.md",
            "PACKAGE-IDENTITY-AUDIT.json",
            "docs/00-meta/package-identity-audit.md",
            "BASIS-PROVENANCE-AUDIT.json",
            "docs/00-meta/basis-provenance-audit.md",
            "SCHEMA-COVERAGE-AUDIT.json",
            "docs/00-meta/schema-coverage-audit.md",
            "SCHEMA-CONFORMANCE-AUDIT.json",
            "docs/00-meta/schema-conformance-audit.md",
            "ALIAS-RETENTION-POLICY.json",
            "CANARY-PROTOCOL.json",
            "CANARY-RUNS.json",
            "LEDGER-AUDIT.json",
            "docs/00-meta/ledger-audit.md",
            "ARCHIVE-ECONOMY-AUDIT.json",
            "docs/00-meta/archive-economy-audit.md",
            "REENTRY-CONTRACT.json",
            "REENTRY-SURFACE-CONFORMANCE.json",
            "CURRENT-RECEIPT.json",
            "REVISION-RECEIPT.json",
            "WITNESS-VOCABULARY.json",
            "SELF-SUFFICIENCY-LEDGER.json",
            "WITNESS-FAMILY-HANDLES.json",
            "docs/20-constitution/open-question-registry.md",
        ],
        "check_surface": "make lint",
        "admission_moves": certified_moves,
        "quarantine_surface": "docs/90-quarantine/wild-speculations-2026-03-08.md",
    },
    "commands": {
        "context_pack": "make context-pack",
        "all_generated_surfaces": "python3 tools/gen_all_generated_surfaces.py",
        "lint": "make lint",
        "replay_capsule": "python3 tools/gen_replay_capsule.py",
        "validation_toolchain": "python3 tools/gen_validation_toolchain_manifest.py",
        "basis_provenance_audit": "python3 tools/gen_basis_provenance_audit.py",
        "schema_coverage_audit": "python3 tools/gen_schema_coverage_audit.py",
        "schema_conformance_audit": "python3 tools/gen_schema_conformance_audit.py",
        "archive_economy_audit": "python3 tools/gen_archive_economy_audit.py",
        "compact_surface_bundle": "python3 tools/gen_compact_surface_bundle.py",
        "reentry_conformance": "python3 tools/gen_reentry_surface_conformance.py",
        "score_external_response": "make score-external-response RESPONSE=response.json EVIDENCE=evidence.json SCORE_SHEET=score-sheet.json SUMMARY_OUT=score-summary.json",
        "package_release": "make package-release STAMP=... SLUG=...",
    },
}
out.write_text(json.dumps(pack, ensure_ascii=False, separators=(",",":")) + "\n", encoding="utf-8")
print(f"wrote {out}")
