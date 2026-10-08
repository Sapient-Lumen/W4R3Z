from pathlib import Path
import re

root = Path('/mnt/data/anonsync_rev0234_work/AnonSync-rev0234-2026.03.21.18.26-networkeligibilityproofpages')
docs = root / 'docs'

new_rev = 'rev0235'
new_ts = '2026.03.21.18.58'
new_code = 'presencewitnessgradepages'

# --- README rewrite ---
readme = f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{new_rev}`
- Timestamp: `{new_ts}` (America/New_York)
- Codename: `{new_code}`

## What changed in this revision

This revision continues directly from `rev0234` and does seven concrete things:

1. Re-checks another current official Resilio cluster so the archive now treats **presence witness grade, hidden-listed peer truth, and subject source witness truth** as a first-class non-clone reason rather than letting them stay split across peer-list, mobile, pause, and troubleshooting pages.
2. Adds one new **Resilio evaluation** document focused on how current Resilio still spreads the ordinary answer to `what is actually present enough for me to trust this row, this peer, or this file right now?` across several help articles.
3. Sharpens the main non-clone claim again: borrow Resilio's candor that `listed`, `online`, `eligible`, `sleeping`, `paused`, and `has a current byte source` are materially different truths, but refuse the contract where operators still have to reconstruct them from several articles.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: presence witness, peer presence review, subject source witness, and presence witness receipt.
5. Extends the interface/workbench doctrine so participation and recovery surfaces now publish presence grade, source grade, strongest safe sentence, and stronger forbidden sentence before the product treats a row or peer dot as enough proof.
6. Refreshes status-bearing doctrine documents — status, scorecard, clone-veto tests, sources, and revision metadata — so the new tranche is integrated rather than bolted on.
7. Packages the result as another continuation archive with the new tranche called out explicitly in the reading order through the document additions themselves.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's page contracts**

This time the evidence is especially clear around **presence witness grade, hidden-listed peer truth, and subject source witness truth**.

Current official docs still openly distinguish real presence-adjacent facts such as:

- `X of Y peers` where `X` is online now and `Y` includes peers that have merely been connected before
- linked-device green/grey dots and sync modes that describe connection and posture, not byte-source sufficiency
- `Hide this device` clearing an offline device from view without unlinking it, and the hidden device reappearing if it comes back online
- `Stopped. Forbidden network` where a visible share is present but not allowed to connect or detect changes on the current network
- Android Auto-sleep or Battery Saver taking the core offline so peers do not see the device online
- ghost-file situations where a subject is still announced in the tree even though no peer currently has the full bytes
- switched-off devices not syncing because a source device must be online for syncing to work

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help articles before the product fully owns these questions:

- is this peer only historically listed, or actually online now
- is it online but ineligible because of pause, forbidden network, or sleep state
- does any currently present peer still have the full bytes for this subject
- is this a ghost announcement, a placeholder-only swarm, or merely delayed transfer
- what exact sentence the product is still allowed to say about presence right now

AnonSync should therefore make **presence witness grade** a first-class product object.
Every serious peer list, absent-file review, source-availability warning, and mobile participation surface should render listedness, route-presence, eligibility, source witness, and strongest safe language before commit or escalation.
'''
(root / 'README.md').write_text(readme)

# --- new docs ---
new_docs = {
    '601-resilio-presence-witness-grade-listedness-route-and-source-proof-evaluation.md': '''# Resilio presence-witness grade, hidden-listed peers, and source-proof evaluation

## Why this pass exists

The archive already had member presence, network eligibility, pause truth, subject non-arrival, and witness locality work.
Those were necessary, but another current Resilio pass still exposes a more ordinary operator seam.
The problem is no longer only `can this share transfer right now` or `why is this subject absent`.
It is now:

- whether a peer is merely **listed historically** or actually **online now**
- whether an online-looking peer is actually **eligible to participate** or is paused, forbidden-network, or sleeping
- whether a subject has a **current byte source** rather than only a route-visible or placeholder-only peer
- whether hiding an offline device changes authority or merely changes the list
- what durable receipt proves the strongest sentence the product is allowed to make about current presence

That seam is still materially real in current official Resilio docs.
They still say the desktop main view shows `X of Y peers`, with `X` as online peers and `Y` as total peers including offline ones, and that offline peers disconnect after 7 days unless power-user settings change it.
They still say clearing an offline device only hides it from view and does not unlink it, and that it reappears if it comes back online.
They still say linked devices show green/grey dots for online/offline and selected sync mode.
They still say a switched-off source device cannot sync because there is no cloud intermediary.
They still say `Stopped. Forbidden network` blocks peer connection and change detection for that share, and that Auto-sleep can make peers stop seeing the device online.
They still say ghost-file warnings occur when peers announced a subject but nobody currently has the full bytes anymore.
The current v3 line still appears active through `3.1.2.1076`.

That is useful candor.
The non-clone problem is workflow ownership.
Resilio still leaves the ordinary sentence `what is actually present enough for me to trust this peer row or this subject row right now?` split across main-view, identity, hide-offline, mobile network, auto-sleep, pause, switched-off, and ghost-file docs.

## What current Resilio gets right

Current official docs still deserve credit for saying plainly that presence is not one bit.
They still distinguish several materially different truths:

- a peer can be in the `Y` total because it has been connected before without being online now
- a device can be hidden from the operator's list without being unlinked or revoked
- a green/grey dot is about current connection, not necessarily byte-source sufficiency for every subject
- a share can be visible yet stopped by forbidden-network policy or by sleeping-core state
- a subject can still be announced in the tree even after no peer retains the full bytes
- a switched-off device cannot act as a source because the system is peer-to-peer rather than cloud-backed

That is better than flattening everything into `online` or `missing`.
AnonSync should keep that candor.

## What current Resilio still leaves fragmented

Current official docs still make the operator reconstruct one ordinary answer from several pages:

- `Sync Main View (Desktop)` explains that `X of Y peers` mixes online-now with historical total peer count.
- `Sync Private Identity & Linking My Devices` explains green/grey dots and linked-device modes.
- `How to clear offline devices?` explains that hidden offline devices are not unlinked and can reappear.
- `Setting network interface per share`, `Settings on mobile platforms`, and `Configuring Auto Sleep & Battery Saver (Android)` explain why a visible share or device may still be ineligible or unseen.
- `How to pause syncing` explains that paused state still allows some non-payload effects.
- `Cannot download files / ... no source peers online for too long time` explains ghost announcements and placeholder-only source loss.
- `Will my devices still sync when switched off?` explains that a source must actually be online.

The operator therefore still has to do archaeology to answer a simple question:

> do I merely see historical membership, or do I have current eligible presence and a real byte source for this subject?

## Why this is a strong non-clone reason

This is not a cosmetic peer-list issue.
It changes the product's claim ceiling.
Without a first-class presence-witness object, the product can accidentally let operators say things that are stronger than the evidence supports, such as:

- `this peer is here` when it is only historically listed or hidden-offline
- `the device is online enough` when the share is actually forbidden-network or sleep-blocked
- `someone has the file` when the tree only has a ghost announcement and placeholders remain
- `the share is gone` when the device was only hidden from view and may return
- `this row proves recoverability` when no current byte source exists on any present peer

All of those can be false for reasons the docs themselves already admit are real.

## Better product move for AnonSync

AnonSync should not clone a contract where presence meaning remains scattered across peer lists, mode dots, mobile settings, sleep policy, and ghost-file warnings.
It should instead make **presence witness grade** first-class.

That means every serious peer row or source-availability warning should publish, in one stable reviewed object:

- peer listedness grade
- route / connection witness grade
- policy eligibility grade
- source-byte witness grade for the subject in question
- strongest safe sentence
- stronger forbidden sentence
- next observation that would strengthen or weaken the claim

## New page family required

This pass therefore adds four explicit replacements:

1. **Presence witness** — what kind of presence proof exists right now for this peer/share/subject.
2. **Peer presence review** — whether a peer is listed, online, hidden, disconnected, sleeping, paused, or merely historical.
3. **Subject source witness** — whether any currently present peer still has the full bytes, only placeholders, or no source at all.
4. **Presence witness receipt** — durable safe language and next observation basis.

## Condensed design verdict

Borrow Resilio's candor that listedness, online dots, network eligibility, sleeping-core state, and current byte-source availability are materially different truths.
Do not clone a product contract where operators still have to reconstruct from several help pages whether a peer row or subject row is present enough to justify a strong action or statement.
''',
    '602-presence-witness-page-listedness-route-eligibility-and-source-grade-interface-spec.md': '''# Presence witness page — listedness, route grade, eligibility, and source-grade interface spec

## Purpose

Give the operator one reviewed answer to:

- what kind of presence proof exists right now
- whether the peer is only historically listed, currently connected, or actually eligible
- whether the subject has a current byte source or only announcement residue
- what sentence is still true right now
- what next observation would strengthen or weaken that sentence

This page is the presence-truth companion to membership, network-eligibility, pause, and subject-delivery pages.
It should appear whenever a peer row, share row, or file row could otherwise overstate what is actually present.

## Inputs

- seat identifier
- peer identifier
- optional subject identifier
- listing grade (`hidden`, `historical-listed`, `currently-listed`, `unknown`)
- route grade (`connected-now`, `disconnected`, `sleep-offline`, `paused`, `unknown`)
- eligibility grade (`eligible`, `share-policy-blocked`, `seat-policy-blocked`, `sleep-blocked`, `paused-limited`, `unknown`)
- source grade for subject (`full-byte-source-present`, `placeholder-only-present`, `ghost-announced-no-source`, `source-may-exist-offline`, `not-applicable`, `unknown`)
- strongest safe sentence
- stronger forbidden sentence
- next strengthening observation
- freshness of each observation plane

## Primary questions this page must answer

1. Is this peer only listed, or actually connected now?
2. If connected, is it actually eligible to participate for this share?
3. If a subject is in view, does any currently present peer still have full bytes for it?
4. What exact sentence is still honest right now?
5. What future observation would justify a stronger sentence?

## Layout

### A. Presence verdict strip

Fields:

- peer label
- optional subject label
- current presence witness grade
- strongest safe sentence

Example verdicts:

- `Peer is historically listed but not connected now`
- `Peer is connected now, but this share is forbidden on the current network`
- `Peer is visible and eligible, but no current byte source is proven for this subject`
- `Peer is connected and eligible; full bytes for this subject are present on this peer`

### B. Listedness card

Show:

- whether the peer is merely in historical total
- whether it is hidden from view rather than revoked
- whether it aged out of ordinary connection view
- freshness of the listing observation

This card exists so the operator can stop treating roster presence as live participation proof.

### C. Route / connection card

Show:

- online/offline witness
- whether the witness comes from live connection, stale roster memory, or inferred absence
- whether pause or sleep affects what the online dot means
- current sync/posture mode if relevant

### D. Eligibility card

Show:

- whether this share may currently connect / detect / transfer on this seat
- whether the blocker is share policy, seat policy, sleep policy, or pause semantics
- strongest capability still allowed
- strongest capability currently blocked

### E. Source-grade card

If a subject is in scope, show:

- whether a current full-byte source is proven
- whether only placeholders are known
- whether the subject is merely announced without any current byte source
- whether an offline peer may still carry the latest bytes
- current fetchability implication

### F. Claim ceiling card

Show together:

- strongest safe sentence
- stronger forbidden sentence
- blocker or missing witness
- next observation that would strengthen the claim

## Compact row contract

A compact row should preserve this order:

1. listing grade
2. route grade
3. eligibility grade
4. source grade
5. strongest safe sentence

Example:

```text
Historically listed     Disconnected     Unknown eligibility     No current byte source proven     Peer remains known but cannot currently serve this subject
```

## Behavior rules

- This page must appear whenever a visible row could be misread as stronger presence than the product can prove.
- The product must not treat `online dot`, `roster listed`, and `current source` as interchangeable.
- If source grade is weaker than peer grade, the weaker grade must win the visible sentence.
- If a hidden-offline device may return, the page must say so rather than implying removal.

## Success criteria

The page is successful only when an operator can answer:

1. what kind of presence proof exists
2. what stronger proof is still missing
3. whether this share is actually eligible now
4. whether current full bytes exist anywhere presently reachable
5. what statement the product may honestly make now
''',
    '603-peer-presence-review-page-online-offline-hidden-and-historical-peer-truth-interface-spec.md': '''# Peer presence review page — online, offline, hidden, and historical-peer truth interface spec

## Purpose

The archive already had membership and network-policy language.
What it still lacked was one exact page for the operator question:

> what does this peer row really mean right now: live peer, hidden peer, sleeping peer, paused peer, or merely historical peer memory?

## Core decision

Any non-trivial peer roster entry must compile to one first-class **Peer presence review** page.
That page is the semantic home of:

- current roster meaning
- live-connection witness
- hidden-vs-unlinked distinction
- pause / sleep / forbidden-network overlays
- strongest safe sentence and next reappearance basis

## Primary page layout

The page always renders the same top-level regions in the same order:

1. presence verdict strip
2. roster meaning card
3. live-witness card
4. overlays card
5. reappearance / receipt card

### 1) Presence verdict strip

Show:

- peer label
- current peer presence class (`live`, `listed-offline`, `hidden-offline`, `sleep-offline`, `paused-limited`, `historical-only`, `unknown`)
- strongest honest one-line summary

Allowed summaries:

- `Peer is connected now and visible in the roster`
- `Peer is hidden from view but not unlinked; it may reappear if it comes back online`
- `Peer is listed historically but currently disconnected`
- `Peer is online as a device, but this share is ineligible on the current network`
- `Peer is offline because the core is sleeping`

### 2) Roster meaning card

Show:

- whether the row comes from current connection or historical total
- whether the peer was hidden by the operator
- whether offline-aging or expiry settings may have changed roster visibility
- whether unlink or severance has actually occurred

The operator must be able to answer:

> is this row about current presence or only historical membership memory?

### 3) Live-witness card

Show:

- current connection witness
- last-confirmed online observation if known
- sync/posture mode for linked peers
- whether the connection evidence is direct, inferred, stale, or absent

### 4) Overlays card

Show rows for overlays that change how presence should be read:

- pause state
- share forbidden-network state
- seat mobile-data block
- auto-sleep / battery stop
- switched-off / no-core state

For each row show:

- applies now?
- strongest narrowed effect
- strongest unaffected nearby truth

### 5) Reappearance / receipt card

Show:

- whether automatic reappearance is expected
- what event would bring the peer back to live presence
- what event would actually remove or sever it instead
- resulting receipt class

## Behavior rules

- This page must appear whenever a peer row could otherwise overstate live participation.
- The product must not let `Hide device` read like `unlink` or `revoke`.
- The product must not let `online` read like `eligible for every share`.
- A stale or historical roster entry must visibly lose to fresher route evidence.

## Compact row contract

A compact row should preserve this order:

1. peer presence class
2. live witness freshness
3. most important overlay
4. strongest safe sentence
5. next reappearance basis

## Non-clone reason

Current official Resilio docs are candid about online dots, historical totals, hidden offline devices, forbidden-network stoppage, and auto-sleep.
AnonSync should keep the candor but own the review directly instead of leaving meaning split across roster, identity, and mobile help pages.
''',
    '604-subject-source-witness-page-announced-online-and-byte-source-grade-interface-spec.md': '''# Subject source witness page — announced, online, and byte-source grade interface spec

## Purpose

Provide one review surface for the operator question:

- is this subject merely announced in the tree
- is some peer currently online but only carrying placeholders
- is there a current full-byte source
- is the best-known source offline and therefore only a weaker hypothesis
- what safe sentence follows from those facts

## Core decision

Every meaningful `no source peers`, `ghost file`, `placeholder-only`, or ambiguous fetchability event should render one first-class **Subject source witness** page.
The receipt is not just troubleshooting detail.
It is the durable proof of what kind of source existence the product had actually established.

## Fixed page structure

### A. Source verdict strip

Show:

- subject label
- source witness grade (`full-byte-source-present`, `online-placeholder-only`, `ghost-announced-no-source`, `offline-source-likely`, `unknown`)
- strongest safe sentence
- generated time

### B. Announcement versus source card

Show together:

- tree announcement present?
- peer roster presence for candidate peers
- current full-byte source proven?
- placeholder-only presence proven?
- whether the subject may exist only on an offline peer

This card exists so the operator can stop treating name visibility as byte visibility.

### C. Candidate-source table

For each candidate peer show:

- peer presence grade
- eligibility grade for this share
- byte role (`full bytes`, `placeholder only`, `unknown`, `offline candidate`)
- latest freshness of that observation
- whether the peer could satisfy a fetch now

### D. Safe action card

Show the narrowest honest next moves, such as:

- `wait for offline candidate peer to return`
- `touch or move local up-to-date version if operator is certain`
- `ignore ghost warning`
- `open peer presence review`
- `move to broader repair only if continuity evidence weakens further`

### E. Safe language block

Show together:

- strongest safe sentence
- stronger forbidden sentence
- blocker basis

Examples:

- safe: `This subject is still announced, but no current byte source is proven`
- forbidden: `This file is available from another peer`
- safe: `An offline peer may still carry the latest bytes`
- forbidden: `The latest bytes are safely recoverable`

## Main row contract

A compact source row should preserve this order:

1. announcement state
2. current best source grade
3. strongest safe sentence
4. narrowest next move
5. stronger forbidden sentence or blocker hint

## Suggested object model

```text
subject_source_witness {
  witness_id,
  subject_ref,
  announcement_present,
  source_grade,
  candidate_peers[],
  strongest_safe_sentence,
  stronger_forbidden_sentence,
  blocker_basis,
  next_moves[],
  generated_at
}
```

## Success criteria

A good page lets a later operator answer:

1. whether the subject is only announced or actually source-backed
2. whether any present peer can currently serve bytes
3. whether placeholders are the only currently known form
4. what safe next move exists without overclaiming
5. what stronger sentence remains forbidden
''',
    '605-presence-witness-receipt-page-listedness-route-grade-and-source-proof-interface-spec.md': '''# Presence witness receipt page — listedness, route grade, and source-proof interface spec

## Purpose

Provide one durable receipt after any meaningful presence-grade event.
The receipt exists to answer:

- what kind of peer or subject presence was actually proven
- whether the proof was roster-only, connection-level, eligibility-level, or byte-source-level
- what strongest safe sentence the product emitted
- what stronger sentence remained forbidden
- how to reopen the relevant review later

## Core decision

Every peer-presence review, subject-source review, hidden-device event, source-loss warning, or presence-strengthening observation should emit a first-class **Presence witness receipt**.
The receipt is not just audit trivia.
It is the durable proof that the product gave a truthful sentence at the moment presence meaning changed.

## Fixed receipt structure

### A. Transition summary

Show:

- peer / seat / optional subject
- presence witness grade observed
- generated time

### B. Why it was graded that way

Show:

- listing grade
- route / connection grade
- eligibility grade
- source grade if subject is in scope
- trigger origin summary

### C. Safe language block

Show together:

- strongest safe sentence
- stronger forbidden sentence
- blocker basis

### D. Strengthening and weakening basis

Show:

- next observation that would strengthen the claim
- next observation that would weaken the claim
- best page to reopen
- whether another seat or surface is better suited for stronger proof

## Main row contract

A compact receipt row should preserve this order:

1. presence witness grade
2. strongest safe sentence
3. stronger forbidden sentence
4. next strengthening basis
5. reopen action

## Suggested object model

```text
presence_witness_receipt {
  receipt_id,
  seat_ref,
  peer_ref,
  subject_ref?,
  listing_grade,
  route_grade,
  eligibility_grade,
  source_grade,
  strongest_safe_sentence,
  stronger_forbidden_sentence,
  blocker_basis,
  strengthen_on[],
  weaken_on[],
  generated_at
}
```

## Success criteria

A good receipt lets a later operator answer:

1. what kind of presence was actually proven
2. what stronger proof was still missing
3. what sentence the product was allowed to say then
4. what stronger sentence remained forbidden
5. what future observation would justify changing the sentence
''',
}

for name, content in new_docs.items():
    (docs / name).write_text(content)

# --- append to major docs ---
def append(path, text):
    p = root / path
    existing = p.read_text()
    if text.strip() in existing:
        return
    p.write_text(existing.rstrip() + '\n\n\n' + text.strip() + '\n')

status_prepend = '''## Latest addendum — presence witness grade and source-proof truth after rev0234

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **presence witness / peer presence review / subject source witness / presence witness receipt**

Current official Resilio docs still show a practical product, but they also still show that one ordinary answer to `what is actually present enough here for me to trust this peer row or file row?` can depend on:

- whether `X of Y peers` is showing live peers or merely historical total peers
- whether a peer was hidden from view rather than unlinked
- whether an online dot is only proving connection while forbidden-network, pause, or sleep policy still narrows participation
- whether any currently present peer still has full bytes for the subject
- whether the current row is only a ghost announcement waiting for an offline source that may never return

So the tighter non-clone line is:

> borrow Resilio's candor that listedness, connection, eligibility, and current source-proof are materially different truths, but refuse any product contract where those still require hopping across peer-list, identity, mobile, pause, and troubleshooting docs.

That yields four more ordinary product-owned pages:

- **Presence witness**
- **Peer presence review**
- **Subject source witness**
- **Presence witness receipt**
'''
status_path = docs / '00-status.md'
status_existing = status_path.read_text()
if status_prepend.strip() not in status_existing:
    status_path.write_text(status_prepend.strip() + '\n\n\n' + status_existing)

append('docs/10-resilio-sync-evaluation.md', '''## Revision addendum — presence witness grade, hidden-listed peers, and source-proof truth after rev0234

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **presence witness / peer presence review / subject source witness / presence witness receipt**

Current official docs still show a practical product, but they also still show that one ordinary answer to `what is actually present enough here for me to trust this peer row or file row?` can depend on peer-list totals, hidden-offline behavior, green/grey dots, forbidden-network state, pause semantics, sleep policy, source-device online status, and ghost-file warnings.

That gives AnonSync a cleaner rule: presence is not one bit. The product should own one typed answer for listedness, route presence, policy eligibility, and current byte-source sufficiency before it lets any peer row, subject row, or recovery suggestion read as stronger proof than the evidence supports.''')

append('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', '''## Revision addendum — borrow line after rev0234: presence witness is real; presence archaeology is not acceptable

Borrow from Resilio:

- the candor that `X of Y peers`, online dots, hidden devices, forbidden-network states, sleep states, and no-source warnings are materially different facts
- the willingness to say when a subject is announced without any current byte source
- the admission that a hidden device can still return and a switched-off source cannot serve bytes

Do not clone from Resilio:

- making current presence meaning depend on reading peer-list, identity, mobile, pause, and troubleshooting docs together
- letting roster presence feel like live source proof
- hiding the difference between connected peer and current byte source

Score this area as:

- **Borrow strongly:** typed presence and source-proof truths
- **Do not clone:** article-fragmented presence inference
- **Replace with:** presence witness, peer presence review, subject source witness, presence witness receipt''')

append('docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md', '''## Revision addendum — clone-veto after rev0234: listed peers may not masquerade as live or source-proving peers

Another current Resilio pass sharpens four more veto tests.

### Veto test 1 — historical roster entry hidden behind live-looking peer row

If the product can show a peer row without proving whether it is only historically listed or actually connected now, it fails.

### Veto test 2 — hidden-offline interpreted as unlinked or gone

If the product can hide a peer from view without preserving the truth that it may reappear and still shares as before, it fails.

### Veto test 3 — connected peer interpreted as current byte source

If the product can show online presence without proving whether any full bytes remain for the subject, it fails.

### Veto test 4 — presence receipt omits proof grade

If the durable receipt can describe a presence event without naming listedness, route grade, eligibility grade, and source grade, it fails.

### New page obligations from this pass

The archive now owes four more ordinary pages:

- **Presence witness**
- **Peer presence review**
- **Subject source witness**
- **Presence witness receipt**''')

append('docs/20-product-direction.md', '''## Revision addendum — product direction after rev0234: presence witness is a first-class reviewed object

AnonSync should treat presence as graded proof, not as a single status icon.

That means:

- model listedness, live connection, policy eligibility, and source sufficiency as separate presence-bearing fields
- show the strongest safe sentence before any peer row, file row, or recovery hint can overclaim
- separate `historically listed`, `live and eligible`, `present but ineligible`, and `announced without source` as distinct product states
- keep presence-witness receipts durable so later cleanup, recovery, and operator communication do not depend on roster folklore''')

append('docs/30-interface-spec.md', '''## Revision addendum — interface grammar after rev0234: name the witness grade before naming the presence claim

The core interface grammar should now explicitly preserve another adjacency rule:

- whenever presence matters, every serious surface must keep **listedness grade**, **route grade**, **eligibility grade**, and **source grade** adjacent
- whenever a peer row changes meaning, every serious surface must keep **live now**, **historical only**, and **may reappear** distinct
- whenever a subject is visible but fetchability is in doubt, every serious surface must keep **announcement**, **candidate source**, and **current byte-source proof** adjacent

The product should not let a peer dot or file row stand in for the whole presence story.''')

append('docs/38-operator-workbench-interface-spec.md', '''## Revision addendum — operator workbench after rev0234: presence queue and source-proof card

The operator workbench should grow two durable elements:

- a **Presence queue** showing peers and subjects whose visible rows overstate current proof
- a **Source-proof card** showing which visible subjects are fully source-backed, placeholder-only, ghost-announced, or waiting on offline candidates

This keeps presence archaeology from collapsing into peer-list folklore.''')

append('docs/39-interface-pattern-language.md', '''## Revision addendum — new pattern after rev0234: listed is not live; live is not source

A serious AnonSync surface should not start with `peer is here` or `file is available` as if one visible row proved the whole thing.
It should first name the witness grade: listedness, live connection, participation eligibility, and byte-source sufficiency.

Pattern name: **Listed is not live; live is not source.**''')

append('docs/40-architecture-decisions.md', '''## Revision addendum — architecture decision after rev0234: presence proof is multi-plane

Decision:

- represent presence proof as first-class typed objects keyed by seat, peer, share, and optional subject
- record listedness, route witness, eligibility witness, and source witness separately rather than collapsing them into one `online` field
- bind receipts and claim ceilings to presence events so later surfaces can explain aftermath without reconstructing several help-page semantics

Rationale:

Current Resilio docs still show that historical roster presence, current connection, current eligibility, and full-byte source availability can diverge materially. AnonSync should therefore not encode presence as a flat status badge.''')

append('docs/50-roadmap.md', '''## Revision addendum — roadmap after rev0234: presence witness grade tranche

Near-term work newly justified by this pass:

1. Add presence-witness object model and claim-ceiling binding.
2. Build presence witness and peer presence review pages.
3. Add subject source-witness review before stronger fetch/recovery claims.
4. Emit presence-witness receipts and workbench cards for overclaim-prone rows.
5. Connect presence receipts into peer lists, ghost warnings, recovery hints, and operator-facing language surfaces.''')

append('docs/sources.md', '''## Revision addendum — presence witness grade, hidden-listed peers, and source-proof truth after rev0234

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about peer-list totals, linked-device dots and modes, hidden offline devices, no-source warnings, mobile network stoppage, auto-sleep, pause semantics, switched-off devices, and the live v3 line.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that `listed`, `online`, `eligible`, and `has a current source` are materially different truths rather than one `present` bit?

> where do those same current docs still show that the ordinary operator answer about `what is actually present enough here for me to trust this row or subject?` still depends on hopping across several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Sync Main View (Desktop)` article, which still says `X of Y peers` means `X` online now and `Y` total including offline, and still says offline peers disconnect after 7 days by default.
- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linked devices show green/grey dots for online/offline and display selected sync modes.
- Resilio's current `How to clear offline devices?` article, which still says clearing only hides a device from view and does not unlink it, and that it reappears if it comes back online.
- Resilio's current `Setting network interface per share`, `Settings on mobile platforms`, and `Configuring Auto Sleep & Battery Saver (Android)` articles, which still say visible shares can be forbidden-network or sleep-blocked rather than route-broken.
- Resilio's current `How to pause syncing` article, which still says pause stops payload movement but not every non-payload effect.
- Resilio's current `Cannot download files / These files cannot be downloaded as there are no source peers online for too long time` article, which still describes ghost-file states where subjects are announced but nobody currently has the bytes.
- Resilio's current `Will my devices still sync when switched off?` article, which still says a source device must actually be online for syncing to work.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the live `3.1.2.1076` line.

## Additional Resilio official sources emphasized in rev0235

- Sync Main View (Desktop)  
  https://help.resilio.com/hc/en-us/articles/204755009-Sync-Main-View-Desktop

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- How to clear offline devices? (desktop only)  
  https://help.resilio.com/hc/en-us/articles/204762439-How-to-clear-offline-devices-desktop-only

- Setting network interface per share  
  https://help.resilio.com/hc/en-us/articles/360001411244-Setting-network-interface-per-share

- Settings on mobile platforms  
  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms

- Configuring Auto Sleep & Battery Saver (Android)  
  https://help.resilio.com/hc/en-us/articles/204762699-Configuring-Auto-Sleep-Battery-Saver-Android

- How to pause syncing  
  https://help.resilio.com/hc/en-us/articles/206217325-How-to-pause-syncing

- Cannot download files / These files cannot be downloaded as there are no source peers online for too long time.  
  https://help.resilio.com/hc/en-us/articles/360010899719-Cannot-download-files-These-files-cannot-be-downloaded-as-there-are-no-source-peers-online-for-too-long-time

- Will my devices still sync when switched off?  
  https://help.resilio.com/hc/en-us/articles/204754199-Will-my-devices-still-sync-when-switched-off

- Resilio Sync 3.0 change log  
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log''')

# Rename root folder
new_root = root.parent / f'AnonSync-{new_rev}-{new_ts}-{new_code}'
if new_root.exists():
    # clean any previous attempt
    import shutil
    shutil.rmtree(new_root)
root.rename(new_root)
print(new_root)
