# Candidate-native identifiability release-seal docket

This document is the outgoing bundle-seal surface for candidate-native identifiability updates under `OQ-0057`.
It does **not** add a ninth identifiability field, replace the route ledger, replace the lifecycle dockets, replace the export / reimport / lineage-merge controls, replace the seal-verification docket, certify the archive as final, promote any lane, or demote any lane by itself.
It answers the next operational question after the lineage-merge docket:

> when the archive emits a release bundle or current-head package, how does the archive prevent that bundle from later being mistaken for an evidence source, an independent witness, or an unqualified closure certificate?

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
- `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`
- `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`
- `docs/40-model/candidate-native-identifiability-head-succession-docket.md`
- `docs/40-model/candidate-native-identifiability-head-branch-arbitration-docket.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

The lineage-merge docket controls what happens when older bundles, forks, cherry-picks, generated archive artifacts, or externally edited trees come back into the archive.
That creates the reciprocal outgoing duty: the current archive should emit release bundles that already say what they are, what they are not, which owner rows support their compressed claims, which generated mirrors are only mirrors, which residual caps survive, and what future merge / reimport treatment they require.

The correct posture is:

**a release bundle is a sealed carrier of current posture, not itself a scientific observation, independent replication, public witness, calibration anchor, or closure certificate. Before an `OQ-0057` release can be reused, compared, cited, rebased, mirrored, exported, or merged, its seal must identify the canonical owner surfaces, current bounded label, surviving caps, generated / mirror surfaces, package boundary, integrity checks, future reimport / lineage rules, and a verification path. If that seal is absent or inconsistent, the bundle may be used for navigation only, not for route credit.**

Use this docket when:
- a revision packages a new release that changes or summarizes `OQ-0057` posture;
- a release slug, receipt, status warning, README posture, START_HERE mirror, context-pack entry, changelog bullet, generated index, or package name compresses candidate-native identifiability credit;
- a future reader wants to cite the bundle itself rather than the route ledger, lifecycle dockets, control dockets, or registry rows;
- a packaged tree contains generated surfaces whose wording might outrank owner rows by convenience;
- a release carries caps, no-closure clauses, or lineage / reimport instructions that must survive downstream copying;
- an extracted tree or zip is being compared against a manifest-derived canonical root;
- a bundle contains non-canonical scratch, duplicate package roots, stale build residue, or mixed-head content.

Do not use it to score a new paper, dataset, proof, experiment, or public replay artifact.
Those enter through evidence intake, challenge response, public-bridge protocol, or adversarial controls.
This docket is for the archive release object that carries the current state of those surfaces.

## Release-seal states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, reimport states, or lineage-merge states.
They say whether a packaged archive release may safely carry bounded `OQ-0057` posture forward.

| Code | Release-seal state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `RS0` | no release boundary | No package, release, mirror, or bundle-level reuse is being made. | Leave this docket unused. | Auditing ordinary row edits as releases. |
| `RS1` | unsealed local scratch | A local tree, extracted copy, or edited package is being used without a current manifest / receipt / status / context seal. | Treat as working scratch; do not cite for posture. | Letting an unsealed working copy donate support. |
| `RS2` | identity drift | Manifest, receipt, status, context, root name, package name, timestamp, previous-revision anchor, or generated restart mirror disagree. | Repair identity or freeze bundle-level reuse. | Treating an inconsistent package as a trustworthy head. |
| `RS3` | mirror-owner inversion | README, START_HERE, changelog, generated index, context posture, status warning, or receipt is being used as the scientific owner. | Route to the canonical owner row; mark mirrors as pointers only. | Letting convenient summaries outrank route / docket owners. |
| `RS4` | owner omission | The release compresses `OQ-0057` posture but omits the owner surfaces, current bounded label, cap, or earliest blocker needed to replay it. | Add the missing owner chain or downgrade to navigation. | Exporting near-closure language without owner rows. |
| `RS5` | cap / export mismatch | The package seal, release title, README, START_HERE, receipt, or context loses a residual cap, publicness condition, no-closure clause, or rollback handle. | Run residual-cap and export-claim repair before release reuse. | Letting release packaging erase boundedness. |
| `RS6` | package contamination | The bundle contains transient scratch, duplicate roots, stale generated output, foreign PDFs, copied old surfaces, mixed-head fragments, or unrebased lineage content. | Remove, rebase, split, or freeze; then rebuild. | Treating packaging residue as curated canonical content. |
| `RS7` | sealed bounded release | Identity matches, owner rows are named, mirrors are marked as mirrors, caps survive, integrity checks pass, future reimport / lineage treatment is explicit, and seal verification is available. | The bundle may be used for navigation, cold replay, bounded export, and future lineage rebase. | Forbidding safe release use merely because releases are derivative. |
| `RS8` | seal failure / quarantine | The package boundary, owner chain, cap state, generated mirrors, or integrity status cannot be reconstructed. | Quarantine the release object or roll back to the last sealed head. | Letting ambiguous package custody create `S4` / `S5` pressure. |

## Mandatory release-seal row

Fill this row whenever a packaged release, extracted tree, release mirror, or bundle-level claim is used to carry `OQ-0057` posture forward.
For `RS0`, no row is needed.
For `RS1`, a one-line scratch warning is enough unless the scratch object is reused.

| Field | Required answer |
|---|---|
| Release-seal id | A release-scoped or local id sufficient to find this seal later. |
| Package object | Zip, extracted tree, generated release artifact, README / START_HERE capsule, receipt, status warning, context-pack posture, changelog bullet, or other bundle-level object. |
| Manifest identity | Revision, timestamp, slug, bundle name, previous revision, and canonical root. |
| Package boundary | Which files are canonical release content and which are scratch, generated mirrors, transient outputs, or excluded objects. |
| Touched `OQ-0057` owners | Route ledger, promotion gate, readiness matrix, lifecycle docket, adversarial-control battery, calibration docket, residual-cap ledger, export / reimport / lineage surface, registry row, or router. |
| Owner-chain pointer | The smallest set of current owner rows that supports the compressed release wording. |
| Generated / mirror surfaces | README, START_HERE, context-pack, status, receipt, changelog, generated index, or other mirrors that must not become primary support. |
| Residual cap carried | The bounded label, target grain, record denominator, publicness / witness condition, earliest blocker, and no-closure sentence that survive export. |
| Integrity checks | Commands or comparisons run: index, lint, package, zip test, root-name check, mirror parity, seal-verification check, or explicit not run. |
| Reimport / lineage instruction | How a future reader should treat this bundle if it returns as evidence, branch, fork, cherry-pick, generated artifact, or external paraphrase. |
| Release-seal state | Which `RS` state applies? |
| Allowed future use | Navigation, cold replay, bounded export, direct-ancestor rebase, challenge input, owner-row repair, or quarantine. |
| Rollback / quarantine handle | Last sealed head, current owner row, or decision trace to use if the package seal fails. |

## Release-seal rules

### 1. A sealed bundle is not independent evidence

A release package can preserve what the current archive decided.
It cannot make that decision more true by being zipped, named, timestamped, mirrored in START_HERE, or summarized in a receipt.
If a future revision cites the package itself as support for `OQ-0057`, the correct move is to trace from the seal to the owner rows and then apply the reimport firewall or lineage-merge docket.

Default failure: `RS3` plus `RI1` or `LM2`.
Default repair: use the bundle as a pointer, not as route credit.

### 2. Identity parity precedes posture reuse

Manifest, receipt, status, context, package name, root name, upstream bundle, generated restart mirrors, and generated index do not need to carry the whole argument.
They do need to agree about which release they describe.
If identity surfaces disagree, the release object is a custody problem before it is a scientific posture object.

Default failure: `RS2`.
Default repair: repair identity and regenerate mirrors before reuse; otherwise quarantine.

### 3. Mirrors must point down to owners

README posture, START_HERE mirrors, context-pack current posture, SURFACE-STATUS warnings, changelog bullets, release receipts, and generated indexes are allowed to be useful.
They are not owner rows for candidate-native identifiability.
A valid seal names which route ledger, lifecycle docket, control docket, cap ledger, export / reimport surface, lineage surface, and registry row actually owns the claim.

Default failure: `RS3` or `RS4`.
Default repair: attach the owner-chain pointer and preserve the bounded label.

### 4. Caps survive packaging or the package is unsafe

A release slug can be compact, but release wording cannot erase boundedness.
If family C is bounded package-grain `S3`, the release cannot export it as near-closure.
If lab / simulation routes are named-discriminator `S3` pockets, the release cannot export them as candidate-native target closure.
If completion bids are target-rich but acquired-record-poor, the release cannot export them as empirically identified completions.

Default failure: `RS5`.
Default repair: rerun the residual-cap ledger and export-claim docket; if the cap cannot be restored, freeze the package claim.

### 5. Package contamination is a release problem, not scientific evidence

A bundled PDF, temporary scratch directory, stale generated index, duplicate root, copied old surface, unrebased fork fragment, or foreign branch residue does not automatically change the science.
It does make the package unsafe as a release carrier until split, removed, rebased, or quarantined.

Default failure: `RS6`.
Default repair: clean the package boundary, rebuild generated surfaces, lint, and retest the zip.

### 6. A sealed release remains derivative when it returns

`RS7` allows a bundle to be used safely for navigation, cold replay, bounded export, and future lineage rebase.
It does not bypass the reimport firewall or lineage-merge docket when that same bundle returns later as support.
The future reader still has to trace to owner rows and preserve caps.

Default safe state: `RS7`.
Default downstream treatment: `RI` for derivative wording, `LM` for returned lineage objects.

### 7. Seal failure freezes bundle-level reuse, not necessarily the underlying claim

If a package seal fails, the archive should not automatically demote the scientific route row.
It should freeze use of the release object until the current canonical owner row can be recovered.
If the owner row survives, it may continue independently of the bad package.
If the owner row cannot be recovered, rollback or quarantine applies.

Default failure: `RS8`.
Default repair: recover current owners; otherwise roll back to the last sealed head.

## Current release posture

Current safe release use for `OQ-0057` is bounded:

| Release object | Allowed use | Unsafe use |
|---|---|---|
| Current sealed zip | Navigation, cold replay, bounded export, and future lineage rebase. | Treat as independent evidence or public witness closure. |
| Manifest / receipt / status / context | Identity, rationale, posture summary, and restart routing. | Treat as scientific owners for route-state claims. |
| README / START_HERE | Human reentry and compressed guardrails. | Quote as proof that `S4` or closure is near. |
| Generated index | File discovery and coverage check. | Treat as canonical owner of field or lifecycle claims. |
| Changelog | Revision history and delta location. | Spend as a field upgrade or calibration anchor. |
| Extracted tree | Inspection and local editing before rebuild. | Merge as current support if identity or package boundary drifted. |

## Release-safe handoff template

When a future revision packages or cites an `OQ-0057` release, use this shape:

> The release bundle is a sealed carrier, not independent evidence. Verify manifest / receipt / status / context identity, regenerate mirrors, name the current owner rows, preserve the minimum residual cap and no-closure sentence, exclude scratch or mixed-head content, and record how this bundle should be handled if it later returns as a reimported summary or lineage object. If the seal cannot be replayed, freeze bundle-level use and fall back to current owner rows or the last sealed head.

## Interaction with export, reimport, and lineage controls

This docket sits at the package boundary.
It does not replace the surrounding controls:

1. The export-claim docket decides whether compact wording may leave an owner row.
2. The reimport firewall decides whether derivative wording that returns later can do more than point back to owners.
3. The lineage-merge docket decides whether older bundles, forks, cherry-picks, or generated archive artifacts can merge branch-local posture.
4. This release-seal docket decides whether the outgoing release carrier itself preserves identity, owner rows, caps, mirrors, package boundary, and future treatment instructions.
5. The seal-verification docket decides whether the actual emitted or returned carrier matches that seal before it is reused.
6. The head-adoption docket decides whether a verified carrier is the current adopted bounded head or only a pointer, ancestor, fork candidate, mirror, challenge input, or quarantine object.

A safe export is not necessarily a sealed release.
A sealed release is not necessarily verified.
A verified sealed release is not necessarily new evidence.
A verified sealed release is not necessarily the current head.
A verified sealed release that returns later still needs reimport, lineage, verification, and adoption handling.

## Net result

This docket prevents release packaging from becoming another evidence-inflation channel.
It keeps the current bundle useful as a durable carrier while preventing zips, manifests, receipts, generated mirrors, README summaries, and changelog bullets from becoming surrogate proof of candidate-native identifiability.

No current lane is promoted to `S4` or `S5`.
No current lane is demoted.
The followthrough queue remains empty until a concrete release object earns a real `RS` row beyond the current sealed bounded-head posture; current-head authority remains downstream of seal verification and head adoption.


## Head-succession handoff

After a carrier verifies and is adopted, a later continuation still needs `docs/40-model/candidate-native-identifiability-head-succession-docket.md` before it replaces the adopted bounded head. A newer timestamp, cleaner package, regenerated mirror, or local edit is only a successor candidate until predecessor identity, lineage relation, owner-row deltas, mirror deltas, validation evidence, residual caps, challenge state, and rollback are replayable.


## Current-authority ledger handoff

If this surface is reused to state current `OQ-0057` posture after adoption, succession, branch arbitration, retirement / vacancy, or reinstatement / thaw, route through `docs/40-model/candidate-native-identifiability-current-authority-ledger.md` and declare one scoped authority object, source custody row, owner rows, exclusions, residual cap, export wording, next admissible transition, and rollback / quarantine handle.
