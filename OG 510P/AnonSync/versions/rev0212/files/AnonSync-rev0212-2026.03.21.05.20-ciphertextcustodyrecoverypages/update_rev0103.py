from pathlib import Path
import re

ROOT = Path('.')

rev = 'rev0103'
ts = '2026.03.18.06.07'
codename = 'reissuelineageboundaryharbor'


def read(path):
    return Path(path).read_text()

def write(path, text):
    Path(path).write_text(text)

# New spec content
new_spec = '''# Offer reissue lineage, successor-artifact boundary, and budget-reset interface spec

## Purpose

The archive already separates:

- offer-artifact lifetime from durable trust promotion
- sender intent from actual redeemer identity
- artifact-level budget from per-attempt trust fanout
- repeated-attempt equivalence from honest slot treatment

One real gap still remained:

> once the honest next action becomes `reissue new artifact`, the operator still needs one explicit answer to whether the replacement artifact is a true fresh invitation, a narrow successor for the same governed subject, or a risky continuation that is carrying forward too much from the old artifact.

This document turns that boundary into one explicit interface contract.
It is the successor-lineage companion to `112-offer-artifact-expiry-and-trust-promotion-boundary-interface-spec.md`, `114-offer-redemption-ledger-and-multi-redeemer-trust-fanout-interface-spec.md`, and `115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md`.

## Why this needs its own spec

Current Resilio docs still make this seam concrete in a useful but incomplete way.
`Sync Share Dialog (Desktop)` says a link may expire after `N` days, may be used only `N` times by whoever, and that after expiry new peers need a **new link from the folder owner**.
At the same time, `Sync functionality in detail` still says that by default you only need to approve a person once because Sync retains a certificate with their identity, while an optional setting can still require approval every time for another shared folder.
`Link structure and flow` still says successful approval mints certificate-backed access for the actual requester.

Taken together, those current docs imply a real operator question that still needs one cleaner contract:

- the old artifact may be expired, exhausted, or intentionally frozen
- the product may honestly recommend `reissue new artifact`
- the new artifact may target the same governed subject, a narrower subject, or a broader future audience
- some trust memory from the old artifact or old redeemer may still exist elsewhere
- without one lineage surface, the operator still has to reconstruct whether the new artifact is a fresh budget island or an accidental continuation of old assumptions

That is not a criticism of reissuing links.
It is a criticism of any surface that says only `get a new link from the folder owner` while leaving predecessor relation, carried-forward policy, and budget reset to folklore.
AnonSync should therefore expose one explicit **offer reissue lineage and successor-boundary contract** wherever a replacement artifact is created after expiry, exhaustion, mismatch, or explicit policy tightening.

## Core rule

A replacement artifact is not just another encoding of the old artifact unless the surface proves that it is.

The product must treat five facts as separate public facts:

1. why the predecessor artifact can no longer be used for this next admission story
2. whether the successor artifact is semantically identical, narrowed, broadened, or freshly scoped
3. which predecessor facts are intentionally carried forward
4. which predecessor facts definitely do **not** carry forward
5. which receipt later proves the exact predecessor-to-successor relation

The product is not fully inspectable until it can answer nine questions in one place:

1. which predecessor artifact is being replaced
2. which governed subject or subject set is in scope
3. why reissue was chosen instead of reusing the old artifact
4. whether the successor is same-scope, narrowed, broadened, or freshly scoped
5. whether the successor budget is a full reset, inherited cap, or intentionally zero until review completes
6. whether sender intent, redeemer expectations, approval requirements, or trust-promotion defaults changed
7. what durable trust from earlier redemptions still exists independently of the successor artifact
8. what tempting but unsafe continuity shortcut is being refused
9. which receipts later prove the predecessor/successor boundary

If the operator still has to infer from an old `expired` badge, remembered approval, and a new copied link whether the replacement artifact really reset the invitation story, the surface is not explicit enough.

## Public objects

### Offer reissue-lineage row

A compact read object describing one predecessor artifact, one successor artifact, and the reviewed relation between them.

Suggested fields:

- `offer_reissue_lineage_row_id`
- `predecessor_offer_ref`
- `successor_offer_ref`
- `subject_ref`
- `reissue_reason` (`expired`, `budget-exhausted`, `equivalence-too-weak`, `unexpected-redeemer`, `policy-tightened`, `operator-rotated`, `delivery-only-copy`, `unknown`)
- `successor_relation` (`same-scope-successor`, `narrowed-successor`, `broadened-successor`, `fresh-scope-successor`, `delivery-only-encoding`, `unknown`)
- `budget_reset_posture` (`fresh-budget-island`, `same-budget-family`, `carried-cap-with-review`, `no-budget-until-review`, `unknown`)
- `carried_forward_policy_summary`
- `explicit_non_carry_summary`
- `recommended_next_action`
- `supporting_receipt_refs[]`

### Offer reissue-boundary explanation

A read object explaining why the successor is or is not a clean replacement boundary.

Suggested fields:

- `offer_reissue_boundary_explanation_id`
- `predecessor_offer_ref`
- `successor_offer_ref`
- `subject_ref`
- `reissue_reason`
- `successor_relation`
- `budget_reset_posture`
- `carried_forward_policy_summary`
- `non_effect_summary`
- `why`
- `proof_refs[]`

### Offer reissue review plan

A prepared review object for deciding whether a successor artifact should inherit, narrow, freeze, or freshly reset predecessor assumptions.

Suggested fields:

- `offer_reissue_plan_id`
- `predecessor_offer_ref`
- `successor_offer_ref` nullable
- `subject_ref`
- `requested_outcome` (`issue-fresh-successor`, `issue-narrowed-successor`, `issue-broadened-successor`, `re-encode-only`, `freeze-old-and-stop`, `reissue-after-fresh-approval`, `keep-current-policy`)
- `proposed_budget_reset_posture`
- `proposed_carry_forward_summary`
- `explicit_non_carry_summary`
- `effect_summary`
- `blockers[]`
- `receipt_promise`

### Offer successor-boundary receipt

A durable object proving how one successor artifact relates to one predecessor artifact.

Suggested fields:

- `offer_successor_boundary_receipt_id`
- `predecessor_offer_ref`
- `successor_offer_ref`
- `subject_ref`
- `reissue_reason`
- `successor_relation`
- `budget_reset_posture`
- `carried_forward_policy_summary`
- `explicit_non_carry_summary`
- `outcome`
- `reviewed_at`
- `proof_refs[]`

## Reissue reasons

### `expired`

Use when the predecessor artifact naturally aged out and a later admission needs a successor artifact.

### `budget-exhausted`

Use when the predecessor artifact has no remaining shared redemption budget.

### `equivalence-too-weak`

Use when the current attempt could not honestly collapse into an earlier slot and the remaining artifact is no longer the right vessel.

### `unexpected-redeemer`

Use when sender intent and actual redeemer mismatch makes reissue safer than stretching the predecessor.

### `policy-tightened`

Use when approval, reuse, or scope policy became stricter and a fresh artifact boundary is part of the safety story.

### `operator-rotated`

Use when the operator intentionally rotates the artifact even though budget may technically remain.

### `delivery-only-copy`

Use only when the operator is changing encoding or transport wrapper without changing the artifact's semantic identity.
This class must be rare and rendered with stronger proof requirements.

## Successor relations

### `same-scope-successor`

Use when the successor governs the same subject and same authority class but intentionally starts a fresh artifact story.

### `narrowed-successor`

Use when the successor keeps part of the predecessor's purpose but reduces audience, role, scope, or reuse policy.

### `broadened-successor`

Use when the successor intentionally widens a predecessor boundary.
This class should require stronger review language.

### `fresh-scope-successor`

Use when the successor starts a new governed subject story and should not be rendered as mere continuation.

### `delivery-only-encoding`

Use when the artifact's semantic identity is unchanged and only its packaging changed.
This class must never silently reset budget or trust lineage.

## Budget reset postures

### `fresh-budget-island`

Use when the successor artifact starts a fully separate redemption budget and should not be confused with predecessor slot history.

### `same-budget-family`

Use when the successor intentionally remains inside one shared budget family.
This class should be rare and rendered with strong caution.

### `carried-cap-with-review`

Use when some predecessor budget constraint intentionally follows the successor, but only because explicit review said so.

### `no-budget-until-review`

Use when the successor object exists in draft or frozen form but cannot yet be redeemed.

## Fixed inspection order

Every reissue-lineage surface should preserve the same sections in the same order:

1. **Predecessor posture and why it stopped being the right artifact**
2. **Successor scope and relation to predecessor**
3. **Budget reset and carry-forward policy**
4. **What definitely is not being carried forward**
5. **Admissible reviewed outcomes**
6. **Receipts and proof links**

### 1) Predecessor posture and why it stopped being the right artifact

This section should show:

- predecessor artifact ID
- predecessor terminal or risky posture
- governed subject in scope
- reissue reason
- next honest action before any successor is assumed

### 2) Successor scope and relation to predecessor

This section should show:

- whether a successor already exists or is still a draft
- successor relation class
- whether sender intent, redeemer expectations, approval policy, or trust-promotion defaults changed
- whether the successor is merely a re-encoding or a genuinely new invitation boundary

### 3) Budget reset and carry-forward policy

This section should show:

- budget reset posture
- whether old slot history still matters for explanation only or for future budget accounting
- any explicit carried-forward constraints
- any explicit carried-forward trust that survives independently of the successor artifact

### 4) What definitely is not being carried forward

This section should make the strongest non-claims obvious.
Examples:

- `new link does not erase earlier successful redemption receipts`
- `fresh successor does not silently inherit old sender-intent match outcome`
- `same subject does not imply same budget family`
- `delivery-only copy does not reset expiry or use count`
- `remembered approval may still exist, but it is not evidence that this successor stayed narrow enough`

### 5) Admissible reviewed outcomes

Admissible outcomes should include:

- `Issue fresh successor`
- `Issue narrowed successor`
- `Issue successor after fresh approval`
- `Record delivery-only re-encoding`
- `Freeze predecessor and stop`
- `Require broader review before issue`

### 6) Receipts and proof links

This section should link separately to:

- predecessor artifact receipt
- predecessor redemption or accounting receipts that motivated reissue
- successor issue receipt or draft plan
- successor-boundary receipt proving what did and did not carry forward

## Surface rules

- `Reissue new artifact` must always open a predecessor/successor boundary review unless the action is provably `delivery-only-encoding`
- a successor artifact must never silently inherit predecessor budget exhaustion, mismatch acceptance, or sender-intent match outcome without explicit carry-forward language
- a `delivery-only-encoding` outcome must be rendered distinctly from `issue fresh successor`
- if a successor broadens audience, role, or reuse policy, the surface must say `broadened successor` plainly rather than calling it mere reissue
- dense/mobile surfaces may compress prose, but they must still keep predecessor posture, successor relation, budget reset posture, and next honest action adjacent

## Non-clone conclusion

Resilio's current docs still make `get a new link from the folder owner` a useful operational answer, but not yet a complete governance answer.
AnonSync should keep the convenience of easy reissue while refusing to let successor artifacts blur into predecessor history.
A replacement artifact must have one explicit lineage boundary so operators can tell whether they started a fresh invitation story, continued one under review, or accidentally carried forward more trust and budget than they meant to.
'''

# README
readme = read('README.md')
readme = re.sub(r'- Revision: `rev0102`', f'- Revision: `{rev}`', readme)
readme = re.sub(r'- Timestamp: `2026\.03\.18\.05\.48` \(America/New_York\)', f'- Timestamp: `{ts}` (America/New_York)', readme)
readme = re.sub(r'- Codename: `equivalencebudgettruthharbor`', f'- Codename: `{codename}`', readme)
readme = re.sub(r'## What changed in this revision\n\nThis revision continues directly from `rev0101` and does six things:\n\n(?:.|\n)*?## Current conclusion',
f'''## What changed in this revision

This revision continues directly from `rev0102` and does six things:

1. Re-checks **Resilio Sync** again around the remaining successor-artifact seam: current docs still say expired links require a **new link from the folder owner**, bounded-use links still fail at `N+1`, and remembered approval can still survive separately across later sharing.
2. Adds a dedicated **offer reissue lineage and successor-boundary interface spec** so the archive no longer stops at `require new artifact`, but also answers `what exactly is the predecessor being replaced for?`, `what carries forward?`, `what definitely does not?`, and `is this truly fresh budget or merely a new encoding of the old invitation?`
3. Tightens the **evaluation** so the non-clone case against Resilio gets sharper again: the product still has useful bounded-use links and durable approval memory, but current docs still leave `new link` too close to a vague continuation story.
4. Extends the **interface, daemon/API, and offer-artifact contract** with reissue-lineage rows, successor-boundary explanations, review plans, and receipts so clients can render `fresh budget island`, `narrowed successor`, `delivery-only copy`, or `broadened successor` without folklore.
5. Adds an additional **canonical flow** showing the new distinction this revision wants: once one artifact is exhausted or too ambiguous to stretch further, the product must expose one predecessor/successor review instead of pretending the next copied link is self-explanatory.
6. Refreshes the **workbench, pattern language, ADRs, roadmap, offer-artifact spec, open questions, status, and reading order** so future revisions keep **reissue lineage separate from raw offer recreation** wherever portable invitation mechanics, approval reuse, and later durable trust meet.

## Current conclusion''',
readme, flags=re.S)
readme = readme.replace('which later attempt is really comparable to which earlier one?', 'which later attempt is really comparable to which earlier one?')
readme = readme.replace('and get one explicit answer with artifact budget, ordered attempts, equivalence class, slot effect, safe reissue guidance, and linked receipts.',
                        'and get one explicit answer with artifact budget, ordered attempts, equivalence class, slot effect, safe reissue guidance, predecessor/successor boundary, and linked receipts.')
readme = readme.replace('- `docs/115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md` — fixed slot-accounting review anatomy for repeated/familiar redemption attempts, equivalence classes, slot effects, and accounting receipts\n',
                        '- `docs/115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md` — fixed slot-accounting review anatomy for repeated/familiar redemption attempts, equivalence classes, slot effects, and accounting receipts\n- `docs/116-offer-reissue-lineage-and-successor-boundary-interface-spec.md` — fixed predecessor/successor review anatomy for reissue reasons, successor relation, budget reset posture, explicit carry-forward limits, and successor-boundary receipts\n')
readme = readme.replace('then `115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md`, then `68-successor-cutover-and-rehome-interface-spec.md`',
                        'then `115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md`, then `116-offer-reissue-lineage-and-successor-boundary-interface-spec.md`, then `68-successor-cutover-and-rehome-interface-spec.md`')
write('README.md', readme)

# Status
status = read('docs/00-status.md')
status = status.replace('This revision is an in-place continuation of `rev0101`', 'This revision is an in-place continuation of `rev0102`')
status = status.replace('spend more time on interface specs, especially where portable offers may be reused, replayed, or hit again by a familiar redeemer while still carrying a shared budget',
                        'spend more time on interface specs, especially where portable offers have reached the honest `reissue` threshold and need a real predecessor/successor boundary')
status = re.sub(r'## Immediate output of this pass\n\n(?:.|\n)*?## The main shift',
'''## Immediate output of this pass

The archive now contains:

- a fairer Resilio comparison that explicitly grants current strengths — maintained Sync v3, bounded-use links, approval-time identity review, prior-approval reuse, and real convenience — while still naming the sharper reason not to clone its `new link from the owner` story wholesale
- a new **offer reissue lineage and successor-boundary interface spec** that defines how one surface should answer `why did we stop using the predecessor artifact?`, `is this successor same-scope, narrowed, broadened, or fresh-scope?`, `what budget posture does it start with?`, and `what definitely did not carry forward?`
- stronger interface, offer-artifact, and daemon/API requirements so reissue-lineage rows, successor-boundary explanations, reissue plans, and successor-boundary receipts become first-class surfaces instead of something reconstructed from expiry badges, exhausted budgets, and remembered approval folklore
- stronger workbench and pattern-language rules so `predecessor posture`, `successor relation`, `budget reset posture`, and `next honest action` remain adjacent across dense and full surfaces
- an additional canonical flow showing the core split this revision wants: `require new artifact` is not the end of the story; the operator also needs one explicit predecessor/successor review before the replacement artifact is trusted
- README, roadmap, ADR, source-note, open-question, status, and reading-order updates so future revisions keep **reissue lineage separate from raw offer recreation** central wherever portable invitation mechanics, approval reuse, and later durable trust meet

## The main shift''', status, flags=re.S)
status = re.sub(r'`rev0101` proved that a serious operator surface needs a public redemption ledger\.\n\n`rev0102` tightens the lifecycle one level further:\n\n> it is not enough to know which attempts hit the artifact\. A serious operator product must also say which later attempts are genuinely new admissions, which are equivalent to an earlier slot, and which should be stopped until a new artifact is issued\.\n\nThat changes the archive in five specific ways:\n\n(?:.|\n)*?## What still remains unresolved',
'''`rev0101` proved that a serious operator surface needs a public redemption ledger.

`rev0102` proved that familiar attempts still need explicit equivalence and slot treatment.

`rev0103` tightens the lifecycle one level further:

> it is not enough to say `require new artifact`. A serious operator product must also say whether the replacement artifact is a fresh invitation boundary, a narrowed successor, a broadened successor, or merely a delivery-only re-encoding of the predecessor.

That changes the archive in five specific ways:

- `reissue new artifact` now opens a predecessor/successor boundary review instead of acting like a self-explanatory terminal recommendation
- successor artifacts now have to say whether they are same-scope, narrowed, broadened, or fresh-scope relative to the predecessor
- budget reset posture is now first-class, so `fresh budget island`, `same budget family`, and `delivery-only copy` stay visibly different
- earlier trust, approval, or mismatch outcomes may now survive independently of the old artifact, but they can no longer masquerade as implicit carry-forward into the successor
- the non-clone case against Resilio gets tighter again: the missing piece is not reissue itself, but the absence of one explicit contract for what a `new link` actually means relative to the old one

## What still remains unresolved''', status, flags=re.S)
status = status.replace('- when same-family but different-seat attempts should collapse by default versus consume a fresh slot\n- whether some subject templates should default `same known peer, new subject` to `require new artifact` even when trust is still fresh\n- how aggressively dense/mobile surfaces should compress compare-against history before they recreate vague `already used by this person` folklore\n- whether suspicious failed attempts should permanently cool the accounting policy for the remaining budget\n- how much UI weight should be given to `require new artifact` when only one slot remains but equivalence proof is weak\n',
                        '- when some successors should be forced to start as `no budget until review` instead of immediately becoming redeemable\n- whether `delivery-only-encoding` should ever be user-visible in lightweight/mobile clients or stay review-only\n- how strongly old mismatch outcomes should bias the product toward `narrowed successor` instead of `same-scope successor`\n- whether some templates should forbid `same budget family` entirely so every successor is always a fresh budget island\n- how much UI weight should be given to predecessor/successor non-carry summaries before the surface becomes noisy\n')
status = status.replace('- `docs/115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md`\n- `update_rev0102.py`\n',
                        '- `docs/116-offer-reissue-lineage-and-successor-boundary-interface-spec.md`\n- `update_rev0103.py`\n')
status = status.replace('- `docs/64-critical-open-questions.md`\n- `docs/sources.md`\n',
                        '- `docs/64-critical-open-questions.md`\n- `docs/sources.md`\n')
write('docs/00-status.md', status)

# Evaluation append
val = read('docs/10-resilio-sync-evaluation.md')
addition = '''

### 10) Reissue still needs an explicit predecessor/successor boundary

Current Resilio docs still say a share link can expire after `N` days, can be limited to `N` uses, and that after expiry new peers need a **new link from the folder owner**.
At the same time, current approval docs still say you only need to approve a person once by default because Sync retains a certificate with their identity, while a stricter setting can still require approval every time for another shared folder.
That is useful, but it still leaves one governance seam too reconstructive:

> when the next safe step is `get a new link`, is that new artifact merely a fresh delivery wrapper, a clean budget reset, a narrowed invitation, or a broader continuation of remembered trust?

AnonSync should keep easy reissue.
It should not clone a surface where successor-artifact meaning has to be inferred from old expiry badges, remembered approval, and later behavior.
The product should expose one explicit predecessor/successor lineage boundary so operators can see what carried forward, what definitely did not, and whether the replacement artifact started a genuinely fresh invitation story.
'''
if addition not in val:
    val += addition
write('docs/10-resilio-sync-evaluation.md', val)

# Interface spec append
iface = read('docs/30-interface-spec.md')
iface += '''

## Offer reissue-lineage and successor-boundary surfaces

Use one explicit family for predecessor/successor artifact boundaries instead of expecting operators to infer what `new link` means from expiry, exhaustion, or remembered approval.

```text
anonsync offer reissue-lineage list --seat self --scope active-offers
anonsync offer reissue-lineage show --predecessor off_01J... --subject incoming:photos-2026
anonsync offer reissue-lineage prepare --predecessor off_01J... --subject incoming:photos-2026 --outcome issue-narrowed-successor --plan
anonsync offer reissue-lineage apply orl_01J...
```

Rules:

- every meaningful `reissue new artifact` action must also expose a reissue-lineage view keyed to one predecessor artifact and one governed subject when relevant
- every reissue-lineage surface must preserve one predecessor posture, one successor relation, one budget reset posture, one explicit non-carry summary, and one next honest action
- `new link` must never silently imply `fresh budget island`; the budget reset posture must say `fresh budget island`, `same budget family`, `carried cap with review`, `no budget until review`, or another equally explicit state
- `reissue-lineage show ... --view review` must render a fixed group order: `predecessor posture and why it stopped being the right artifact`, `successor scope and relation to predecessor`, `budget reset and carry-forward policy`, `what definitely is not being carried forward`, `admissible reviewed outcomes`, `receipts and proofs`
- `delivery-only-encoding` must render distinctly from `issue fresh successor`
- successor-boundary review must never silently widen audience, change sender-intent posture, reset expiry/use-count, or carry mismatch outcomes forward without explicit language
- the primary verb in rich or textual surfaces should inherit the truthful lineage label (`Issue fresh successor`, `Issue narrowed successor`, `Record delivery-only copy`, `Freeze predecessor and stop`) instead of collapsing back to generic `Copy link` or `Share again`
'''
write('docs/30-interface-spec.md', iface)

# API append
api = read('docs/31-daemon-api-spec.md')
api += '''

## Offer reissue-lineage and successor-boundary API contract

```text
GET  /v1/offer-reissue-lineage-rows
GET  /v1/offer-reissue-lineage-rows/{offer_reissue_lineage_row_id}
GET  /v1/offer-reissue-boundary-explanations/{offer_reissue_boundary_explanation_id}
POST /v1/offer-reissue-plans
GET  /v1/offer-reissue-plans/{offer_reissue_plan_id}
POST /v1/offer-reissue-plans/{offer_reissue_plan_id}/apply
GET  /v1/offer-successor-boundary-receipts/{offer_successor_boundary_receipt_id}
```

Rules:

- `offer-reissue-lineage-rows` must make predecessor posture, successor relation, budget reset posture, and recommended next action available without forcing clients to diff two raw offer manifests manually
- `offer-reissue-boundary-explanations` must say what carried forward and what definitely did not
- `offer-reissue-plans` must reject ambiguous `delivery-only` requests when scope, budget, or policy drift means the successor is actually semantically new
- successor-boundary receipts must remain readable even if both predecessor and successor later expire, are revoked, or disappear from default active lists
'''
write('docs/31-daemon-api-spec.md', api)

# Flows append
flows = read('docs/32-interface-flows.md')
flows += '''

## Flow 162 — exhausted artifact, narrowed successor, and honest budget reset

### Situation

- Maya created a two-use portable offer for `incoming:family-album-2026`
- slot 1 went to `tablet-lapis`
- slot 2 was consumed by a carefully reviewed but broader-than-ideal redemption path
- Maya now wants to admit `Noah-laptop`, but the archive has already concluded the old artifact should not be stretched any further
- the product must not pretend that copying a fresh link is self-explanatory

### Expected surface

1. The operator opens:

   - `anonsync offer reissue-lineage show --predecessor off_01Jalbum_multi --subject incoming:family-album-2026`

2. The review pane preserves this order:

   - predecessor posture and why it stopped being the right artifact
   - successor scope and relation to predecessor
   - budget reset and carry-forward policy
   - what definitely is not being carried forward
   - admissible reviewed outcomes
   - receipts and proof links

3. The predecessor section says:

   - `predecessor -> off_01Jalbum_multi`
   - `terminal posture -> budget exhausted`
   - `reissue reason -> budget exhausted plus earlier broader-than-ideal redemption history`
   - `next honest action -> review successor boundary before issue`

4. The successor section says:

   - `requested outcome -> issue narrowed successor`
   - `successor relation -> narrowed successor`
   - `sender intent -> reviewed seat expected`
   - `approval policy -> all peers require approval`
   - `trust promotion default -> subject only`

5. The budget section says:

   - `budget reset posture -> fresh budget island`
   - `predecessor slot history -> explanation only`
   - `carried forward -> same governed subject label`
   - `not carried forward -> old remaining budget (none), old mismatch tolerance, old broader trust default`

6. The non-claims section says:

   - `issuing the successor does not erase earlier redemption receipts`
   - `same governed subject does not imply same budget family`
   - `remembered approval from earlier peers does not auto-admit Noah through the successor`
   - `new encoding would not have been enough here; this is a genuine successor boundary`

### Why this matters

A weaker product shape would say only `link expired/used up, create new link` and leave the operator to reconstruct whether the replacement artifact really started a fresh story.
This flow proves the archive wants a stricter contract: predecessor posture first, successor relation second, budget reset and non-carry facts third, and only then issuance of the replacement artifact.
'''
write('docs/32-interface-flows.md', flows)

# Workbench append
wb = read('docs/38-operator-workbench-interface-spec.md')
wb += '''

## Offer reissue-lineage cards

Dense cards for artifacts that reached a real `reissue` threshold should render:

- `Predecessor` — expired, exhausted, mismatch-cooled, or policy-tightened
- `Successor relation` — same-scope successor, narrowed successor, broadened successor, fresh-scope successor, or delivery-only copy
- `Budget reset` — fresh island, same family, carried cap, no budget until review
- `Next action` — often `Issue narrowed successor`, `Review carry-forward`, or `Record delivery-only copy`

Rules:

- dense cards must keep `Predecessor`, `Successor relation`, and `Budget reset` adjacent
- dense cards must not compress genuine successor issuance into one vague `New link created` badge
- when the successor is narrowed or freshly scoped, the card should prefer that truthful label over generic `Reissued`
'''
write('docs/38-operator-workbench-interface-spec.md', wb)

# Pattern append
patterns = read('docs/39-interface-pattern-language.md')
patterns += '''

## Pattern 61 — reissue must show predecessor truth, not just successor convenience

Portable-offer surfaces must not collapse `new link` into one generic recovery action.

They should answer, in order:

1. why the predecessor stopped being the right artifact
2. whether the successor is same-scope, narrowed, broadened, or merely re-encoded
3. what budget posture the successor begins with
4. what definitely is not carried forward
5. what the next honest action is

Bad compression:

- `New link created`
- `Share again`
- `Fresh invite`

Good compression:

- `Predecessor exhausted`
- `Narrowed successor`
- `Fresh budget island`
- `Old broader trust default not carried forward`
- `Next safe action: issue after approval`
'''
write('docs/39-interface-pattern-language.md', patterns)

# ADR append
adrs = read('docs/40-architecture-decisions.md')
adrs += '''

## ADR-116 — successor artifacts must have explicit predecessor lineage and budget-reset truth

**Status:** Accepted

**Context:** Current Resilio docs still say expired links require a new link from the owner, bounded-use links fail at `N+1`, and remembered approval can still survive separately across later sharing. Once the product already knows the right answer is `require new artifact`, operators otherwise still have to reconstruct whether the replacement is just another wrapper for the same invitation story or a genuinely fresh boundary with narrower policy and reset budget.

**Decision:** AnonSync will model reissue lineage and successor-boundary review as a first-class layer with predecessor posture, successor relation, budget-reset posture, explicit carry-forward summaries, non-carry summaries, and durable successor-boundary receipts.

**Consequences:**

- `reissue new artifact` becomes a reviewable governance act rather than a shallow convenience verb
- successor artifacts can honestly say whether they are same-scope, narrowed, broadened, fresh-scope, or delivery-only
- delivery-only copies stop masquerading as fresh budget islands
- UI/API must support predecessor/successor receipts so later audit can tell what really changed at reissue time
'''
write('docs/40-architecture-decisions.md', adrs)

# Roadmap append
roadmap = read('docs/50-roadmap.md')
roadmap += '''

## Revision addendum — successor-artifact lineage and budget reset

This revision adds the next offer-governance layer:

- reissue-lineage, successor-boundary-explanation, and successor-boundary-receipt object model work so `require new artifact` can become one explicit predecessor/successor contract instead of a vague restart gesture
- UI and API work so `fresh budget island`, `narrowed successor`, `delivery-only copy`, and `broadened successor` stay visibly distinct
- lineage work linking replacement artifacts back to the exact predecessor posture and accounting or mismatch history that made reissue honest
'''
write('docs/50-roadmap.md', roadmap)

# Offer artifact spec append
offer = read('docs/52-capability-offer-and-claim-artifact-spec.md')
offer += '''

## Reissue is not enough; successor lineage must also be explicit

Once the product already knows the honest next action is `reissue new artifact`, the public artifact model must preserve one more layer of truth:

- predecessor artifact and terminal/risky posture
- reissue reason
- successor relation (`same-scope`, `narrowed`, `broadened`, `fresh-scope`, `delivery-only`)
- budget reset posture
- carried-forward policy summary
- explicit non-carry summary
- successor-boundary receipt

Offer semantics should remain honest about non-effects:

- creating a successor does not erase predecessor receipts
- same governed subject does not imply same budget family
- delivery-only re-encoding does not reset expiry or use count
- remembered approval may survive independently of the predecessor artifact, but it must not silently stand in for successor scope review
'''
write('docs/52-capability-offer-and-claim-artifact-spec.md', offer)

# Open questions append
questions = read('docs/64-critical-open-questions.md')
questions += '''

## 30) When should a successor artifact be forced to start as a fresh budget island?

The archive now separates raw offer recreation from explicit predecessor/successor lineage, but one policy seam still needs real judgment:

- when should `same governed subject` still default to `fresh budget island` instead of any shared budget family
- whether some tightly controlled templates should ever allow `carried cap with review`, or whether that is always too reconstructive
- how strongly old mismatch, broader-than-ideal redemption, or suspicious failed attempts should bias the product toward `narrowed successor`
- when `delivery-only-encoding` should be allowed at all instead of forcing full successor review

This matters because too much carry-forward recreates `new link, same hidden story`, while too little carry-forward could make ordinary safe reissue feel heavier than it needs to be.
'''
write('docs/64-critical-open-questions.md', questions)

# Sources update
sources = read('docs/sources.md')
sources = re.sub(r'# Source notes for rev0101\n\nThis revision leaned especially on the same current official Resilio sources already listed below, but with fresh attention on the multi-redemption seam: current share-dialog docs still expose `Only new peers`, `All peers`, and use-count controls where each `N\+1` attempt by whoever fails, while link-flow docs still say the actual requester is fingerprinted and granted certificate-backed access\.',
                 '# Source notes for rev0103\n\nThis revision leaned especially on the same current official Resilio sources already listed below, but with fresh attention on the successor-artifact seam: current share-dialog docs still say expired links require a new link from the owner and that each `N+1` attempt by whoever fails, while current approval/link-flow docs still say remembered approval can survive separately across later sharing and successful approval still mints certificate-backed access.',
                 sources, flags=re.S)
write('docs/sources.md', sources)

# Add new spec file
write('docs/116-offer-reissue-lineage-and-successor-boundary-interface-spec.md', new_spec)

# README/source note fix for rev title maybe any old rev numbers in README conclusion? not critical.

# Add to archive map if previous exact line absent fallback append near docs/115 mention
readme = read('README.md')
if 'docs/116-offer-reissue-lineage-and-successor-boundary-interface-spec.md' not in readme:
    readme = readme.replace('`docs/115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md`', '`docs/115-offer-redemption-equivalence-and-slot-consumption-policy-interface-spec.md`\n- `docs/116-offer-reissue-lineage-and-successor-boundary-interface-spec.md`')
write('README.md', readme)

# update status files list updated with new script
if not Path('update_rev0103.py').exists():
    pass

print('Applied rev0103 updates.')
