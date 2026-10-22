# Ward rev0099 — verification-intake receipts, proof-drift guards, and metadata lineage audit

Current revision: `rev0099` — verification-intake receipts, proof-drift guards, and metadata lineage audit.

Ward is the trust/governance companion for SlopOS. Rev0099 adds verification-intake receipts so external proof can be verified, failed, absent, or conflicted without becoming remedy completion, quarantine clearance, export, repair, action, status-pointer mutation, or authority.

Latest pass links:

- [docs/00-meta/research-synthesis-2026-05-26-pass-xcix.md](docs/00-meta/research-synthesis-2026-05-26-pass-xcix.md)
- [docs/00-meta/slopos-companions-evaluation-2026-05-26-pass-xcix.md](docs/00-meta/slopos-companions-evaluation-2026-05-26-pass-xcix.md)
- [docs/30-architecture/specimen-flow-96-verification-intake-proof-drift-guards-and-metadata-lineage-audit.md](docs/30-architecture/specimen-flow-96-verification-intake-proof-drift-guards-and-metadata-lineage-audit.md)

Latest surfaces:

- `docs/20-assurance/governance-verification-intake-receipt-v0.md`
- `schemas/governance-verification-intake-receipt.v0.json`
- `tools/check_governance_verification_intakes.py`
- `tools/check_metadata_lineage_integrity.py`
- `docs/30-architecture/specimen-flow-96-verification-intake-proof-drift-guards-and-metadata-lineage-audit.md`

## Founding compression

**custody facet + claim set + witness material + appraisal lane + spend gate + durable verdict residue**

## How to navigate

1. Start-here briefing: [`START_HERE.md`](START_HERE.md)
2. Charter: [`docs/00-meta/charter.md`](docs/00-meta/charter.md)
3. Lessons: [`docs/00-meta/lessons-we-must-learn.md`](docs/00-meta/lessons-we-must-learn.md)
4. Datacube construction protocol: [`docs/00-meta/datacube-construction-protocol.md`](docs/00-meta/datacube-construction-protocol.md)
5. Research synthesis, pass XCIX: [`research-synthesis-2026-05-26-pass-xcix.md`](docs/00-meta/research-synthesis-2026-05-26-pass-xcix.md)
6. Datacube evaluation, pass XCIX: [`slopos-companions-evaluation-2026-05-26-pass-xcix.md`](docs/00-meta/slopos-companions-evaluation-2026-05-26-pass-xcix.md)
7. Noun-promotion rubric: [`docs/00-meta/noun-promotion-rubric.md`](docs/00-meta/noun-promotion-rubric.md)
8. Load-bearing source register: [`docs/00-meta/load-bearing-source-register.md`](docs/00-meta/load-bearing-source-register.md)
9. Source review queue: [`docs/00-meta/source-review-queue.md`](docs/00-meta/source-review-queue.md)
10. Architecture overview: [`docs/30-architecture/architecture-overview.md`](docs/30-architecture/architecture-overview.md)
11. Specimen flow index: [`docs/30-architecture/specimen-flow-index.md`](docs/30-architecture/specimen-flow-index.md)
12. Latest specimen: [`specimen-flow-95-remediation-closures-verification-debts-and-runbook-audit.md`](docs/30-architecture/specimen-flow-95-remediation-closures-verification-debts-and-runbook-audit.md)
13. Promotion gates: [`docs/30-architecture/promotion-gates-and-specimen-tests.md`](docs/30-architecture/promotion-gates-and-specimen-tests.md)
14. Non-decisions: [`docs/30-architecture/design-splits-and-non-decisions.md`](docs/30-architecture/design-splits-and-non-decisions.md)
15. Inspiration harvest: [`docs/90-inspirations/steal-these-ideas.md`](docs/90-inspirations/steal-these-ideas.md)


## New in rev0098

- **governance remediation-closure receipt v0** — non-authority post-remediation receipt downstream of rollback-remediation.
- **closure-scope and verification-evidence digests** — bind source remediation state, closure effect, evidence kind, and verification debt.
- **handoff/closure fences** — review closure and handoff acknowledgment cannot become rollback, remedy, quarantine clearance, export, status-pointer mutation, or authority.
- **tool-runbook audit/refactor** — `tools/check_tool_runbook_integrity.py` keeps `tools/README.md`, the checker registry, and `make check` runbook aligned.

## New in rev0097

- **governance rollback-remediation receipt v0** — non-authority post-observation receipt downstream of outcome observations.
- **remediation-scope digest** — binds source observation, target, recipient, projection policy, requested remediation effect, and consequence class.
- **remedy handoff fences** — mismatches can maintain quarantine, open rollback review, or request a handoff, but cannot execute rollback or remedy.
- **schema-catalog audit/refactor** — `tools/check_schema_catalog_integrity.py` audits governance schema files against the checker registry.

## New in rev0096

- **governance outcome-observation receipt v0** — non-authority post-execution observation receipt downstream of use-execution.
- **observed-outcome digest** — binds observed effect, target, recipient class, projection policy, observer class, and observation state.
- **rollback guards** — mismatches quarantine and require rollback review without performing rollback, repair, remedy, or status-pointer mutation.
- **unavailable-observation hold** — no observation means no green current claim.
- **fixture-catalog audit/refactor** — `tools/check_fixture_catalog_integrity.py` audits registry-backed fixture-family layout and schema parity.

## New in rev0094

- **governance reuse-gate receipt v0** — consequence-specific, non-authority gate downstream of receiver convergence.
- **consequence-scope digest** — binds request id, purpose, recipient class, source release, cache subject, consequence class, requested effect, and projection policy.
- **safe reuse states** — display/internal review may be allowed narrowly, export is held for evidence-release, high-consequence repair/action is refused, and receiver gaps quarantine reuse.
- **schema registry audit/refactor** — checker registry entries now carry schema ids and schema paths, and registry integrity verifies them.
- **reuse-gate checker** — validates five positive fixtures and twenty negative fixtures covering digest drift, purpose drift, export laundering, high-consequence shortcuts, receiver-gap hiding, projection leaks, dropped fences, and request-window inversion.

## New in rev0093

- **governance receiver-convergence receipt v0** — non-authority convergence receipt downstream of signal-notification reconciliation.
- **receiver-set and overlap digests** — binds receiver identity classes, status-channel ids, status-channel cuts, affected-consumer overlap, and source reconciliation bytes.
- **mixed receiver states** — all-converged, partial-lag, divergent-cut, duplicate-suppressed, and fork-quarantined states stay visible instead of becoming one global green badge.
- **registry-integrity audit/refactor** — the checker registry now checks itself for revision parity, registered checker scripts, fixture-family coverage, and positive/negative fixture presence.
- **receiver-convergence checker** — validates five positive fixtures and twenty negative fixtures covering digest drift, count inflation, divergent-cut laundering, partial-complete laundering, quorum-as-authority, status-pointer mutation, public leaks, dropped fences, duplicate promotion, and fork winner injection.

## New in rev0092

- **governance signal-notification reconciliation receipt v0** — non-authority reconciliation receipt downstream of signal-notification fanout.
- **consumer refresh proof binding** — each refreshed consumer must carry a checked recertification receipt whose release, recipient, purpose, projection, and cache-subject digest match the source notification basis.
- **mixed reconciliation states** — partial refresh, dead-letter quarantine, duplicate suppression, and conflict holds stay visible instead of collapsing into a green fanout badge.
- **checker-suite audit/refactor** — `governance_common.py` and `governance_checker_registry.json` make the growing validator suite auditable as data.
- **reconciliation checker** — validates five positive fixtures and twenty negative fixtures covering source digest drift, consumer-set drift, ack-as-refresh laundering, recertification mismatch, dead-letter/duplicate/conflict promotion, public leaks, missing labels, status-pointer mutation, and high-consequence effects.

## New in rev0091

- **governance signal-notification receipt v0** — non-authority fanout receipt downstream of signal ingestion.
- **affected-consumer set digest** — binds required downstream consumers before delivery, acknowledgment, retry, or dead-letter states are summarized.
- **acknowledgment limits** — delivery and consumer acknowledgments remain notification facts, not refresh, recertification, or authority.
- **stale-consumer closure** — pending and dead-lettered consumers quarantine the affected cache subject until consumer-local recertification or manual resolution exists.
- **signal-notification checker** — validates five positive fixtures and twenty negative fixtures covering digest drift, consumer-set drift, payload drift, sealed leakage, ack laundering, dead-letter-as-delivery, partial fanout laundering, conflict-winner selection, identity leakage, high-consequence effects, status-pointer mutation, and notification-as-recertification.

## New in rev0090

- **governance signal-ingestion receipt v0** — non-authority receiver-observation receipt downstream of recertification.
- **event-key and subject binding** — binds stream, source/id, subject digest, cache-subject digest, envelope digest, delivery channel, and source recertification digest.
- **race guards** — distinguishes accepted basis-changing signals, duplicate signals, stale watermarks, conflicting signals, irrelevant signals, and rejected invalid signals.
- **follow-up binding** — accepted signals require recertification before reuse; conflicting signals hold without a winner; duplicates/stale signals do not change cache state.
- **signal-ingestion checker** — validates five positive fixtures and eighteen negative fixtures covering digest drift, sender/channel failure, duplicate-as-new-change, stale-as-current, conflict auto-resolution, public leakage, missing labels, dropped fences, and push-ack/poll-order laundering.

## New in rev0089

- **governance recertification receipt v0** — non-authority cache-currentness receipt downstream of dispute resolution.
- **cache-subject digest** — binds cached resolution, release, recipient, purpose, source item, and projection policy so stale cache keys cannot drift silently.
- **status and refresh recheck** — checks status channel, recipient-refresh channel, projection policy, owner-map epoch, successor state, branch state, follow-up signals, and clock window.
- **cache invalidation states** — distinguishes current-refresh-required, invalidated stale, quarantine sustained, historical-only, and recheck-required states.
- **recertification checker** — validates five positive fixtures and nineteen negative fixtures covering digest drift, missed signals, projection drift, cache-as-authority, public leakage, purpose drift, notification gaps, stale-cache reuse, and high-consequence effects.

## New in rev0088

- **governance dispute-resolution receipt v0** — non-authority recovery/hold receipt downstream of chain integrity.
- **source-chain immutability** — resolution checks the source chain-integrity receipt bytes and source-chain digest instead of editing prior history.
- **branch-set binding** — observed branches are digested and every branch receives a selected, rejected, quarantined, pending, or historical-only disposition.
- **recovered-head humility** — a recovered current status pointer still requires refresh and source-packet replay before any consequence.
- **projection-safe closure** — public dispute closure can disclose state class without leaking sealed branch evidence, private stewards, reviewer identities, conflicts, org maps, partner fragments, or exact hidden branch counts.
- **dispute-resolution checker** — validates four positive fixtures and seventeen negative fixtures covering digest drift, already-canonical sources, branch mismatch, losing-branch reuse, leakage, notice gaps, high-consequence effects, purpose drift, old-channel reuse, source mutation, and quarantine/current-head collapse.

## New in rev0087

- **governance chain-integrity receipt v0** — non-authority lineage receipt over ordered release, follow-up, and succession/transfer members.
- **deterministic chain digest** — binds ordered member ids and byte digests so member swaps or missing receipts cannot masquerade as the same status chain.
- **canonical head / fork hold split** — current status heads remain recheck pointers only; forked chains publish no current head and hold reuse.
- **branch-minimized projection** — public views can disclose bucketed fork state without leaking private steward, reviewer, conflict, or partner evidence.
- **chain-integrity checker** — validates four positive fixtures and fourteen negative fixtures covering digest mismatch, missing chain digest, unchecked members, source-release mismatch, purpose drift, fork-as-canonical collapse, public leakage, missing labels, high-consequence effects, dropped fences, wrong head, old-channel reuse, branch reuse, and nonmonotonic lineage.

## New in rev0086

- **governance succession/transfer receipt v0** — non-authority lifecycle receipt over one source evidence-release receipt and optional latest release follow-up.
- **predecessor closure** — predecessor/contact/status channel must be notified, ended, and marked as having no continuing authority.
- **successor binding** — successor acceptance, pending, refusal, held-recheck, or dual-control-pending state is recorded without becoming approval or delegation.
- **status-channel rotation** — old status URLs can be invalidated and new status pointers published without mutating release/follow-up history.
- **succession-transfer checker** — validates four positive fixtures and fourteen negative fixtures covering missing acceptance, old-channel reuse, scope expansion, successor-as-authority, digest drift, pending reuse, public steward leaks, dropped fences, high-consequence transfer effects, and missing no-authority labels.

## New in rev0085

- **governance evidence-release follow-up receipt v0** — non-authority lifecycle receipt over one prior evidence-release receipt.
- **recipient acknowledgment closure** — acknowledgment proves receipt only; it cannot become approval, stewardship acceptance, or authority.
- **revocation/correction/quarantine status pointers** — expired, corrected, superseded, or misused bundles carry stale labels and status pointers without mutating the original release.
- **reuse refusal** — held-recheck notices and stale bundles are refused when downstream actors try to reuse them without refresh.
- **release-followup checker** — validates five positive fixtures and fourteen negative fixtures covering digest drift, state mismatch, notice gaps, public leaks, expired-current laundering, missing status pointers, dropped fences, high-consequence follow-up, channel mismatch, mutation, and reuse-without-refresh.

## New in rev0084

- **governance evidence-release receipt v0** — non-authority wrapper for exported governance evidence, restricted review bundles, audit snapshots, and held-recheck notices.
- **recipient/purpose binding** — each release names recipient class, purpose, retention horizon, refresh/revocation channel, and no-authority watermark.
- **source/selection digest parity** — release receipts bind back to one batch/search or search-continuity receipt plus selection digest, query digest, and projection-policy digest.
- **field and omission guards** — public releases require sensitive field denial, sealed evidence redaction, and safe omission disclosure instead of exact hidden counts.
- **evidence-release checker** — validates four positive fixtures and sixteen negative fixtures covering digest drift, public sealed leaks, weak-state upgrades, dropped fences, raw partner fragments, expired release, and high-consequence action during release.

## New in rev0083

- **governance search-continuity receipt v0** — non-authority wrapper over paginated or long-running governance search.
- **cursor drift guard** — compares query digest, request fingerprint, projection-policy digest, owner-map epoch, packet-compaction watermark, and prior page digest before allowing same-snapshot continuation.
- **sealed omission closure** — permits none, presence-only, bucketed range, or DP/noisy count with privacy budget; rejects exact public sealed counts and sensitive omission details.
- **search-continuity checker** — validates batch/search page digests, drift response states, sealed-omission disclosure, completeness, and no high-consequence continuation effects.
- **five positive and twelve negative fixtures** — cover safe page two, held projection-policy drift, public bucketed omissions, restricted exact review, compaction recheckpoint, and tempting pagination/oracle failures.

## New in rev0082

- **governance batch/search receipt v0** — aggregate/search wrapper over consumer receipts, marked `batch_search_receipt_only`.
- **mixed-state guard** — preserves member state and replay-status counts so route-only, consequence-grade, restricted, and historical-only receipts cannot collapse into one green badge.
- **projection join closure** — keeps member projection classes visible, redacts sealed/restricted rows in broader views, and discloses projection/replay omissions.
- **batch/search checker** — validates member digests, mirrors, forbidden-effect unions, cursor/query binding, no raw authority counts, and no aggregate high-consequence effects.
- **four positive and twelve negative fixtures** — cover internal mixed search, public owner routing, current batch summaries, restricted break-glass/history mixes, and attractive aggregation failures.

## New in rev0081

- **governance decision consumer receipt v0** — downstream record for one consumer's handling of one decision event, marked `consumer_receipt_only`.
- **replay diff and compaction guard** — records whether event/packet replay stayed current, downgraded to history, or was held because compacted streams/tombstone retention made currentness unsafe.
- **consumer checker** — validates event digest parity, packet-ref mirroring, state non-upgrade, forbidden-effect preservation, projection safety, no-authority labels, and compacted-stream safeguards.
- **five positive and ten negative fixtures** — Helm, Harbor, Schell, SlopOS, and historical-downgrade paths plus failures for digest drift, weak-state export, dropped fences, unsafe compaction, packetless action, public leakage, state upgrade, replay-diff mismatch, and missing no-authority labels.

## New in rev0080

- **governance decision event v0** — compact derived receipt for one evaluated packet action, bound to packet id plus SHA-256 digest and marked `derived_receipt_only`.
- **decision-event parity checker** — validates packet digest, action posture parity, proof summary, projection safety, break-glass expiry/review debt, forbidden effects, and consumer-profile closure.
- **four consumer fixtures** — Helm owner-hint rendering, Schell minimized break-glass receipt, Harbor recompute recheck, and SlopOS CH-AREF attachment.
- **eight negative fixtures** — reject missing/mismatched packet digests, routing-to-export promotion, public sealed-evidence leaks, held-action inflation, expired break-glass replay, event-as-grant, and missing forbidden-effect fences.

## New in rev0079

- **routing-hint closure** — owner/catalog/dashboard labels may support only read-only routing actions when the packet proves non-sensitive evidence, safe projection, and explicit forbidden promotions.
- **break-glass closure** — emergency sealed review must carry trigger, scope, expiry, allowed interim actions, rollback plan, post-hoc review deadline, and review debt before it can support even temporary access.
- **projection closure** — public/external views are checked so sealed conflicts, raw partner fragments, reviewer identities, private org maps, and incident details cannot leak through governance evidence.
- **fixture expansion** — governance handoff check now covers three positive fixtures and fourteen negative fixtures, including routing-hint promotion, sensitive routing evidence, missing break-glass expiry, and public projection leaks.

## New in rev0078

- **governance handoff packet v0** — compact schema-shaped packet that compiles stewardship charter, delegation warrant, escalation handoff, currentness, conflict, budget, privacy/projection, agent boundary, and proof-obligation results for one requested governance consequence.
- **governance proof obligations** — PO-GOV-001 through PO-GOV-011: subject binding, duties/exclusions, currentness, delegator authority, caveats, escalation acceptance, conflict/quorum, agent boundary, break-glass, rehydration, and projection/minimization.
- **decay fixtures and checker** — one positive provider-risk quarantine fixture plus ten negative fixtures wired into `make check`, rejecting owner-label laundering, expired delegation, handoff non-acceptance, agent-boundary collapse, stale owner maps, privacy break-glass without review debt, and forbidden re-delegation.
- **residue spine and seam map** — explicit can-support/must-not-imply edges plus cross-cube boundaries with SlopOS, Steward, Helm, Harbor, Foundry, Schell, and ViewFS.

## New in rev0077

- **stewardship charter** — compact scoped accountability and maintenance posture for a cube subject, naming accountable parties, role types, permitted duties, excluded powers, effective cut, review cadence, conflict posture, successor/backstop lane, and evidence pointers.
- **delegation warrant** — compact evidence that a human, team, system, agent, reviewer, or temporary lane may perform a named task under bounded scope, time, capability, caveats, budget/payer, privacy/projection, re-delegation, revocation, and audit conditions.
- **escalation handoff** — compact routing/acceptance residue for issues that exceed a local steward or delegate, naming trigger, severity, from/to lanes, supplied/withheld evidence, requested/granted/denied authority, interim effect, deadline, notices, and closure state.

## New in rev0076

- **contest packet** — compact challenge wrapper for a bounded answer-adjacent subject: answer capsule, cell, cohort, export, action warrant, consequence receipt, learning label, model summary, scenario output, or verification bundle, including challenger/standing posture, grounds, requested remedy, submitted/missing evidence, admissibility/refusal posture, privacy/projection limits, and interim effect.
- **adjudication docket** — compact review-process residue for a contest packet, naming reviewer lane, independence/expertise/conflict posture, procedure/rules snapshot, evidence admitted/excluded, replay/check posture, interim holds, outcome, rationale, unresolved questions, and appeal-next posture.
- **remedy receipt** — compact downstream-effect record for uphold, correct, amend, attach-disagreement, withdraw, suppress, re-render, re-export, notify, rollback, fence, learn-exclude, or refuse-remedy outcomes, including derivative reach, residual gaps, non-erasure limits, and currentness impact.

## New in rev0075

- **custody trail** — compact chronological handling residue for answer-adjacent evidence, naming holders, transfers, purposes, access/projection class, fixity checks, transformations, redactions, and gaps without claiming current answer truth.
- **retention charter** — compact lifecycle posture naming why material is retained, for whom, for how long, at what detail/projection level, under which hold/erasure/privacy/audit pressures, and with which review gates.
- **disposition receipt** — compact record for deletion, expiry, redaction, transfer, sealing, hold-extension, digest-only reduction, cryptographic-erasure/sanitization claim, or refused disposal, including residual material and non-amnesia limits.

## New in rev0074

- **verification bundle** — compact, possibly redacted packet of answer-adjacent evidence for review, challenge, audit, dispute, rehydration, or replay; it references capsules, cuts, contracts, receipts, validation material, privacy/projection fences, and known gaps without becoming live authority.
- **replay recipe** — compact recipe for rerunning, recomputing, or checking an answer under a named replay class: byte-identical, value-identical, tolerance-identical, verdict-identical, explanation-identical, redacted-check-only, or not-replayable.
- **attestation envelope** — signed, logged, endorsed, witnessed, or digest-bound claim wrapper around a bundle, recipe, answer, run, export, or verification result; it records issuer, subject, predicate/profile, proof/log posture, expiry/revocation, and non-authority limits.

## New in rev0073

- **intent binding** — compact residue tying natural-language or agent-origin requests to explicit cube meaning: actor/lane, original wording or digest, follow-up context, ambiguity/disambiguation, selected metrics/axes/grain/window/scope/consequence class, denied alternatives, and safe-language/refusal posture.
- **translation warrant** — compact evidence that generated cube query, semantic-layer request, SQL, tool plan, or answer-shape contract is covered, checked, bounded, and reviewable against metric cards, query contracts, scope lenses, projection curtains, invariants, and refusal/degradation rules.
- **tool-call leash** — compact execution boundary for model-invoked or agent-suggested tools, including exposed capability subset, roots/sources/view boundaries, effect class, validated arguments, budgets, approval, dry-run/retry posture, execution receipt, result caps, and non-authority posture.

## New in rev0072

- **scenario capsule** — compact residue for one forecast, simulation, stress test, synthetic augmentation, imputation, what-if, sensitivity, or counterfactual answer, including source cuts, scenario class, assumptions, intervention vector, horizon, model/simulator/generator posture, seed/nondeterminism evidence, diagnostics, uncertainty, allowed use, and non-observed status.
- **counterfactual warrant** — compact evidence that a “would have happened if” claim is identified, partly identified, simulated-only, not identified, or refused, including treatment, outcome, population, assumptions, estimand, refutation/sensitivity posture, feedback taint, holdout evidence, and action limits.
- **synthetic boundary** — compact boundary around generated, imputed, simulated, forecasted, sampled, cloned, stress-test, or synthetic rows/cells/features/exemplars, including generation method, diagnostics, privacy/quality posture, marking, allowed joins/rollups/training/export uses, and naturalization prohibition.

## New in rev0071

- **learning loop ledger** — compact residue for proposed or actual use of cube answers, consequences, outcomes, labels, features, rewards, or agent memory in learning/evaluation/policy tuning, including training/evaluation cuts, point-in-time feature posture, label maturity, drift/skew checks, promotion decision, and rollback/fence requirements.
- **holdout witness** — compact evidence that a population, cohort, reference path, or assignment remained clean enough to measure intervention-shaped effects, including randomization unit, intended/observed allocation, SRM/exposure diagnostics, spillover, guardrails, privacy, and contamination posture.
- **feedback taint fence** — compact boundary around outcomes, clicks, reviewer choices, labels, metrics, examples, exports, or summaries shaped by prior cube answers, recommendations, alerts, quarantines, rankings, or UI exposure, including allowed uses and decontamination requirements.

## New in rev0070

- **threshold witness** — compact trigger-condition evidence for an answer-derived alert, recommendation, or control-loop candidate, including comparator/baseline, duration, cadence, tolerance, stabilization, no-data/error/refusal posture, grouping/inhibition/silence/dedupe posture, and pending/firing/resolved/withheld state.
- **action warrant** — compact permission-to-use record saying which consequence class a cube answer may support and under which scope, policy, freshness, quality, semantic, privacy, uncertainty, budget, human-review, rate, rollback, and rehydration conditions.
- **consequence receipt** — compact after-the-fact residue for proposed, accepted, rejected, applied, no-op, duplicate-suppressed, inhibited, silenced, withdrawn, fenced, or errored consequences resulting from cube answers.

## New in rev0069

- **concept anchor** — compact semantic identity card for a groupable axis, member, code, term, status, bucket, or unit-like qualifier, with owner/definition/version/effective cut, label snapshots, status, selectable/abstract posture, and policy sensitivity kept separate from display text.
- **crosswalk warrant** — compact bridge evidence for renamed, split, merged, broader, narrower, related, partner-supplied, or unmapped concepts, including direction, grade, cardinality, loss notes, effective period, reviewer/evidence, and refusal/no-map posture.
- **hierarchy cut** — compact rollup/classification membership snapshot for one answer, comparison, render, or export, including closure, version/effective cut, abstract/selectable nodes, subtotal/all/unknown semantics, rollup law, and unmapped/excluded members.
