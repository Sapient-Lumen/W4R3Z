# Candidate-native identifiability lineage-merge docket

This document is the branch / bundle custody surface for candidate-native identifiability updates under `OQ-0057`.
It does **not** add a ninth identifiability field, replace the route ledger, replace the reimport firewall, create a general version-control policy for the whole archive, promote any lane, or demote any lane by itself.
It answers the next operational question after the reimport firewall:

> when an older release, alternate fork, copied archive fragment, cherry-picked document, generated-only index, or externally edited bundle returns to the archive, how does the archive prevent stale or fork-local `OQ-0057` credit from being merged as current posture?

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
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

The reimport firewall blocks derivative **sentences** from becoming self-cited evidence.
A different problem remains: a whole archive package, older release, fork, copied document subset, or downstream edited bundle can return with its own local posture.
That returned bundle may contain canonical-looking surfaces, claim ids, route rows, generated indexes, receipts, and release slugs.
Those features make it easy to confuse **lineage custody** with **current support**.

The correct posture is:

**a returned archive bundle is a lineage object, not automatically a current owner. Before any `OQ-0057` route state, readiness class, lifecycle decision, adversarial-control pass, calibration anchor, residual cap, export state, or reimport repair is merged from that bundle, the archive must identify the source lineage, compare it with the current head, rebase touched owner rows through the current docket stack, split genuinely new evidence from stale branch posture, and preserve the most restrictive surviving cap.**

Use this docket when:
- an older release is uploaded as the starting point for a new revision;
- a prior archive bundle is cited as support for a current `OQ-0057` claim;
- an external fork or local copy edited candidate-native identifiability surfaces;
- a single markdown file is cherry-picked from another bundle;
- a generated index, release receipt, or START_HERE capsule is used to infer what changed in another lineage;
- two bundles disagree about family-C, completion-bid, lab / simulation, witness-side, or cosmological identifiability posture;
- a future revision wants to keep new text from one branch while inheriting old route credit from another.

Do not use it for ordinary single-source evidence intake.
A new paper, dataset, proof, record object, or public replay artifact enters through the evidence-intake docket.
This docket is for archive-lineage artifacts and branch-local posture.

## Lineage-merge states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, export states, or reimport states.
They say whether a returned archive lineage may update current `OQ-0057` support.

| Code | Lineage state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `LM0` | no lineage merge | No prior bundle, fork, copied surface, or branch-local posture is being merged. | Leave this docket unused. | Auditing ordinary current-head edits as if they were forks. |
| `LM1` | same-head navigation | The returned object is the current head or an exact copy used only for navigation. | Use as a pointer; no posture credit is created. | Treating a duplicate bundle as corroboration. |
| `LM2` | direct-ancestor rebase | The source is an older direct ancestor and its rows are being consulted. | Rebase through all later owner rows before reuse. | Importing pre-upgrade posture after later dockets exist. |
| `LM3` | stale-ancestor credit | The older bundle contains credit touched by later supersession, challenge, calibration, cap, export, or reimport changes. | Prefer current owners; rerun decay / replay / challenge checks if any old credit is proposed. | Spending a pre-repair label as if it survived. |
| `LM4` | orphan cherry-pick | A copied markdown fragment lacks the docket chain, owner rows, manifest / receipt, or upstream bundle needed to reconstruct support. | Treat as text only; reconstruct from canonical current owners or freeze. | Letting one good paragraph import hidden support. |
| `LM5` | alternate-fork disagreement | A forked or externally edited bundle has a conflicting field cell, route state, readiness row, closure state, or cap. | Run conflict adjudication and decision trace before any merge. | Choosing the more favorable branch by convenience. |
| `LM6` | mixed branch / new evidence | The returned bundle mixes old archive posture with genuinely new paper, proof, dataset, challenge, or replay content. | Split lineage echo from new content; route new content to evidence intake or challenge response. | Laundering new evidence through stale branch posture. |
| `LM7` | rebase-complete bounded merge | The source lineage is identified, touched rows are rebased, caps survive, conflicts are adjudicated, and a trace / replay handle exists. | Merge only the bounded, owner-anchored delta named by the row. | Forbidding useful branch work when it survives current controls. |
| `LM8` | lineage failure / freeze | The branch relation, owner chain, source evidence, current cap, or conflict outcome cannot be reconstructed. | Freeze, roll back, or replace with current unresolved posture. | Letting ambiguous bundle provenance create `S4` / `S5` pressure. |

## Mandatory lineage row

Fill this row whenever a prior bundle, fork, cherry-picked surface, copied archive fragment, or generated release artifact is used to support or change `OQ-0057` posture.
For `LM0` or `LM1`, a one-line no-merge / navigation note is enough.

| Field | Required answer |
|---|---|
| Lineage id | A release-scoped or local id sufficient to find this merge later. |
| Returning lineage object | Whole zip, extracted tree, single markdown file, generated index, receipt, START_HERE capsule, fork commit, manuscript appendix, or other archive-lineage artifact. |
| Source revision / bundle | Claimed revision, timestamp, slug, upstream bundle, or explicit unknown. |
| Relation to current head | Same head, direct ancestor, older ancestor, alternate fork, cherry-pick, mixed branch, unknown. |
| Proposed use | Navigation, owner-row recovery, field-cell update, route-state update, readiness update, challenge, rollback, export repair, or broad-mirror wording. |
| Touched `OQ-0057` owners | Route ledger, promotion gate, readiness matrix, lifecycle docket, control docket, calibration docket, residual-cap ledger, export / reimport surface, registry row, or router. |
| Common ancestor / divergence point | The latest shared release or owner row, if known. |
| Current-head owner row | The current canonical row that owns the claim after later revisions are considered. |
| Branch-local claim | The exact field, route, readiness, cap, or closure claim being imported. |
| Later-docket gap check | Which later protocols or dockets did not exist in the source lineage or were not run there. |
| Supersession / challenge / cap check | Whether later decay, challenge, closure, adversarial, calibration, residual-cap, export, or reimport states touch the branch-local claim. |
| Echo / new-content split | Which parts are older archive posture and which, if any, are genuinely new evidence, proof, replication, contradiction, or challenge. |
| Merge state | Which `LM` state applies? |
| Allowed import | Navigation only, owner-row repair, field-local delta, lifecycle repair, challenge input, bounded merge, or freeze. |
| Trace / rollback handle | Where a future reader can replay the merge, undo it, or recover the most restrictive current owner. |

## Lineage rules

### 1. Ancestors do not outrank current owners

A direct ancestor can explain why a row exists.
It does not decide whether that row still carries current support after later dockets, challenges, controls, calibration, caps, export rules, or reimport rules were added.
Older rows must be rebased through current owner surfaces before they are reused.

Default failure: `LM2` or `LM3`.
Default repair: cite the ancestor as history, then use the current owner row and rerun any later docket that touches the claim.

### 2. Forks are not consensus by accumulation

Two branches saying similar optimistic things do not create independent support if they share the same source owner or if one copied the other's summary.
Two branches disagreeing does not allow the editor to pick the more favorable field state.
A fork conflict must be scope-split, precedence-corrected, retagged, quarantined, route-frozen, or witness-separated before posture changes.

Default failure: `LM5`.
Default repair: run conflict adjudication, then trace the branch decision.

### 3. Cherry-picks carry no hidden chain

A copied paragraph from another bundle is not enough.
If it lacks the route ledger row, lifecycle chain, owner precedence, residual cap, export state, and rollback handle, it can at most be a search clue.
The current archive must reconstruct support from canonical owners.

Default failure: `LM4`.
Default repair: recover the source owner and docket chain; otherwise freeze the import.

### 4. Generated release surfaces are lower-trust lineage clues

`ARCHIVE_INDEX.generated.md`, release receipts, START_HERE mirrors, context-pack posture, and changelog bullets are useful for locating surfaces and deltas.
They are not branch-local scientific owners.
When a generated or mirror surface is the only available support, combine this docket with the reimport firewall and downgrade to navigation unless the owner chain can be recovered.

Default failure: `LM4` plus `RI1` or `RI2`.
Default repair: trace to the owning route / lifecycle / control / calibration / cap row in the current head.

### 5. New evidence inside an old bundle must be split

A returned bundle may contain a stale archive state and a genuinely new paper, proof, dataset, replication, challenge, or public replay object.
The old branch posture still goes through lineage merge.
The new artifact goes through evidence intake or challenge response.
The presence of new evidence does not launder older branch-local route states.

Default failure: `LM6` if not split.
Default repair: split lineage echo from new content, then run the correct docket on each part.

### 6. Merge preserves the most restrictive surviving cap

If one lineage says bounded package-grain `S3`, another says named-discriminator `S3`, and a third says near-`S4`, the merged row does not inherit the strongest phrase.
It carries the most restrictive owner-supported cap until calibration, adversarial controls, challenge closure, and public-bridge checks say otherwise.

Default failure: `LM3`, `LM5`, or `LM8`.
Default repair: use residual-cap preservation and calibration anchors before broad wording changes.

### 7. Safe lineage merge is bounded and replayable

A successful lineage merge is not a general endorsement of the source bundle.
It is one bounded delta with an identified source lineage, current-head owner, docket-gap check, conflict outcome, preserved cap, and replay / rollback handle.
This is `LM7`.

## Current lineage posture

Current safe lineage use for `OQ-0057` is intentionally narrow:

| Returning object | Allowed use | Unsafe use |
|---|---|---|
| Current release copy | Navigation and integrity comparison. | Treating an exact copy as independent confirmation. |
| Direct older release | Historical recovery of why a row was introduced. | Importing its field state after later controls exist. |
| Alternate fork | Candidate delta after conflict adjudication. | Selecting the optimistic route state without rebase. |
| Single copied markdown file | Search clue or owner locator. | Importing route support without the docket chain. |
| Generated index or receipt | Locate files and revision rationale. | Treat generated text as the owner of identifiability posture. |
| External edited bundle | Possible new evidence / challenge after splitting. | Treat external packaging as public witness closure. |

## Merge-safe handoff template

When a future revision starts from an older or forked bundle, use this shape before changing `OQ-0057` posture:

> The source bundle is a lineage object, not current evidence. Identify its relation to the current head, recover the common ancestor and owner rows, split stale archive posture from genuinely new evidence or challenge content, rebase touched claims through the current docket stack, preserve the most restrictive surviving cap, and record a trace / rollback handle. If any owner chain or conflict cannot be reconstructed, freeze the route state rather than importing the branch label.

## Interaction with the reimport firewall

The reimport firewall handles derivative wording.
This docket handles derivative **archive lineages**.
They often run together:

1. A release note, user answer, abstract, or paraphrase that returns as support needs an `RI` state.
2. A prior release bundle, fork, cherry-picked surface, or generated archive artifact that returns as support needs an `LM` state.
3. If a returning bundle also contains derivative summaries, run the firewall on those summaries and this docket on the branch relation.

A safe reimport is not necessarily a safe merge.
A safe merge is not necessarily safe to export.
The archive should keep those approvals separate.

## Net result

This docket prevents archive provenance from becoming another evidence-inflation channel.
It keeps older releases, forks, copied surfaces, and generated release artifacts downstream of current canonical owner rows rather than letting branch-local posture re-enter as current support.

No current lane is promoted to `S4` or `S5`.
No current lane is demoted.
The followthrough queue remains empty until a concrete returning lineage object earns a real `LM` row.

## Release-seal note

Bundle-level reuse of this `OQ-0057` posture is downstream of `docs/40-model/candidate-native-identifiability-release-seal-docket.md`, `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`, `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`, and `docs/40-model/candidate-native-identifiability-head-succession-docket.md`: packages, manifests, receipts, generated mirrors, README / START_HERE summaries, changelog bullets, and context posture are carriers and pointers, not surrogate route evidence, and their identity, owner-chain, cap, mirror, package-boundary, lineage, challenge, rollback, current-head authority, and successor-transition status must verify, adopt, and succeed before reuse as current posture.


## Head-succession handoff

After a carrier verifies and is adopted, a later continuation still needs `docs/40-model/candidate-native-identifiability-head-succession-docket.md` before it replaces the adopted bounded head. A newer timestamp, cleaner package, regenerated mirror, or local edit is only a successor candidate until predecessor identity, lineage relation, owner-row deltas, mirror deltas, validation evidence, residual caps, challenge state, and rollback are replayable.
