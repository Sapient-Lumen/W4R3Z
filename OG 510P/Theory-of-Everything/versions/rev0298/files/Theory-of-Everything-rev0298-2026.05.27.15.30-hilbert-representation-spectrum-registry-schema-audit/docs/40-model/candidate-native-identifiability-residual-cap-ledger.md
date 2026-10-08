# Candidate-native identifiability residual-cap ledger

This document is the residual-cap preservation surface for candidate-native identifiability updates under `OQ-0057`.
It does **not** add a ninth identifiability field, replace calibration anchors, rerun adversarial controls, promote any lane, demote any lane by itself, or convert bounded route credit into witness-package closure.
It answers the next operational question after a route score has been calibrated:

> once a score has been normalized as bounded, conditional, package-grain, mixed-record, weaker-control, borrowed-public, or witness-separated, how does the archive prevent that residual cap from disappearing when the score is reused in broad mirrors, live-family readouts, release notes, or later comparison rows?

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
- `docs/40-model/candidate-native-identifiability-export-claim-docket.md`
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`

## Compression verdict

The calibration-anchor docket prevents unlike `S` labels from being compared under hidden denominator changes.
That still leaves a second inflation path: **residual-cap evaporation**.

A score can be honestly calibrated and still be misused later if its cap is dropped:

- `bounded package-grain S3` becomes simply `S3`;
- `record-denominator mixed / borrowed-public` becomes `record-bearing`;
- `named discriminator-class S3` becomes `candidate-native identifiability progress`;
- `conditional public bridge` becomes `public bridge`;
- `weaker-control pass` becomes `adversarial-control pass`;
- `witness-separated support` becomes identifiability support;
- `non-comparable row` becomes a ranked row in a broad mirror;
- `no live lane reaches S4` becomes `one lane is close to S4` because the remaining blocker is no longer carried.

The correct posture is:

**every calibrated route label that is reused outside its owning row must carry its residual cap, owner boundary, and earliest remaining blocker; if the cap cannot be preserved, the reuse must freeze, split, retag, or downgrade to non-comparable prose.**

This ledger is deliberately downstream of calibration.
Calibration asks whether a score has the right anchors.
The residual-cap ledger asks whether those anchors and blockers survive when the score is copied into another surface.

Use it when:
- a calibrated `S2`, bounded `S3`, candidate-`S4`, `S4`, or `S5` label is reused in a router, registry, README, trajectory map, workstream, receipt, or release status;
- a readiness row, promotion row, adversarial-control row, challenge-closure row, or comparison row moves from its local table into broad posture prose;
- a summary says a lane is strongest, closer, more public, more record-bearing, more stable, better controlled, or more ready than another lane;
- a bounded score is reused without its target grain, record denominator, route width, control difficulty, publicness condition, witness-owner boundary, or first remaining blocker;
- a later edit wants to shorten a label for readability but the omitted qualifier changes posture.

Do not use it for local prose edits that do not reuse route-state, readiness, calibration, promotion, public-bridge, or witness-handoff credit.

## Residual-cap states

These codes are not route scores, calibration states, evidence-intake states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, or promotion states.
They say whether a calibrated label has preserved its remaining cap when it is reused.

| Code | Residual-cap state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `RC0` | no cap transfer needed | The edit does not reuse a calibrated score, readiness state, public-bridge condition, control pass, or witness-handoff credit outside its owning row. | Leave the cap ledger unchanged. | Turning every wording repair into a cap exercise. |
| `RC1` | cap missing | A calibrated or bounded label is reused without its residual cap, owner boundary, or first remaining blocker. | Freeze the reuse or restore the full cap before broad posture changes. | Letting `bounded S3` become plain `S3`. |
| `RC2` | cap owner mismatch | The cap belongs to witness-package, lab, simulation, local-law, cosmological-package, or source-quality credit, but the reuse spends it as identifiability credit. | Retag the owner and preserve the identifiability cap. | Letting non-identifiability credit pay identifiability debt. |
| `RC3` | cap narrowed but not mirrored | The owning row narrowed a score, but a mirror, router, registry, or release note still carries the older wider label. | Repair mirrors or open conflict / replay review if the older label cannot be justified. | Keeping stale broad posture after local narrowing. |
| `RC4` | cap split required | One score now carries multiple target grains, record denominators, publicness conditions, or control regimes that cannot share one cap. | Split the label into separate capped rows before reuse. | Hiding heterogeneous denominators inside one familiar label. |
| `RC5` | cap weakened by challenge or control | A challenge closure, adversarial control, or calibration failure weakened the cap, but the reuse still quotes the stronger prior cap. | Carry the weaker cap or freeze reuse pending replay / challenge closure. | Spending pre-challenge credit after damage. |
| `RC6` | cap borrowed from public / witness infrastructure | Public custody, independence, replay, objectivity, or witness-package support is being reused as if it were a native route cap. | Witness-separate and label the public / witness condition. | Treating borrowed publicness as native identifiability closure. |
| `RC7` | cap-preserved bounded reuse | The score is reused with target grain, record denominator, route width, control difficulty, publicness condition, owner boundary, and earliest blocker intact. | Reuse is allowed only with the cap preserved in the consuming surface. | Forgetting why the score was bounded. |
| `RC8` | cap failure / posture freeze | The cap cannot be replayed, conflicts across mirrors, or changes the meaning of the reused score. | Freeze broad posture, split / retag rows, or roll back the consuming mirror. | Letting unreplayable or contradictory caps carry current-state language. |

## Mandatory residual-cap row

Fill this row whenever calibrated route credit is reused outside its owning row.
For `RC0`, a one-line no-transfer note is enough.

| Field | Required answer |
|---|---|
| Cap id | A release-scoped or local id sufficient to find this cap later. |
| Source row | Which route-ledger, readiness, promotion, adversarial-control, calibration, challenge-closure, or decision-trace row supplies the score? |
| Consuming surface | Which router, registry, README line, trajectory line, workstream, receipt, release status, or broad mirror will reuse it? |
| Reused label | What score or posture phrase is being reused? |
| Full bounded label | What is the exact capped label that must travel with the reuse? |
| Target grain cap | Full theory, bounded package, named discriminator class, formal corridor, lab contrast, observer frame, cosmological proposal class, or other grain. |
| Record denominator cap | Formal, simulated, boundary, lab, public custody, independent implementation, candidate-native, witness-package, or mixed / borrowed record class. |
| Route-width cap | One example, one benchmark ecology, one regime, one package, one quotient class, one family, or generic target class. |
| Control cap | Which hostile controls were passed, weakened, failed, not run, or only conditionally run. |
| Publicness cap | Internal, published, hosted, custody-preserved, independently replayable, challenge-closed, reconditioned, or witness-dependent. |
| Owner boundary | Which part belongs to candidate-native identifiability and which part belongs elsewhere. |
| Earliest remaining blocker | The first route field, public-bridge condition, calibration mismatch, adversarial-control gap, or witness-package debt that still prevents stronger credit. |
| Consuming wording | The exact wording allowed in the consuming surface. |
| Residual-cap state | Which `RC` state applies? |
| Replay / rollback handle | Where a later reader can reconstruct the cap and when the consuming wording must be rolled back. |

## Cap-carrier rules

### 1. Bounded labels must travel whole

A calibrated score is not just the letter / number state.
It is the state plus its target grain, record denominator, route width, control difficulty, publicness condition, owner boundary, and first remaining blocker.
If the consuming surface cannot carry all of that, it must either stay local or use a deliberately weaker phrase such as `bounded partial row`, `named discriminator-class pocket`, or `non-comparable support`.

Default failure: `RC1`.
Default repair: restore the full bounded label or remove the broad posture claim.

### 2. First remaining blocker is mandatory

A residual cap is not merely a disclaimer.
It names the earliest blocker that still prevents stronger credit.
For candidate-native identifiability, the most common blockers are target-grain mismatch, record-denominator mismatch, borrowed public bridge, incomplete hostile controls, non-native same/different rule, unstable inverse margin, no abstention owner, or witness-package debt.

Default failure: `RC1` or `RC3`.
Default repair: carry the first blocker into the consuming surface.

### 3. Cap splits beat compressed prose

If a lane has one genuine lab-record `S3` pocket, one formal target-rich `S2` corridor, and one public-bridge weak point, do not compress them into one average lane label.
Split the caps.
A single compressed label is allowed only when all reused support shares the same target grain, record denominator, control difficulty, publicness condition, and owner boundary.

Default failure: `RC4`.
Default repair: split the row before reuse.

### 4. Damaged caps propagate downward

If challenge closure, adversarial control, calibration, replay, or conflict review weakens a cap, the weaker cap must replace the older label in every consuming surface that still spends that score.
A broad mirror may not keep the old positive label because the underlying clue remains interesting.

Default failure: `RC5`.
Default repair: replay / rollback the consuming surfaces and carry the weaker cap.

### 5. Public and witness caps do not become native caps

Public custody, independence, replay, objectivity, challenge closure, and witness-package support can improve the archive's evidential posture.
They do not by themselves erase candidate-native identifiability caps.
When those supports are imported, the consuming label must say whether publicness is native, borrowed, conditioned, or witness-separated.

Default failure: `RC6`.
Default repair: witness-separate and preserve the identifiability cap.

### 6. Readability is not a reason to erase caps

Broad mirrors can be compact, but compactness cannot change posture.
If the full cap is too long for a restart line, use a short capped phrase and point to the owner row.
Do not shorten by deleting the cap.

Default failure: `RC1` or `RC8`.
Default repair: use a stable short label that is defined in the owner surface.

## Current live-lane residual caps

### Family C

Family C may be reused as the strongest current partial route only with the cap:
**bounded package-grain `S3`; mixed boundary / dictionary / simulator / code-subspace / public-replay denominator; hostile controls incomplete; public bridge conditional; candidate-native identifiability closure unpaid.**
The first remaining blocker is still generic candidate-native same/different and public-bridge ownership rather than another reconstruction benchmark.

### Completion bids

Completion bids may be reused as target-rich `S1`/`S2` support only with the cap:
**formal / corridor / completion-bid target-grain credit; acquired public record denominator absent unless a specific route supplies it; no generic candidate-native inverse-to-public-record closure.**
The first remaining blocker is usually acquisition plus public record-to-target inversion, not formal richness.

### Laboratory and simulation routes

Lab and simulation routes may be reused as record-richer `S2` support, or named discriminator-class `S3` pockets, only with the cap:
**bounded target quotient or externally chosen contrast; record denominator often stronger than completion bids but candidate-target grain narrower; publicness may be ordinary lab publicness rather than candidate-native bridge.**
The first remaining blocker is usually candidate-target ownership and route-width scope.

### Witness-side frame and observer routes

Witness-side frame routes may be reused as equivalence, transport, public-portability, or witness-discipline support only with the cap:
**access / frame / public-transport discipline below route closure; not candidate-native identifiability unless acquisition, inverse, stability, abstention, and public-bridge fields are also paid for a target quotient.**
The first remaining blocker is owner separation.

### Cosmological proposal classes

Cosmological proposal-class rows may be reused only with the cap:
**burden-accounting, proposal-class, measure / selection / relaxation / local-law split support, not candidate-native identifiability, unless a local record-bearing target quotient is supplied.**
The first remaining blocker is local record-bearing identifiability route, not global explanatory ambition.

## Minimal update policy

- If the result is `RC0`, do not change route posture.
- If the result is `RC1`, restore the cap or freeze the consuming reuse.
- If the result is `RC2`, retag to the correct owner and preserve the identifiability cap.
- If the result is `RC3`, repair mirrors or open replay / conflict review.
- If the result is `RC4`, split the cap before reusing the score.
- If the result is `RC5`, carry the weaker cap or freeze reuse pending challenge / replay closure.
- If the result is `RC6`, witness-separate the borrowed public or witness support.
- If the result is `RC7`, reuse only with the cap intact.
- If the result is `RC8`, freeze broad posture and roll back the consuming mirror until the cap is replayable.

## Current posture

This revision installs a residual-cap ledger for future reuse of calibrated candidate-native identifiability labels.
No concrete residual-cap row is run in this revision.
No live lane is promoted to `S4` or `S5`, no live lane is demoted, and the followthrough queue stays empty until a concrete score reuse, broad mirror, challenge closure, adversarial-control result, or promotion attempt earns a residual-cap row.
The only posture change is procedural: calibrated route labels may not travel into broad mirrors unless their bounded label, owner boundary, and earliest remaining blocker travel with them.

## Reimport firewall handoff

If this surface is later cited through a release note, restart capsule, generated index, user-facing answer, abstract, handoff note, or external paraphrase, that derivative wording is only a pointer. Before it supports `OQ-0057` posture, route state, readiness, calibration, residual-cap transfer, publicness, witness credit, or promotion pressure, use `docs/40-model/candidate-native-identifiability-reimport-firewall.md` to reanchor the claim to canonical owner rows, preserve caps and freshness, and split echo from genuinely new content.

## Lineage-merge handoff

If this surface returns through an older release, fork, cherry-picked document, generated archive artifact, or externally edited bundle, do not merge its route state directly. Use `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md` to identify the source lineage, rebase touched owner rows through the current `OQ-0057` stack, split stale branch posture from genuinely new evidence or challenge content, and preserve the most restrictive surviving cap.

## Release-seal note

Bundle-level reuse of this `OQ-0057` posture is downstream of `docs/40-model/candidate-native-identifiability-release-seal-docket.md`, `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`, `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`, and `docs/40-model/candidate-native-identifiability-head-succession-docket.md`: packages, manifests, receipts, generated mirrors, README / START_HERE summaries, changelog bullets, and context posture are carriers and pointers, not surrogate route evidence, and their identity, owner-chain, cap, mirror, package-boundary, lineage, challenge, rollback, current-head authority, and successor-transition status must verify, adopt, and succeed before reuse as current posture.
