# Candidate-native identifiability reimport firewall

This document is the echo-control surface for candidate-native identifiability updates under `OQ-0057`.
It does **not** add a ninth identifiability field, replace the export-claim docket, create a citation policy for the whole archive, promote any lane, or demote any lane by itself.
It answers the next operational question after export hygiene:

> when an export-safe summary, release note, restart card, abstract, user answer, generated index line, or external paraphrase later returns to the archive, how does the archive prevent that derivative wording from being counted as new route evidence or independent support?

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
- `docs/40-model/cross-family-candidate-native-identifiability-audit.md`
- `docs/40-model/family-c-identifiability-stack.md`
- `docs/40-model/completion-bid-credit-stack.md`
- `docs/40-model/witness-package-burden-router.md`
- `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md`
- `docs/40-model/candidate-native-identifiability-release-seal-docket.md`
- `docs/40-model/candidate-native-identifiability-seal-verification-docket.md`
- `docs/40-model/candidate-native-identifiability-head-adoption-docket.md`

## Compression verdict

The export-claim docket makes a compact claim safe to leave its owning row.
That still leaves a separate reimport path:

- a release note can be cited later as if the release itself proved a route-state change;
- a user-facing answer can become a convenient but lossy source for a future claim-registry entry;
- a generated index or restart mirror can be treated as the canonical owner instead of a pointer to owners;
- an abstract can be quoted back into the archive as independent confirmation of the archive's own posture;
- an external paraphrase can preserve the exciting words and drop the caps, then return as apparent outside support;
- a future model-generated summary can cite an earlier summary rather than the route ledger, docket chain, and owner row;
- a polished `X7` export can be mistaken for new evidence even though it was only a bounded description of prior evidence.

The correct posture is:

**exported wording is a pointer, not an evidence source. Any derivative summary that re-enters `OQ-0057` must be reanchored to canonical owner rows, split from any genuinely new external content, and barred from increasing route, readiness, publicness, calibration, or witness credit merely by being repeated.**

This firewall is downstream of the export-claim docket.
The export docket asks whether the compact wording may leave.
The reimport firewall asks whether later uses of that compact wording are allowed to support a new update.

Use it when:
- a release note, receipt, changelog, README line, START_HERE capsule, context-pack posture, generated index line, user answer, abstract, talk slide, email, manuscript paragraph, or external paraphrase is cited in a later `OQ-0057` update;
- a future evidence-intake row cites an archive summary instead of a paper, dataset, proof, route ledger, lifecycle docket, or canonical owner row;
- an outside response to the archive mixes a paraphrase of archive posture with genuinely new criticism, data, proof, or replication;
- a derivative summary is proposed as support for a promotion, demotion, challenge closure, publicness claim, calibration anchor, residual cap, or exported comparison;
- a broad mirror wants to reuse a compact phrase because it is memorable, not because its owner row still supports it.

Do not use it for ordinary outbound summaries that are not later used as support.
Those stay under the export-claim docket.

## Reimport states

These codes are not route scores, field states, evidence states, decay states, propagation states, adjudication states, trace states, replay states, challenge states, closure states, adversarial-control states, calibration states, residual-cap states, or export states.
They say whether a derivative summary may re-enter as support.

| Code | Reimport state | Meaning | Required archive action | Blocked overclaim |
|---|---|---|---|---|
| `RI0` | no reimport | The exported wording is not being used as later support. | Leave this firewall unused. | Auditing every outbound sentence twice. |
| `RI1` | summary-as-source | A derivative summary is cited as if it were the owning route evidence. | Replace it with the canonical owner row or downgrade to unresolved posture. | Treating a release note as proof of a field update. |
| `RI2` | self-citation loop | The support chain cycles through archive exports, restart mirrors, user answers, or generated indexes without reaching primary rows. | Break the loop and restart from evidence intake / owner surfaces. | Making repetition look like corroboration. |
| `RI3` | cap-losing paraphrase | The reimported wording drops bounded, conditional, witness-separated, borrowed-public, weaker-control, or no-closure qualifiers. | Restore the cap or mark the import unusable for posture. | Letting a paraphrase upgrade a bounded row. |
| `RI4` | stale-export reentry | The export predates later decay, challenge, control damage, calibration failure, cap repair, or route retagging. | Rerun lifecycle checks before reuse; stale wording cannot update posture. | Importing an old safe sentence after it stopped being safe. |
| `RI5` | external-echo amplification | An outside text repeats archive posture without new independent evidence but is treated as external support. | Count it as echo only; split off any genuinely new claims for evidence intake. | Turning archive publicity into independent confirmation. |
| `RI6` | mixed new-content split | The returning artifact contains both archive paraphrase and new data, proof, criticism, replication, or challenge. | Split the artifact: echo content gets no credit; new content enters the appropriate docket. | Letting new-content presence launder inherited summary wording. |
| `RI7` | reanchored derivative reuse | The derivative wording is used only as a navigational handle and points back to source owner rows, caps, lifecycle states, and rollback handles. | Reuse is allowed as a pointer, not as route evidence. | Forbidding readable handoffs when they remain owner-anchored. |
| `RI8` | reimport failure / freeze | The derivative claim cannot be reanchored, is stale, conflicts with owner rows, or would change posture by echo. | Freeze, roll back, or replace with canonical unresolved wording. | Allowing citation loops to create `S4`/`S5` pressure. |

## Mandatory reimport row

Fill this row whenever exported or derivative `OQ-0057` wording is later used as support, citation, or update input.
For `RI0`, a one-line no-reimport note is enough.

| Field | Required answer |
|---|---|
| Reimport id | A release-scoped or local id sufficient to find this reimport later. |
| Returning artifact | Release note, receipt, README, START_HERE, context-pack, generated index, user answer, abstract, slide, email, manuscript, outside article, or other derivative surface. |
| Proposed use | Navigation pointer, source support, evidence intake, challenge, promotion attempt, calibration anchor, residual-cap transfer, export repair, or broad mirror wording. |
| Claimed support | What the artifact is being asked to support. |
| Original export state | Which `X` state, source row, and rollback handle authorized the earlier export, if any. |
| Canonical owner row | The route-ledger, readiness, lifecycle, control, calibration, residual-cap, export, claim-registry, or open-question row that actually owns the claim. |
| Primary evidence path | The paper, dataset, proof, record object, protocol, docket chain, or owner surface reached after removing derivative wording. |
| Cap preservation check | Whether bounded label, owner boundary, comparison denominator, public / witness condition, and no-closure sentence survived. |
| Freshness check | Whether supersession, decay, challenge, closure, control, calibration, residual-cap, or export state changed after the derivative wording was written. |
| Echo / new-content split | Which parts are mere paraphrase and which, if any, are new evidence or challenge content. |
| Allowed credit | Navigation only, field-local evidence, challenge input, lifecycle repair, no posture credit, or freeze. |
| Reimport state | Which `RI` state applies? |
| Repair / rollback handle | Where a future reader can break the loop, reconstruct the source, or retire the derivative wording. |

## Firewall rules

### 1. Exported summaries are not primary evidence

A valid `X7` export is a safe statement about prior credit.
It is not itself a new route artifact, new public carrier, new challenge closure, new adversarial control, new calibration anchor, or new residual cap.
Any later update must follow the export back to the owning route row or primary evidence path.

Default failure: `RI1`.
Default repair: replace the summary citation with the owner row and rerun the relevant docket only if the owner row changed.

### 2. Generated mirrors are pointers, not owners

`START_HERE.md`, `context-pack.json`, `ARCHIVE_INDEX.generated.md`, release receipts, and user-facing summaries can be excellent restart handles.
They are not canonical scientific owners for candidate-native identifiability posture.
A future edit may cite them to find the right surface, but it must not spend them as evidence.

Default failure: `RI2`.
Default repair: trace to `OQ-0057`, the claim registry, and the specific route / lifecycle / control / calibration / cap / export row.

### 3. External echo does not become independent support

If an outside text repeats the archive's own bounded wording, that repetition is not an independent replication, public witness, public reference standard, or candidate-native record.
It can be cited as reception history only.
If the outside text also adds a new proof, dataset, contradiction, replication, or challenge, split the new content and run evidence intake or challenge response on that part alone.

Default failure: `RI5`.
Default repair: mark the paraphrase as echo and route the new claim through `E`, `Q`, `Z`, or witness-package surfaces.

### 4. Paraphrase cannot improve a cap

A derivative phrase may preserve or weaken a route state.
It may not strengthen one.
If `bounded package-grain S3` returns as `S3`, `near S4`, `publicly identified`, `adversarially controlled`, or `candidate-native closure`, the reimport is unsafe even if the original export was safe.

Default failure: `RI3`.
Default repair: restore the full bounded label or discard the derivative phrasing.

### 5. Stale exports are lower-trust than current owners

An export that was safe in one revision may become unsafe after supersession, decay, replay failure, challenge, closure change, adversarial-control damage, calibration repair, residual-cap change, or export rollback.
Later imports must prefer current owner rows over older summary prose.

Default failure: `RI4`.
Default repair: rerun freshness checks and use the current owner row, not the old export.

### 6. Reimport cannot create promotion pressure by accumulation

Many echoes of one bounded claim still count as one bounded claim.
A stack of release notes, summaries, generated indexes, talks, or external paraphrases cannot raise readiness, publicness, calibration, or promotion pressure unless at least one artifact supplies new non-echo route content.

Default failure: `RI2` or `RI5`.
Default repair: dedupe echoes and count only the primary owner row.

### 7. Safe reimport is navigational

A derivative phrase can be reused safely when it is explicitly navigational: it points the reader to the current canonical owner, preserves the cap, says whether there is new content, and refuses posture credit for the derivative wording itself.
This is `RI7`.

## Current reimport posture

Current safe reimports for `OQ-0057` are intentionally narrow:

| Returning artifact | Allowed use | Unsafe use |
|---|---|---|
| Release slug or receipt | Find the added docket and upstream bundle. | Count the release as evidence that identifiability improved. |
| README / START_HERE capsule | Navigate to `OQ-0057`, `CL-0147`, and the route stack. | Cite the capsule as the owner of route state. |
| Generated index | Locate a file. | Treat filesystem presence as route evidence. |
| User-facing answer | Handoff summary only if it preserves source row and cap. | Use the answer as a new archive source. |
| Abstract or talk title | Public pointer to the current bounded posture. | Treat public repetition as public witness closure. |
| External paraphrase | Reception / echo unless it adds new evidence. | Treat outside repetition as independent confirmation. |

## Reimport-safe answer template

When a future update wants to rely on an earlier summary, use this shape unless a concrete owner row says otherwise:

> The earlier summary is a pointer, not evidence. Reopen the canonical owner row, check whether its bounded label, public / witness condition, lifecycle state, calibration, residual cap, and export state still hold, split any genuinely new content from echoed wording, and then run the appropriate intake or challenge docket. Repetition of the same summary does not promote any lane.

## Interaction with export hygiene

A valid outbound claim normally needs `X7` from `docs/40-model/candidate-native-identifiability-export-claim-docket.md`.
A later inbound use normally needs `RI7` from this firewall.
Those are different approvals:

1. `X7` means the wording may leave without overclaim.
2. `RI7` means the returning wording may be used as a pointer without becoming evidence.

If an exported summary returns without a source owner, cap, freshness check, and echo / new-content split, it is `RI1`–`RI5` or `RI8`, not support.


## Lineage-merge handoff

If the returning object is not only a derivative sentence but an older release, forked bundle, cherry-picked markdown surface, generated archive artifact, or externally edited archive tree, this firewall is not enough.
First classify the derivative wording here, then use `docs/40-model/candidate-native-identifiability-lineage-merge-docket.md` to identify the branch relation, rebase touched owner rows through the current docket stack, split stale branch posture from genuinely new content, and preserve the most restrictive surviving cap before any current posture changes.

## Net result

This firewall prevents the archive's own successful compression from becoming the next evidence-inflation channel.
It keeps release notes, restart mirrors, user-facing capsules, abstracts, and external echoes downstream of canonical owner rows rather than letting them re-enter as independent support.

No current lane is promoted to `S4` or `S5`.
No current lane is demoted.
The followthrough queue remains empty until a concrete returning artifact earns a real `RI` row.
