from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / 'docs'

files = {
'1234-resilio-operator-attestation-certainty-override-ignore-proceed-and-destructive-assumption-fragmentation-evaluation.md': r'''# Resilio operator-attestation, certainty-override, ignore/proceed, and destructive-assumption fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- a ghost-file warning can be hidden with `Ignore All`, and the warning itself can be disabled
- the same ghost-file situation may still hide a more up-to-date version on some offline peer
- the documented remediation for that unresolved situation is operator-driven: if you are certain the local version is the most up-to-date, touch the files or move them out and back in
- repairing `Service files missing` requires a stronger operator judgment: before recreating the sync instance, make sure nothing important remains in Archive, then delete `.sync`
- connecting two pre-populated trees is permitted and may merge trees, reuse equal hashes, and let latest-timestamp content replace remote content
- the `Folder not empty` warning can be a genuinely dangerous merge/overwrite situation or a harmless reconnect to the place that already hosted the folder before, and the docs tell the operator to proceed in the reconnect case

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to contribute correctness-critical assertions in several different informal styles:

- **ignore this warning because it is harmless now**
- **I am certain my local copy is the newest one**
- **I checked Archive and there is nothing important left there**
- **this non-empty path is the same previously synced tree, not a dangerous merge target**

Those are not the same assertion.
They have different blast radii, different expiry conditions, and different evidentiary floors.

Current Resilio docs still spread them across troubleshooting prose and action tips instead of one stable contract.
So the operator still has to reconstruct:

1. **what exactly am I asserting on behalf of the product?**
2. **what evidence did I rely on, and what evidence is still missing?**
3. **how destructive is the consequence if I am wrong?**
4. **when does this assertion expire or need to be reopened?**

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow three habits directly:

- **say openly when product truth is incomplete and the operator is being asked to supply judgment**
- **say openly when an action is proceeding on an assumption rather than on machine proof**
- **say openly when a warning dismissal changes visibility only, not world truth**

But AnonSync should reject four weaker habits:

- vague `if you are certain` wording with no structured evidence ledger
- `Ignore` / `Proceed` buttons that do not publish the exact assertion being made
- destructive recovery steps that rely on private human checking with no receipt
- silent expiry of human assumptions after new peers, new scans, or new chronology evidence arrives

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1235` — Operator attestation contract sheet
- `1236` — Local-truth assertion review
- `1237` — Destructive-assumption proof
- `1238` — Attestation expiry timeline
- `1239` — Operator attestation lineage receipt

These pages keep the Resilio candor and reject the casual-assumption contract.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that some sync incidents still require human judgment; refuse any interface contract where `ignore`, `proceed`, `touch`, `reconnect`, or `recreate` quietly depends on unstructured operator certainty rather than one explicit attestation object with evidence basis, blast radius, expiry, and blocked stronger sentence.
''',
'1235-operator-attestation-contract-sheet-page-assertion-class-evidence-basis-blast-radius-and-expiry-interface-spec.md': r'''# Operator attestation contract sheet page: assertion class, evidence basis, blast radius, and expiry interface spec

## Purpose

The archive already has warning pages, repair reviews, chronology proofs, and destructive-action reviews.
What it still lacked was one ordinary page for the narrower question:

> what exactly is the operator asserting here because product proof is incomplete, what evidence supports that assertion, how dangerous is it if wrong, and when does that assertion expire?

Current official Resilio docs make this seam concrete.
They still tell the operator to ignore certain warnings, proceed through non-empty-folder cases, touch files if the local version is believed to be newest, and recreate a sync instance after privately checking Archive.
That is useful truth.
It should not remain informal prose.

## Core decision

AnonSync must expose one first-class **Operator attestation contract sheet** whenever an operator assertion is materially changing what the product is allowed to do or say.

The sheet exists to answer six things in one place:

1. what assertion class is being made
2. what evidence basis supports it
3. which machine proof is still missing
4. what blast radius follows if the assertion is wrong
5. when the attestation expires
6. what stronger sentence remains blocked even if the attestation is accepted

## Fixed page order

1. **Assertion header**
2. **Evidence basis card**
3. **Missing machine proof card**
4. **Blast-radius card**
5. **Expiry and reopen triggers**
6. **Commit rail and blocked stronger sentence**

### 1) Assertion header

Show at minimum:

- `operator_attestation_id`
- actor handle
- assertion class
- scope (`single-file`, `subtree`, `subject`, `repair-rung`, `runtime`, `unknown`)
- strongest safe sentence
- stronger blocked sentence
- attestation freshness

Supported assertion classes must include:

- `warning-is-no-longer-actionable`
- `local-copy-is-newest`
- `non-empty-target-is-intended-same-tree`
- `archive-reviewed-nothing-critical-remains`
- `destructive-recreate-is-acceptable`
- `other-reviewed-human-assertion`

Example safe sentence:

- `Proceeding on operator attestation that this non-empty target is the previously bound tree, not a fresh merge target.`

### 2) Evidence basis card

Show evidence rows grouped by class:

- local observations reviewed
- peer observations reviewed
- archive/history reviewed
- path-lineage reviewed
- chronology reviewed
- file-presence reviewed
- unsupported / private memory only

Each row must show:

- evidence source
- freshness
- corroboration grade
- whether it is machine-observed or human-only
- whether it supports or weakens the attestation

The operator must be able to answer:

> what did I actually look at before asserting this?

### 3) Missing machine proof card

Show which stronger proof is absent, for example:

- no live corroboration from all peers
- no authoritative chronology winner proof
- no complete Archive / history scan proof
- no preserved path-lineage proof
- no byte-equivalence proof across trees
- no runtime witness for safe recreate

The product must say plainly when it is accepting an attestation because world proof is incomplete, not because the stronger proof does not matter.

### 4) Blast-radius card

Separate these consequences explicitly:

- visibility-only change
- warning-suppression change
- chronology reannouncement risk
- overwrite / delete risk
- successor-epoch creation risk
- peer-wide convergence risk
- irreversible residue loss risk

Each row must show worst-case if wrong, expected survivor classes, and whether rollback remains possible.

### 5) Expiry and reopen triggers

Every attestation must publish its expiry basis.
Possible reopen triggers include:

- offline peer returns
- rescan discovers new contradiction
- Archive / history view changes
- path identity no longer matches
- new clock / chronology evidence appears
- subject recreated or rebound
- new operator / seat reopens the same object

The operator must be able to answer:

> when will this attestation stop being trustworthy?

### 6) Commit rail and blocked stronger sentence

Only actions that match the attestation may appear, such as:

- `Accept visibility-only ignore`
- `Proceed with same-tree reconnect`
- `Republish using reviewed local-newest attestation`
- `Commit destructive recreate after archive review`
- `Decline attestation and reopen investigation`
- `Emit attestation receipt`

The rail must also show the strongest forbidden statement, for example:

- `All peers agree this file is gone.`
- `This recreate preserved continuity.`
- `This non-empty target is definitely byte-identical.`
- `No more recent version can still surface.`

## Public object

### Operator attestation contract sheet

Fields:

- `operator_attestation_id`
- `assertion_class`
- `scope_ref`
- `actor_ref`
- `evidence_rows[]`
- `missing_machine_proof_rows[]`
- `blast_radius_rows[]`
- `expiry_rows[]`
- `allowed_actions[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. assertion
2. evidence basis
3. missing proof
4. blast radius
5. expiry basis
6. strongest next action

Example:

```text
local-copy-is-newest     local mtime plus manual file inspection only     no corroboration from offline peer     republish may overwrite later-returning winner     expires if any absent peer returns or chronology evidence changes     Emit attestation receipt before republish
```

## Rules

### Rule 1 — the product must name the human assertion explicitly

Never hide a human-supplied truth inside a generic `Proceed`, `Ignore`, or `Retry` button.

### Rule 2 — visibility change and world change must stay separate

Muting a warning is not the same thing as proving the world condition is gone.

### Rule 3 — destructive attestation must carry expiry and residue duty

A human claim that `nothing important remains` must always publish what was reviewed, what was not reviewed, and what will be irretrievable if wrong.

### Rule 4 — accepting an attestation does not upgrade blocked machine proof

The UI may proceed on a reviewed assertion.
It may not silently upgrade that to universal proof.
''',
'1236-local-truth-assertion-review-page-ghost-warning-reconnect-same-path-and-prepopulated-tree-branches-interface-spec.md': r'''# Local-truth assertion review page: ghost warning, reconnect-same-path, and pre-populated-tree branches

This page exists so three superficially similar buttons stop pretending to mean the same thing:

- `Ignore All` on a no-source / ghost warning
- `OK` on a non-empty destination / pre-populated tree attach
- `Proceed` on a reconnect to a location that already hosted this subject

All three require human judgment.
They do not require the same judgment.

## Operator question

> which local-truth assertion am I being asked to make here, what branch am I choosing, and what exactly happens if my assumption is wrong?

## When this page must appear

Render whenever the operator is about to:

- hide a ghost-file warning without world proof that the file is globally gone
- republish local bytes because they are believed to be newest despite absent peers
- connect a subject to a non-empty tree
- reconnect to a path that might be the same prior tree or might be an accidental merge target
- accept a merge where latest timestamp may replace existing content

## Fixed page order

1. **Branch chooser**
2. **What this branch asserts**
3. **Contradiction risks**
4. **Safer weaker alternative**
5. **Receipt consequence**

## 1) Branch chooser

Offer mutually exclusive branches such as:

- `Hide warning only; do not claim world absence`
- `Local tree is reviewed same-tree reconnect`
- `Local tree is pre-populated merge target`
- `Local bytes are believed newest; republish after attestation`
- `Abort and gather more proof`

The operator must be able to answer: **which branch am I actually choosing?**

## 2) What this branch asserts

For the chosen branch, show:

- assertion class
- reviewed scope
- what evidence was inspected
- what the branch does **not** prove

Examples:

- `Hide warning only` asserts only that warning visibility should change locally; it does not prove that no peer still has newer bytes.
- `Same-tree reconnect` asserts that the non-empty target is the previously bound tree, not an unrelated directory that would create a risky merge.
- `Pre-populated merge target` asserts willingness to let hash comparison, latest timestamp, and tree merge operate on a directory that already has material.
- `Local bytes are believed newest` asserts reviewed local superiority strong enough to justify touch or equivalent republish behavior despite incomplete peer truth.

## 3) Contradiction risks

Show contradiction rows such as:

- offline peer returns with newer content
- current path is similar-looking but not the same prior tree
- pre-existing files in target are overwritten or deleted by merge
- hidden Archive / history evidence contradicts local certainty
- current timestamps are not authoritative enough for the planned branch

Each row must show confidence, blast radius, and whether rollback is still possible.

The operator must be able to answer: **what exact contradiction could prove me wrong?**

## 4) Safer weaker alternative

Always show a weaker path, such as:

- `Keep warning visible and wait for peer return`
- `Inspect path lineage before reconnect`
- `Connect to empty sibling directory instead`
- `Inspect Archive and chronology before republish`
- `Export attestation receipt without commit`

The operator must be able to answer: **what is the least-strong action that still moves me forward?**

## 5) Receipt consequence

On commit, issue a receipt that preserves:

- chosen branch
- human assertion used
- evidence reviewed
- contradiction risks left open
- expiry trigger
- stronger blocked sentence

## Primary actions

Examples:

- `Hide warning only`
- `Proceed as same-tree reconnect`
- `Proceed as risky merge target`
- `Republish via reviewed local-newest attestation`
- `Back out and inspect more proof`

Do not use vague primaries such as `Continue`, `OK`, or `Proceed anyway` without the explicit branch phrase.

## What this page must never imply

It must never imply that these are the same:

- hiding a warning and proving absence
- reconnecting the same prior tree and merging into a fresh occupied tree
- reviewing local bytes and proving universal chronology superiority
- operator willingness to risk overwrite and machine proof that overwrite is correct
''',
'1237-destructive-assumption-proof-page-archive-reviewed-overwrite-risk-and-successor-epoch-commit-interface-spec.md': r'''# Destructive-assumption proof page: archive-reviewed, overwrite-risk, and successor-epoch commit

This page exists so a destructive step based on human review stops looking like an ordinary repair click.
The canonical cases are:

- recreating a subject after `Service files missing`
- deleting hidden continuity state after checking Archive
- accepting overwrite / delete risk on a pre-populated target
- proceeding when the product cannot prove continuity preservation

## Operator question

> if I commit this destructive step on the strength of my own review, what exactly did I review, what survives, what becomes a successor epoch, and what stronger preservation claim remains blocked?

## When this page must appear

Render whenever the operator is about to:

- delete `.sync`-class continuity state or equivalent service capsule
- recreate a subject after checking Archive / history manually
- accept merge semantics that may overwrite existing local material
- commit a repair where preserved continuity is not machine-proved
- approve a successor epoch because the old one is no longer trusted

## Fixed page order

1. **Destructive step summary**
2. **Human review checklist with attested results**
3. **Survivor map**
4. **Successor-epoch verdict**
5. **Proof ceiling after commit**

## 1) Destructive step summary

Show:

- destructive step class (`delete-service-capsule`, `recreate-subject`, `merge-into-occupied-tree`, `overwrite-acceptance`, `other`)
- current reason
- whether the step is reversible
- strongest safe sentence
- stronger blocked sentence

The operator must be able to answer: **what destructive boundary am I crossing?**

## 2) Human review checklist with attested results

Require explicit reviewed answers for:

- Archive / history inspected? with result
- unsynced local-only material inspected? with result
- path-lineage inspected? with result
- overwrite targets inspected? with result
- peer / chronology uncertainty acknowledged? with result

Each checklist row must force one of:

- `reviewed and clear`
- `reviewed and still risky`
- `not reviewed`
- `not applicable`

The operator must be able to answer: **what did I personally check before destroying state?**

## 3) Survivor map

Show survivor expectations for:

- payload bytes
- Archive / history bytes
- continuity spine / subject identity
- local path binding
- peer expectations
- receipts and audit trail

The map must explicitly separate:

- `survives in place`
- `survives only as residue`
- `recreated successor`
- `lost if assumption is wrong`
- `unknown`

## 4) Successor-epoch verdict

Show one verdict:

- `preserved continuity still proved`
- `successor epoch intentionally created`
- `destructive repair without continuity proof`
- `unknown`

If the verdict is not `preserved continuity still proved`, the page must state that the product is moving forward on reviewed necessity, not preserved identity proof.

The operator must be able to answer: **am I fixing the same subject, or creating a reviewed successor?**

## 5) Proof ceiling after commit

Show what the product will and will not be able to say afterwards.

Allowed examples:

- `A new subject instance was created after reviewed archive check.`
- `Overwrite-capable merge proceeded on operator attestation.`
- `Continuity preservation remains unproved.`

Blocked examples:

- `Nothing important was lost.`
- `This was the same subject all along.`
- `Every overwritten file was expendable.`
- `Archive contained nothing valuable everywhere.`

## Primary actions

Examples:

- `Commit reviewed successor epoch`
- `Back out and inspect Archive again`
- `Export destructive-assumption receipt`
- `Open survivor map in detail`

## Receipt / audit consequence

Committing this page must emit one receipt preserving:

- destructive step class
- attested checklist results
- survivor map
- successor-epoch verdict
- blocked stronger sentence
- expiry / reopen conditions
''',
'1238-attestation-expiry-timeline-page-peer-return-rescan-new-evidence-and-reopen-triggers-interface-spec.md': r'''# Attestation expiry timeline page: peer return, rescan, new evidence, and reopen triggers

This page exists because a human assertion is not timeless.
A judgment that was reasonable five minutes ago can become stale the moment a peer returns, a rescan finds contradiction, or new history evidence appears.

## Operator question

> when does this attestation stop carrying decision weight, what events reopen it, and what previously hidden contradiction could surface later?

## When this page must appear

Render whenever an operator attestation remains active after commit, especially for:

- hidden ghost/no-source warnings
- local-newest republish claims
- same-tree reconnect claims
- destructive recreate after archive review
- overwrite-risk acceptance on occupied targets

## Fixed page order

1. **Current attestation status**
2. **Expiry ladder**
3. **Reopen triggers**
4. **Automatic downgrades**
5. **Historical branch changes**

## 1) Current attestation status

Show:

- attestation id
- currently active / expired / contradicted / superseded status
- strongest safe sentence right now
- next likely invalidator
- current risk if left unreviewed

## 2) Expiry ladder

Every attestation must have one explicit expiry rung:

- `session-only`
- `until next scan`
- `until absent peers return`
- `until path lineage changes`
- `until successor-epoch commit`
- `until stronger machine proof arrives`
- `manual expiry only`

The operator must be able to answer: **what event naturally ends the validity of this attestation?**

## 3) Reopen triggers

Render trigger rows such as:

- offline peer observed online again
- new chronology evidence conflicts with local-newest claim
- folder tree rescan reveals contradiction
- Archive/history contents change or become visible
- path bind no longer matches the attested same-tree target
- recreated subject obtains a new spine witness
- another operator requests stronger claim language

Each row must show severity and whether it changes only wording or also action safety.

## 4) Automatic downgrades

The system must automatically downgrade previous claims when expiry happens.
Examples:

- `ignored ghost warning` downgrades back to `visibility choice only; world absence unproved`
- `local-newest` downgrades to `republished on stale operator evidence`
- `same-tree reconnect` downgrades to `path continuity requires rereview`
- `archive reviewed clear` downgrades to `destructive step completed; no continuing proof of universal emptiness`

The operator must be able to answer: **what safe sentence survives after expiry?**

## 5) Historical branch changes

Show a timeline of:

- attestation issued
- attestation committed
- contradiction seen
- claim downgraded
- attestation superseded by stronger proof
- attestation reopened for human rereview

## Main surface

The subject workspace should expose a compact **Human assertions** card with:

- active attestation count
- contradicted attestation count
- nearest expiry trigger
- action: `Review assertion timeline`

## What this page prevents

Without this page, the product quietly carries stale human certainty forward as if it were durable system truth.
AnonSync must instead age operator assumptions openly and on schedule.
''',
'1239-operator-attestation-lineage-receipt-page-assertion-basis-scope-expiry-and-blocked-stronger-sentences-interface-spec.md': r'''# Operator attestation lineage receipt page: assertion basis, scope, expiry, and blocked stronger sentences

Every human-supplied assertion that materially affects behavior or claim language must emit one durable receipt.
This receipt is the audit answer to:

> who supplied missing certainty here, what exactly did they assert, what did they review, how far did that assertion reach, when did it expire, and what stronger sentence remained blocked?

## Receipt fields

- `operator_attestation_receipt_id`
- `attestation_id`
- `assertion_class`
- `actor_ref`
- `scope_ref`
- `commit_action`
- `evidence_reviewed[]`
- `missing_machine_proof[]`
- `blast_radius_summary`
- `expiry_basis`
- `reopen_triggers[]`
- `supersession_ref` nullable
- `strongest_safe_sentence`
- `blocked_stronger_sentence`
- `issued_at`

## Human-readable layout

### 1) Assertion summary

State in one sentence what the operator asserted and what commit depended on it.

Example:

- `Operator asserted that this occupied target is the previously bound tree, allowing same-tree reconnect without treating the path as a fresh merge target.`

### 2) Evidence basis

List the evidence classes actually reviewed and keep `not reviewed` visible where applicable.

### 3) Consequence scope

Show whether the attestation changed:

- warning visibility only
- reconnect path choice
- republish eligibility
- destructive repair approval
- overwrite acceptance

### 4) Expiry and invalidators

Show the first-class expiry basis and the highest-signal reopen triggers.

### 5) Blocked stronger sentence

Keep the strongest forbidden sentence permanently adjacent to the receipt.
This is the anti-folklore protection.

## Example compact receipt rows

```text
warning-is-no-longer-actionable     warning hidden locally only     no proof every peer lacks bytes     expires when any absent peer returns     blocked: all sources are gone
```

```text
archive-reviewed-nothing-critical-remains     destructive recreate approved     archive reviewed by human only     expires after successor epoch created or new residue discovered     blocked: no valuable recovery material existed anywhere
```

## Rules

### Rule 1 — receipt language must keep human truth human

Never rewrite a human attestation as machine proof.

### Rule 2 — receipts must survive even if UI banners disappear

Later operators need to know that a risky step depended on judgment, not on universal proof.

### Rule 3 — supersession must not erase the original assumption

A later stronger proof may supersede the attestation, but the original assertion and its blast radius must remain inspectable.
''',
}

status_addendum = r'''## Revision addendum — operator attestation, certainty override, and destructive assumption truth after rev0348

This tranche locks the next seam around **operator attestation and reviewed human certainty**.
The key decisions now made explicit in the archive are:

- **operator attestation is first-class product state rather than a side effect of `Ignore`, `Proceed`, `OK`, `touch`, or `recreate` advice**
- **warning dismissal, local-newest assertion, same-tree reconnect assertion, archive-reviewed destructive approval, and risky merge acceptance are different assertion classes**
- **human evidence basis, missing machine proof, blast radius, and expiry must be published together**
- **visibility change is weaker than world truth, and reviewed necessity is weaker than preserved continuity proof**
- **every serious human-certainty event now needs one receipt that preserves assertion class, evidence reviewed, expiry basis, blast radius, and the blocked stronger sentence**

New docs added in this tranche:

- `1234-resilio-operator-attestation-certainty-override-ignore-proceed-and-destructive-assumption-fragmentation-evaluation.md`
- `1235-operator-attestation-contract-sheet-page-assertion-class-evidence-basis-blast-radius-and-expiry-interface-spec.md`
- `1236-local-truth-assertion-review-page-ghost-warning-reconnect-same-path-and-prepopulated-tree-branches-interface-spec.md`
- `1237-destructive-assumption-proof-page-archive-reviewed-overwrite-risk-and-successor-epoch-commit-interface-spec.md`
- `1238-attestation-expiry-timeline-page-peer-return-rescan-new-evidence-and-reopen-triggers-interface-spec.md`
- `1239-operator-attestation-lineage-receipt-page-assertion-basis-scope-expiry-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `Ignore All` can no longer hide whether the operator only changed visibility or supplied a stronger claim about world absence
- `touch these files if you are certain` can no longer hide which certainty was supplied, what evidence backed it, and when that certainty expires
- `just proceed` on reconnect or pre-populated targets can no longer hide whether the branch is same-tree reconnect or overwrite-capable risky merge
- `make sure Archive has nothing important` can no longer stay private human memory before destructive recreate
- later operators can open one receipt and see what the human asserted here, why the product accepted that assertion, what remained unproved, and what stronger sentence was still blocked

'''

NEW_FILES = list(files)

if __name__ == '__main__':
    for name, content in files.items():
        (DOCS / name).write_text(content.rstrip() + '\n', encoding='utf-8')

    status_path = DOCS / '00-status.md'
    old = status_path.read_text(encoding='utf-8')
    if 'operator attestation, certainty override' not in old:
        status_path.write_text(status_addendum + old, encoding='utf-8')

    missing = [name for name in NEW_FILES if not (DOCS / name).exists()]
    if missing:
        raise SystemExit(f'Missing rev0349 docs: {missing}')
    print('rev0349 docs written and ready')
