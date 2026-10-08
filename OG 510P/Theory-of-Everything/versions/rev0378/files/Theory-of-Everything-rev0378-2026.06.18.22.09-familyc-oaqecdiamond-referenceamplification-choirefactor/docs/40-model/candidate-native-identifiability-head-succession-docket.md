# Candidate-native identifiability head-succession docket

This document is the post-adoption succession surface for candidate-native identifiability custody under `OQ-0057`.
It does **not** add a ninth identifiability field, replace the route ledger, replace head adoption, certify a lane as closed, promote any lane, demote any lane, or turn revision order into evidence.
It answers the next operational question after the head-adoption docket:

> once a bounded head has been adopted, when may a later continuation replace it as the current `OQ-0057` head rather than remaining a scratch edit, metadata refresh, mirror-only drift, fork candidate, challenged successor, or rollback input?

Read this together with:
- `docs/40-model/candidate-native-identifiability-cashout-template.md`
- `docs/40-model/candidate-native-identifiability-route-ledger.md`
- `docs/40-model/candidate-native-identifiability-promotion-gate.md`
- `docs/40-model/candidate-native-identifiability-promotion-readiness-matrix.md`
- `docs/40-model/candidate-native-identifiability-evidence-intake-docket.md`
- `docs/40-model/candidate-native-identifiability-supersession-decay-docket.md`
- `docs/40-model/candidate-native-identifiability-dependency-propagation-docket.md`
- `docs/40-model/candidate-native-identifiability-conflict-adjudication-docket.md`
- `docs/40-model/candidate-native-identifiability-decision-trace-docket.md`
- `docs/40-model/candidate-native-identifiability-replay-rollback-docket.md`
- `docs/40-model/candidate-native-identifiability-challenge-response-docket.md`
- `docs/40-model/candidate-native-identifiability-challenge-closure-docket.md`
- `docs/40-model/candidate-native-identifiability-adversarial-control-battery.md`
- `docs/40-model/candidate-native-identifiability-calibration-anchor-docket.md`
- `docs/40-model/candidate-native-identifiability-residual-cap-ledger.md`
- `docs/40-model/candidate-native-identifiability-export-claim-docket.md`
- `docs/40-model/candidate-native-identifiability-reimport-firewall.md`
- `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md`
- `docs/40-model/candidate-native-identifiability-release-seal-docket.md`
- `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`
- `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`
- `docs/40-model/candidate-native-identifiability-head-branch-arbitration-docket.md`
- `docs/40-model/candidate-native-identifiability-head-retirement-vacancy-docket.md`
- `docs/40-model/current-head-control-router.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

Head adoption selects a verified bounded carrier as the current authority object.
That is necessary but not sufficient for successor authority.
A later release can be newer but carry only mirror changes; a local extracted tree can be cleaner but start from the wrong parent; a cherry-picked owner row can be scientifically interesting but lineage-unsafe; a packaging repair can validate the same head without becoming a new head; a challenge response can narrow one field without electing the whole bundle; and a generated restart mirror can say “current” while the owner rows still describe the prior adopted head.

The correct posture is:

**succession is a transition claim, not a freshness claim. A later candidate may replace the adopted bounded `OQ-0057` head only if it names the predecessor head, proves direct-descendant or explicitly rebased lineage, separates owner-row deltas from mirror-only changes, reruns the relevant evidence / lifecycle / control dockets for touched cells, preserves the most restrictive residual cap and no-closure wording, verifies package and mirror parity, closes or scopes route-bearing challenges, and records a rollback handle. If those conditions fail, the candidate remains a scratch continuation, metadata refresh, fork candidate, challenged successor, or rollback input; it cannot set current-head posture by timestamp, filename, regenerated index, or successful lint alone.**

Use this docket when:
- a new release, extracted root, copied continuation, returned bundle, or generated release surface is proposed as the successor to the current adopted `OQ-0057` head;
- the archive needs to distinguish a real owner-row delta from a metadata, README, START_HERE, receipt, context, changelog, or generated-index refresh;
- multiple candidate successors descend from the same adopted head;
- a direct descendant includes scientific owner changes, release-custody changes, challenge closures, cap repairs, or mirror-only drift;
- a local edit was made after package verification and must be classified before packaging;
- a rollback, challenge freeze, quarantine, or lineage rebase changes which successor may continue the head;
- a future handoff says “next version” or “new head” and must not equate nextness with authority.

Do not use this docket to decide whether a new scientific result improves an identifiability field.
That remains the job of evidence intake, field protocols, adversarial controls, calibration, residual caps, and the promotion gate.
This docket decides whether a post-adoption continuation may become the next bounded authority carrier for already-scored `OQ-0057` posture.

## Head-succession states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, reimport states, lineage-merge states, release-seal states, seal-verification states, or head-adoption states.
They say whether a candidate continuation may replace an adopted bounded head.

| Code | Head-succession state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `HS0` | no succession claim | No adopted head is being replaced. | Leave this docket unused. | Auditing ordinary local reading as a head transition. |
| `HS1` | scratch continuation | A local edit, analysis copy, extracted tree, or working branch exists but is not proposed as successor head. | Mark scratch or navigation-only; do not update head mirrors. | Treating every edited tree as the next head. |
| `HS2` | metadata / mirror refresh only | The bundle changes receipt, manifest, README, START_HERE, context, changelog, generated index, or package cleanup without owner-row delta. | Rebuild and verify as a carrier refresh; keep prior head posture unless adoption metadata truly changes. | Letting mirror polish become scientific or authority gain. |
| `HS3` | unreconciled successor candidate | The continuation changes owner rows but lacks direct-descendant proof, rebase, docket chain, or cap preservation. | Run lineage merge, evidence intake, dependency propagation, and cap checks before successor use. | Treating an edited owner row as current by file presence. |
| `HS4` | owner-delta successor | The candidate is a direct descendant or rebased branch with explicit owner-row deltas and docket-state consequences. | Record touched owners, unchanged owners, mirrors, caps, validation, and rollback before adoption. | Hiding route-impacting edits inside release packaging. |
| `HS5` | mirror-only successor drift | Top-level mirrors imply a successor head that owners do not support. | Repair mirrors or downgrade them to navigation; do not update current posture. | Electing a head through README, status, context, or changelog wording. |
| `HS6` | challenged / frozen successor | The candidate would otherwise continue the head, but an unresolved challenge, quarantine, rollback trigger, cap failure, verification failure, or witness-separation issue bars succession. | Freeze transition until the blocking docket closes or scope-splits. | Letting a disputed successor inherit authority by recency. |
| `HS7` | adopted bounded successor | The candidate is a direct or rebased successor whose owner deltas, docket chain, caps, mirrors, validation, challenge state, and rollback handle agree. | Allow bounded current-head continuation and future release / verification / adoption reuse. | Treating succession as route promotion or witness closure. |
| `HS8` | succession failure / rollback | The successor relation cannot be justified, or later replay shows the transition was invalid. | Roll back to the prior adopted bounded head or current owner rows; quarantine successor authority. | Letting ambiguous successor history set broad posture. |

## Mandatory head-succession row

Fill this row whenever a candidate continuation, new release, extracted tree, copied root, branch, fork, generated surface, or local edit is proposed as replacing an adopted `OQ-0057` head.
For `HS0`, no row is needed.
For `HS1`, a compact scratch label is enough unless the continuation is later cited as current authority.

| Field | Required answer |
|---|---|
| Head-succession id | A release-scoped or local id sufficient to find the transition decision later. |
| Predecessor adopted head | Prior `HA7` carrier, current owner rows, or explicit none if bootstrapping. |
| Candidate successor | Zip, extracted root, copied tree, local branch, generated release object, or owner-row set. |
| Succession trigger | Scientific owner delta, lifecycle docket outcome, challenge closure, cap repair, package repair, mirror refresh, rollback, or explicit not-current scratch work. |
| Lineage relation | Direct descendant, rebased fork, cherry-pick, metadata refresh, mirror-only object, external edit, generated artifact, or unknown. |
| Owner-row delta map | Exact owner rows changed, rows deliberately unchanged, and any changed route fields, readiness rows, caps, or public-bridge conditions. |
| Docket-state chain | Evidence / supersession / propagation / adjudication / trace / replay / challenge / closure / adversarial / calibration / residual-cap / export / reimport / lineage / release / verification / adoption states touched by the transition. |
| Mirror delta map | README, START_HERE, SURFACE-STATUS, context-pack, receipt, changelog, generated index, curated index, and other mirrors updated or intentionally held. |
| Validation evidence | Index, lint, package, zip test, root-name check, mirror parity, owner replay, or explicit not-run state. |
| Residual cap / no-closure state | Minimum cap, target grain, record denominator, publicness / witness condition, earliest blocker, and no-closure wording carried into the successor. |
| Challenge / freeze state | Open or closed `Q`, `Z`, `R`, `SV`, `RS`, `LM`, `RI`, `X`, `RC`, `K`, `NC`, or lifecycle blockers that affect succession. |
| Excluded non-successor artifacts | Scratch roots, old bundles, generated mirrors, forks, or copied fragments that remain navigation-only. |
| Allowed use after decision | Navigation, current-head continuation, bounded export, lineage rebase, challenge input, owner repair, rollback, or quarantine. |
| Head-succession state | Which `HS` state applies? |
| Rollback / quarantine handle | Predecessor adopted head, owner row, trace id, release object, or external block to use if the successor fails later. |

## Head-succession rules

### 1. A revision number is not a proof of succession

A higher revision id, later timestamp, clean package name, or regenerated index can identify a candidate carrier.
It cannot prove that the candidate replaced the current head.
The transition must trace from predecessor head to candidate successor through owner-row deltas and docket outcomes.

Default failure: `HS2` or `HS5`.
Default repair: treat the object as a carrier refresh until owner deltas and adoption chain are named.

### 2. Metadata-only releases do not update route posture

A release can be valuable because it fixes package boundary, mirror parity, or restart hygiene.
If the scientific owner rows do not change, the successor record should say so.
The safe claim is “same bounded head carried by a cleaner release,” not “new identifiability progress.”

Default safe state: `HS2`.
Blocked overclaim: packaging repair as route delta.

### 3. Owner deltas must pass their native dockets before succession

If a successor changes route fields, readiness states, caps, challenge outcomes, public-bridge claims, calibration anchors, evidence status, or witness-package handoffs, it must run the appropriate owner dockets before succession.
A successor cannot hide scientific changes inside package, receipt, or generated-index updates.

Default failure: `HS3`.
Default repair: split carrier changes from owner deltas; run the route stack only where touched.

### 4. Mirrors follow the successor; they do not create it

README, START_HERE, SURFACE-STATUS, context-pack, receipt, changelog, generated index, curated index, and handoff summaries are useful mirrors.
They become unsafe if they move to a new-head story before the owner-row and docket-chain transition exists.

Default failure: `HS5`.
Default repair: repair mirrors to predecessor posture or add the missing succession row.

### 5. The most restrictive surviving cap carries forward

A successor that keeps bounded package-grain `S3`, mixed-record denominator, borrowed-public bridge, named-discriminator pocket, witness-separated support, non-comparable row, or no-closure wording must carry that cap everywhere the successor is reused.
If a successor erases the cap, it is not safer because it is newer.

Default failure: `HS6` or `HS8`.
Default repair: rerun residual-cap, export, seal, verification, adoption, and succession checks.

### 6. Challenges can block succession even after adoption

A predecessor may remain adopted while a candidate successor is frozen.
A challenge can target the successor delta, its mirror wording, its cap preservation, its lineage, or its validation evidence without invalidating all predecessor credit.
The archive should freeze the transition narrowly rather than demote the whole lane by association.

Default failure: `HS6`.
Default repair: answer and close the challenge, scope-split the successor, or roll back to predecessor.

### 7. Succession is not scientific promotion

`HS7` says a candidate continuation is the next bounded authority carrier.
It does not make family C `S4`, turn completion bids into acquired-record rows, turn lab routes into candidate-native target closure, or close witness-package debt.
Scientific promotion still requires the eight-field route, lifecycle, hostile-control, calibration, residual-cap, and public-bridge stack.

Default export wording: “adopted bounded successor; no live lane reaches `S4` or `S5`.”

### 8. Failed succession rolls back to the predecessor, not to summary prose

If a successor later fails replay, validation, cap preservation, challenge closure, lineage, or owner precedence, roll back to the predecessor adopted head or current owner rows.
Do not choose a README sentence, generated index line, or package name as the rollback target.

Default failure: `HS8`.
Default repair: predecessor owner recovery first, last verified/adopted carrier second, quarantine third.

## Current succession posture

Current safe successor use for `OQ-0057` is bounded:

| Object | Succession posture | Allowed use | Unsafe use |
|---|---|---|---|
| New direct-descendant release with owner delta | Candidate `HS4`; `HS7` only after docket chain, caps, validation, adoption, and mirrors agree. | Bounded current-head continuation. | Scientific route promotion by revision number. |
| Package cleanup or generated mirror refresh | `HS2` if owner rows are unchanged. | Cleaner carrier, navigation, cold replay. | Identifiability-progress claim. |
| Edited extracted tree | `HS1` or `HS3` until owner delta and lineage are classified. | Scratch work, candidate input, split ledger. | Current posture by local edit. |
| Returned fork or branch | `HS3` until rebased and verified. | Challenge input or bounded delta after rebase. | Successor head by cleanliness or novelty. |
| Mirror says current but owners do not | `HS5`. | Repair target. | Head election through summary wording. |
| Challenge-frozen continuation | `HS6`. | Frozen candidate and rollback handle. | Authority inheritance by recency. |
| Validated direct successor | `HS7`. | Bounded export, current-head navigation, future verification and adoption reuse. | `S4` / `S5` closure language. |

## Succession-safe handoff template

When a future revision presents itself as the next version of `OQ-0057` posture, use this shape:

> Treat a newer carrier as a successor candidate, not an automatic head. Name the predecessor adopted head, candidate successor, succession trigger, lineage relation, owner-row delta map, docket-state chain, mirror delta map, validation evidence, residual cap, no-closure sentence, challenge / freeze state, excluded non-successor artifacts, allowed use, and rollback handle. If the transition cannot be replayed, keep the candidate as scratch, metadata refresh, fork input, challenged successor, or quarantine; do not let revision order, successful package validation, or summary wording transfer authority by itself.

## Interaction with release, verification, adoption, and lineage controls

This docket sits after head adoption and governs replacement of one adopted bounded head by another; head retirement / vacancy governs withdrawal when no safe replacement exists:

1. The export-claim docket decides whether compact wording may leave an owner row.
2. The reimport firewall decides whether derivative wording that returns later can do more than point back to owners.
3. The lineage-merge docket decides whether older bundles, forks, cherry-picks, or generated archive artifacts can merge branch-local posture.
4. The release-seal docket states what an outgoing carrier is allowed to carry.
5. The seal-verification docket checks whether the actual carrier matches that seal.
6. The head-adoption docket decides whether a verified carrier is an adopted bounded head or only a pointer, ancestor, fork candidate, mirror, challenge input, or quarantine object.
7. This head-succession docket decides whether a later continuation can replace that adopted head as the next bounded authority carrier.
8. The head-branch arbitration docket decides what happens when two or more successor candidates, forks, cherry-picks, or scope-split continuations compete for that same current-head slot.
9. The head-retirement / vacancy docket decides what happens when a failed succession or failed branch contest should withdraw, scope, vacate, or quarantine current-head authority instead of selecting a replacement.

A sealed release can fail verification.
A verified release can fail adoption.
An adopted release can fail succession to a later candidate.
A successful successor remains derivative of owner rows.
A successful successor remains bounded by `OQ-0057` caps and no-closure wording.
A successful successor that returns later still needs reimport, lineage, verification, adoption, and succession handling.
A successful successor that faces a rival successor later still needs branch arbitration before unique head authority is spent.
A failed successor can trigger scoped retirement or vacancy instead of predecessor revival or weak successor election.

## Net result

This docket prevents a post-adoption custody inflation channel: confusing the newest validated continuation with a legitimate successor head.
It keeps next-version work useful while preventing revision numbers, timestamps, extracted roots, generated mirrors, and clean packages from becoming authority-transfer proof.
A future package may replace the adopted bounded `OQ-0057` head only when predecessor identity, direct or rebased lineage, owner-row deltas, docket-chain consequences, mirror deltas, validation evidence, residual caps, no-closure wording, challenge / freeze state, and rollback are all replayable.

No current lane is promoted to `S4` or `S5`.
No current lane is demoted.
The followthrough queue remains empty until a concrete successor candidate earns a real `HS` row beyond the current bounded direct-descendant posture.


A later attempt to restore any retired, vacant, or quarantined successor authority should use `docs/40-model/candidate-native-identifiability-head-reinstatement-thaw-docket.md`; re-entry conditions trigger review rather than automatic authority revival.


## Current-authority ledger handoff

If this surface is reused to state current `OQ-0057` posture after adoption, succession, branch arbitration, retirement / vacancy, or reinstatement / thaw, route through `docs/40-model/candidate-native-identifiability-current-authority-ledger.md` and declare one scoped authority object, source custody row, owner rows, exclusions, residual cap, export wording, next admissible transition, and rollback / quarantine handle.
