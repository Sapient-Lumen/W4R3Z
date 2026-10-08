# Candidate-native identifiability seal-verification docket

This document is the post-release verification surface for candidate-native identifiability bundle custody under `OQ-0057`.
It does **not** add a ninth identifiability field, replace the release-seal docket, replace the head-adoption docket, certify a lane as closed, promote any lane, demote any lane, or turn a zip file into evidence.
It answers the next operational question after the release-seal docket:

> after a release says it is sealed, how does the archive verify that the emitted or returned object actually preserves the claimed identity, owner chain, mirror status, residual caps, no-closure wording, package boundary, and adoption prerequisites?

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
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

The release-seal docket says what an outgoing bundle is allowed to carry forward.
That is necessary but not sufficient: a sealed claim can still drift if the emitted zip, extracted root, manifest, receipt, status warning, context posture, README / START_HERE mirrors, changelog, generated index, and canonical owner rows do not actually agree.
A future reader should not have to trust the release label, the slug, or the fact that packaging succeeded.
They need a verification outcome that says whether the bundle-level carrier can be used for navigation, cold replay, bounded export, lineage rebase, head-adoption review, or only quarantine.

The correct posture is:

**a release seal is a claim about bundle custody; seal verification is the check that the custody claim survives contact with the actual artifact. A bundle may enter head-adoption review only if its manifest-derived identity, extracted root, receipt, surface status, context posture, generated mirrors, owner-chain pointers, residual caps, no-closure clauses, package boundary, and rebuild / package checks agree. If verification fails, the bundle may point to possible owners, but it cannot donate route credit, publicness credit, calibration support, residual-cap support, release-head authority, or current-head authority.**

Use this docket when:
- a packaged zip, extracted tree, generated release object, or copied package root is used as current-head support;
- a manifest, receipt, SURFACE-STATUS warning, context-pack posture, README / START_HERE mirror, changelog bullet, or generated index is used to summarize `OQ-0057` posture;
- a release-seal row claims `RS7` but the actual files, mirrors, or root name have not been checked;
- an extracted tree is edited locally and then repackaged;
- a returned bundle is lineage-merged and its identity or owner-chain parity is uncertain;
- a release is used for cold replay, bounded export, reimport triage, or challenge response;
- the package contains multiple possible roots, stale generated surfaces, transient files, or a mismatch between package name and manifest identity.

Do not use this docket to decide whether a new scientific artifact improves a route field.
That remains the job of evidence intake, field protocols, adversarial controls, calibration, and the promotion gate.
This docket is for verifying the release carrier that preserves or transports those decisions.

## Seal-verification states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, reimport states, lineage-merge states, or release-seal states.
They say whether the actual bundle object matches the seal it claims to carry.

| Code | Seal-verification state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `SV0` | no verification needed | No release object, bundle mirror, extracted tree, or package-level posture is being reused. | Leave this docket unused. | Auditing ordinary owner-row edits as packages. |
| `SV1` | unverified carrier | A bundle, root, mirror, or summary is being reused before identity, owner-chain, cap, mirror, and package-boundary checks are run. | Treat as navigation only until checked. | Spending a label because packaging existed. |
| `SV2` | identity parity failure | Manifest, receipt, status, context, START_HERE identity, package filename, extracted root, previous-revision anchor, or timestamp disagree. | Repair identity or freeze release-level reuse. | Treating an inconsistent object as current head. |
| `SV3` | boundary / contents failure | The zip, root, or extracted tree has duplicate roots, missing required surfaces, transient files, stale generated output, mixed-head content, foreign bulky artifacts, or unexpected package residue. | Clean, split, rebuild, or quarantine. | Treating contaminated package contents as curated canon. |
| `SV4` | mirror parity failure | README, START_HERE, SURFACE-STATUS, context-pack, changelog, receipt, generated index, or curated index no longer mirrors the canonical owner posture. | Regenerate mirrors or downgrade them to stale navigation. | Letting stale mirrors outrank owners. |
| `SV5` | owner-chain replay failure | The release wording names no current owner rows, names stale rows, or cannot replay the bounded posture from route / lifecycle / control / cap / export / lineage / seal owners. | Route to current owners or freeze bundle authority. | Treating a release slug or receipt as the owner. |
| `SV6` | cap / no-closure parity failure | The bundle loses the bounded label, earliest blocker, witness-owner boundary, publicness condition, residual cap, no-closure sentence, or future reimport / lineage treatment. | Run residual-cap, export, reimport, lineage, and release-seal repairs before reuse. | Letting verified-looking bundles erase boundedness. |
| `SV7` | verified sealed bounded carrier | Identity, boundary, mirrors, owner chain, residual caps, no-closure wording, rebuild commands, and package integrity checks agree. | Allow navigation, cold replay, bounded export, direct-ancestor rebase, and challenge input only. | Treating all releases as unsafe merely because they are derivative. |
| `SV8` | verification failure / quarantine | The release object cannot be checked enough to decide parity, or failures remain after repair. | Quarantine bundle-level reuse and fall back to current owners or last verified sealed head. | Letting ambiguous custody create `S4` / `S5` pressure. |

## Mandatory seal-verification row

Fill this row whenever a release-seal state, package object, extracted tree, release mirror, or bundle-level claim is reused as current support or outward posture.
For `SV0`, no row is needed.
For `SV1`, a one-line unchecked-carrier warning is enough unless the object is reused.

| Field | Required answer |
|---|---|
| Seal-verification id | A release-scoped or local id sufficient to find the verification later. |
| Carrier checked | Zip, extracted tree, generated release object, copied root, README / START_HERE capsule, manifest, receipt, status warning, context posture, changelog bullet, generated index, or other package-level object. |
| Claimed seal state | Which `RS` state or release-seal row the carrier claims. |
| Expected identity | Revision, timestamp, slug, bundle name, previous revision, upstream bundle, and canonical root. |
| Observed identity | What the actual carrier, extracted root, manifest, receipt, status, context, and START_HERE identity surfaces report. |
| Boundary scan | Required surfaces present, duplicate roots absent, transients absent, bulky foreign artifacts absent, generated outputs current, and mixed-head residue absent. |
| Mirror parity check | README, START_HERE, SURFACE-STATUS, context-pack, changelog, receipt, generated index, and curated index agree with owner posture or are explicitly stale. |
| Owner-chain replay | Smallest current owner rows that reproduce the compressed `OQ-0057` wording. |
| Residual cap / no-closure parity | Bounded label, target grain, record denominator, witness-owner boundary, publicness condition, earliest blocker, no-closure wording, and rollback / quarantine handle. |
| Command / integrity evidence | `make index`, `make lint`, `make package`, zip integrity test, root-name check, required-surface check, or explicit not run. |
| Reimport / lineage treatment | How the carrier should be handled if it later returns as a summary, fork, cherry-pick, copied root, generated artifact, or external paraphrase. |
| Seal-verification state | Which `SV` state applies? |
| Allowed future use | Navigation, cold replay, bounded export, direct-ancestor rebase, challenge input, owner repair, or quarantine. |
| Repair / rollback handle | Current owner row, current verified head, last verified sealed head, or quarantine pointer. |

## Verification rules

### 1. Release-seal success is not self-verifying

`RS7` says a release is intended to be a sealed bounded carrier.
It does not by itself prove the emitted zip, extracted tree, generated mirrors, or copied root still match that seal.
Before a bundle can be reused, the verifier checks identity, boundary, mirrors, owners, caps, and integrity evidence.

Default failure: `SV1` if no check exists; `SV2` through `SV6` if a check fails.
Default repair: verify from current owner rows, then rerun package integrity.

### 2. Identity mismatches are custody failures before they are scientific disagreements

If the package filename says one revision, the manifest says another, the receipt points to a different upstream bundle, or the extracted root is not manifest-derived, the archive has a custody problem.
Do not try to resolve it by reading the scientific prose harder.
First repair the carrier identity or quarantine the package-level claim.

Default failure: `SV2`.
Default repair: align manifest / receipt / status / context / root / START_HERE, then regenerate mirrors.

### 3. Package contents must not smuggle extra support

A valid carrier should not contain retained PDFs, transient caches, duplicate package roots, stale generated outputs, scratch notes, copied older roots, or mixed-head surfaces.
Such contamination does not automatically alter the scientific route, but it does prevent bundle-level trust until removed, split, rebased, or quarantined.

Default failure: `SV3`.
Default repair: clean the boundary, rebuild, lint, package, and retest.

### 4. Mirrors are verified as mirrors

README posture, START_HERE blocks, context-pack posture, SURFACE-STATUS warnings, changelog bullets, revision receipts, curated index, and generated index help humans restart.
Verification asks whether they point to the same owner chain and carry the same cap.
It does not elevate them into owners.

Default failure: `SV4` or `SV5`.
Default repair: regenerate mirrors or retag stale mirrors as navigation only.

### 5. Caps and no-closure clauses are part of the artifact boundary

A bundle that keeps all files but drops the bounded label, earliest blocker, publicness condition, witness-owner boundary, no-closure clause, or future reimport / lineage treatment is not a safe carrier of `OQ-0057` posture.
It has preserved text but lost the control state that makes the text honest.

Default failure: `SV6`.
Default repair: rerun residual-cap, export, reimport, lineage, and release-seal checks before reuse.

### 6. Byte identity is useful but not sufficient

A zip byte hash may change because of compression metadata or rebuild environment, while the content carrier remains equivalent.
Conversely, a byte-identical stale package can still be unsafe if later owner rows supersede it.
This docket therefore prioritizes manifest-derived identity, required-surface presence, owner-chain replay, cap parity, and package-boundary cleanliness over treating a raw zip hash as final authority.

Default safe use: content / owner parity plus integrity checks.
Default unsafe use: hash-only confidence without owner-chain replay.

### 7. Verified carriers remain derivative

`SV7` allows a bundle to be used for navigation, cold replay, bounded export, direct-ancestor rebase, and challenge input.
It does not turn the bundle into scientific evidence, public witness closure, an independent replication, or a calibration anchor.
When the same object returns later, it still goes through reimport or lineage controls.

Default safe state: `SV7`.
Default downstream treatment: `RI` for derivative wording, `LM` for returned archive lineage, `RS` for outgoing seal, and `SV` for carrier parity.

### 8. Verification failure freezes bundle-level reuse, not necessarily current owners

If a bundle fails verification, the underlying canonical owner rows may still be sound.
Freeze the carrier, not the science, unless the owner row itself cannot be recovered or has been superseded, contradicted, or quarantined by later dockets.

Default failure: `SV8`.
Default repair: fall back to current owner rows or the last verified sealed head.

## Current verification posture

Current safe bundle-level use for `OQ-0057` remains bounded:

| Carrier | Verification posture | Unsafe use |
|---|---|---|
| Current package zip | May be used as a verified sealed bounded carrier after manifest / receipt / status / context / root / owner / cap / package checks pass. | Treat as evidence, witness closure, or score upgrade. |
| Extracted root | May be inspected and edited if it matches manifest-derived identity and contains no package contamination. | Reuse after local edits without rerunning index, lint, package, and verification. |
| Manifest / receipt / status / context | May establish release identity and compact posture if they agree. | Replace route / lifecycle / cap owners. |
| README / START_HERE | May help restart and point to owner rows. | Spend compressed wording as proof of near-closure. |
| Generated index | May check filesystem coverage. | Act as canonical owner of a field or route claim. |
| Changelog | May locate deltas. | Donate field credit or calibration support. |

## Verification-safe handoff template

When a future revision packages, cites, imports, or challenges an `OQ-0057` release, use this shape:

> Treat the bundle as a derivative carrier until verified. Check manifest / receipt / status / context / START_HERE identity, extracted-root name, required surface presence, generated mirror parity, owner-chain replay, residual-cap and no-closure preservation, package-boundary cleanliness, rebuild / lint / package evidence, and future reimport / lineage treatment. If any check fails, freeze bundle-level reuse and fall back to current owner rows or the last verified sealed head.

## Interaction with release sealing and lineage controls

This docket sits after release sealing and before any later reuse of the carrier:

1. The release-seal docket states what the outgoing carrier is allowed to carry.
2. This seal-verification docket checks whether the actual carrier matches that seal.
3. The head-adoption docket decides whether a verified carrier is the current adopted bounded head or only a pointer, ancestor, fork candidate, mirror, challenge input, or quarantine object.
4. The export-claim docket decides whether compact wording may leave owner rows.
5. The reimport firewall decides whether derivative wording that returns later can do more than point back to owners.
6. The lineage-merge docket decides whether older bundles, forks, cherry-picks, or generated archive artifacts can merge branch-local posture.

A release can be well sealed but not yet verified.
A verified release remains derivative.
A verified release is not necessarily the current head.
A verified release that returns later still needs reimport, lineage, verification, and adoption handling.

## Net result

This docket prevents package labels and seal prose from becoming trust shortcuts.
It makes release custody auditable without promoting zips, receipts, generated mirrors, or changelog bullets into scientific support.
A future bundle may carry bounded `OQ-0057` posture only when identity, contents, mirrors, owner chain, caps, no-closure wording, commands, future treatment, and downstream head-adoption status agree.

No current lane is promoted to `S4` or `S5`.
No current lane is demoted.
The followthrough queue remains empty until a concrete carrier earns a real `SV` row beyond the current verified bounded-head posture; current-head authority remains downstream of head adoption.


## Head-succession handoff

After a carrier verifies and is adopted, a later continuation still needs `docs/40-model/candidate-native-identifiability-head-succession-docket.md` before it replaces the adopted bounded head. A newer timestamp, cleaner package, regenerated mirror, or local edit is only a successor candidate until predecessor identity, lineage relation, owner-row deltas, mirror deltas, validation evidence, residual caps, challenge state, and rollback are replayable.


## Current-authority ledger handoff

If this surface is reused to state current `OQ-0057` posture after adoption, succession, branch arbitration, retirement / vacancy, or reinstatement / thaw, route through `docs/40-model/candidate-native-identifiability-current-authority-ledger.md` and declare one scoped authority object, source custody row, owner rows, exclusions, residual cap, export wording, next admissible transition, and rollback / quarantine handle.
