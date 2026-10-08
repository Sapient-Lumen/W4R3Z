# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `rev0106`
- Timestamp: `2026.03.18.07.09` (America/New_York)
- Codename: `previewhintboundaryharbor`



## What changed in this revision

This revision continues directly from `rev0105` and does six things:

1. Re-checks **Resilio Sync** again around the remaining field-boundary seam: current docs still say a clicked Sync link opens a landing page that shows basic folder info, may hand off into the app through a protocol rewrite, and keeps the parameters after `#` out of the request to the Resilio server, while the same share can still travel as link, QR, or copied text.
2. Adds a dedicated **offer preview-hint provenance and sealed-authority field partition spec** so the archive no longer stops at `how did this arrive?` or `are these carriers the same offer?`, but also answers `which fields were mere hints?`, `which stayed sealed until local parse?`, and `which later actions may rely on which fields?`
3. Tightens the **evaluation** so the non-clone case against Resilio gets sharper again: the product still has useful minimal-link and preview mechanics, but current docs still leave field-level authority boundaries too implicit once name/size hints, wrapper/protocol mechanics, and local parse all touch the same portable offer story.
4. Extends the **interface, daemon/API, and offer-artifact contract** with field-provenance rows, field-partition explanations, review plans, and field-partition receipts so clients can render `hint only`, `sealed until parse`, `authoritative after parse`, and `not enough yet` without folklore.
5. Adds an additional **canonical flow** showing the new distinction this revision wants: a landing-page preview can show just enough to orient the user while still keeping later claim/trust/budget reasoning gated on local parse and later review.
6. Refreshes the **workbench, pattern language, ADRs, roadmap, offer-artifact spec, open questions, status, and reading order** so future revisions keep **preview hints separate from sealed authority-bearing fields** wherever portable invitation mechanics, browser handoff, and later durable trust meet.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

The sharper reason after this revision is: Resilio still has strong mechanics, and some of them are worth copying in spirit — especially minimal link payloads, practical browser/app handoff, and the separation between landing-page request and `#` fragment. What AnonSync should not copy is a surface where human-facing preview hints, delivery-wrapper mechanics, and sealed authority-bearing fields still have to be reconstructed after the fact. The product should let the operator ask all of `what was merely previewed?`, `what stayed sealed until local parse?`, `which fields are authoritative now?`, `what later decisions may rely on them?`, and `what definitely may not be inferred from preview alone?` and get one explicit answer with field role, exposure posture, authority posture, and linked receipts.

We **should** continue to borrow and reinterpret several of its strongest product ideas:

## Archive map

- `docs/00-status.md` — scope, honesty notes, and revision deltas
- `docs/10-resilio-sync-evaluation.md` — updated evaluation of Resilio Sync and its implications
- `docs/20-product-direction.md` — narrowed product thesis and non-goals
- `docs/30-interface-spec.md` — CLI/operator interface specification
- `docs/31-daemon-api-spec.md` — local daemon API, events, auth, and compatibility contract
- `docs/32-interface-flows.md` — canonical operator workflows and expected UX semantics
- `docs/33-transport-runtime-spec.md` — bundled transport/runtime/session contract
- `docs/34-linux-filesystem-scope.md` — Linux-first filesystem support tiers and behavioral contract
- `docs/35-embedded-transport-lifecycle.md` — provenance, persistence, update, and shutdown contract for bundled Tor/I2P support
- `docs/36-route-exposure-known-host-and-lease-spec.md` — publication, dialing, peer-pinned direct paths, and temporary direct-route exceptions
- `docs/37-contact-link-approval-and-succession-spec.md` — contact memory, pending peers, bounded introductions, approval scope, and successor continuity
- `docs/38-operator-workbench-interface-spec.md` — workbench screens, review lanes, share/detail views, proof panels, and danger-zone rules
- `docs/39-interface-pattern-language.md` — cross-surface layout, action hierarchy, proof-drawer rules, batch-operation limits, and verb vocabulary
- `docs/65-exit-review-and-replacement-interface-spec.md` — fixed review-pane anatomy, exit/replacement entry points, and channel-parity rules for dangerous actions
- `docs/66-claim-and-adoption-intake-interface-spec.md` — fixed intake-pane anatomy for offers, incoming visibility, path choice, and authority review
- `docs/67-link-and-constellation-join-interface-spec.md` — fixed join-pane anatomy for identity continuity, member class/defaults, visibility blast radius, and authority review
- `docs/68-successor-cutover-and-rehome-interface-spec.md` — fixed cutover-pane anatomy for predecessor/candidate compare, continuity carry-forward, target root/runtime, rewrite scope, and residue review
- `docs/69-compromise-containment-and-trust-rotation-interface-spec.md` — fixed compromise-pane anatomy for incident trigger/scope, freeze/revoke/rotate actions, successor handling, and residue review
- `docs/70-dormant-peer-reentry-and-stale-state-review-spec.md` — fixed stale-return pane anatomy for dormancy, chronology confidence, re-entry authority, divergence/source reality, and receipt review
- `docs/71-destructive-replay-and-delete-wave-review-spec.md` — fixed destructive-replay pane anatomy for trigger scope, effect budget, preservation truth, source confidence, and pre-apply consent
- `docs/72-conflict-adjudication-and-path-collision-review-spec.md` — fixed conflict-review pane anatomy for semantic class, candidate posture, compatibility reality, loser handling, and adjudication receipts
- `docs/73-local-derivation-and-self-edge-review-spec.md` — fixed same-host-derivation pane anatomy for source/target truth, topology safety, authority+lifecycle coupling, target-tier semantics, and derivation receipts
- `docs/74-authority-mutation-and-grant-boundary-review-spec.md` — fixed authority-mutation pane anatomy for current authority, desired boundary delta, active subject fallout, substrate effects, and mutation receipts
- `docs/75-overlap-containment-and-graph-topology-review-spec.md` — fixed topology-review pane anatomy for graph subjects, containment/propagation shape, path/root-boundary effects, safe topology actions, and topology receipts
- `docs/76-writer-contention-and-quiescence-review-spec.md` — fixed contention-review pane anatomy for contested scope, writer/lock reality, notification/filesystem posture, quiesce actions, and contention receipts
- `docs/77-capacity-fit-and-scale-admission-review-spec.md` — fixed capacity-fit pane anatomy for subject role, local capacity/index cost, freshness posture, path blockers, admissible modes, and fit receipts
- `docs/78-bringup-and-control-entry-interface-spec.md` — fixed bring-up pane anatomy for host role, state/continuity choice, identity posture, control/network posture, blockers, and bring-up receipts
- `docs/79-browser-independent-control-integrity-and-auth-repair-spec.md` — server-declared control capability, browser/client integrity findings, bounded auth repair, and browser-independent recovery paths
- `docs/80-reviewed-mutation-credential-and-apply-gate-interface-spec.md` — fixed mutation-gate pane anatomy, short-lived mutation grants, authority binding, and explicit apply proof
- `docs/81-target-custody-and-exclusive-bind-review-spec.md` — fixed custody-review pane anatomy for discovered markers, current owner lineage, continuity-safe path claims, collision blocking, and custody receipts
- `docs/82-safety-critical-channel-parity-and-surface-capability-spec.md` — fixed channel-parity review anatomy for requested action, semantic parity, current-channel degradation, safe handoff, and durable handoff receipts
- `docs/83-execution-seat-and-runtime-profile-reachability-spec.md` — fixed execution-seat review anatomy for runtime-principal/service-seat switch, state continuity, reachable-target delta, notification/freshness downgrade, and seat-switch receipts
- `docs/84-subject-label-and-authority-identity-continuity-spec.md` — fixed naming/identity review anatomy for relabeling, alias preservation, same-person continuity claims, authority replacement fallout, and identity-label receipts
- `docs/85-share-annex-and-live-data-separation-spec.md` — fixed share-layout review anatomy for live namespace guarantees, annex placement, residue/history posture, cleanup classes, and layout receipts
- `docs/86-semantic-fallback-and-optimization-review-spec.md` — fixed semantic-optimization review anatomy for requested profile, guarantees at risk, detection/verification posture, degraded-target findings, and optimization receipts
- `docs/87-revocation-recall-and-retained-copy-attestation-spec.md` — fixed recall-review anatomy for requested boundary change, current byte/authority reality, retained-copy findings, recall posture, and recall receipts
- `docs/88-share-authority-epoch-and-stale-capability-rotation-spec.md` — fixed epoch-rotation review anatomy for requested boundary change, current epoch map, stale-capability fallout, derivative migration, convergence posture, and rotation receipts
- `docs/89-observer-readonly-local-write-and-serve-rights-spec.md` — fixed observer-rights review anatomy for requested posture, visibility reality, local-write behavior, onward serving, projection/class limits, and observer-rights receipts
- `docs/91-fetchability-and-full-copy-witness-spec.md` — fixed fetchability review anatomy for requested materialization intent, source-backing, full-copy witnesses, ghost/stale-announcement handling, and fetchability receipts
- `docs/92-file-availability-and-materialization-interface-spec.md` — concrete interface contract for answer strips, witness/fetchability chips, subtree tables, batch splitting, and receipt-backed materialization actions
- `docs/93-file-availability-action-matrix-and-surface-contract-spec.md` — per-row availability state tuple, action admissibility matrix, selection-bar rules, dense/mobile compression rules, and CLI parity for next-safe-action rendering
- `docs/94-availability-row-anatomy-and-review-pane-spec.md` — literal availability-row layout, review-trigger contract, inline-vs-reviewed action gate, dense/mobile card rules, and microcopy guidance for state/source/action adjacency
- `docs/95-announcement-inbox-and-local-claim-separation-spec.md` — pathless incoming-share visibility, local-claim states, local-hide versus wider-withdraw semantics, and inbox/review grammar for arrival truth
- `docs/96-approval-seat-and-constellation-scope-review-interface-spec.md` — approval-queue rows, acting-seat review grammar, one-share versus future-scope approval horizons, and receipt-backed blast-radius truth
- `docs/97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md` — prior-trust match rows, narrow auto-admit boundaries, fresh-claim guardrails, and remembered-approval tightening/revocation grammar
- `docs/98-share-local-presence-and-mode-decomposition-interface-spec.md` — decomposition of share announcement, claim, bind, byte posture, and future-arrival policy so one `mode` label never answers all of them
- `docs/99-arrival-placement-suggestion-and-collision-review-interface-spec.md` — suggested-path drafts, collision classes, reviewed bind choices, and placement receipts that keep recommendation distinct from commitment
- `docs/100-standing-arrival-template-and-default-root-review-interface-spec.md` — seat-scoped standing future-arrival templates with explicit effect buckets, pinned exceptions, and template-governance receipts
- `docs/101-effective-arrival-explanation-and-counterfactual-interface-spec.md` — one explanation surface for why a subject is in this stage on this seat now, including non-causes and counterfactuals
- `docs/102-policy-delta-preview-and-arrival-simulation-interface-spec.md` — standing-policy impact previews with effect buckets, named example subjects, explicit non-effects, and simulation-backed retroactivity receipts
- `docs/103-standing-policy-lineage-and-subject-attribution-interface-spec.md` — effective standing-policy version history, grandfathered-subject attribution, current-vs-applied compare surfaces, and lineage-backed explanation receipts
- `docs/104-subject-policy-drift-and-realignment-review-interface-spec.md` — drift-population views, per-subject realignment classes, reviewed refresh/keep/pin actions, and receipts proving intentional divergence
- `docs/105-exception-aging-renewal-and-rereview-interface-spec.md` — intentional-exception aging classes, review horizons, renewal/return-to-policy outcomes, and receipts proving that long-lived divergence remained deliberate
- `docs/106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md` — remembered-approval freshness classes, cooling reasons, touch-renewal/freeze outcomes, and receipts proving whether long-lived trust stayed live, narrowed, or stopped authorizing reuse
- `docs/107-approval-memory-lineage-and-authorization-trace-interface-spec.md` — approval-memory lineage nodes, origin-versus-current trust compare, per-subject authorization trace, and receipts proving which exact trust act authorized later convenience
- `docs/108-approval-memory-constellation-mutation-and-family-rebase-interface-spec.md` — trust-family split/rebase after certificate takeover, hidden-device return, or linked-device-set mutation, with descendant postures and receipts proving what still inherits remembered approval
- `docs/109-approval-memory-descendant-liveness-and-reachability-confidence-interface-spec.md` — descendant liveness classes, evidence basis, current-role honesty, and receipts proving which descendants are live, stale, hidden, reappeared, or historical only
- `docs/110-approval-memory-descendant-role-eligibility-and-capability-proof-interface-spec.md` — per-subject descendant capability rows, proof-basis classes, eligibility blockers, reviewed outcomes, and receipts proving who may honestly act as byte source, approval seat, both, or neither
- `docs/111-approval-memory-reuse-policy-and-subject-override-precedence-interface-spec.md` — subject-level reuse-policy rows, precedence outcomes, winning-rule explanations, reviewed override outcomes, and receipts proving when remembered approval may or may not be reused for one governed subject
- `docs/112-offer-artifact-expiry-and-trust-promotion-boundary-interface-spec.md` — offer-lifetime rows, trust-promotion postures, reviewed promotion outcomes, and receipts proving what durable remembered approval, if any, survived after a one-time or expiring invitation
- `docs/113-offer-recipient-intent-and-redeemer-identity-boundary-interface-spec.md` — sender-intent rows, redeemer-identity explanations, mismatch outcomes, and receipts proving who actually redeemed a portable offer and what trust, if any, was promoted afterward
- `docs/114-offer-redemption-ledger-and-multi-redeemer-trust-fanout-interface-spec.md` — artifact-budget rows, per-attempt ledger entries, trust-fanout review plans, and receipts proving which attempts consumed shared offer budget and what trust survived from each
- `docs/115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md` — equivalence rows, slot-accounting explanations, and receipts proving whether a later attempt collapses into an earlier slot, consumes a new slot, or should force reissue
- `docs/116-offer-reissue-lineage-and-successor-boundary-interface-spec.md` — fixed predecessor/successor review anatomy for reissue reasons, successor relation, budget reset posture, explicit carry-forward limits, and successor-boundary receipts
- `docs/117-offer-delivery-handoff-provenance-and-preview-authority-boundary-interface-spec.md` — fixed delivery-event review anatomy for received-via, preview hints, external-touch posture, browser/app handoff, authority boundary, and delivery-handoff receipts
- `docs/118-offer-carrier-alias-equivalence-and-canonical-artifact-identity-spec.md` — fixed carrier-alias review anatomy for canonical offer identity, wrapper/protocol/QR alias classes, equivalence posture, normalization basis, and carrier-alias receipts
- `docs/119-offer-preview-hint-provenance-and-sealed-authority-field-partition-spec.md` — fixed field-partition review anatomy for preview-visible hints, sealed authority-bearing fields, authoritative-after-parse facts, non-inference boundaries, and field-partition receipts
- `docs/120-offer-preview-sufficiency-and-omitted-governance-non-inference-spec.md` — fixed preview-sufficiency review anatomy for what a preview is sufficient for, which governance-bearing fields are omitted, which unsafe inferences are refused, and how omission-aware receipts keep recognition separate from governance truth
- `docs/40-architecture-decisions.md` — design decisions and tradeoffs
- `docs/41-report-and-intervention-language.md` — common report envelope, freshness/severity language, and safe operator intervention grammar
- `docs/42-state-root-and-service-profile-spec.md` — active root inspection, service-profile semantics, root transition plans, and audit/receipt rules
- `docs/43-mount-binding-repair-and-preservation-spec.md` — bound-path health, detach/repair semantics, preservation sets, and binding receipts
- `docs/44-file-intent-deviation-and-restore-spec.md` — file-action scope, deviation cases, restore rules, and file-intent receipts
- `docs/45-activity-phase-and-scheduling-spec.md` — runtime phase truth, recurring windows, and explicit transfer-control semantics
- `docs/46-namespace-projection-and-placeholder-spec.md` — share namespace visibility, mount-level omission/placeholder policy, and projection-effect receipts
- `docs/47-settlement-barrier-and-readiness-spec.md` — readiness policies, settlement barriers, and settlement receipts for high-signal actions
- `docs/48-history-conflict-and-rollback-provenance-spec.md` — timeline objects, restore candidates, conflict linkage, and rollback receipts
- `docs/49-filesystem-portability-and-semantic-fidelity-spec.md` — portability policy, fidelity contracts, drift cases, and fidelity receipts
- `docs/51-space-pressure-reclaim-and-retention-budget-spec.md` — space ledgers, budget policies, pressure cases, reclaim plans, and reclaim receipts
- `docs/52-capability-offer-and-claim-artifact-spec.md` — offer artifacts, delivery encodings, offer policy, and claim receipts
- `docs/53-transfer-policy-and-throughput-budget-spec.md` — transfer policy, throughput budgets, transfer explanations, and transfer-budget receipts
- `docs/54-attention-escalation-and-notification-parity-spec.md` — attention policy, attention events, escalation semantics, and attention receipts
- `docs/55-control-access-and-session-boundary-spec.md` — control-access policy, endpoint exposure, access tokens, control sessions, and access receipts
- `docs/56-recovery-material-and-continuity-bundle-spec.md` — recovery posture, custody classes, continuity claims, and recovery receipts
- `docs/57-release-channel-upgrade-and-compatibility-boundary-spec.md` — release posture, upgrade plans, compatibility boundaries, and release receipts
- `docs/58-policy-origin-defaults-and-precedence-spec.md` — defaults profiles, policy bindings, effective-policy explanations, and policy receipts
- `docs/59-diagnostic-evidence-and-support-bundle-spec.md` — diagnostic incidents, evidence bundles, redaction profiles, and evidence receipts
- `docs/60-override-lease-and-temporary-exception-spec.md` — shared lease lifecycle for temporary exceptions, expiry/exhaustion truth, and override receipts
- `docs/61-personal-constellation-and-authority-domain-spec.md` — constellation membership, member class, authority domains, and constellation receipts
- `docs/50-roadmap.md` — phased roadmap
- `docs/64-critical-open-questions.md` — short list of the biggest unresolved design questions
- `docs/sources.md` — source list used for this revision

## Reading order

Read `10-resilio-sync-evaluation.md` first, then `20-product-direction.md`, then `33-transport-runtime-spec.md`, then `35-embedded-transport-lifecycle.md`, then `36-route-exposure-known-host-and-lease-spec.md`, then `37-contact-link-approval-and-succession-spec.md`, then `30-interface-spec.md`, then `38-operator-workbench-interface-spec.md`, then `39-interface-pattern-language.md`, then `65-exit-review-and-replacement-interface-spec.md`, then `66-claim-and-adoption-intake-interface-spec.md`, then `67-link-and-constellation-join-interface-spec.md`, then `96-approval-seat-and-constellation-scope-review-interface-spec.md`, then `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md`, then `98-share-local-presence-and-mode-decomposition-interface-spec.md`, then `99-arrival-placement-suggestion-and-collision-review-interface-spec.md`, then `100-standing-arrival-template-and-default-root-review-interface-spec.md`, then `101-effective-arrival-explanation-and-counterfactual-interface-spec.md`, then `102-policy-delta-preview-and-arrival-simulation-interface-spec.md`, then `103-standing-policy-lineage-and-subject-attribution-interface-spec.md`, then `104-subject-policy-drift-and-realignment-review-interface-spec.md`, then `105-exception-aging-renewal-and-rereview-interface-spec.md`, then `106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md`, then `107-approval-memory-lineage-and-authorization-trace-interface-spec.md`, then `108-approval-memory-constellation-mutation-and-family-rebase-interface-spec.md`, then `109-approval-memory-descendant-liveness-and-reachability-confidence-interface-spec.md`, then `110-approval-memory-descendant-role-eligibility-and-capability-proof-interface-spec.md`, then `111-approval-memory-reuse-policy-and-subject-override-precedence-interface-spec.md`, then `112-offer-artifact-expiry-and-trust-promotion-boundary-interface-spec.md`, then `113-offer-recipient-intent-and-redeemer-identity-boundary-interface-spec.md`, then `114-offer-redemption-ledger-and-multi-redeemer-trust-fanout-interface-spec.md`, then `115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md`, then `116-offer-reissue-lineage-and-successor-boundary-interface-spec.md`, then `117-offer-delivery-handoff-provenance-and-preview-authority-boundary-interface-spec.md`, then `118-offer-carrier-alias-equivalence-and-canonical-artifact-identity-spec.md`, then `119-offer-preview-hint-provenance-and-sealed-authority-field-partition-spec.md`, then `120-offer-preview-sufficiency-and-omitted-governance-non-inference-spec.md`, then `68-successor-cutover-and-rehome-interface-spec.md`, then `69-compromise-containment-and-trust-rotation-interface-spec.md`, then `70-dormant-peer-reentry-and-stale-state-review-spec.md`, then `71-destructive-replay-and-delete-wave-review-spec.md`, then `72-conflict-adjudication-and-path-collision-review-spec.md`, then `73-local-derivation-and-self-edge-review-spec.md`, then `74-authority-mutation-and-grant-boundary-review-spec.md`, then `75-overlap-containment-and-graph-topology-review-spec.md`, then `76-writer-contention-and-quiescence-review-spec.md`, then `77-capacity-fit-and-scale-admission-review-spec.md`, then `78-bringup-and-control-entry-interface-spec.md`, then `79-browser-independent-control-integrity-and-auth-repair-spec.md`, then `80-reviewed-mutation-credential-and-apply-gate-interface-spec.md`, then `81-target-custody-and-exclusive-bind-review-spec.md`, then `82-safety-critical-channel-parity-and-surface-capability-spec.md`, then `83-execution-seat-and-runtime-profile-reachability-spec.md`, then `84-subject-label-and-authority-identity-continuity-spec.md`, then `85-share-annex-and-live-data-separation-spec.md`, then `86-semantic-fallback-and-optimization-review-spec.md`, then `87-revocation-recall-and-retained-copy-attestation-spec.md`, then `88-share-authority-epoch-and-stale-capability-rotation-spec.md`, then `89-observer-readonly-local-write-and-serve-rights-spec.md`, then `91-fetchability-and-full-copy-witness-spec.md`, then `92-file-availability-and-materialization-interface-spec.md`, then `93-file-availability-action-matrix-and-surface-contract-spec.md`, then `94-availability-row-anatomy-and-review-pane-spec.md`, then `95-announcement-inbox-and-local-claim-separation-spec.md`, then `41-report-and-intervention-language.md`, then `42-state-root-and-service-profile-spec.md`, then `43-mount-binding-repair-and-preservation-spec.md`, then `44-file-intent-deviation-and-restore-spec.md`, then `45-activity-phase-and-scheduling-spec.md`, then `46-namespace-projection-and-placeholder-spec.md`, then `47-settlement-barrier-and-readiness-spec.md`, then `48-history-conflict-and-rollback-provenance-spec.md`, then `49-filesystem-portability-and-semantic-fidelity-spec.md`, then `51-space-pressure-reclaim-and-retention-budget-spec.md`, then `52-capability-offer-and-claim-artifact-spec.md`, then `53-transfer-policy-and-throughput-budget-spec.md`, then `54-attention-escalation-and-notification-parity-spec.md`, then `55-control-access-and-session-boundary-spec.md`, then `56-recovery-material-and-continuity-bundle-spec.md`, then `57-release-channel-upgrade-and-compatibility-boundary-spec.md`, then `58-policy-origin-defaults-and-precedence-spec.md`, then `59-diagnostic-evidence-and-support-bundle-spec.md`, then `60-override-lease-and-temporary-exception-spec.md`, then `61-personal-constellation-and-authority-domain-spec.md`, then `31-daemon-api-spec.md`, then `34-linux-filesystem-scope.md`, then `32-interface-flows.md`, then `64-critical-open-questions.md`.



## Revision addendum — preview-hint provenance and sealed-authority field partition

This revision adds the next portable-offer governance layer:

- field-provenance-row, field-partition-explanation, field-partition-review-plan, and field-partition-receipt object model work so browser landing pages, QR-adjacent previews, copied text, and app-parsed artifacts no longer collapse into one vague `opened link` story
- UI and API work so `hint only`, `sealed until parse`, `authoritative after parse`, and `not enough yet` stay visibly distinct
- lineage work linking later claim, trust, and budget consequences back to the exact field classes they relied on instead of letting preview familiarity masquerade as authority


## Revision addendum — preview sufficiency must stay separate from field visibility

Portable offers can now keep field classes explicit without yet telling the operator whether the preview is enough for any real decision.
The interface contract must therefore preserve five adjacent truths wherever one portable offer is previewed before full local parse:

- `Preview showed`
- `Missing governance fields`
- `Enough for`
- `Not enough for`
- `Next honest action`

A serious interface must be able to say:

- the landing page gave enough to recognize the likely subject
- the same preview did **not** say what permission class, approval posture, expiry policy, or use-count budget governs the offer
- those omissions are named as omissions rather than hidden behind a calm-looking preview
- the next safe action is `Inspect locally`, not `Connect` or `Trust` on the strength of recognition alone

The operator must not need product lore, prior chats, or remembered defaults to backfill the governance story.
