from pathlib import Path

root = Path('/mnt/data/anonsync_rev0287/AnonSync-rev0287-2026.03.22.05.03-residencypromisequeueclarity')
docs = root / 'docs'

def prepend(path: Path, text: str):
    old = path.read_text()
    path.write_text(text.rstrip() + '\n\n\n' + old)

new_docs = {
    '868-resilio-artifact-family-token-opacity-and-epoch-fork-evaluation.md': '''# Resilio artifact-family, token-opacity, and epoch-fork evaluation

## Why this pass exists

The archive already had strong work on join consequence, claim lanes, approval, mutable grants, and linked identity.
What it still lacked was one explicit evaluation of a narrower but highly consequential seam:

> where does current Resilio actually explain what an access artifact **is**, what governance it carries by itself, and what happens when that artifact is rotated?

Current official Resilio docs are still useful because they do not pretend every share token is the same thing.
They still openly say that:

- only **Standard** folders use raw keys
- the **first character** of a key identifies a different capability family (`A`, `B`, `D`, `E`, `F`, `M`)
- an `F` key is ciphertext-only custody and cannot decrypt names or content
- an `M` key links devices into one identity family rather than merely granting one folder
- share **links** are different from raw keys because the link carries a temporary key and an approval flow
- the browser landing page is only a carrier shell and the meaningful parameters live after `#`
- after approval the owner generates an **X509 certificate** and signs an ACL entry for the joining identity
- changing a raw key is **not** distributed automatically, and peers with the old key continue syncing with each other while the changed peer moves to a new epoch

That is excellent candor.
It is also a strong reason not to clone the exact contract.

## What current Resilio still gets right

### 1) Artifact family is real product meaning

Resilio is still right that a device-link artifact, a folder read-write key, a read-only key, an encrypted custody key, and an approval-bearing web link are not mere presentation variants.
They are materially different authority objects.

### 2) Browser carrier and authority artifact are different things

Resilio is still right that the web landing page is not itself the authority.
The URL shell, the hash fragment, the temporary key, the requester's public key, later certificate issuance, and ACL mutation are distinct parts of the path.

### 3) Rotation can create parallel epochs

Resilio is also right to say that a key change is not magical global replacement.
Old-key peers can continue among themselves.
That is a real and important operator truth.

## Why AnonSync still should not clone it

### 1) Too much authority meaning remains encoded inside opaque tokens

Current Resilio still expects the operator to know or learn that the first character of a raw key implies a different capability family.
That is clever engineering, but it is not a sufficient operator contract.
A token should be inspectable as a product object, not understood only by folklore or support docs.

### 2) Carrier convenience still risks hiding governance differences

A link can arrive by browser, clipboard, QR, e-mail template, or manual paste.
But current docs still leave the operator to mentally reconstruct whether the arriving thing is:

- a bearer-style raw key
- an approval-bearing temporary-key link
- a linked-identity family key
- an encrypted-custody artifact
- a successor artifact that will fork prior continuity

Carrier convenience is worth keeping.
Making it the main explanation is not.

### 3) Rotation truth still sounds too much like an implementation caveat

`Change the key` is not just maintenance.
It can produce a parallel cohort that keeps syncing on the old epoch.
That is governance truth and continuity truth, not a footnote.
A product should expose it before issuance or rotation, not after damage.

### 4) Artifact family and resulting seat role are still nearby but not owned together

Current Resilio docs still require the operator to combine `Key structure and flow`, `Link structure and flow`, identity docs, share-dialog docs, and local-share caveats before they can answer one ordinary question:

> what exact authority object am I issuing or accepting, and what parallel continuity will survive if I rotate it later?

That should belong to one stable page family.

## Hard decisions now locked for AnonSync

1. **Artifact family must be inspectable before use.** An opaque pasted token is never the only explanation of rights.
2. **Seat-link artifacts and subject-access artifacts must never share one flattened grammar.** `Join my device family` and `join this subject` are different contracts.
3. **Carrier must not determine semantics.** Browser-open, QR, paste, and local import are carriers; the inspected artifact object owns the meaning.
4. **Rotation is an epoch event.** Replacing a live artifact must preview surviving old cohorts, successor issuance, and retirement order.
5. **Issuance and intake both emit receipts.** The system must remember what artifact family, ceiling, expiry, and fork boundary existed at review time.

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Capability artifact**
- **Issuance preview**
- **Incoming artifact intake**
- **Artifact rotation / fork warning**
- **Artifact issuance receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that links, keys, encrypted-custody artifacts, and linked-identity artifacts are truly different. But it is also current evidence that too much authority meaning still lives inside opaque tokens and support prose. AnonSync should keep the candor and refuse the token-opacity contract.''',

    '869-capability-artifact-page-family-embedded-ceiling-approval-path-and-safe-presentation-interface-spec.md': '''# Capability artifact page: family, embedded ceiling, approval path, and safe presentation interface spec

## Purpose

This page answers one ordinary question:

> what kind of authority artifact is this, what power is embedded in it already, and what still requires later approval or review?

The page exists because operators should not need folklore about prefixes, URL fragments, or delivery carrier to understand an authority object.

## Core decision

Every authority-bearing token or exportable invite object must render one first-class **Capability artifact** page.
That page owns:

- artifact family
- embedded capability ceiling
- approval path
- continuity scope
- safe-display rules
- strongest safe sentence

## Fixed page order

1. artifact strip
2. family card
3. capability ceiling card
4. approval path card
5. continuity scope card
6. safe presentation card
7. receipt / lineage rail

### 1) Artifact strip

Show:

- artifact family
- candidate subject or seat family
- current carrier
- freshness state
- strongest next-safe action

Artifact families must include at minimum:

- `seat-link`
- `subject-access`
- `subject-observer`
- `subject-writer`
- `subject-owner-like`
- `opaque-custody`
- `ciphertext-custody`
- `unknown / untrusted`

### 2) Family card

Publish:

- whether the artifact targets one subject, a future subject family, or a seat-link relationship
- whether the artifact is direct authority or merely an approval-seeking claim
- whether the artifact can be re-shared or only consumed
- whether the artifact is native, imported, derived, or superseded

### 3) Capability ceiling card

Show the strongest authority this artifact could ever yield if all later approvals succeed.
Examples:

- observe only
- read current and future bytes
- write upstream
- share onward
- hold ciphertext only
- join a linked seat family

The page must also show stronger forbidden interpretations.

### 4) Approval path card

Show one explicit path:

- `self-sufficient bearer artifact`
- `requires review by eligible approver`
- `requires seat-link acceptance`
- `requires stronger proof before evaluation`
- `blocked / invalid / stale`

Also show whether later approval may narrow the artifact below its ceiling.

### 5) Continuity scope card

Publish:

- current subject scope
- future-arrival scope
- descendant scope
- whether consuming this artifact preserves current continuity, joins an existing lineage, or begins a successor epoch

### 6) Safe presentation card

Because many artifacts are portable secrets or live invitations, the page must control how they are shown:

- fully hidden by default
- redacted preview allowed?
- exportable as text / QR / local handoff?
- may be copied again after issuance?
- screenshot-safe or not?

The page must distinguish `inspect artifact` from `reveal secret`.

### 7) Receipt / lineage rail

Show linked issuance receipt, supersession receipt, or intake receipt when available.

## Rules

### Rule 1 — artifact family must not be inferred from carrier alone

A browser-opened thing may still be a subject invite, a seat-link claim, or an invalid artifact.
Carrier alone is never enough.

### Rule 2 — ceiling must not impersonate result

An artifact that can produce writer access after approval must not be described as if writer access already exists.

### Rule 3 — seat-link and subject-access stay separate

An artifact that joins a seat family must not be shown with the same grammar as an artifact that grants one subject.

### Rule 4 — inspect and reveal are separate actions

The page must permit semantic inspection without forcing full secret exposure.

## Acceptance criteria

A later operator can:

- tell what artifact family is in play
- tell what authority ceiling is embedded versus still pending review
- distinguish carrier from meaning
- inspect the artifact safely without overexposing secrets
- reopen the right continuity or approval workflow from this page''',

    '870-issuance-preview-page-expiry-use-budget-recipient-binding-and-fork-warning-interface-spec.md': '''# Issuance preview page: expiry, use budget, recipient binding, and fork warning interface spec

## Purpose

This page exists because `copy link`, `show QR`, and `rotate key` are not small UI actions.
They create authority objects with scope, lifetime, and continuity consequences.

The operator question is:

> if I issue this artifact now, what exact authority object will exist, who is it for, how long will it work, and what continuity damage or fork could this create later?

## Core decision

Every serious invite, link, key, QR, or successor artifact issuance must render one first-class **Issuance preview** page before export.

## Fixed page order

1. issuance strip
2. resulting artifact card
3. recipient binding card
4. expiry and use-budget card
5. continuity and fork-warning card
6. safe export options
7. pending receipt summary

### 1) Issuance strip

Show:

- artifact family to be issued
- source seat / subject
- intended audience
- strongest next-safe action

### 2) Resulting artifact card

Publish:

- resulting family
- resulting authority ceiling
- approval requirement if any
- onward-share ceiling
- whether this issuance preserves current artifact epoch or creates a successor artifact

### 3) Recipient binding card

Show how tightly issuance is bound:

- unbound / bearer-style
- expected claimant identity
- reviewed recipient fingerprint or identity
- lane-restricted recipient set
- one-time claim only

If recipient binding is weak, the page must say so bluntly.

### 4) Expiry and use-budget card

Show:

- no expiry / fixed expiry / claim-once / use-limited / freshness-limited
- use budget remaining at issuance
- whether the budget is global or recipient-bound
- what happens after expiry or budget exhaustion

### 5) Continuity and fork-warning card

This card is mandatory whenever issuance replaces or rotates another live artifact.
Show:

- whether old artifacts remain valid
- whether old cohorts continue syncing together
- whether this is a narrowing, widening, or successor epoch
- retirement order required to avoid accidental parallel continuity
- strongest safe sentence and stronger forbidden sentence

### 6) Safe export options

Offer export carriers, but preserve semantics:

- copy text
- QR display
- local handoff
- reviewed send path
- hold without export

The page must make clear that changing carrier does not change authority semantics.

### 7) Pending receipt summary

Preview the issuance receipt fields that will be frozen on commit.

## Rules

### Rule 1 — issuance must preview the artifact, not just the carrier

`Copy link` is not a sufficient pre-commit explanation.

### Rule 2 — rotation must preview fork risk

If old and new artifacts can coexist, the page must warn that continuity may fork.

### Rule 3 — recipient binding truth must be explicit

A bearer-style artifact must not sound recipient-bound just because the operator intends one recipient.

### Rule 4 — expiry must be semantically visible

Expiry and click/use budgets belong to authority review, not hidden advanced options.

## Acceptance criteria

A later operator can:

- reconstruct what artifact was issued and why
- see how tightly the recipient was bound
- see expiry and use budget clearly
- understand whether this issuance risks parallel epochs
- tell which export carriers were available without confusing carrier for meaning''',

    '871-incoming-artifact-intake-page-token-family-preview-info-and-acceptability-verdict-interface-spec.md': '''# Incoming artifact intake page: token family, preview info, and acceptability verdict interface spec

## Purpose

This page exists because `paste token`, `open link`, and `scan QR` are intake actions, not immediate acceptance.
An incoming artifact may be valid, stale, stronger than intended, or continuity-changing.

The operator question is:

> what did I just receive, what can I safely know before consuming it, and is it acceptable to proceed on this seat right now?

## Core decision

Every incoming invite or authority artifact must render one first-class **Incoming artifact intake** page before commit.

## Fixed page order

1. intake strip
2. parsed-family card
3. preview-info card
4. acceptability verdict card
5. seat-fit card
6. continuity consequence card
7. intake receipt summary

### 1) Intake strip

Show:

- intake carrier
- parsed artifact family or `unknown`
- current seat
- strongest next-safe action

### 2) Parsed-family card

Publish:

- artifact family
- whether parsing is complete, partial, or failed
- whether local semantic inspection succeeded without secret reveal
- whether the artifact appears superseded, exhausted, stale, or revoked

### 3) Preview-info card

Show the strongest safe preview available before commit:

- candidate subject or seat family label
- approximate scope / size / class when known
- requested right or ceiling
- approval path expected
- issuer identity proof when available

The page must also show what is still unknown until deeper review or approval.

### 4) Acceptability verdict card

Show one explicit verdict:

- `safe to continue to review`
- `safe to continue and claim`
- `requires stronger identity proof`
- `blocked by local policy`
- `blocked by stale or exhausted artifact`
- `blocked because artifact family is not allowed on this seat`

### 5) Seat-fit card

Show:

- whether this seat may consume the artifact
- whether another seat is the safer claimant
- whether local storage / capability / trust posture is insufficient
- whether this intake would unexpectedly join a seat family rather than one subject

### 6) Continuity consequence card

Publish:

- whether acceptance preserves current continuity
- whether it creates a new subject presence only
n- whether it links the entire seat into a broader family
- whether it risks replacing a current identity or creating a fork

### 7) Intake receipt summary

Preview the receipt that will survive accept, defer, or reject.

## Rules

### Rule 1 — intake is not auto-commit

Opening or pasting an artifact may not silently finalize the join.

### Rule 2 — strongest safe preview only

The page must show useful preview information without pretending unknowns are known.

### Rule 3 — seat-link surprises must be loud

If the artifact would link or replace seat identity rather than merely add one subject, the page must say so before acceptance.

### Rule 4 — stale or exhausted artifacts stay visible as blocked artifacts

The product must not flatten them into generic parse failure.

## Acceptance criteria

A later operator can:

- tell what kind of artifact arrived
- see what is known before acceptance
- understand whether this seat should consume it
- distinguish local policy block from artifact invalidity
- reopen the right approval or continuity page without repeating intake folklore''',

    '872-artifact-rotation-fork-warning-page-old-cohort-survival-successor-issuance-and-retirement-order-interface-spec.md': '''# Artifact rotation / fork warning page: old cohort survival, successor issuance, and retirement order interface spec

## Purpose

This page exists because rotating a live invite, key, or linked-seat artifact can create multiple concurrently valid continuity islands.
That is not a cosmetic warning.
It is a governance event.

The operator question is:

> if I rotate this artifact, who keeps talking on the old epoch, what new epoch am I creating, and what retirement order avoids accidental split continuity?

## Core decision

Every live artifact rotation must render one first-class **Artifact rotation / fork warning** page.

## Fixed page order

1. rotation strip
2. old-epoch map
3. successor artifact card
4. fork-risk card
5. retirement-order plan
6. continuity receipt summary

### 1) Rotation strip

Show:

- current artifact family
- target successor family
- subject or seat family affected
- strongest next-safe action

### 2) Old-epoch map

Publish:

- known members of the old cohort
- who can still communicate on the old artifact
- whether old access survives until explicit retirement
- evidence freshness of this map

### 3) Successor artifact card

Show:

- new artifact family
- new ceiling
- new approval / binding / expiry choices
- whether the successor is narrower, wider, or same ceiling but new epoch

### 4) Fork-risk card

Show one verdict:

- `no fork risk; old artifact already dead`
- `limited fork risk; successor created but old cohort empty`
- `live parallel continuity likely`
- `high fork risk; old cohort active and retirement incomplete`

Also show strongest safe sentence and stronger forbidden sentence.

### 5) Retirement-order plan

Show the safest order among:

- issue successor first
- notify cohort
- wait for acknowledgements
- retire old artifact
- reread roster and confirm old-epoch silence

If safe retirement is impossible, say so.

### 6) Continuity receipt summary

Preview what the rotation receipt will preserve:

- old epoch reference
- successor epoch reference
- fork-risk verdict
- retirement order chosen
- unresolved survivors

## Rules

### Rule 1 — rotation is not framed as mere refresh

If old peers can continue on the old artifact, the page must name this as epoch split risk.

### Rule 2 — survivor maps must be freshness-bound

Retirement claims must preserve how fresh the survivor evidence was.

### Rule 3 — successor issuance and old retirement stay on one page

Operators must not be forced to open separate pages to understand the fork.

### Rule 4 — no false clean-cut language

The page may not say `rotated` as if all peers automatically moved.

## Acceptance criteria

A later operator can:

- tell whether old cohorts survive
- see what successor artifact was created
- understand the risk of parallel continuity
- follow a safe retirement order
- preserve honest continuity language in the final receipt''',

    '873-artifact-issuance-receipt-page-family-ceiling-expiry-and-successor-boundary-interface-spec.md': '''# Artifact issuance receipt page: family, ceiling, expiry, and successor boundary interface spec

## Purpose

This receipt exists because portable authority artifacts are easy to misremember later.
Operators need one durable object that says exactly what was issued, with what ceiling, and whether it created or replaced an epoch.

## Core decision

Every exported invite, key, link, QR-backed artifact, or successor artifact must emit an **Artifact issuance receipt**.

## Required receipt fields

### A. Identity

- receipt id
- issued-at timestamp
- issuing seat
- reviewed surface
- carrier options offered

### B. Artifact family

- artifact family
- native / derived / successor status
- direct subject or seat-family scope

### C. Ceiling and path

- strongest embedded ceiling
- approval requirement
- onward-share ceiling
- recipient binding class

### D. Lifetime

- expiry class
- expiry instant if fixed
- use/click budget if relevant
- exhaustion behavior

### E. Continuity

- same-epoch or successor-epoch verdict
- prior artifact / epoch reference when relevant
- fork-risk verdict at issuance time
- retirement plan reference when relevant

### F. Language guard

Store together:

- strongest safe sentence
- stronger forbidden sentence

## Example safe sentences

- `As issued, this artifact could only begin a reviewed subject-access claim; it did not itself prove writer access had been granted.`
- `As issued, this successor artifact created a new access epoch while older artifacts still required explicit retirement.`
- `As issued, this artifact was bound only loosely to an intended recipient and should be treated as bearer-style until consumed.`

## Anti-confusion rules

### Rule 1 — carrier is not the family

The receipt must preserve the artifact family separately from whether it was shown as QR, copied as text, or sent by another lane.

### Rule 2 — ceiling is not result

If later approval was required, the receipt may not sound as though final access had already been granted.

### Rule 3 — successor boundaries must survive memory drift

If the issuance created a successor epoch, the receipt must keep the old/new boundary visible.

### Rule 4 — lifetime semantics must survive

Expiry, exhaustion, and freshness limits must remain visible even after the operator forgets the issuing dialog.

## Compact row contract

A compact receipt row should preserve:

1. artifact family
2. scope phrase
3. ceiling phrase
4. lifetime phrase
5. epoch phrase
6. strongest safe sentence fragment

Example:

```text
subject-access artifact · design subtree · writer ceiling after approval · expires in 3 days / 1 remaining claim · successor epoch / old artifact still live pending retirement · safe to say this was an approval-bearing invite, not an immediate grant
```

## Acceptance criteria

A later operator can:

- reconstruct what was issued
- distinguish artifact family from export carrier
- tell whether approval was still required
- see expiry and exhaustion truth
- see whether the issuance created a successor boundary or stayed in the same epoch'''
}

for name, content in new_docs.items():
    (docs / name).write_text(content)

prepend(root / 'README.md', '''## Revision addendum — artifact-family inspection, token-opacity refusal, and epoch-fork warning

This revision continues directly from `rev0287` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **raw key families, approval-bearing web links, temporary-key link flow, identity-link `M` keys, share-dialog expiry/use budgets, and key-change epoch fork behavior**.
2. Tightens the non-clone line again: borrow Resilio's candor that keys, links, encrypted-custody artifacts, and seat-link artifacts are materially different; refuse any contract where too much authority meaning still lives inside opaque tokens and support prose.
3. Adds one new **Resilio evaluation** document focused on why present-day token-family truth and key-rotation fork truth are still too scattered and too opaque to clone directly.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: capability artifact, issuance preview, incoming artifact intake, artifact rotation / fork warning, and artifact issuance receipt.
5. Makes one hard product decision explicit: **artifact family must be inspectable before use**. A pasted token is never the only explanation of rights.
6. Makes another hard product decision explicit: **seat-link artifacts and subject-access artifacts never share one flattened grammar**. `join my device family` and `join this subject` are different contracts.
7. Makes a third hard product decision explicit: **rotation is an epoch event**. Replacing a live artifact must preview surviving old cohorts, successor issuance, and retirement order.
8. Packages the result as another continuation archive whose new tranche makes the `artifact family / intake semantics / successor fork` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's opaque artifact contract**

This time the reason is especially clear around **raw key families, temporary-key links, certificate-backed approval, and key-change fork behavior**.
Current official materials simultaneously show that:

- `Key structure and flow` still says only Standard folders use raw keys, that the first key character encodes materially different types (`A`, `B`, `D`, `E`, `F`, `M`), that `F` is ciphertext-only custody, and that `M` is an identity-link artifact.
- the same current article still says key change is not distributed automatically and that old-key peers keep syncing with each other after one peer changes key.
- `Link structure and flow` still says share links carry a temporary key in the hash fragment, that the browser landing page is only a carrier shell, that the claimant sends a locally generated public key, and that approval mints an X509 certificate plus ACL entry before access becomes live.
- `Sync Share Dialog (Desktop)` still says links and keys differ materially because keys do not use the approval mechanism, and still keeps expiry and use-budget semantics inside the issuance flow.
- `Sync Private Identity & Linking My Devices` still says an `M`-key path can take over another device's identity, fingerprint, and configured shares, which proves that a seat-link artifact is not just another folder invite.

That candor is useful.
The operator contract is still too opaque.
AnonSync should not clone a world where the operator still has to infer from token prefixes, browser wrappers, and separate support notes whether the thing in hand is a bearer-style raw key, an approval-bearing invite, a seat-link artifact, a ciphertext-custody capability, or a successor artifact that will fork continuity.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful truths are real, but the present-day artifact contract still hides too much governance inside opaque tokens and still treats rotation/fork truth too much like implementation detail instead of one owned workflow.**

## New documents in rev0288

- `868` Resilio artifact family, token opacity, and epoch fork evaluation
- `869` Capability artifact page
- `870` Issuance preview page
- `871` Incoming artifact intake page
- `872` Artifact rotation / fork warning page
- `873` Artifact issuance receipt page''')

prepend(docs / '00-status.md', '''## Latest addendum — artifact-family truth, intake inspection, and epoch-fork warning after rev0287

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **current Resilio still treats artifact family as real semantics, which is good**
- **too much of that meaning still lives inside opaque tokens, browser wrappers, and article archaeology, which is not good enough to clone**
- **key rotation still behaves like epoch fork truth, not a harmless refresh**

Hard decisions made in this tranche:

1. **Artifact family must be inspectable before use.** A token is never its own explanation.
2. **Seat-link and subject-access artifacts stay separate.** AnonSync never flattens `join this seat family` into `join this subject`.
3. **Carrier never owns semantics.** QR, browser-open, paste, and local handoff are delivery lanes; the inspected artifact object owns the meaning.
4. **Rotation is an epoch event.** Successor issuance must preview surviving old cohorts and retirement order.
5. **Issuance and intake both emit receipts.** Later operators should not need token folklore to reconstruct what was issued or accepted.

That yields five more ordinary product-owned pages:

- **Capability artifact page**
- **Issuance preview page**
- **Incoming artifact intake page**
- **Artifact rotation / fork warning page**
- **Artifact issuance receipt page**

This tranche closes a real gap between earlier join/approval doctrine and the actual authority object that crosses the wire.''')

prepend(docs / '10-resilio-sync-evaluation.md', '''## Revision addendum — artifact-family opacity and epoch-fork truth after rev0287

Another current official Resilio pass still strengthens the same broad conclusion: the product remains useful to study precisely because it is honest about token families and continuity forks.
Current official docs still say only Standard folders use raw keys; key type is materially encoded by the first character; `F` is encrypted custody that cannot decrypt names or content; `M` links devices into one identity family; links carry a temporary key and require an approval flow that culminates in X509 certificate issuance and ACL mutation; and changing a raw key is not distributed automatically, so old-key peers continue syncing among themselves while the changed peer moves to a new epoch.

That is excellent substance.
The non-clone issue is that too much of the operator-facing meaning still has to be inferred from token internals and separate support articles.
AnonSync should therefore keep the semantic distinctions and replace the opaque-token contract with inspected artifact objects, issuance previews, intake reviews, fork warnings, and receipts.''')

prepend(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', '''## Revision addendum — scorecard after rev0287: keep artifact candor, reject token-opacity and silent epoch forks

New scorecard line added explicitly:

| Artifact family / approval path / successor epoch fork | Strong but too opaque | **Adapt** | Current docs rightly distinguish raw keys, temporary-key links, identity-link `M` keys, and ciphertext-only custody, but too much operator meaning still lives inside token internals and support prose; key rotation also creates real old/new epochs that deserve workflow ownership | **Capability artifact**, **Issuance preview**, **Incoming artifact intake**, **Artifact rotation / fork warning**, and **Artifact issuance receipt** pages |

The sharpened borrow line here is:

- keep the truth that artifact families are genuinely different
- keep the truth that browser carrier is not the same as authority artifact
- keep the truth that rotation can fork continuity
- do **not** clone a contract where operators must learn token meaning from prefixes, hash fragments, and later support archaeology''')

prepend(docs / '39-interface-pattern-language.md', '''## Revision addendum — interface pattern after rev0287: inspect the artifact, then choose the carrier

Another recurring pattern is now explicit:

- **artifact meaning must be inspected before carrier choice or commit**
- **intake is review, not auto-acceptance**
- **rotation is successor/fork review, not refresh copy**

Pattern rule:

1. parse or classify the incoming/outgoing artifact into a stable family object
2. show embedded ceiling, approval path, continuity scope, and forbidden stronger sentence before export or acceptance
3. let carrier choice happen only after semantics are visible
4. when replacing a live artifact, keep old cohort survival and retirement order on the same page
5. freeze the result in issuance or intake receipts so later operators do not rely on token folklore

This pattern keeps the archive from regressing into `paste this secret and trust that everyone knows what it means`.''')

prepend(docs / '40-architecture-decisions.md', '''## Revision addendum — architecture decision after rev0287: compile authority artifacts and rotation forks into first-class objects

Decision:

- portable authority artifacts and their successor forks must compile into first-class inspected objects rather than raw opaque strings plus help-article lore

Why:

- current official Resilio material still shows that token family, approval path, and continuity consequences are real but partially hidden inside key prefixes, hash fragments, and separate flow articles
- carrier changes should not change semantics, which means semantics need an object separate from carrier
- rotation can leave old cohorts live, so successor issuance is continuity governance rather than mere regeneration

Implications:

- create a `capability_artifact` object
- create an `artifact_issuance_preview` object and `artifact_issuance_receipt` object
- create an `incoming_artifact_intake` object
- create an `artifact_rotation_fork_review` object preserving old cohort evidence, successor epoch, and retirement order
- require all projections to render artifact family, ceiling, approval path, and fork-risk explicitly rather than reconstructing them from token text

Rejected alternative:

- treat links/keys/QR as mostly equivalent carriers, keep semantics implicit, and handle rotation as a background refresh

Reason rejected:

- that would recreate exactly the token-opacity and silent-fork contract the archive is explicitly refusing to clone''')

prepend(docs / '50-roadmap.md', '''## Revision addendum — roadmap after rev0287: artifact inspection and successor-fork tranche

Another tranche is now reserved more explicitly:

- make authority artifacts inspectable objects before export or intake
- make carrier choice happen after semantics, not before
- make intake a review surface rather than automatic acceptance
- make live artifact rotation compile into successor/fork review with survivor map and retirement order
- make issuance and intake both leave durable receipts preserving ceiling, expiry, and epoch boundary

Added this tranche to the roadmap:

- `868` Resilio artifact family, token opacity, and epoch fork evaluation
- `869` Capability artifact page
- `870` Issuance preview page
- `871` Incoming artifact intake page
- `872` Artifact rotation / fork warning page
- `873` Artifact issuance receipt page

This tranche exists so AnonSync does not inherit the `opaque token now, governance meaning later` contract visible in current sync-product sharing flows.''')

prepend(docs / 'sources.md', '''## Revision addendum — artifact-family opacity and epoch-fork work after rev0287

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about raw key families, temporary-key links, approval/certificate flow, identity-link `M` keys, share-dialog expiry/use budgets, and key-change epoch forks.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that links, keys, ciphertext-custody artifacts, and linked-identity artifacts are materially different authority objects?

> where do those same current docs still show that the ordinary operator answer about `what exactly is this token and what fork happens if I rotate it?` depends on token internals and several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Key structure and flow` article, which still says only Standard folders use raw keys, that the first character determines materially different key types (`A`, `B`, `D`, `E`, `F`, `M`), that `F` is ciphertext-only custody, that `M` is an identity-link key, and that key changes are not distributed automatically so old-key peers continue syncing together after one peer changes key.
- Resilio's current `Link structure and flow` article, which still says the browser landing page is a carrier shell, that meaningful parameters live after `#`, that links contain a temporary key, that the claimant sends a locally generated public key, and that approval generates an X509 certificate plus signed ACL entry before access becomes live.
- Resilio's current `Sync Share Dialog (Desktop)` article, which still says keys and links differ materially because keys do not use the approval mechanism and still publishes expiry and use-budget settings during issuance.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says devices linked with one identity use an `M`-key path, that taking the M-key from one device can transfer identity name, fingerprint, and configured shares to another, and that linking two already-running devices can replace one certificate and remove Advanced folders from the app.
- Resilio's current `Sharing a folder locally` article, which still says local shares are neither full peers nor ordinary onward shares, that they inherit ceilings from the source share, and that some permission changes require remove-and-reshare rather than in-place mutation.

## Additional Resilio official sources emphasized in rev0288

- Key structure and flow  
  https://help.resilio.com/hc/en-us/articles/206767810-Key-structure-and-flow

- Link structure and flow  
  https://help.resilio.com/hc/en-us/articles/204754739-Link-structure-and-flow

- Sync Share Dialog (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204790709-Sync-Share-Dialog-Desktop

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Sharing a folder locally  
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally''')

print('Applied rev0288 modifications.')
