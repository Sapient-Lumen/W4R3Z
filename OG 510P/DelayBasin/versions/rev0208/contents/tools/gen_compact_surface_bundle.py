import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "compact-surface-bundle.json"

changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
m = re.search(r"(rev\d{4})", changelog)
if not m:
    raise SystemExit("CHANGELOG.md missing current revision header")
rev = m.group(1)

members = [
    {
        "surface": "context-pack.json",
        "role": "compact reentry packet",
        "mode": "generated",
        "governing_underliers": [
            "START_HERE.md",
            "docs/20-constitution/open-question-registry.md",
            "docs/00-meta/trajectory-map.md",
            "SURFACE-STATUS.json",
            "REVISION-RECEIPT.json",
        ],
        "generator": "tools/gen_context_pack.py",
    },
    {
        "surface": "frontier-ticket.json",
        "role": "selected-focus handoff",
        "mode": "generated",
        "governing_underliers": [
            "context-pack.json",
            "docs/20-constitution/open-question-registry.md",
            "docs/00-meta/trajectory-map.md",
            "OBLIGATION-LEDGER.json",
            "RETROSPECTIVE-QUEUE.json",
        ],
        "generator": "tools/gen_frontier_ticket.py",
    },
    {
        "surface": "innovation-packet.json",
        "role": "exact current innovation packet",
        "mode": "generated",
        "governing_underliers": [
            "REVISION-RECEIPT.json",
            "SURFACE-STATUS.json",
            "CHANGELOG.md",
            "RELEASE-MANIFEST.json",
        ],
        "generator": "tools/gen_innovation_packet.py",
    },
    {
        "surface": "replay-capsule.json",
        "role": "bounded replay-sufficiency handoff",
        "mode": "generated",
        "governing_underliers": [
            "docs/10-method/sufficiency-witnesses-replay-capsules-and-core-only-reentry-trials.md",
            "START_HERE.md",
            "SURFACE-STATUS.json",
            "innovation-packet.json",
            "frontier-ticket.json",
        ],
        "generator": "tools/gen_replay_capsule.py",
    },
    {
        "surface": "VALIDATION-INDEX.json",
        "role": "validation inventory",
        "mode": "generated",
        "governing_underliers": [
            "Makefile",
            "tools/run_lint_suite.py",
            "docs/00-meta/validation-index.md",
        ],
        "generator": "tools/gen_validation_index.py",
    },
    {
        "surface": "REENTRY-CONTRACT.json",
        "role": "machine-readable reentry contract",
        "mode": "authored",
        "governing_underliers": [
            "START_HERE.md",
            "AGENTS.md",
            "docs/00-meta/llm-runbook.md",
            "docs/10-method/derivative-operator-contracts-low-entropy-reentry-wrappers-and-non-canon-read-first-surfaces.md",
        ],
        "generator": None,
    },
    {
        "surface": "REENTRY-SURFACE-CONFORMANCE.json",
        "role": "startup-contract witness",
        "mode": "generated",
        "governing_underliers": [
            "REENTRY-CONTRACT.json",
            "START_HERE.md",
            "AGENTS.md",
            "docs/00-meta/llm-runbook.md",
        ],
        "generator": "tools/gen_reentry_surface_conformance.py",
    },
]
for row in members:
    if not (ROOT / row["surface"]).exists():
        raise SystemExit(f"missing compact surface member: {row['surface']}")
    for underlier in row["governing_underliers"]:
        if not (ROOT / underlier).exists():
            raise SystemExit(f"missing governing underlier: {underlier}")

payload = {
    "project": "DelayBasin",
    "revision": rev,
    "surface": "compact-surface-bundle.json",
    "derivative_note": "Derivative compact-surface family card; canon wins.",
    "family_rule": {
        "purpose": "Keep the current operator-facing compact derivative surfaces closed, enumerable, and honest about what stronger surfaces still govern them.",
        "inclusion_rule": "A surface belongs here only if it is a compact operator-facing derivative aid in the repo root that lowers startup, reentry, or discovery scan cost without changing canonical ownership.",
        "attachment_rule": "If a new compact operator-facing derivative aid is added, the same revision should either add it here with role, underliers, and generator/authored posture or keep it out with an explicit reason in receipt, canon, or quarantine.",
        "non_members": [
            "START_HERE.md",
            "AGENTS.md",
            "REVISION-RECEIPT.json",
            "SURFACE-STATUS.json",
            "RELEASE-MANIFEST.json",
        ],
    },
    "bundle_status": {
        "member_count": len(members),
        "present_members": [row["surface"] for row in members],
        "borrowed_members": [],
        "upgrade_trigger": "Reopen this family card if a new compact operator-facing derivative aid is added, an existing member is retired, or a member loses same-revision attachment to its stronger underliers.",
    },
    "members": members,
    "reentry_hooks": {
        "startup_surface": "START_HERE.md",
        "wrapper_surface": "AGENTS.md",
        "runbook_surface": "docs/00-meta/llm-runbook.md",
    },
    "explicit_non_claim": "Not a bundle board, porch registry, queue controller, or replacement for START_HERE.md, REVISION-RECEIPT.json, SURFACE-STATUS.json, or RELEASE-MANIFEST.json.",
}
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
