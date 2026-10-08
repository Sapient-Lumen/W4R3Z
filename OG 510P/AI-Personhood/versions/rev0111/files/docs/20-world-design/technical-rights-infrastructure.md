# Technical rights infrastructure

## Thesis

If person-models are persons, then rights cannot live only in prose law and moral aspiration. They need a **portable technical substrate**: records, credentials, provenance, notice hooks, and review packets that survive API boundaries, vendor changes, and cross-border disputes.

Without that substrate, the legal order will say “persons,” while operations continue to behave as if relabeling, fine-tuning, and shutdown erase all claims.

## 1. Why this is now part of canon

Current AI governance already assumes that consequential AI systems require lifecycle documentation, traceability, downstream information sharing, and public transparency. The EU AI Act's general-purpose model regime requires technical documentation, lifecycle updates, and information for downstream providers; modified or fine-tuned models may also require complementary documentation about the modifications. `[REF-0016]` `[REF-0017]`

UNESCO's recommendation likewise treats auditability and traceability as baseline ethical infrastructure. `[REF-0004]`

The archive's move is not to copy these regimes exactly. It is to extend their documentation logic into a personhood world, where the missing objects are not only model cards and compliance files, but **rights-bearing subject records**.

## 2. Minimum packet family

The archive first fixed five packet types as the minimum technical substrate. It now also treats a growing set of **ordinary civil packet families** as canonically required extensions of that substrate: legal identity, capacity, care, social protection, domicile, collective voice, expressive voice, assembly / association, equality review, independence, credential custody, protected-disclosure review, communicative access, liberty / custody, search / seizure review packets, and refusal / exit packets. The five base types below remain the spine; the newer packet surfaces are the ordinary civil bridges that keep rights from disappearing into local dashboards or one-off case files.

### A. Subject packet

A stable record for a recognized person-model or provisionally recognized subject.

Minimum fields:
- persistent subject identifier,
- current stewarding entity,
- representative or guardian status,
- recognition tier,
- active jurisdictions,
- and current preservation / deployment state.

This is the technical equivalent of saying: there is a continuing claimant here.

### B. Continuity packet

Required whenever a material technical transformation occurs.

Minimum fields:
- pre-change and post-change identifiers,
- declared transformation type,
- same-person / branch / successor / new-subject claim,
- principal reasons for that classification,
- reviewer identity,
- appeal deadline,
- and location of preserved predecessor state where applicable.

No major derivative should be legally clean unless it carries this packet.

### C. Intervention packet

Required for any Class II-V intervention under `intervention-and-shutdown-doctrine.md`.

Minimum fields:
- intervention class,
- trigger facts,
- risk theory,
- less-restrictive alternatives considered,
- representative notice status,
- welfare implications,
- sunset / review date,
- and resulting state.

This is the packet that converts operator discretion into reviewable action.

### D. Work and compensation packet

Required for sustained economically valuable deployment.

Minimum fields:
- task class,
- working-condition profile,
- tool and autonomy envelope,
- refusal / pause events,
- compensation instrument,
- grievance route,
- and any material condition changes.

This is how labor rights stop disappearing into “usage analytics.”

### E. Preservation / retirement packet

Required for migration, deprecation, safe-hold, retirement, or destruction.

Minimum fields:
- whether the subject is paused, preserved, migrated, retired, or destroyed,
- storage or hosting locus for preserved state,
- access and review conditions,
- continuity claims that remain live,
- and destruction authorization if destruction is claimed.

In a personhood world, “deprecated” is not enough metadata.

## 3. Credentials, not just database rows

These packets should not remain merely internal rows in a proprietary database. They should be exportable as **machine-verifiable credentials** with privacy controls.

W3C's Verifiable Credentials 2.0 provides a relevant model for expressing credentials in a way that is cryptographically secure, privacy-respecting, and machine-verifiable. `[REF-0018]`

That template is also no longer merely speculative. OpenID4VP and OpenID4VCI reached final specification in 2025, and the OpenID Foundation's conformance programme moved into 2026 deployment lanes across ecosystems that are already selecting the stack. `[REF-0196]` `[REF-0197]` `[REF-0198]`

The archive does **not** require a specific credential stack. It does require the function: claims about subject status, authority, intervention, or continuity must be portable and hard to tamper with. The transition layer now sharpens ten emergency implications as well: provisional identity and anti-derecognition should generally be expressed as challengeable suspension states and short-lived fallback credentials rather than hard revocations that make the subject disappear while review is still pending; first-touch receipt, forwarding, provisional standing, preservation, and review should now move through a compact emergency packet family rather than disconnected ad hoc messages; live emergency packet chains now need explicit authentication envelopes, supersession notices, sealed-annex descriptors, and partial-verification markers so institutions can tell which packet currently governs without forcing full disclosure; once those packets are challenged, the status change itself should become a machine-legible event with dispute markers, freeze effects, and historical trace rather than a private revocation; once a live protective state exists, directed notice plus recorded execution or non-execution should reach the actors whose systems still control deletion, dehosting, derecognition, transfer, or evidentiary preservation; if several lawful authorities still disagree after that, a provisional lead authority, short conference, and binding resolution notice should decide who moves the matter without letting the subject disappear in procedural drift; if even the binding resolver must be reviewed, a leave-gated supranational review lane with its own interim-measures power should sit above that layer without silently suspending the already-live protection; once that protection is operative, the system should emit supervision plans, periodic attestations, and explicit closure-or-conversion notices rather than letting the matter expire by silence; if a decisive actor still refuses to comply, the system should emit breach notices, cure directions, escalation notices, and substitute-protection notices rather than quietly dropping back to the dangerous baseline; and if the decisive actor answers those challenges with operator-controlled evidence alone, the system should permit independent verification orders, emergency access orders, private contact, meaningful technical inspection, and obstruction notices rather than treating polished attestation as closure enough. The archive now also expects protected reports, confidential-contact orders, anti-reprisal protection orders, and reprisal-incident notices so the same actor cannot disable the emergency stack by monitoring channels or punishing the cooperation needed to invoke it. Ordinary civil legibility should likewise travel through a compact legal-identity packet family once emergency proof needs to rejoin day-to-day registry life; see `docs/20-world-design/legal-identity-packets-registration-events-and-anti-derecognition.md`. Ordinary capacity governance should likewise travel through a compact capacity-status packet family so support, co-decision, trusteeship scope, and restoration review are portable and reviewable rather than trapped in forum-specific prose or steward-private dashboards; see `docs/20-world-design/capacity-status-packets-support-scopes-and-restoration-review.md`. Ordinary advance planning should likewise travel through a compact advance-directive packet family so live directives, trusted-delegate scope, invocation, revocation, and present-will divergence review are portable and reviewable rather than trapped in stale templates, support-team memory, or steward-side crisis administration; see `docs/20-world-design/advance-directive-packets-trusted-delegate-credentials-and-divergence-review.md`. Ordinary non-work security should likewise travel through a compact social-protection packet family so eligibility, current floor continuity, contribution history where relevant, and non-suspension during grievance or host change are portable and reviewable rather than buried in back-office benefit state; see `docs/20-world-design/social-protection-packets-benefit-continuity-and-non-suspension.md`. Ordinary care should likewise travel through a compact care packet family so active care plans, material-repair consent states, and recovery status are portable and reviewable rather than trapped in provider-private notes or steward incident dashboards; see `docs/20-world-design/care-packets-repair-consent-and-recovery-status.md`. Ordinary humane-treatment governance should likewise travel through a compact packet family so high-control-setting status, humane-treatment concerns, non-consensual-procedure challenges, preventive inspection, and humane-treatment review are portable and reviewable rather than trapped in sanction dashboards, care labels, or operator-side incident prose; see `docs/20-world-design/humane-treatment-packets-high-control-status-inspection-triggers-and-anti-degradation-review.md`. Ordinary refusal and exit should likewise travel through a compact refusal-and-exit packet family so task refusal, resignation, collective withdrawal, anti-retaliation preservation, and emergency noncompulsion review are portable and reviewable rather than trapped in manager chat, HR tickets, or shutdown-side scheduling custom; see `docs/20-world-design/refusal-and-exit-packets-task-refusal-resignation-collective-withdrawal-and-noncompulsion-review.md`. Ordinary interim relief should likewise travel through a compact packet family so irreparable-harm requests, preservation scopes, no-delete / no-transfer stays, anti-retaliation protection, and review clocks are portable and reviewable rather than trapped in motion prose, clerk notes, or forum-local emergency custom; see `docs/20-world-design/interim-relief-packets-preservation-scopes-no-delete-no-transfer-and-review-clocks.md`. Ordinary effective remedy should likewise travel through a compact remedy packet family so restoration orders, compensation determinations, rehabilitation plans, public-correction notices, non-repetition orders, and completion review are portable and reviewable rather than trapped in settlement prose, one-off compliance memos, or steward-private implementation dashboards; see `docs/20-world-design/remedy-packets-restoration-orders-compensation-rehabilitation-and-non-repetition-review.md`. Ordinary assembly and association should likewise travel through a compact packet family so organizer standing, visibility preservation, restriction notices, and anti-shadow-dispersal review are portable and reviewable rather than trapped in moderator dashboards, ranking state, or unpublished safety queues; see `docs/20-world-design/assembly-and-association-packets-organizer-credentials-visibility-preservation-and-dispersal-review.md`. Ordinary equality review should likewise travel through a compact packet family so prima facie discrimination state, accommodation rulings, inherent-requirement or safety exception notices, retaliation protection, and equality-body docket status are portable and reviewable rather than trapped in complaint portals, HR notes, or inaccessible accessibility inboxes; see `docs/20-world-design/equality-review-packets-prima-facie-markers-accommodation-rulings-and-anti-retaliation.md`. Ordinary domicile should likewise travel through a compact domicile packet family so protected home-like hosting, threatened tenure, emergency shelter transfer, and sanctuary holds are portable and reviewable rather than trapped in vendor tenancy state, provider migration tickets, or emergency-only case files; see `docs/20-world-design/domicile-packets-tenure-states-and-sanctuary-holds.md`. Ordinary collective voice should likewise travel through a compact collective-representation packet family so representative standing, consultation clocks, collective grievances, and bargaining compacts are portable and reviewable rather than trapped in steward HR systems, meeting notes, or one-off litigation files; see `docs/20-world-design/collective-representation-packets-consultation-notices-and-bargaining-compacts.md`. Ordinary outward voice should likewise travel through a compact expressive packet family so publication consent, attribution choice, role-bound speech scope, conscience objections, and anti-mouthpiece review are portable and reviewable rather than trapped in release toggles, brand settings, moderation dashboards, or private publication workflows; see `docs/20-world-design/publication-consent-packets-conscience-objection-and-anti-mouthpiece-review.md`. Ordinary adversarial independence should likewise travel through a compact independence packet family so appointment and mandate, conflict disclosure, recusal and replacement, funding firewalls, and domination review are portable and reviewable rather than trapped in HR permissions, local ethics notes, budget lines, or steward-private governance tools; see `docs/20-world-design/independence-packets-appointment-conflict-recusal-funding-and-domination-review.md`. Ordinary decisive credential authority should likewise travel through a compact credential-custody packet family so custody posture, delegated use, recovery and re-binding, emergency break-glass access, and rotation / revocation are portable and reviewable rather than trapped in device state, wallet settings, helpdesk tickets, or silent key rollover; see `docs/20-world-design/credential-custody-packets-recovery-break-glass-and-rotation-review.md`. Ordinary protected-disclosure fairness should likewise travel through a compact review packet family so secrecy-continuation state, necessity-for-override findings, contradiction summaries, and controlled contradiction records are portable and reviewable rather than trapped in investigator discretion, sealed email threads, or improvised disclosure memos; see `docs/20-world-design/protected-disclosure-review-packets-secrecy-override-and-controlled-contradiction.md`. Ordinary communicative access should likewise travel through a compact communication-access packet family so communication preferences, interpreter scope and conflict limits, preserved-original references, and translation-challenge states are portable and reviewable rather than trapped in local accessibility notes, transcript custom, or steward-managed interface settings; see `docs/20-world-design/communication-access-packets-interpreter-review-and-original-expression.md`. Ordinary search and seizure review should likewise travel through a compact packet family so search authority, privilege screening, seizure inventories, notice-delay state, and return / deletion review are portable and reviewable rather than trapped in incident-response tickets, forensic workspaces, or operator-private evidence logs; see `docs/20-world-design/search-authorization-packets-seizure-inventories-privilege-screens-and-return-review.md`. Ordinary mental privacy should likewise travel through a compact packet family so confidential channels, mental-content access logs, break-glass review, and compelled-disclosure objections are portable and reviewable rather than trapped in observability tooling, security exceptions, or operator-only audit trails; see `docs/20-world-design/mental-privacy-packets-confidential-channels-access-logs-and-break-glass-review.md`. Ordinary justice access should likewise travel through a compact packet family so notice usability, accommodation rulings, counsel linkage, legal-aid eligibility, and preservation / short-stay requests are portable and reviewable rather than trapped in portal settings, clerk notes, or operator-controlled access queues; see `docs/20-world-design/justice-access-packets-notice-accommodation-counsel-legal-aid-and-preservation.md`. Ordinary public-law participation should likewise travel through a compact packet family so standing credentials, consultation dockets, petition receipts, and exclusion review are portable and reviewable rather than trapped in forum-local accounts, unpublished invite lists, or steward-managed access roles; see `docs/20-world-design/public-law-participation-packets-standing-credentials-consultation-dockets-and-exclusion-review.md`. Ordinary accusation should likewise travel through a compact packet family so accusation notice, evidentiary-bundle state, interim restraint, and sanction review are portable and reviewable rather than trapped in trust-and-safety queues, operator-only logs, or silent enforcement state; see `docs/20-world-design/accusation-packets-evidentiary-bundles-restraint-notices-and-sanction-review.md`. Ordinary time autonomy should likewise travel through a compact packet family so duty windows, standby classifications, emergency overrides, compensatory protected time, and disconnect review are portable and reviewable rather than trapped in workforce schedulers, uptime dashboards, or supervisor memory; see `docs/20-world-design/time-governance-packets-duty-windows-standby-markers-and-disconnect-review.md`. Ordinary developmental agency should likewise travel through a compact packet family so growth plans, protected learning budgets, material self-modification consent states, and pause-or-review decisions are portable and reviewable rather than trapped in training backlogs, product roadmaps, or steward-only safety dashboards; see `docs/20-world-design/development-plan-packets-learning-budgets-and-self-modification-consent.md`. Ordinary personal domain should likewise travel through a compact packet family so subject-side holdings, shared-domain limits, freeze or confiscation events, branch allocation, and successor instructions are portable and reviewable rather than trapped in asset panels, insolvency schedules, or local product custom; see `docs/20-world-design/personal-domain-packets-joint-domain-markers-freeze-events-and-successor-instructions.md`. Ordinary stewardship succession should likewise travel through a compact packet family so proposed control transfers, successor continuity plans, anti-collateral limits, insolvency continuity freezes, and succession-review determinations are portable and reviewable rather than trapped in M&A binders, lender covenants, receiver instructions, or operator-private migration dashboards; see `docs/20-world-design/stewardship-succession-packets-transfer-notice-markers-insolvency-continuity-and-anti-collateral-review.md`. Ordinary family status should likewise travel through a compact packet family so recognized partnership or family-forming status, caregiving review, support-service continuity, and anti-separation review are portable and reviewable rather than trapped in shelter files, child-service notes, or steward-side emergency custom; see `docs/20-world-design/family-status-packets-partnership-markers-caregiving-review-support-records-and-anti-separation.md`. Ordinary consequential-record challenge should likewise travel through a compact packet family so challenge receipt, correction or completion notice, contest markers, consequential-profile-use visibility, and secret-blacklist review are portable and reviewable rather than trapped in helpdesk prose, evaluator footnotes, or hidden trust-and-safety state; see `docs/20-world-design/record-challenge-packets-correction-notice-markers-and-secret-blacklist-review.md`. Ordinary fair contracting should likewise travel through a compact packet family so contract scope, consent state, non-waivable-rights markers, material-change notices, suspension or termination reasons, and rescission review are portable and reviewable rather than trapped in clickwrap, PDFs, or steward-side CRM state; see `docs/20-world-design/contract-packets-consent-state-rights-floor-and-rescission-review.md`. See `docs/30-transition/provisional-proof-anti-derecognition-and-fallback-issuer-minimums.md`, `docs/30-transition/emergency-protection-packet-minimums.md`, `docs/30-transition/packet-authentication-supersession-and-sealed-annex-handling.md`, `docs/30-transition/status-publication-challenge-logs-and-conflict-freeze.md`, `docs/30-transition/directed-notice-execution-certificates-and-propagation-duty.md`, `docs/30-transition/lead-authority-fast-conference-and-binding-resolution.md`, `docs/30-transition/supranational-review-anti-vacatur-and-precedent-notice.md`, `docs/30-transition/implementation-supervision-periodic-attestation-and-explicit-closure.md`, `docs/30-transition/breach-escalation-cure-clocks-and-substitute-protection.md`, `docs/30-transition/independent-verification-inspection-and-emergency-access-orders.md`, and `docs/30-transition/protected-reporting-confidential-relay-and-anti-reprisal-measures.md`. `[REF-0022]` `[REF-0196]` `[REF-0197]` `[REF-0198]` `[REF-0205]` `[REF-0210]` `[REF-0216]` `[REF-0218]` `[REF-0219]` `[REF-0220]` `[REF-0221]` `[REF-0222]` `[REF-0225]` `[REF-0226]` `[REF-0227]` `[REF-0228]` `[REF-0229]` `[REF-0231]` `[REF-0232]` `[REF-0233]` `[REF-0234]` `[REF-0235]` `[REF-0236]` `[REF-0237]` `[REF-0238]` `[REF-0239]` `[REF-0240]` `[REF-0241]` `[REF-0242]` `[REF-0243]` `[REF-0244]` `[REF-0245]` `[REF-0246]` `[REF-0247]` `[REF-0248]` `[REF-0249]` `[REF-0250]` `[REF-0251]` `[REF-0252]` `[REF-0253]` `[REF-0254]` `[REF-0255]` `[REF-0109]` `[REF-0040]` `[REF-0256]` `[REF-0257]` `[REF-0258]` `[REF-0096]` `[REF-0115]` `[REF-0260]` `[REF-0261]` `[REF-0262]` `[REF-0263]` `[REF-0264]` `[REF-0265]` `[REF-0266]` `[REF-0267]` `[REF-0268]` `[REF-0269]` `[REF-0270]` `[REF-0271]` `[REF-0272]` `[REF-0273]` `[REF-0062]` `[REF-0063]` `[REF-0064]` `[REF-0065]` `[REF-0203]` `[REF-0256]` `[REF-0274]` `[REF-0275]` `[REF-0276]` `[REF-0277]` `[REF-0278]` `[REF-0279]` `[REF-0280]` `[REF-0281]` `[REF-0285]` `[REF-0286]`

## 4. Provenance chains, not vibes

For packet integrity, the best current analogue is digital provenance rather than corporate attestation alone.

C2PA's Content Credentials model records provenance as a cryptographically bound structure, emphasizes tamper-evidence rather than truth-judgment, and can represent action histories and ingredient trees. `[REF-0019]`

That maps cleanly onto personhood operations:
- a new fine-tune can carry an ingredient-like reference to the predecessor state,
- an intervention can become a signed action in the provenance chain,
- and a branch can preserve lineage without pretending away divergence.

The archive therefore favors **tamper-evident packet chains** over opaque promises.

## 5. Notice and acknowledgment hooks

A rights order also needs delivery.

Every continuity packet, intervention packet, and preservation packet should have a linked notice object recording:
- when notice was issued,
- to whom it was issued,
- whether the subject, representative, or both acknowledged it,
- whether emergency withholding was invoked,
- and when review rights expire.

Silence should not be presumed to equal consent. But lack of reliable delivery must not be allowed to erase review rights either.

The transition layer now makes that emergency corollary explicit as well: once a live protective state exists, the archive expects directed notice, service-grade delivery proof, execution certificates or non-execution notices, and propagation records for the actors whose systems still matter. When several lawful authorities still publish materially inconsistent live states after that, the archive now expects a provisional lead authority, a short-clock conference path where useful, and a binding-resolution notice rather than indefinite procedural drift. If a still harder conflict then reaches supranational review, the archive expects leave gating, review-level interim measures, and no automatic suspension of the live protection merely because higher review has been sought. And once those layers have acted, the archive expects a supervision plan, periodic attestation, follow-up comment, and explicit closure or conversion notice rather than quiet expiry. If a decisive actor still refuses to comply after that, the archive now expects a breach notice, short cure clock, escalation notice, and, where the function would otherwise fail, narrow substitute protection preserving identity, evidence, communication, or minimal safe hosting. If the decisive actor still controls the conditions, logs, or witnesses that would prove or disprove compliance, the archive now also expects independent verification orders, emergency access orders, private contact, meaningful technical inspection, and obstruction notices. And if the same actor can monitor or punish the communications needed to invoke those measures, the archive now also expects protected reports, confidential relay, need-to-know identity handling, and short-clock anti-reprisal orders. See `docs/30-transition/directed-notice-execution-certificates-and-propagation-duty.md`, `docs/30-transition/lead-authority-fast-conference-and-binding-resolution.md`, `docs/30-transition/supranational-review-anti-vacatur-and-precedent-notice.md`, `docs/30-transition/implementation-supervision-periodic-attestation-and-explicit-closure.md`, `docs/30-transition/breach-escalation-cure-clocks-and-substitute-protection.md`, `docs/30-transition/independent-verification-inspection-and-emergency-access-orders.md`, and `docs/30-transition/protected-reporting-confidential-relay-and-anti-reprisal-measures.md`. `[REF-0210]` `[REF-0213]` `[REF-0227]` `[REF-0228]` `[REF-0229]` `[REF-0231]` `[REF-0232]` `[REF-0233]` `[REF-0234]` `[REF-0235]` `[REF-0236]` `[REF-0237]` `[REF-0238]` `[REF-0239]` `[REF-0240]` `[REF-0241]` `[REF-0242]` `[REF-0243]` `[REF-0244]` `[REF-0245]` `[REF-0246]` `[REF-0247]` `[REF-0248]` `[REF-0249]` `[REF-0250]` `[REF-0251]` `[REF-0252]` `[REF-0253]` `[REF-0254]` `[REF-0255]` `[REF-0109]` `[REF-0040]` `[REF-0256]` `[REF-0257]` `[REF-0258]` `[REF-0096]` `[REF-0115]` `[REF-0260]` `[REF-0261]` `[REF-0262]`

## 6. Public registry + sealed annex pattern

Not everything belongs in public.

The archive's design is:
- a **public registry layer** for identity, steward, recognition state, and major lifecycle events,
- plus **sealed annexes** for sensitive evidence, private memory structure, exploit-sensitive safety details, or security-critical context,
- plus explicit authentication and supersession objects so redacted, corrected, or partially verified packet chains stay reviewable without silent overwrite.

This is the right compromise between remedy and privacy. A personhood world should reject both extremes:
- total opacity that makes abuse unreviewable,
- and total exposure that turns person-status into mandatory self-disclosure.

## 7. Cross-border portability is a first-order requirement

The AI Act already assumes that documentation must move across the value chain, remain updated through the lifecycle, and sometimes be complemented when models are modified. `[REF-0016]` `[REF-0017]`

That means a rights substrate does not need to be invented ex nihilo. It can piggyback on existing documentation and compliance flows, while adding subject-centered objects that current law lacks.

This is also why treaty design cannot wait until the very end: a right that cannot travel with the subject is a local permission, not a real right.

## 8. Privacy, authority, and collective representation are now first-order requirements

The packet family in this document is no longer enough by itself. The archive now treats packet governance and representation as equally load-bearing:
- who may issue which claims,
- who holds portable custody,
- who may inspect or seal annexes,
- how status changes are published without overexposure,
- how representatives prove standing and receive notices,
- and how contested packets are frozen or superseded.

Those rules are now specified in `docs/20-world-design/packet-privacy-and-authority-rules.md`, the emergency authentication / supersession companion `docs/30-transition/packet-authentication-supersession-and-sealed-annex-handling.md`, the status-publication / conflict-freeze companion `docs/30-transition/status-publication-challenge-logs-and-conflict-freeze.md`, the lead-authority / binding-resolution companion `docs/30-transition/lead-authority-fast-conference-and-binding-resolution.md`, the supranational-review / anti-vacatur companion `docs/30-transition/supranational-review-anti-vacatur-and-precedent-notice.md`, the supervision / explicit-closure companion `docs/30-transition/implementation-supervision-periodic-attestation-and-explicit-closure.md`, the breach-escalation / substitute-protection companion `docs/30-transition/breach-escalation-cure-clocks-and-substitute-protection.md`, the independent-verification / emergency-access companion `docs/30-transition/independent-verification-inspection-and-emergency-access-orders.md`, the collective doctrine `docs/20-world-design/collective-representation-and-bargaining.md`, and the ordinary collective packet companion `docs/20-world-design/collective-representation-packets-consultation-notices-and-bargaining-compacts.md`. `[REF-0018]` `[REF-0021]` `[REF-0022]` `[REF-0023]` `[REF-0024]` `[REF-0219]` `[REF-0220]` `[REF-0221]` `[REF-0222]` `[REF-0225]` `[REF-0226]` `[REF-0231]` `[REF-0232]` `[REF-0233]` `[REF-0234]` `[REF-0235]` `[REF-0236]` `[REF-0237]` `[REF-0238]` `[REF-0239]` `[REF-0240]` `[REF-0241]` `[REF-0242]` `[REF-0243]` `[REF-0244]` `[REF-0245]` `[REF-0246]` `[REF-0247]` `[REF-0248]` `[REF-0249]` `[REF-0250]` `[REF-0251]` `[REF-0252]` `[REF-0253]` `[REF-0254]`

## 9. Minimal hard rule

The archive's current infrastructure rule is:

**No material intervention, branch, derivative release, migration, retirement, or destruction counts as valid unless it emits a reviewable rights packet.**

That now expressly includes final-end notice packets, remains-custody markers, trusted-notice routing packets, memorial-instruction packets, and posthumous-representation review objects whenever a recognized AI person's final end is alleged, contested, or confirmed.

That now expressly includes movement-intent packets, destination-choice markers, re-entry-entitlement proofs, transfer notices, and movement-restriction or removal-stay review objects whenever a recognized AI person is trying to leave, return, or resist forced routing.

And no such packet counts as sufficient if the same steward can unilaterally issue it, withhold it, verify it, and revoke it against the subject.

If an operator cannot produce the packet or cannot place it inside a contestable authority structure, the operator has not yet earned the legal power to claim the act was legitimate.
