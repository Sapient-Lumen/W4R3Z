from pathlib import Path
import shutil
import re

src = Path('/mnt/data/anonsync_rev0087')
dst = Path('/mnt/data/anonsync_rev0088')
if dst.exists():
    shutil.rmtree(dst)
shutil.copytree(src, dst)

rev = 'rev0088'
ts = '2026.03.18.03.18'
codename = 'arrivalexplainabilityharbor'

new_doc = '''# Effective arrival explanation and counterfactual interface spec

The archive already separates announcement from claim, claim from bind, standing approval memory from local claim, placement suggestion from committed bind, and standing seat templates from current share posture.
What still remained too easy to reconstruct from several places at once was the operator question that appears the moment a share arrives or reappears on one machine:

> why is this subject in *this* state on *this* machine right now, what exact standing memory or template influenced it, and what would have happened differently if one of those governing facts were narrower?

This document turns that question into one explicit interface contract.
It is the explanation companion to `58-policy-origin-defaults-and-precedence-spec.md`, the local-arrival companion to `95-announcement-inbox-and-local-claim-separation-spec.md`, the remembered-trust companion to `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md`, and the standing-template companion to `100-standing-arrival-template-and-default-root-review-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a way that is useful for AnonSync design.
`Sync Private Identity & Linking My Devices`, `Sync functionality in detail`, `Folder Types and Management`, `Synchronization Modes`, and `How to manually set the location of the folders synced across linked devices?` together still describe later arrival behavior through a mixture of:

- linked-device automatic visibility of all folders
- prior approval memory and optional future linked-device auto-approval
- pending folders that can auto-connect after prior approval
- per-device synchronization mode (`Disconnected`, `Selective Sync`, `Synced`)
- default folder location / `Simple mode` placement behavior
- later `Connect` ritual for custom placement

That is real convenience.
It is not one operator-facing explanation surface.
The operator still has to reconstruct the answer to `why did this land this way here?` from several docs and several UI areas.

AnonSync should not accept that reconstruction burden.
Every arrived, matched, claimed, or bound subject should therefore expose one explicit explanation object that says:

- what stage this subject is in on this machine
- what standing memory or template influenced that stage
- which facts were merely explanatory versus actually acted upon
- what narrower or broader governing conditions would have changed
- which receipts later prove the local acts that really happened

## Core rule

Every local arrival-worthy subject should have a **why-here explanation**.
That explanation is not merely a log entry or a tooltip.
It is a stable projection over the public model that keeps six things adjacent:

1. current local stage
2. causal chain
3. governing standing state
4. explicit non-causes / untouched facts
5. counterfactual differences
6. next honest verbs

If the operator must jump between inbox rows, approval history, defaults pages, path review, and support text to answer those six questions, the interface is still too magical.

## Public objects

### Arrival explanation

A read object describing why one subject currently appears as announced, matched, claimed, unbound, placed, or bound on one seat.

Suggested fields:

- `arrival_explanation_id`
- `seat_ref`
- `subject_ref`
- `subject_kind` (`incoming-share`, `pending-folder`, `claimed-share`, `bound-share`, `re-entry`)
- `current_local_stage` (`announced`, `matched`, `claim-suggested`, `claimed-unbound`, `placement-reviewed`, `bound`, `hidden-local`, `blocked`)
- `causal_steps[]`
- `governing_refs[]`
- `counterfactuals[]`
- `next_actions[]`
- `receipt_refs[]`
- `computed_at`

### Causal step

One ordered statement in the explanation chain.
Each step should say what kind of fact it is and whether it changed local state or merely explained why lower-friction review was possible.

Suggested fields:

- `ordinal`
- `step_kind` (`announcement`, `approval-match`, `seat-template`, `policy-pin`, `claim`, `placement-suggestion`, `bind`, `materialization`, `manual-hide`, `blocker`)
- `effect_kind` (`explanatory-only`, `admitted-lower-friction`, `drafted`, `committed`, `prevented`, `unchanged`)
- `summary`
- `source_ref`
- `receipt_ref` nullable

### Counterfactual

A stable explanation of what would differ under one narrower or broader governing fact.
This exists so the operator can tell whether a remembered approval, template, or pin actually mattered.

Suggested fields:

- `counterfactual_id`
- `variant_kind` (`no-approval-memory`, `narrower-template`, `different-default-root`, `pinned-away`, `fresh-review-required`, `no-collision`, `seat-changed`)
- `predicted_stage`
- `predicted_next_action`
- `difference_summary`

## Fixed explanation order

Every full explanation surface should preserve the same sections in the same order:

1. **Subject and current stage**
2. **Why it is here now**
3. **Governing standing state**
4. **What did *not* happen**
5. **Counterfactuals**
6. **Next honest actions**
7. **Receipts and proofs**

### 1) Subject and current stage

This section should say:

- which seat we are talking about
- which subject we are talking about
- the current local stage
- whether bytes are announced only, claimed, bound, or materialized

The operator must be able to answer: **what is true right here, before explanation begins?**

### 2) Why it is here now

This section should render the causal chain in ordinary language.
For example:

```text
Announced from linked family scope
Matched prior approval memory for Maya (lower-friction only)
Seat template suggested claim under family-arrivals
No local claim was auto-applied
Suggested placement drafted /tank/family/Photos-2026
Bound path still pending review
```

The operator must be able to answer: **which facts actually caused this state and in what order?**

### 3) Governing standing state

This section should name the standing objects that influenced the current stage:

- approval memory or approval-match object
- seat template / default root
- pins or overrides
- scope and origin

The operator must be able to answer: **which standing policy or remembered trust influenced this subject?**

### 4) What did *not* happen

This section is mandatory.
It should explicitly name easy confusions that are false, for example:

- prior approval memory did **not** itself create a local bind
- seat template did **not** rewrite already bound sibling shares
- placement suggestion did **not** yet commit a path
- current arrival did **not** widen future approval memory

The operator must be able to answer: **what tempting but wrong story should I avoid?**

### 5) Counterfactuals

At least two counterfactuals should be available whenever standing memory or standing template materially influenced the stage.
Typical examples:

- `Without prior approval memory: this subject would be pending fresh review`
- `With announce-only seat template: this subject would remain announced with no claim suggestion`
- `With different default root: the drafted placement candidate would differ, but no bind would yet exist`

The operator must be able to answer: **which governing fact actually mattered, and how much?**

### 6) Next honest actions

This section should offer verbs that match the current stage and explanation truth, such as:

- `Open fresh approval review`
- `Claim here`
- `Open placement review`
- `Keep announced only`
- `Hide on this machine`
- `Inspect governing template`
- `Inspect approval memory`

It must not flatten unlike stages into one generic verb such as `Connect`, `Open`, or `Continue`.

### 7) Receipts and proofs

This section should link to the durable artifacts that prove any actual local act:

- approval receipt or approval-match receipt
- claim receipt
- placement receipt
- bind or policy receipt

A pure explanation with no local mutation may have no new receipt of its own, but it should still say which existing receipts support the chain.

## Row and card contract

A compact row should keep these facts adjacent, in this order:

1. subject
2. current local stage
3. strongest governing explanation
4. strongest non-cause / untouched fact
5. next honest action

Example:

```text
Photos-2026   claim-suggested   matched prior approval + family template   no local bind yet   Explain
```

Opening the row should show a drawer with the fixed explanation order above.

## Dense/mobile rule

Dense and mobile clients may compress the prose, but they must still preserve:

- current local stage
- strongest governing cause
- one explicit non-cause
- one counterfactual entry point
- the next honest verb

A dense client may shorten `Without approval memory this would wait for fresh review` to `No memory => fresh review`, but it may not omit the counterfactual concept entirely.

## CLI contract

Minimal commands:

```text
anonsync arrival explain --subject incoming:photos-2026 --seat home-nas
anonsync arrival explain --subject incoming:photos-2026 --seat home-nas --json
anonsync arrival explain --subject incoming:photos-2026 --seat home-nas --counterfactual no-approval-memory
anonsync arrival trace --subject incoming:photos-2026 --seat home-nas
anonsync arrival receipts --subject incoming:photos-2026 --seat home-nas
```

The plain-text rendering should answer, without cross-referencing other pages:

- why the subject is visible here now
- whether remembered trust merely lowered friction or actually changed local state
- whether standing template only drafted placement or already committed a bind
- what one narrower governing fact would have changed
- which receipt proves any real local mutation

## Design tests

The model is not good enough if any of the following remains true:

- the operator still has to remember which settings page or support article explains why this arrival auto-connected, stayed pending, or drafted a path
- the surface still lets prior approval memory masquerade as a local bind
- the surface still lets a drafted default root masquerade as a committed path
- counterfactuals are unavailable, so the operator cannot tell whether standing memory or standing template actually mattered
- the next action is still a generic `Connect` or `Open` that hides whether the subject is announced, claimed, or bind-ready

## Why this matters

A mature AnonSync surface should let the operator move from `why is this here?` to `which prior trust or template influenced it?` to `what would have been different under a narrower policy?` without leaving the public model.
That is the explanation standard this document locks in.
'''

(dst / 'docs/101-effective-arrival-explanation-and-counterfactual-interface-spec.md').write_text(new_doc)

# README metadata updates
readme = (dst / 'README.md').read_text()
readme = re.sub(r'- Revision: `rev\d+`', f'- Revision: `{rev}`', readme)
readme = re.sub(r'- Timestamp: `[^`]+` \(America/New_York\)', f'- Timestamp: `{ts}` (America/New_York)', readme)
readme = re.sub(r'- Codename: `[^`]+`', f'- Codename: `{codename}`', readme)
readme = re.sub(r'This revision continues directly from `rev0086` and does six things:[\s\S]*?## Current conclusion', '''This revision continues directly from `rev0087` and does six things:

1. Re-checks **Resilio Sync** again, this time around the remaining operator-explanation seam: current docs still spread later-arrival behavior across linked-device universal visibility, remembered approval, optional future linked-device auto-approval, pending-folder auto-connect after prior approval, per-device synchronization mode, default folder location, and later `Connect` ritual for custom placement.
2. Adds a dedicated **effective arrival explanation and counterfactual interface spec** so the archive no longer tolerates `why did this show up here like this?` being answered only by jumping between inbox rows, approval history, template defaults, and placement review.
3. Tightens the **evaluation** so the non-clone case against Resilio gets sharper again: the product has strong mechanics and real convenience, but current docs still make later-arrival causality too reconstructive instead of first-class.
4. Extends the **object model and daemon/API contract** with explicit arrival-explanation, causal-step, and counterfactual resources so clients can render one truthful `why here` surface instead of inferring it from scattered state.
5. Adds an additional **canonical interface flow** showing the core distinction the archive now wants: remembered approval may lower friction and standing template may draft a candidate path, but only later explicit local acts create claim, bind, or materialized bytes.
6. Refreshes the **workbench, pattern language, ADRs, roadmap, open questions, status, source notes, and reading order** so future revisions keep **arrival explainability** central wherever convenience and truthful causality meet.

## Current conclusion''', readme)
# add one bullet under should borrow or conclusion list if present
needle = '- a first-class semantic-runtim'
if needle in readme:
    pass
# append a short note near current conclusion if not already
if 'why this arrival is here now' not in readme:
    readme = readme.replace('We **still should not clone Resilio Sync wholesale**.\n\nWe **should** continue to borrow and reinterpret several of its strongest product ideas:\n', 'We **still should not clone Resilio Sync wholesale**.\n\nThe sharper reason after this revision is: Resilio still has strong mechanics, but current docs still make later-arrival causality too reconstructive. AnonSync should let the operator ask `why is this here now?` and get one causal answer with proofs and counterfactuals.\n\nWe **should** continue to borrow and reinterpret several of its strongest product ideas:\n')
(dst / 'README.md').write_text(readme)

# Status
status = f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0087`, driven by the current request:

- continue researching and tightening the archive without letting it sprawl
- evaluate Resilio Sync further so the non-clone case stays evidence-based rather than rhetorical
- spend more time on interface specs, especially where later-arrival behavior still hides behind convenience state instead of one honest explanation surface
- keep Linux-first, overlay-first, and least-privilege assumptions intact unless the evidence actually breaks them
- preserve the useful parts of Resilio's convenience model without inheriting reconstruction burden around later arrivals
- make sure the archive can answer not only `what happens next?` but also `why is this subject here in this exact stage on this exact machine?`

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- a fairer Resilio comparison that explicitly grants current strengths — maintained Sync v3, 2025 feature polish such as file-download priority and clickable `Can't download file`, strong selective materialization, useful linked-device convenience, remembered approvals, and practical standing defaults — while still naming the sharper reason not to clone its later-arrival explanation story wholesale
- a new **effective arrival explanation and counterfactual interface spec** that defines how one surface should answer `why is this subject here now?`, `which standing memory or template influenced it?`, `what definitely did not happen yet?`, and `what would have been different under narrower conditions?`
- stronger interface and daemon/API requirements so later-arrival causality becomes a first-class read surface instead of something reconstructed from approval pages, template pages, and placement pages separately
- stronger workbench and pattern-language rules so `matched prior approval`, `template suggested only`, `no local bind yet`, and `without memory this would be fresh review` remain visibly different across dense and full surfaces
- an additional canonical flow showing the core causal split the archive now wants: remembered trust and standing template may lower friction or draft candidates, but only later explicit local acts create claim, bind, or byte materialization
- README, roadmap, ADR, open-question, status, and source-note updates so future revisions keep **arrival explainability** central wherever convenience and truthful causality meet

## The main shift

`rev0087` proved that standing future-arrival policy needs its own reviewed governance object.

`rev0088` tightens the operator-truth problem one level further:

> it is not enough to separate announcement, approval memory, standing template, claim, and placement in principle. A serious operator product must also specify how one machine explains the causal chain that produced the subject the operator is staring at right now.

That changes the archive in five specific ways:

- later-arrival explanation is now treated as a first-class read surface, not an emergent property of several good-but-separate objects
- every arrival-worthy subject now needs one `why here` projection that keeps current stage, causes, non-causes, counterfactuals, and next verb adjacent
- remembered approval and standing template are now required to state whether they merely lowered friction or actually changed local state
- `Connect`-style generic verbs are now even less acceptable because the causal contract must say whether the subject is announced, claim-suggested, unbound, or actually bound
- the non-clone case against Resilio gets tighter again: the missing piece is not convenience or selective sync, but the absence of one explicit later-arrival explanation contract

## What still remains unresolved

This revision intentionally still leaves important questions open, including:

- how much arrival-causality detail should appear by default before dense/mobile surfaces become noisy
- when counterfactuals may stay lightweight versus opening a fuller policy-origin or approval-memory sheet
- how much explanation reuse is safe before stale cached `why here` summaries become misleading after later policy mutation
- how broadly the product should highlight `what did not happen` before the surface starts feeling repetitive
- how aggressive reviewed auto-claim may ever become before it starts feeling magical again
- whether currently claimed-but-unbound subjects should ever be eligible for template refresh in v1
- how much remembered scope or role state can be reused before `claim` quietly degenerates back into `Connect`
- how dense/mobile clients should expose `drafted only`, `matched only`, and `bound only` without recreating hidden defaults
- how broad one reviewed mutation grant may be in v1 before explicit authority becomes either too reusable or too noisy
- when long-offline or clock-uncertain peers should be allowed to resume writable participation without first-class re-entry review
- when remote delete or overwrite waves should always force destructive-replay review instead of ordinary sync progress
- how aggressive default compromise freezes should be before the product starts turning suspicion into disruptive magic
- how aggressive the default review queue should be before it becomes noisy

## Files added in this revision

- `docs/101-effective-arrival-explanation-and-counterfactual-interface-spec.md`
- `update_rev0088.py`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/30-interface-spec.md`
- `docs/31-daemon-api-spec.md`
- `docs/32-interface-flows.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/64-critical-open-questions.md`
- `docs/101-effective-arrival-explanation-and-counterfactual-interface-spec.md`
- `docs/sources.md`
'''
(dst / 'docs/00-status.md').write_text(status)

# Evaluation append
p = dst / 'docs/10-resilio-sync-evaluation.md'
text = p.read_text()
if '### 9c) Later-arrival causality still requires reconstruction' not in text:
    insert_after = 'AnonSync should therefore split those facts apart.\nRemembered approval may explain why an arrival skips identity re-vetting or lands in a lower-friction queue, but it should not silently masquerade as `safe to connect here now`.\n'
    addition = '''\n\n### 9c) Later-arrival causality still requires reconstruction\n\nThis is the explanation seam this revision cares about most.\nResilio's current docs still make the operator reconstruct later-arrival causality from several places at once. `Sync Private Identity & Linking My Devices` says linked devices automatically make all folders available and that a remote user can choose to auto-approve all linked devices for future sharing after approving one. `Folder Types and Management` says pending folders can automatically connect if that user approved you before. `Sync functionality in detail` says retained approval means the next shared folder with that person may not need approval. And the linked-device placement docs still route careful custom location through `Disconnected` and later `Connect`, with default-folder behavior and duplicate-index fallback living elsewhere.\n\nThat is good convenience.\nBut it still means the operator question `why is this here in this state on this machine?` is not answered by one first-class explanation surface.\nThe operator still has to reconstruct whether a subject is here because of:\n\n- ambient linked-device announcement\n- remembered approval\n- standing seat template / default root\n- local claim\n- later placement review\n- or some combination of the above\n\nAnonSync should do better.\nThe product should preserve the convenience mechanics while insisting on one causal explanation surface that says, in order, what stage is true now, what standing memory influenced it, what did not happen yet, and what narrower governing fact would have changed.\n'''
    text = text.replace(insert_after, insert_after + addition)
p.write_text(text)

# Interface spec updates
p = dst / 'docs/30-interface-spec.md'
text = p.read_text()
if '31. **Later-arrival causality must be explorable.' not in text:
    text = text.replace('30. **Filesystem fidelity must stay legible after bind.**\n   Portability policy, active pathname/metadata semantics, degraded notification posture, and later drift should remain inspectable as durable mount state rather than dissolving back into one stale preflight warning.\n', '30. **Filesystem fidelity must stay legible after bind.**\n   Portability policy, active pathname/metadata semantics, degraded notification posture, and later drift should remain inspectable as durable mount state rather than dissolving back into one stale preflight warning.\n\n31. **Later-arrival causality must be explorable.**\n   A subject that appears, matches prior trust, drafts a candidate path, or stalls before bind should expose one truthful `why here now` explanation surface with causes, non-causes, counterfactuals, and proof links.\n')
if 'which standing template, approval memory, or placement suggestion influenced this arrival' not in text:
    text = text.replace('- which recovery step rebound this device or share state\n', '- which recovery step rebound this device or share state\n- which standing template, approval memory, or placement suggestion influenced this arrival\n- which tempting story is false because no local claim or bind has happened yet\n')
if '## Arrival explanation contract' not in text:
    text += '''\n\n## Arrival explanation contract\n\nImportant later-arrival subjects should support one explanation projection that keeps the following adjacent:\n\n- current local stage\n- causal chain\n- governing standing state\n- explicit non-causes\n- counterfactual differences\n- next honest verbs\n- supporting receipts\n\nThe operator should be able to move from `why is this subject here?` to `what prior trust or standing template influenced it?` without opening three unrelated pages.\nGeneric verbs such as `Connect` should be considered insufficient wherever the truthful next act depends on whether the subject is merely announced, claim-suggested, unbound, or already bound.\n'''
p.write_text(text)

# API spec append
p = dst / 'docs/31-daemon-api-spec.md'
text = p.read_text()
if '## Arrival explanation additions' not in text:
    text += '''\n\n## Arrival explanation additions\n\n### `arrival_explanation`\n\nA read projection that explains why one subject currently appears in one local stage on one reviewed seat.\n\nSuggested fields:\n\n- `arrival_explanation_id`\n- `seat_ref`\n- `subject_ref`\n- `current_local_stage` — `announced`, `matched`, `claim-suggested`, `claimed-unbound`, `placement-reviewed`, `bound`, `hidden-local`, `blocked`\n- `primary_cause_summary`\n- `causal_steps[]`\n- `governing_refs[]`\n- `non_causes[]`\n- `counterfactuals[]`\n- `next_actions[]`\n- `receipt_refs[]`\n- `computed_at`\n\n### `causal_step`\n\nOrdered explanation step for one arrival explanation.\n\nSuggested fields:\n\n- `ordinal`\n- `step_kind` — `announcement`, `approval-match`, `seat-template`, `policy-pin`, `claim`, `placement-suggestion`, `bind`, `materialization`, `manual-hide`, `blocker`\n- `effect_kind` — `explanatory-only`, `admitted-lower-friction`, `drafted`, `committed`, `prevented`, `unchanged`\n- `summary`\n- `source_ref`\n- `receipt_ref` nullable\n\n### `arrival_counterfactual`\n\nExplains what stage and next action would differ under one narrower or broader governing fact.\n\nSuggested fields:\n\n- `counterfactual_id`\n- `variant_kind` — `no-approval-memory`, `narrower-template`, `different-default-root`, `pinned-away`, `fresh-review-required`, `no-collision`, `seat-changed`\n- `predicted_stage`\n- `predicted_next_action`\n- `difference_summary`\n\n### Routes\n\n```text\nGET  /v1/seats/{seat_id}/arrivals/{subject_ref}/explanation\nGET  /v1/arrival-explanations/{arrival_explanation_id}\nGET  /v1/arrival-explanations/{arrival_explanation_id}/trace\nGET  /v1/arrival-explanations/{arrival_explanation_id}/counterfactuals\nGET  /v1/arrival-explanations/{arrival_explanation_id}/receipts\n```\n\n### Required answers\n\nThe explanation endpoints should be able to answer at least:\n\n- why the subject is visible on this seat now\n- whether remembered approval or standing template merely lowered friction or actually changed local state\n- whether a drafted candidate path exists without a committed bind\n- what one narrower governing fact would have changed\n- which receipts prove the real local acts that have happened so far\n\n### Events\n\n- `arrival.explanation_viewed`\n- `arrival.explanation_recomputed`\n- `arrival.counterfactual_requested`\n```\n'''
    # fix accidental trailing code fence by replacing final ``` with nothing? Actually included. Let's clean after.
    text = text.replace('### Events\n\n- `arrival.explanation_viewed`\n- `arrival.explanation_recomputed`\n- `arrival.counterfactual_requested`\n```\n', '### Events\n\n- `arrival.explanation_viewed`\n- `arrival.explanation_recomputed`\n- `arrival.counterfactual_requested`\n')
p.write_text(text)

# Flows append
p = dst / 'docs/32-interface-flows.md'
text = p.read_text()
if '## Flow 147 — explain why this arrival is here now' not in text:
    text += '''\n\n## Flow 147 — explain why this arrival is here now\n\n### Situation\n\n- `Home-NAS` is linked in a personal constellation\n- Maya previously approved one device and chose to allow future sharing across linked devices\n- `Home-NAS` has standing template `family-arrivals` with admission `claim-suggested` and path template `/tank/family/{{share_name}}`\n- a new subject `Photos-2026` appears on `Home-NAS`\n- the operator sees that the row is already `claim-suggested` and wants to know whether anything local already happened or whether the product is only explaining lower friction\n\n### Workbench path\n\n1. The arrival row shows:\n\n```text\nPhotos-2026   claim-suggested   matched prior approval + family template   no local bind yet   Explain\n```\n\n2. Opening `Explain` renders the fixed explanation order from `101-effective-arrival-explanation-and-counterfactual-interface-spec.md`:\n\n   - subject and current stage\n   - why it is here now\n   - governing standing state\n   - what did not happen\n   - counterfactuals\n   - next honest actions\n   - receipts and proofs\n\n3. The causal chain says, in order:\n\n   - subject was announced from linked family scope\n   - prior approval memory matched Maya's identity and allowed lower-friction handling\n   - standing template for `family-arrivals` suggested claim and drafted `/tank/family/Photos-2026`\n   - no local claim was auto-applied\n   - no local bind exists yet\n   - no bytes were materialized\n\n4. The `what did not happen` section explicitly says:\n\n   - remembered approval did not itself create a local bind\n   - the standing template did not widen future approval memory\n   - the drafted path is not yet a committed path\n   - already bound sibling shares remain unchanged\n\n5. Counterfactuals show:\n\n   - without remembered approval: `pending fresh review`\n   - with announce-only template: `announced only` and no drafted candidate path\n\n6. Honest next verbs are:\n\n   - `Claim here`\n   - `Open placement review`\n   - `Keep announced only`\n   - `Inspect approval memory`\n   - `Inspect seat template`\n\n### CLI sketch\n\n```text\nanonsync arrival explain --subject incoming:photos-2026 --seat home-nas\nanonsync arrival explain --subject incoming:photos-2026 --seat home-nas --counterfactual no-approval-memory\nanonsync arrival receipts --subject incoming:photos-2026 --seat home-nas\n```\n\n### Why this matters\n\nA weaker product shape would have left the operator inferring, from scattered state, whether `Photos-2026` is here because the product already connected it, because a linked-device default fired, or because a prior approval simply lowered friction.\nThis flow proves the archive wants a stricter contract: one explanation surface, explicit non-causes, and explicit counterfactuals before any further local act.\n'''
p.write_text(text)

# Workbench append
p = dst / 'docs/38-operator-workbench-interface-spec.md'
text = p.read_text()
if '## Arrival explanation drawer' not in text:
    text += '''\n\n## Arrival explanation drawer\n\nThe workbench should expose a first-class `Explain` drawer for incoming, matched, claimed-unbound, and newly bound subjects.\nThis drawer exists so the operator does not have to reconstruct later-arrival causality from inbox state, approval history, template settings, and placement review separately.\n\n### Required compact-row columns\n\n- subject\n- current local stage\n- strongest governing explanation\n- strongest explicit non-cause\n- next honest action\n\nExample:\n\n```text\nPhotos-2026   claim-suggested   matched prior approval + family template   no local bind yet   Explain\n```\n\n### Drawer rule\n\nOpening the row should preserve the fixed explanation order from `101-effective-arrival-explanation-and-counterfactual-interface-spec.md`:\n\n1. subject and current stage\n2. why it is here now\n3. governing standing state\n4. what did not happen\n5. counterfactuals\n6. next honest actions\n7. receipts and proofs\n\n### Compactness rule\n\nDense surfaces may compress prose, but they must still preserve one explicit non-cause and one counterfactual entry point.\nThe workbench should never force the operator to leave the row just to learn that prior approval lowered friction but did not yet create a bind.\n'''
p.write_text(text)

# Pattern language append
p = dst / 'docs/39-interface-pattern-language.md'
text = p.read_text()
if '## Pattern 47 — every arrival-worthy subject deserves one why-here explanation' not in text:
    text += '''\n\n## Pattern 47 — every arrival-worthy subject deserves one why-here explanation\n\nA subject that arrived through linked visibility, remembered approval, standing template, or later placement suggestion should expose one compact explanation surface.\nThat surface should keep these adjacent:\n\n1. current stage\n2. strongest cause\n3. strongest non-cause\n4. one counterfactual\n5. next honest verb\n\nGood compression:\n\n```text\nPhotos-2026   claim-suggested   matched prior approval + family template   no local bind yet   Explain\n```\n\nBad compression:\n\n```text\nPhotos-2026   Connected   Open\n```\n\nThe bad form hides whether the subject is merely announced, lightly admitted, claimed, or bound.\nA mature operator surface should not make the user learn that difference from support prose.\n\n## Pattern 47a — every explanation needs at least one explicit non-cause\n\nWhenever a standing memory or default influenced a subject, the surface should say not only what *did* happen, but one important thing that *did not* happen.\nExamples:\n\n- `approval memory matched, but no local bind exists yet`\n- `template drafted a path, but no claim was auto-applied`\n- `placement suggestion exists, but sibling bound shares were untouched`\n\nWithout an explicit non-cause, convenience surfaces drift back toward magical interpretation.\n\n## Pattern 47b — counterfactuals are part of trustworthiness, not optional garnish\n\nA useful explanation surface should let the operator see one narrower or broader governing case and how the stage would differ.\nExamples:\n\n- `No remembered approval => fresh review required`\n- `Announce-only template => no claim suggestion`\n\nThis matters because operators do not merely need chronology; they need help judging which governing fact actually mattered.\n'''
p.write_text(text)

# ADR append
p = dst / 'docs/40-architecture-decisions.md'
text = p.read_text()
if '## ADR-101 — later-arrival convenience must compile to one explicit explanation surface' not in text:
    text += '''\n\n## ADR-101 — later-arrival convenience must compile to one explicit explanation surface\n\n### Status\nAccepted\n\n### Context\n\nThe archive now separates announcement, approval memory, standing seat templates, claim, placement, and bind.\nWhat still remained too easy to hide was the operator question that comes after those decisions already exist: why is this subject in this stage on this machine right now?\nCurrent Resilio docs still answer that question only indirectly through linked-device visibility, remembered approvals, pending-folder auto-connect behavior, standing modes, default roots, and later `Connect` ritual.\n\n### Decision\n\nAnonSync will require one first-class arrival-explanation surface for later-arrival subjects.\nThat surface must render current stage, causal chain, governing standing state, explicit non-causes, counterfactuals, next honest verbs, and proof links in one place.\nRemembered approval and standing template may explain lower friction or drafted candidates, but they must explicitly say whether they changed local state or merely influenced review posture.\n\n### Consequences\n\nPositive:\n\n- later-arrival convenience becomes auditable rather than magical\n- support burden falls because `why here now` has one public answer surface\n- richer and denser clients can share one explanation contract without inventing new semantics\n\nNegative:\n\n- the model adds one more read projection family and counterfactual machinery\n- some compact surfaces will need to spend space on non-causes and counterfactual entry points\n- implementers have to keep explanation recomputation aligned with the underlying state graph so stale summaries do not mislead\n'''
p.write_text(text)

# Roadmap append
p = dst / 'docs/50-roadmap.md'
text = p.read_text()
if '- arrival-explanation and counterfactual surfaces' not in text:
    text = text.replace('Deliver:\n\n- encrypted-replica permission\n', 'Deliver:\n\n- arrival-explanation and counterfactual surfaces for incoming/matched/claimed/bound subjects\n- encrypted-replica permission\n')
    text = text.replace('Exit criteria:\n\n- “store on untrusted node, recover from trusted node” works cleanly\n', 'Exit criteria:\n\n- operators can ask `why is this share here now?` and get one truthful causal answer without state archaeology\n- “store on untrusted node, recover from trusted node” works cleanly\n')
p.write_text(text)

# Open questions append
p = dst / 'docs/64-critical-open-questions.md'
text = p.read_text()
if '## 64) How much arrival-causality detail should be visible by default before explanation surfaces become either noisy or too magical?' not in text:
    text += '''\n\n## 64) How much arrival-causality detail should be visible by default before explanation surfaces become either noisy or too magical?\n\nThe archive is now clearer that later-arrival subjects need first-class explanation surfaces with causes, non-causes, counterfactuals, and proofs, but one policy seam remains open:\n\n- how many causal steps should render by default before the drawer becomes a miniature audit log instead of a working explanation\n- when should counterfactuals stay lightweight versus opening the fuller policy-origin or approval-memory sheet\n- how aggressively should the product highlight `what did not happen` before expert users start treating it as repetitive chrome\n- how much explanation caching is acceptable before policy mutation or later local acts require recomputation\n\nThis matters because weak defaults recreate exactly the state-archeology problem the archive is trying to escape, while overly exhaustive defaults could turn every simple arrival card into a wall of provenance.\n'''
p.write_text(text)

# Sources note update
p = dst / 'docs/sources.md'
text = p.read_text()
text = re.sub(r'# Source notes for rev\d+', '# Source notes for rev0088', text, count=1)
intro = 'This revision leaned especially on the same current official Resilio sources already listed below, but with fresh attention on the later-arrival explanation seam: linked-device universal visibility, remembered approval, pending-folder auto-connect after prior approval, standing synchronization modes, default roots, Android `Simple mode`, and later `Connect` ritual still answer `why is this here now?` only in pieces.\n\n'
text = re.sub(r'This revision leaned especially on[\s\S]*?# Sources\n', intro + '# Sources\n', text, count=1)
p.write_text(text)

# Update docs with metadata or append status maybe enough
# zip
(dst / 'update_rev0088.py').write_text(Path('/mnt/data/update_rev0088.py').read_text())
