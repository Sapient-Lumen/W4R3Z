# Candidate-native identifiability head-adoption docket

This document is the post-verification head-adoption surface for candidate-native identifiability bundle custody under `OQ-0057`.
It does **not** add a ninth identifiability field, replace the route ledger, replace seal verification, certify a lane as closed, promote any lane, demote any lane, or turn a package into evidence.
It answers the next operational question after the seal-verification docket:

> after a carrier verifies, when may it become the current `OQ-0057` head rather than remaining a verified pointer, direct ancestor, fork candidate, mirror artifact, or challenge input?

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
- `docs/40-model/candidate-native-identifiability-head-succession-docket.md`
- `docs/40-model/candidate-native-identifiability-head-branch-arbitration-docket.md`
- `docs/40-model/current-head-control-router.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

Seal verification answers whether an actual carrier matches the seal it claims.
That is necessary but not sufficient for current-head reuse.
A direct ancestor can verify locally while being stale; a fork can verify internally while disagreeing with the current owner chain; a generated mirror can verify as a mirror while still being non-owner; a repaired package can verify after cleaning while still lacking adoption; and a challenge-frozen carrier can be replayable while still barred from head use.

The correct posture is:

**verification is a carrier-integrity claim; head adoption is an authority-transfer claim. A verified bundle may become the current `OQ-0057` head only if its lineage relation, owner-chain replay, revision ordering, residual caps, no-closure wording, challenge / freeze state, mirror parity, package boundary, and rollback handle all agree with the current canonical owners. If adoption fails, the carrier may still be useful for navigation, cold replay, lineage rebase, challenge input, or owner repair, but it cannot set current-head posture, overwrite broader mirrors, or donate route credit.**

Use this docket when:
- a verified zip, extracted tree, copied root, generated release object, or returned bundle is proposed as the current `OQ-0057` head;
- multiple verified carriers exist and the archive must decide which one has current authority;
- a direct-ancestor release verifies but a newer adopted head exists;
- a fork, cherry-pick, or externally edited bundle verifies under its own seal but has not been lineage-rebased;
- README, START_HERE, SURFACE-STATUS, context-pack, changelog, receipt, or generated index language says or implies “current head”;
- a rollback, challenge freeze, quarantine, or owner-row repair changes which carrier may be treated as head;
- a local extracted tree is edited and repackaged after verification;
- a release is used as the basis for a user-facing next-version handoff.

Do not use this docket to decide whether new scientific evidence improves an identifiability field.
That remains the job of evidence intake, field protocols, adversarial controls, calibration, and the promotion gate.
This docket decides only whether a verified carrier may be adopted as the current authority carrier for bounded `OQ-0057` posture.

## Head-adoption states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, reimport states, lineage-merge states, release-seal states, or seal-verification states.
They say whether a verified or candidate carrier may act as the current `OQ-0057` head.

| Code | Head-adoption state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `HA0` | no adoption needed | No package, mirror, or carrier is being promoted from verified object to current-head authority. | Leave this docket unused. | Auditing ordinary owner-row edits as head changes. |
| `HA1` | verified non-head pointer | The carrier verifies but is used only for navigation, cold replay, challenge input, or owner lookup. | Preserve pointer status and do not update head mirrors. | Treating every verified object as current. |
| `HA2` | stale direct ancestor | The carrier is a verified ancestor of the current head but lacks the latest adopted owner rows, caps, or mirrors. | Use for lineage / rollback only; do not spend as current posture. | Letting an old verified release outrank a newer adopted head. |
| `HA3` | fork / branch candidate | The carrier verifies internally but is not a direct adopted descendant, or it carries branch-local edits. | Run lineage merge, evidence intake, and conflict review before adoption. | Treating fork cleanliness as current-head authority. |
| `HA4` | mirror-only head drift | A README, START_HERE, status warning, context posture, generated index, receipt, or changelog implies head status without owner-chain adoption. | Repair mirrors or downgrade them to navigation. | Letting a summary title create head authority. |
| `HA5` | owner-precedence repair | Current canonical owner rows survive, but the carrier or mirrors point at an older, derivative, or incomplete owner chain. | Repoint the carrier to owners before adopting or reuse owners directly. | Treating package identity as stronger than canonical owners. |
| `HA6` | challenged / frozen candidate head | The carrier would otherwise verify, but an unresolved challenge, quarantine, rollback trigger, cap failure, or witness-separation condition bars adoption. | Freeze adoption until the blocking docket closes. | Letting disputed custody become current by freshness. |
| `HA7` | adopted bounded current head | The carrier verifies, is the selected current descendant, preserves owner-chain replay, caps, no-closure wording, mirror parity, challenge state, and rollback handle. | Allow current-head navigation, cold replay, bounded export, direct-descendant continuation, and future verification. | Treating adoption as `S4` / `S5` scientific promotion. |
| `HA8` | adoption failure / rollback | Adoption cannot be justified, or required parity fails after attempted repair. | Roll back to the last adopted bounded head or current owner rows; quarantine carrier-level authority. | Letting an ambiguous head set broad posture. |

## Mandatory head-adoption row

Fill this row whenever a verified carrier, release mirror, package object, returned bundle, or generated summary is proposed as current head for `OQ-0057` posture.
For `HA0`, no row is needed.
For `HA1`, a compact pointer note is enough unless the carrier is cited as current authority.

| Field | Required answer |
|---|---|
| Head-adoption id | A release-scoped or local id sufficient to find the adoption decision later. |
| Candidate carrier | Zip, extracted tree, copied root, manifest / receipt pair, generated mirror, returned bundle, or owner-row set. |
| Claimed verification state | Which `SV` row, package check, or explicit not-run state backs the candidate. |
| Prior adopted head | Last adopted bounded head, current owner rows, or explicit none. |
| Lineage relation | Direct descendant, direct ancestor, fork, cherry-pick, mirror-only object, external edit, generated artifact, or unknown. |
| Owner-chain replay | Smallest current owner rows that reproduce the proposed current-head `OQ-0057` posture. |
| Freshness / revision order | Revision, timestamp, upstream bundle, branch relation, and any newer competing head. |
| Challenge / freeze state | Open `Q`, `Z`, `R`, `SV`, `RS`, `LM`, `RI`, `X`, `RC`, `K`, `NC`, or lifecycle blockers that bar adoption. |
| Residual cap / no-closure state | Bounded label, witness-owner boundary, publicness condition, earliest blocker, and no-closure wording that must travel with the adopted head. |
| Mirror adoption set | README, START_HERE, SURFACE-STATUS, context-pack, changelog, receipt, generated index, and curated index updates required or deliberately not made. |
| Excluded non-head artifacts | Verified carriers, forks, summaries, or mirrors that remain navigation-only. |
| Allowed use after decision | Navigation, cold replay, bounded export, direct-descendant continuation, lineage rebase, challenge input, owner repair, rollback, or quarantine. |
| Head-adoption state | Which `HA` state applies? |
| Rollback / quarantine handle | Last adopted bounded head, owner row, trace id, or release object to use if this adoption fails later. |

## Head-adoption rules

### 1. Verification is necessary but not sufficient

A carrier that passes seal verification has proven custody parity, not authority.
It may still be an ancestor, fork, mirror, branch snapshot, generated artifact, or challenge-frozen object.
Before it can set current posture, this docket must decide whether it is the current adopted descendant or only a verified pointer.

Default safe state: `HA1`.
Promotion to head: only after owner-chain replay, lineage relation, cap preservation, and challenge state agree.

### 2. Freshness is not a head election

A newer timestamp, package filename, or local edit does not automatically outrank the last adopted bounded head.
If the newer carrier is not a direct descendant of the adopted head, or if it contains branch-local edits, it is a fork candidate until lineage merge and evidence intake classify the delta.

Default failure: `HA3`.
Default repair: run lineage merge; split new evidence from branch posture; then rerun verification and adoption.

### 3. Owners outrank carriers

If a package, receipt, START_HERE mirror, changelog bullet, or generated index disagrees with the route ledger, lifecycle dockets, control dockets, cap ledger, export / reimport / lineage surfaces, seal surfaces, or open-question registry, the owner chain wins.
The carrier may be repaired, but it cannot overwrite the owners merely because it verifies as a package.

Default failure: `HA4` or `HA5`.
Default repair: repoint mirrors to owners; regenerate; keep the carrier navigation-only until parity returns.

### 4. Adoption cannot erase caps

A head may be adopted only with the most restrictive surviving cap.
If bounded package-grain `S3`, mixed-record support, borrowed-public bridge, witness-separated support, non-comparable labels, or no-closure wording are present in the owners, the adopted head must carry them.
A cap-preserving ancestor is safer than a cap-erasing fresh package.

Default failure: `HA6` or `HA8`.
Default repair: rerun residual-cap, export, release-seal, and seal-verification checks before adoption.

### 5. Challenge and quarantine states bar adoption until closed

A candidate head that has unresolved route-bearing challenge, closure-barred credit, field quarantine, conflict freeze, verification failure, release-seal failure, or lineage failure cannot become current merely because it packages cleanly.
The correct posture is frozen candidate head until the blocking docket gives a re-entry condition.

Default failure: `HA6`.
Default repair: close the challenge, split the scope, or roll back to the last adopted bounded head.

### 6. Mirrors update after adoption, not before

README, START_HERE, SURFACE-STATUS, context-pack, changelog, receipt, generated index, and curated index are allowed to mirror the adopted head.
They do not elect it.
If mirrors move first, the adoption row must either repair them back to the old head or name the owner-chain decision that justifies the new head.

Default failure: `HA4`.
Default repair: regenerate mirrors after owner adoption; mark stale mirrors as navigation only.

### 7. Adoption is not scientific promotion

`HA7` says a bounded carrier is the selected current head for archive custody.
It does not make family C `S4`, turn completion bids into acquired-record rows, turn lab routes into candidate-target closure, or close witness-package debt.
Scientific promotion still requires the eight-field route, field protocols, lifecycle dockets, hostile controls, calibration, caps, public bridge, and promotion gate.

Default blocked overclaim: “adopted head means near closure.”
Default export wording: “adopted bounded current head; no live lane reaches `S4` or `S5`.”

### 8. Failed adoption rolls back narrowly

If adoption fails, freeze carrier-level authority without automatically demoting the underlying scientific route.
Recover current owner rows if possible.
If owner rows cannot be replayed, roll back to the last adopted bounded head rather than letting multiple verified carriers compete silently.

Default failure: `HA8`.
Default repair: owner recovery first, last adopted head second, quarantine third.

## Current adoption posture

Current safe head use for `OQ-0057` is bounded:

| Object | Adoption posture | Allowed use | Unsafe use |
|---|---|---|---|
| Current validated release | `HA7` only after index, lint, package, zip test, root-name check, and mirror parity pass. | Current-head navigation, cold replay, bounded export, direct-descendant continuation. | Scientific route promotion or closure language. |
| Previous verified release | Usually `HA2` once a newer adopted head exists. | Rollback anchor, lineage comparison, cold replay. | Override newer owner rows by package cleanliness. |
| Returned fork or edited root | `HA3` until lineage merge, evidence intake, conflict review, verification, and adoption finish. | Candidate input and split ledger. | Current posture by freshness. |
| README / START_HERE / context / status | Mirror only unless backed by owner-chain adoption. | Human / machine re-entry. | Electing head through summary wording. |
| Generated index / changelog / receipt | Locator or rationale mirror only. | Delta discovery and release replay. | Claim owner or route evidence. |
| Challenge-frozen carrier | `HA6` until closure. | Challenge input and quarantine handle. | Current-head authority. |

## Adoption-safe handoff template

When a future revision uses, packages, cites, imports, or links an `OQ-0057` release as current head, use this shape:

> Treat a verified carrier as navigation until adopted. Name the prior adopted head, the candidate carrier, lineage relation, owner-chain replay, freshness relation, residual cap, no-closure sentence, challenge / freeze state, mirror adoption set, excluded non-head artifacts, allowed future use, and rollback handle. If any piece fails, keep the carrier as a pointer or roll back to the last adopted bounded head; do not let package verification, a new timestamp, or summary wording set current posture by itself.

## Interaction with release, verification, reimport, and lineage controls

This docket sits after seal verification and before current-head reuse; head succession and branch arbitration then governs replacement of the adopted head by a later continuation:

1. The export-claim docket decides whether compact wording may leave an owner row.
2. The reimport firewall decides whether derivative wording that returns later can do more than point back to owners.
3. The lineage-merge docket decides whether older bundles, forks, cherry-picks, or generated archive artifacts can merge branch-local posture.
4. The release-seal docket states what an outgoing carrier is allowed to carry.
5. The seal-verification docket checks whether the actual carrier matches that seal.
6. This head-adoption docket decides whether a verified carrier is the current adopted bounded head or only a pointer, ancestor, fork candidate, mirror, challenge input, or quarantine object.
7. The head-succession docket decides whether a later release, extracted continuation, local edit, generated mirror, or branch may replace that adopted bounded head as the next authority carrier.

A release can be well sealed but not verified.
A verified release can still be non-head.
An adopted head remains derivative of owner rows.
An adopted head that returns later still needs reimport, lineage, verification, adoption, and succession review.
A later candidate successor is not elected by revision order; it must pass the head-succession docket before replacing an adopted head.

## Net result

This docket prevents a final custody inflation channel: confusing a verified carrier with current authority.
It makes head selection explicit without promoting packages, receipts, generated mirrors, changelog bullets, or START_HERE summaries into scientific support.
A future bundle may carry current bounded `OQ-0057` posture only when seal verification is complete, lineage is direct or rebased, owner-chain replay survives, residual caps and no-closure wording persist, challenges and freezes are closed or scoped, mirrors follow owners, rollback is named, and later successor transitions are replayable.

No current lane is promoted to `S4` or `S5`.
No current lane is demoted.
The followthrough queue remains empty until a concrete carrier earns a real `HA` row beyond the current adopted bounded-head posture.


## Current-authority ledger handoff

If this surface is reused to state current `OQ-0057` posture after adoption, succession, branch arbitration, retirement / vacancy, or reinstatement / thaw, route through `docs/40-model/candidate-native-identifiability-current-authority-ledger.md` and declare one scoped authority object, source custody row, owner rows, exclusions, residual cap, export wording, next admissible transition, and rollback / quarantine handle.
