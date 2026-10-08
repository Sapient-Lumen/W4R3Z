#!/usr/bin/env python3
from __future__ import annotations

import json

from archive_meta import GENERATED, current_revision, generated_at_utc

CURRENT_REV = current_revision()
CHAIN_RANGE = list(range(812, 825))

NOTE_LABELS = {
    812: "form ladder / threshold choice",
    813: "legitimacy and mandate",
    814: "fiscal risk",
    815: "administration and operating home",
    816: "oversight and audit",
    817: "participation, user route, and redress",
    818: "information and public record",
    819: "boundary and membership",
    820: "amendment, renewal, and reapproval",
    821: "dispute resolution",
    822: "assets and liabilities",
    823: "contracts, concessions, and procurement",
    824: "regulation, inspection, and enforcement",
}


def classify(note: int, live_count: int, reserved_count: int, case_count: int) -> str:
    if note == 812:
        return "dispatcher foundation"
    if live_count >= max(5, case_count - 1):
        return "core field"
    if live_count >= 4:
        return "common field"
    if live_count + reserved_count >= 4:
        return "escalation field"
    if live_count > 0:
        return "specialized field"
    return "latent field"


def recommendation(note: int, classification: str) -> str:
    if note == 812:
        return "keep as the form-choice threshold; do not bury the ladder inside recurrence counts"
    if classification == "core field":
        return "candidate for the future cross-boundary-form manual core, while preserving the original note until a drafted merge keeps its tests"
    if classification == "common field":
        return "candidate for a shared evidence / membership chapter, not a deletion target"
    if classification == "escalation field":
        return "keep as an escalation annex; low live count is expected because the field is triggered by assets, contracts, enforcement, amendment, or disputes"
    if classification == "specialized field":
        return "keep active as a narrow trigger note; do not generalize it into every case"
    return "retain as latent until another applied packet proves whether it should merge, narrow, or retire"


def render_markdown(data: dict) -> str:
    lines = [
        "# Cross-boundary consolidation audit",
        "",
        f"Generated for `{data['revision']}` from `generated/CASE_PACKET_MATRIX.json`.",
        "",
        "## Audit holding",
        "",
        data["audit_holding"],
        "",
        "## Chain-field recurrence",
        "",
        "| Note | Label | Classification | Live | Reserved | Recommendation |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]
    for row in data["chain_fields"]:
        lines.append(
            f"| `{row['note']}` | {row['label']} | {row['classification']} | {row['live_count']} | {row['reserved_count']} | {row['recommendation']} |"
        )
    lines.extend([
        "",
        "## Consolidation map",
        "",
    ])
    for item in data["consolidation_map"]:
        lines.append(f"- **{item['bucket']}**: {item['notes']} — {item['instruction']}")
    lines.extend([
        "",
        "## Do-not-collapse fields",
        "",
    ])
    for item in data["do_not_collapse"]:
        lines.append(f"- `{item['note']}` {item['label']}: {item['reason']}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    matrix = json.loads((GENERATED / "CASE_PACKET_MATRIX.json").read_text(encoding="utf-8"))
    case_count = int(matrix.get("case_count", 0))
    live_counts = {int(k): int(v) for k, v in matrix.get("live_chain_note_counts", {}).items()}
    reserved_counts = {int(k): int(v) for k, v in matrix.get("reserved_chain_note_counts", {}).items()}
    cases = matrix.get("cases", [])

    fields = []
    for note in CHAIN_RANGE:
        live = live_counts.get(note, 0)
        reserved = reserved_counts.get(note, 0)
        cl = classify(note, live, reserved, case_count)
        fields.append({
            "note": note,
            "label": NOTE_LABELS.get(note, "unlabeled"),
            "classification": cl,
            "live_count": live,
            "reserved_count": reserved,
            "live_cases": [c.get("case_id") for c in cases if note in c.get("live_chain_notes", [])],
            "reserved_cases": [c.get("case_id") for c in cases if note in c.get("reserved_notes", [])],
            "recommendation": recommendation(note, cl),
        })

    data = {
        "revision": CURRENT_REV,
        "generated_at_utc": generated_at_utc(),
        "generated_from": "generated/CASE_PACKET_MATRIX.json",
        "case_count": case_count,
        "audit_holding": "The 812-824 chain should now be read through the 860 manual and the 861 defeat-test discipline. It is manual-ready, but not deletion-ready: consolidation must keep a dispatcher foundation, core legitimacy/fiscal/admin/oversight/user fields, shared information and membership fields, separate escalation annexes, and explicit soft-law, database-waist, plural-order, supplier-dependency, municipal-distress handback, symbolic-authority / mandate-capacity, fragile-jurisdiction capacity-floor, model-mediated evidentiary-proxy / automated-decision, generative-guidance reliance, staff-facing AI shadow-action, transition-receipt / decommissioning, platform-migration / reprocurement, ecological legal-personhood / rights-of-nature, and entitlement-continuity / procedural-churn, payment-redress / refund-state, credential-access / identity-proofing, representative-access / proxy-authority, health-benefit, climate-utility, housing-continuity, cyber/software-continuity, and election-continuity cautions from the newer applied packets.",
        "chain_fields": fields,
        "consolidation_map": [
            {"bucket": "manual front door", "notes": "848 plus 860 and 861", "instruction": "use the dispatcher, manual, and defeat tests as the first-entry route before any chain note is cited"},
            {"bucket": "form foundation", "notes": "812", "instruction": "keep as the form-choice ladder inside the manual; do not bury the minimum-sufficient-form question"},
            {"bucket": "core operating fields", "notes": "813-817", "instruction": "draft as the manual core only while preserving fiscal, oversight, participation, and redress tests"},
            {"bucket": "shared evidence and boundary fields", "notes": "818-819", "instruction": "merge with strong examples because public record and membership surfaces are common but not equally heavy in thin cases"},
            {"bucket": "escalation annexes", "notes": "820-824", "instruction": "keep visibly separate; each protects a distinct heavy-power path that can be hidden by generic connector language"},
            {"bucket": "waist-capture annex", "notes": "856 plus 862-863", "instruction": "add explicit soft-law-hardening and database-alert tests to prevent recommendations, ratings, alerts, and data systems from becoming hidden authority"},
            {"bucket": "plural-order annex", "notes": "864 plus 865", "instruction": "add authority-lane, consent / co-decision, legal-person, retained-state-duty, public-rights, and remedy tests when Indigenous authority, legal personality, or relational territory is live"},
            {"bucket": "supplier-dependency annex", "notes": "859 plus 866-867", "instruction": "add public-owner, processor, admin-access, product-purpose, benefit-proof, opposition, fallback, and exit-rehearsal tests when cloud, SaaS, AI, identity, analytics, or platform suppliers become public-service infrastructure"},
            {"bucket": "municipal distress handback annex", "notes": "583 plus 861 and 868-869", "instruction": "add legal-trigger, active-power, waiver, reactivation, local-capacity, service-continuity, record-publication, democratic-damage, and final-release tests when fiscal distress, receivership, state oversight, devolution, or handback is live"},
            {"bucket": "symbolic-authority annex", "notes": "861 plus 870-871", "instruction": "add mandate-owner, resource-control, data-reality, contract-traceability, provider-dependence, principal-accountability, attribution-boundary, transition-receipt, and recharter-choice tests when a visible body is credited, blamed, abolished, absorbed, or expanded for a public outcome whose operative levers sit elsewhere"},
            {"bucket": "capacity-floor annex", "notes": "861 plus 872-873", "instruction": "add mandate-capacity, host-owner, pledge-to-deployment, access-class, civilian-harm, humanitarian-boundary, justice-chain, private-force, emergency-record, and handback-ladder tests when fragile-jurisdiction or donor-dependent support arrangements are treated as operative authority"},
            {"bucket": "model-decision annex", "notes": "857 plus 861 and 874-875", "instruction": "add legal-authority, evidentiary-proxy, burden, data-lineage, human-determination, notice / explanation, review / stay, vulnerability, business-rule scrutiny, and remediation-loop tests when data matches, models, rule engines, scores, calculators, workflows, or AI systems may create legal or similarly significant public effects"},
            {"bucket": "generative-assistant annex", "notes": "856 plus 859, 861, 867, 874, and 876-878", "instruction": "add public-owner, canonical-corpus, source-trace, reliance-warning, answer-consistency, accessibility, correction-clock, incident-disclosure, supplier / model-change, human-handoff, and withdrawal / transition-receipt tests when public chatbots, RAG assistants, service bots, or generated guidance shape conduct or service access without a formal decision"},
            {"bucket": "staff-copilot annex", "notes": "856 plus 859, 861, 867, 874, 876, and 879-883", "instruction": "add use-case register, input/source lineage, output capture, review-quality, queue-effect, release-gate, sensitive-data, model-change, and feedback-loop tests when internal AI tools shape public action without direct public output"},
            {"bucket": "transition-receipt annex", "notes": "861 plus 884-886", "instruction": "add terminal-status, successor-function, affected-user, record-preservation, data-closeout, procurement / contract, incident-learning, cost-benefit, residual-dependency, and relaunch-gate tests when a tool, platform, body, emergency measure, supplier arrangement, or AI system is ended, converted, absorbed, migrated, made optional, or relaunched"},
            {"bucket": "platform-migration annex", "notes": "859 plus 867, 884, and 887-889", "instruction": "add old/new authority, data / identity / entitlement mapping, backlog and remedy tail, rule / configuration readiness, interface dependency, parallel-run reconciliation, cutover / rollback, affected-user continuity, contract / supplier exit, legacy fallback, and post-migration value / harm tests when a public platform, portal, SaaS tenant, account system, status-proof service, payroll system, data hub, case-management system, identity register, or supplier-backed infrastructure is replaced, migrated, reprocured, dual-run, cut over, made digital-only, or retired"},
            {"bucket": "ecological-personhood annex", "notes": "864 plus 890-893", "instruction": "add subject-boundary, guardian-spine, community-authority, scientific-baseline, remedy-budget, enforcement / standing, liability-boundary, ordinary-regime non-displacement, public-record, and failure-route tests when ecosystems are recognized as legal persons, living entities, or rights-bearing subjects"},
            {"bucket": "entitlement-continuity annex", "notes": "857 plus 861, 874, 884, 887, and 894-896", "instruction": "add entitlement-owner, renewal-window, ex parte, notice-comprehension, deadline, procedural-loss-denominator, payment / coverage continuity, assisted-route, appeal / reinstatement, transitional-protection, and learning-loop tests when an existing benefit, health coverage, tax credit, housing support, disability-linked support, income support, status proof, or service entitlement is renewed, redetermined, migrated, converted, closed, deadline-gated, or moved into a new claim / account / portal route"},
            {"bucket": "payment-redress annex", "notes": "857 plus 861, 884, 887, 894, and 897-900", "instruction": "add claimant-owner, legal / harm basis, calculation, payment-state, interim / final, lost-record, review-clock, fraud-control, family / support, publication-cost, and learning-loop tests when redress, compensation, refunds, refundable credits, settlements, or support-scheme payments are live"},
            {"bucket": "credential-access annex", "notes": "406 plus 856, 857, 861, 887, 894, 897, and 901-904", "instruction": "add service-consequence, assurance-fit, proofing-route, delegated-authority, relying-party, recovery, privacy / biometric, outage / fallback, standards-reapproval, and public-metric tests when login, identity proofing, federation, wallets, passkeys, or shared identity providers gate public services"},
            {"bucket": "representative-access annex", "notes": "857 plus 861, 887, 894, 897, 901, and 905-909", "instruction": "add authority-type, capacity / consent, credential-separation, payment-fiduciary, notice-routing, revocation / restoration, conflict / misuse, cross-system migration, appeal / health-information, and public-metric tests when payees, appointees, guardians, tax professionals, appeal representatives, helpers, caregivers, or delegated users can act for a person"},
        ],
        "do_not_collapse": [
            {"note": 820, "label": NOTE_LABELS[820], "reason": "material amendments and reapproval clocks are rare but constitutional when triggered"},
            {"note": 821, "label": NOTE_LABELS[821], "reason": "dispute ladders recur in contracts, enforcement, and treaty settings but should not be presumed for every thin service hub"},
            {"note": 822, "label": NOTE_LABELS[822], "reason": "asset and liability ledgers are heavy when present and dangerous when hidden"},
            {"note": 823, "label": NOTE_LABELS[823], "reason": "contracts and concessions can become constitutional escape hatches if merged into generic administration"},
            {"note": 824, "label": NOTE_LABELS[824], "reason": "inspection, licensing, detention, sanctions, and recommendations require explicit legal-owner and review boundaries"},
        ],
    }
    (GENERATED / "CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (GENERATED / "CROSS_BOUNDARY_CONSOLIDATION_AUDIT.md").write_text(render_markdown(data), encoding="utf-8")
    print("OK: wrote generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.json and generated/CROSS_BOUNDARY_CONSOLIDATION_AUDIT.md")


if __name__ == "__main__":
    main()
