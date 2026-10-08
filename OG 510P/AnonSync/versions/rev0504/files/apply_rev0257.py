from pathlib import Path
import re

root = Path('/mnt/data/work0257')

rev = 'rev0257'
timestamp = '2026.03.21.22.26'
codename = 'replayclassshiftceiling'

# New docs content
new_docs = {
    'docs/711-resilio-replay-class-piece-shift-and-differential-sync-edition-evaluation.md': '''# Resilio replay class, piece shift, and differential-sync edition ceiling evaluation

## Why this seam matters

Another current official Resilio pass exposes a sharper non-clone reason than a generic `incremental sync is fast` slogan.
Resilio's public Sync FAQ still says files are split into pieces from **32 KB to 2 MB**, that usually **only changed pieces** are transferred, but that if the edit shifts all pieces the **whole file is re-synced** instead. The same official FAQ still says **Sync Business** has a **diff delta sync** feature for that shifted-file case. Official Resilio documentation for Active Everywhere goes even further: administrators can still choose whether to disable differential sync entirely, retain or drop hashes, and accept whole-file replay on slower disks or when hash availability is weak. The live Sync v3 help-center line still runs through **3.1.2.1076**.\n
That is exactly the kind of truth AnonSync should not hide under one reassuring sentence like `incremental`, `delta`, `efficient`, or `only changed parts`.
The real operator contract already has several materially different replay classes:

1. **piecewise replay** — changed pieces only
2. **shift-sensitive fallback** — whole-file resend when piece boundaries move
3. **diff-delta replay** — stronger changed-block replay when the edition/runtime supports it
4. **full-file replay by policy** — the system intentionally prefers resend over recheck because CPU/disk cost is judged too high

Resilio is candid that these are real.
The non-clone problem is again workflow ownership.
The operator still has to reconstruct the answer to `what replay class is actually in force for this file/job/seat right now?` from a consumer FAQ, enterprise/job-profile documentation, and performance-tuning guidance.

## What current official docs still say

### 1) Public Sync FAQ already narrows the `only changed pieces` promise

The current Sync FAQ still says:

- each file is split into pieces from 32 KB to 2 MB depending on file size
- only changed pieces are usually transferred
- if an edit shifts all pieces, the **whole file** is re-synced
- Sync Business has **diff delta sync** to avoid full re-sync even in that shifted-file case

That means the ordinary public promise is already not one thing.
It is a layered replay ladder.

### 2) Official enterprise documentation makes replay class policy-bearing

Current official Resilio documentation for pre-seeded synchronization still says that after a file is judged to need sync, the system follows the **Disable differential sync** parameter:

- `Yes` means the whole file is synced across the network
- `No` means the system checks file pieces, hashes them, discovers changed pieces, and syncs only those

The same documentation still ties replay quality to hash strategy and ownership reality:

- lazy indexing can leave only the owner with usable hashes
- forcing owner hashing or retaining hashes changes replay cost and future reuse
- weak or absent hash availability can turn changed-file replay back into heavier resend behavior

So replay class is not merely an implementation detail.
It is a real policy choice with CPU, disk, and network consequences.

### 3) Best-practice guidance shows the contract is workload-shaped, not universal

Current official Resilio best-practice pages for VDI / profile-style workloads still say:

- on slower storage it may be preferable to disable differential sync and just re-transfer the file
- on faster storage it may be worth rechecking and sending only changed pieces
- rolling-checksum choices affect whether shifted blocks can still be reused
- some storage families are advised to leave differential sync off because the local recheck cost is too high

That is strong operational candor.
But it also means the user-facing product should not collapse `changed file` into one imaginary replay path.

## Why AnonSync should not clone this contract

AnonSync should absolutely borrow the Resilio instinct that replay cost is a first-class operational truth and that the product should admit when CPU/disk cost can outweigh network savings.

AnonSync should **not** clone a contract where:

- `incremental` can still mean three or four materially different replay classes
- shift-sensitive fallback to full resend appears only after the fact
- stronger diff-delta capability is edition- or runtime-dependent without one ordinary posture page
- operators have to infer from help prose whether replay is limited by edit shape, hash availability, disk speed, or product tier

The product should instead surface one ordinary answer before a heavy replay starts:

> **What replay class is active here, why, what could make it worse, and what stronger class is unavailable?**

## Product obligations this evaluation adds

AnonSync should add one explicit family around **replay class honesty**:

1. **Replay class posture** — current class, strongest available class, edit-shape ceiling, and hash basis
2. **Replay cost review** — before commit or policy change, show likely CPU/disk/network tradeoff and whole-resend risk
3. **Replay evidence** — piece map, rolling/diff lane, and why the current subject is using this class right now
4. **Replay receipt** — preserve the class actually used and the strongest sentence the product may safely say afterward

## Tightened conclusion

Borrow Resilio's candor that changed-file replay is workload-shaped and policy-bearing.
Do not clone a product contract where `only changed pieces`, `delta`, or `incremental` still hide **piece-shift full resend**, **hash-availability fallback**, and **edition-gated stronger replay**.''',

    'docs/712-replay-class-posture-page-piecewise-shift-sensitive-and-full-resend-ceiling-interface-spec.md': '''# Replay class posture page: piecewise, shift-sensitive fallback, and resend ceiling interface spec

## Purpose

Give one ordinary page that answers:

> when this subject changes, what replay class is actually active right now, what stronger class is unavailable, and what edit shapes can still force a whole resend?

This page exists because `incremental`, `delta`, `sync changed parts`, and `efficient` are not one honest truth.

## Core rule

Every subject whose future changes may replay over a network must publish a **replay class posture**.
The posture must distinguish at least these classes:

- `full-file replay`
- `piecewise replay`
- `piecewise replay with shift-sensitive fallback`
- `diff-delta replay`
- `local-copy replay`
- `mixed / class may vary by seat`
- `unknown`

A UI may use friendlier labels, but the underlying class must still be inspectable.

## Required sections

### 1) Current replay class

Show:

- current replay class
- strongest class this subject can honestly claim now
- whether the current class is stable or workload-dependent
- strongest safe sentence

Example sentences:

- `Changed content usually replays as changed pieces.`
- `Some edits can still force a whole-file resend because block boundaries shift.`
- `This job currently prefers full resend over local recheck.`
- `A stronger diff-delta class exists elsewhere, but not for this seat/tier.`

### 2) Basis for the class

Show the current reasons:

- edition / runtime capability
- policy flags in force
- hash availability
- rolling-checksum / diff lane availability
- storage / CPU posture if it materially narrows the class
- whether the claim is per-subject, per-seat, or per-job

### 3) Edit-shape ceiling

The operator must see which edits are known to narrow replay quality:

- append-only likely safe for piecewise replay
- in-place change likely safe for piecewise replay
- prefix insert / structural shift may force whole resend
- rename/move may reuse local bytes without network replay
- unclear edit shape means ceiling remains uncertain

### 4) Stronger unavailable class

Show the best counterfactual class that is not available now, and why:

- edition unavailable
- policy disabled
- hashes absent
- rolling/diff lane unavailable
- substrate too slow / too expensive for local recheck
- unknown

### 5) Cost posture

Present a three-axis expectation row:

- network cost tendency (`low`, `mixed`, `high`)
- local CPU/disk cost tendency (`low`, `mixed`, `high`)
- interruption penalty (`resume by pieces`, `whole-file restart risk`, `unknown`)

## Required actions

- `Review replay cost change`
- `Inspect replay evidence`
- `Prefer lower network cost`
- `Prefer lower local recheck cost`
- `Keep current posture`

Never present a toggle like `Use differential replay` without showing the replay class it produces and the whole-resend counterfactual.

## Data model

- `replay_posture_id`
- `subject_id`
- `scope_kind` (`subject`, `job`, `seat`, `pair`)
- `current_replay_class`
- `best_available_replay_class`
- `fallback_replay_class`
- `edit_shape_ceiling[]`
- `basis[]`
- `hash_availability`
- `edition_gate`
- `network_cost_tendency`
- `local_cost_tendency`
- `interruption_penalty`
- `safe_sentence`
- `evidence_ref`
- `last_computed_at`

## Failure this page prevents

Without this page, operators learn too late that `changed parts only` was only true until a piece-shifting edit, a missing-hash seat, or a disabled differential policy turned the next save into a full resend.

AnonSync should instead keep replay class, narrowing basis, and cost posture adjacent before work begins.''',

    'docs/713-replay-cost-review-page-edit-shape-hash-availability-and-network-vs-cpu-tradeoff-interface-spec.md': '''# Replay cost review page: edit shape, hash availability, and network-vs-CPU tradeoff interface spec

## Purpose

Review a pending policy change, workload choice, or subject mutation that may alter replay cost.
The page answers:

> if I commit this change, will future edits replay by changed pieces, by full resend, or by a stronger diff lane, and what exactly am I trading between network cost and local compute?

## Review triggers

Open this page when any of the following happen:

- enabling or disabling differential replay
- changing hash-retention or lazy-hash policy
- moving a subject to a slower or faster storage class
- changing workload profile for large mutable files
- importing a seat/job whose replay class is weaker than local defaults
- choosing a profile optimized for WAN savings vs local CPU savings

## Required sections

### 1) Proposed replay delta

Show current vs proposed:

- current replay class
- proposed replay class
- strongest likely fallback under adverse edit shape
- whether the change is stronger, weaker, or mixed

### 2) Why the class changes

State the winning reasons:

- policy flip
- edition/runtime difference
- changed hash-retention basis
- changed storage/disk profile
- missing rolling/diff lane
- subject moved to a seat with weaker replay support

### 3) Edit-shape examples

The review must show concrete examples, not just theory:

- `append 10 MB to end of 40 GB file`
- `modify bytes in place inside existing block range`
- `insert bytes near beginning and shift later offsets`
- `rename only`

For each example, show expected replay class and confidence.

### 4) Cost tradeoff

Always render a three-column forecast:

| Axis | Current | Proposed |
| --- | --- | --- |
| Network replay | low / mixed / high | low / mixed / high |
| Local CPU/disk recheck | low / mixed / high | low / mixed / high |
| Whole-resend risk after shift | low / mixed / high | low / mixed / high |

### 5) Unsafe shorthand rewrite

Ban vague summaries like:

- `better performance`
- `faster sync`
- `more efficient`

Replace them with sentences like:

- `This change saves local CPU by accepting more full-file resend.`
- `This change spends more local hash work to reduce network replay.`
- `This change does not remove whole-resend risk for piece-shifting edits.`

### 6) Commit actions

- `Commit proposed replay policy`
- `Keep current policy`
- `Open replay evidence`
- `Narrow to selected subject class`

## Receipt obligations

A commit from this page must later preserve:

- current and proposed replay class
- edit-shape examples shown
- dominant reason for class change
- network-vs-local-cost forecast
- strongest unavailable class

## Data model

- `replay_cost_review_id`
- `subject_or_policy_target_id`
- `current_replay_class`
- `proposed_replay_class`
- `fallback_class_if_shifted`
- `cause[]`
- `example_forecasts[]`
- `network_cost_delta`
- `local_cost_delta`
- `whole_resend_risk_delta`
- `stronger_unavailable_class`
- `commit_scope`
- `receipt_ref`

## Failure this page prevents

Without this review, a product quietly turns `optimize this profile` or `use incremental sync` into an uninspected bet about edit shape, hash availability, and who pays the cost — disk/CPU now or network later.

AnonSync should make that trade explicit before commit.''',

    'docs/714-replay-evidence-page-piece-map-delta-lane-and-full-resend-risk-interface-spec.md': '''# Replay evidence page: piece map, delta lane, and full-resend risk interface spec

## Purpose

Provide proof adjacent to the claim:

> why is this subject using this replay class right now, and what evidence supports the claim that the next mutation will replay cheaply or expensively?

## Evidence classes

The page should classify evidence as one or more of:

- `policy only`
- `hash dataset present`
- `piece map present`
- `rolling / diff lane available`
- `full-resend forced by class`
- `shift-risk inferred from edit shape`
- `observed replay outcome`
- `unknown`

## Required sections

### 1) Current replay proof

Show:

- current replay class
- evidence strength (`weak`, `moderate`, `strong`)
- whether the claim is predictive or observed
- last observed replay outcome if available

### 2) Hash and map availability

Show what proof material actually exists:

- file hash present yes/no
- block/piece hashes present yes/no
- retained between runs yes/no
- owner-only availability yes/no
- evidence tied to current absolute path yes/no

### 3) Delta lane health

Show whether the stronger lane is usable now:

- rolling checksum lane active / inactive / unavailable
- diff-delta lane active / inactive / unavailable
- disabled by policy / edition / seat / substrate
- notes about why the lane is unavailable

### 4) Full-resend risk explanation

Explain the strongest current reason full resend may still happen:

- edit likely shifts many later offsets
- hashes unavailable
- policy intentionally prefers resend
- current class does not support stronger delta
- evidence insufficient

### 5) Observed outcomes

If historical evidence exists, show a compact ledger:

- timestamp
- edit-shape summary
- replay class actually used
- bytes rechecked locally
- bytes replayed over network
- whether whole resend occurred

## Required actions

- `Open replay posture`
- `Review replay cost change`
- `Export replay evidence`
- `Recompute evidence now`

## Data model

- `replay_evidence_id`
- `subject_id`
- `current_replay_class`
- `evidence_strength`
- `policy_basis[]`
- `file_hash_present`
- `piece_hashes_present`
- `retained_hash_dataset_present`
- `owner_only_hash_dependence`
- `path_binding_status`
- `delta_lane_status`
- `full_resend_risk_reason[]`
- `observed_outcomes[]`
- `last_recomputed_at`

## Failure this page prevents

Without evidence, a product can say `incremental replay active` even when the current seat only has policy rhetoric and no surviving piece/hash evidence to support that claim.

AnonSync should require proof before it over-speaks about changed-part replay.''',

    'docs/715-replay-receipt-page-replay-class-basis-expected-cost-and-edition-ceiling-interface-spec.md': '''# Replay receipt page: replay class, basis, expected cost, and edition ceiling interface spec

## Purpose

Preserve the replay truth that was actually in force when a policy was applied or a heavy mutation was reviewed.

The receipt answers:

> what replay class did the product claim, on what basis, with what full-resend ceiling, and what stronger class was unavailable at the time?

## Receipt fields

Every replay receipt must preserve at least:

1. subject or policy target
2. current replay class
3. strongest available class at commit time
4. strongest unavailable class and why unavailable
5. current fallback / full-resend ceiling
6. evidence strength
7. hash/piece-map availability snapshot
8. network-cost tendency
9. local-CPU/disk-cost tendency
10. review origin (`policy change`, `subject review`, `profile import`, `mutation review`)
11. strongest safe sentence used in UI
12. timestamp and actor

## Example safe sentences

- `At commit time this subject used piecewise replay, but piece-shifting edits could still force full resend.`
- `At commit time this profile intentionally preferred full resend over local differential recheck.`
- `At commit time stronger diff-delta replay was unavailable on this seat/tier.`

## Required comparisons

A receipt must let the operator compare later against:

- current replay class now
- replay class at receipt time
- what basis changed since then
- whether a stronger class later became available

## Data model

- `replay_receipt_id`
- `target_id`
- `target_kind`
- `recorded_replay_class`
- `best_available_class`
- `unavailable_stronger_class`
- `unavailable_reason[]`
- `fallback_ceiling`
- `evidence_strength`
- `hash_snapshot`
- `piece_map_snapshot`
- `network_cost_tendency`
- `local_cost_tendency`
- `safe_sentence`
- `origin`
- `actor_ref`
- `recorded_at`

## Failure this page prevents

Without this receipt, operators later only remember `we turned on delta` or `this was incremental`, and lose the more honest record that the system still had a shift-triggered full-resend ceiling or an edition gate.

AnonSync should keep replay-class truth durable enough to survive later folklore.'''
}

for rel, content in new_docs.items():
    p = root / rel
    p.write_text(content.rstrip() + "\n", encoding='utf-8')

(root / 'update_rev0257.py').write_text(
    '# Revision 0257 bundle update script placeholder.\n'
    '# This bundle adds docs 711-715 and updates core archive notes for replay-class / piece-shift / differential-sync ceiling work.\n',
    encoding='utf-8'
)

# Helper to prepend text if not already present

def prepend(path_rel, text):
    p = root / path_rel
    old = p.read_text(encoding='utf-8')
    if text.strip() in old:
        return
    p.write_text(text.rstrip() + '\n\n' + old, encoding='utf-8')

# Update README
readme_old = (root / 'README.md').read_text(encoding='utf-8')
new_header = f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{rev}`
- Timestamp: `{timestamp}` (America/New_York)
- Codename: `{codename}`

## What changed in this revision

This revision continues directly from `rev0256` and does seven concrete things:

1. Re-checks another current official Resilio cluster around **piecewise replay, piece-shift whole-file fallback, Business-only stronger diff-delta language in the public FAQ, and enterprise/job-profile policy that can intentionally choose full resend over local differential recheck**.
2. Sharpens the non-clone line again: borrow Resilio's candor that replay cost is workload-shaped and policy-bearing, while refusing any contract where operators still reconstruct `what replay class is active here, when will edits trigger whole resend, and which stronger replay lane is unavailable` from FAQ pages and enterprise tuning docs.
3. Adds one new **Resilio evaluation** document focused on how current official docs still spread one ordinary operator answer about `how expensive will the next changed-file replay actually be?` across Sync FAQ material and official Resilio documentation.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: replay class posture, replay cost review, replay evidence, and replay receipt.
5. Extends the interface/workbench doctrine so every serious changed-file replay claim now publishes **current replay class, fallback/full-resend ceiling, edit-shape risk, hash basis, stronger unavailable class, and strongest safe sentence** before commit.
6. Refreshes the core doctrine documents actually touched in this pass — README, status, evaluation, borrow-line scorecard, clone-veto tests, product direction, pattern language, architecture decisions, roadmap, critical open questions, and sources — so the new tranche is integrated rather than floating.
7. Packages the result as another continuation archive whose new tranche makes the `incremental claim / piece-shift fallback / differential lane / replay-cost review` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's mutable replay-class contract**

This time the evidence is especially clear around **public Sync FAQ language that usually only changed pieces are transferred, but that piece-shifting edits can still force a whole-file resend; Business-only stronger diff-delta language for that case; and official Resilio documentation that still lets administrators intentionally choose full resend or changed-piece replay depending on hash policy, storage cost, and workload shape**.

Current official docs still openly distinguish real facts such as:

- `changed parts only` is not the same truth as `diff-delta replay survives piece shifts`
- piecewise replay can still collapse to whole-file resend when edit shape shifts later blocks
- replay class can be weakened intentionally to save local CPU/disk work
- stronger replay may be edition-, runtime-, or policy-gated rather than universally available
- the live Sync v3 line still appears through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several docs before the product fully owns these questions:

- what replay class is active for this subject right now
- whether the current promise survives prefix-insert or other piece-shifting edits
- whether replay is limited by edit shape, missing hashes, disabled differential policy, or product tier
- what stronger replay class exists but is unavailable here
- what later receipt proves the class that was actually in force when the policy was committed

AnonSync should therefore make **replay class posture** and **replay cost review** first-class product objects.
Every serious replay-affecting change should render current class, fallback ceiling, edit-shape risk, hash basis, unavailable stronger class, and receipt language before the product treats `incremental`, `delta`, or `optimize transfer` as self-explanatory.

## Legacy revision notes preserved below
'''
# replace first header block up to legacy revision notes
m = re.search(r'^# AnonSync.*?## Legacy revision notes preserved below\n', readme_old, flags=re.S)
if m:
    readme_new = new_header + readme_old[m.end():]
else:
    readme_new = new_header + '\n' + readme_old
(root / 'README.md').write_text(readme_new, encoding='utf-8')

# Status addendum
prepend('docs/00-status.md', '''## Latest addendum — replay class, piece-shift fallback, and differential-lane ceiling after rev0256

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **replay class posture / replay cost review / replay evidence / replay receipt**

Current official Resilio docs still say files are split into pieces from `32 KB` to `2 MB`, that usually only changed pieces are transferred, but that if edits shift all pieces the whole file is re-synced; the same current FAQ still says Sync Business has diff-delta sync for that shifted-file case. Separate official Resilio documentation still says administrators may intentionally disable differential sync so the whole file is replayed, or keep it on and pay the local hash/recheck cost to send only changed pieces.
So the tighter non-clone line is:

> borrow Resilio's candor that replay cost is workload-shaped and policy-bearing, but refuse any product contract where operators still reconstruct `what replay class is active here, when edits will collapse to whole resend, and what stronger lane is unavailable` from FAQ prose and enterprise tuning pages.

That yields four more ordinary product-owned pages:

- **Replay class posture**
- **Replay cost review**
- **Replay evidence**
- **Replay receipt**''')

# Evaluation addendum
prepend('docs/10-resilio-sync-evaluation.md', '''## Revision addendum — replay class, piece-shift full resend, and edition-gated stronger delta after rev0256

Current official Resilio docs are still admirably candid that changed-file replay is not one stable truth: the public Sync FAQ still says files are split into pieces from `32 KB` to `2 MB`, that only changed pieces are usually transferred, but that a piece-shifting edit can still force a whole-file resend; the same FAQ still says Sync Business has diff-delta sync for that case. Official Resilio documentation for other job families still says administrators may disable differential sync and intentionally prefer whole-file replay, or keep differential replay enabled and pay the extra local hash/recheck cost instead.

That candor is worth borrowing.
The non-clone problem is again page ownership.
Current Resilio still spreads the ordinary operator answer to `what replay class is active here, how could the next edit narrow it, and what stronger class is unavailable?` across a consumer FAQ, enterprise/job-profile documentation, and workload-tuning guidance rather than one stable product-owned posture/review/evidence/receipt family.

AnonSync should therefore keep the candor and replace the contract with one explicit replay-class family.''')

# Scorecard addendum
prepend('docs/11-resilio-borrow-line-and-non-clone-scorecard.md', '''## Revision addendum — borrow line after rev0256: changed-file replay must become a published class, not a slogan

Keep:

- the candor that replay can be piecewise, whole-file, or stronger-delta depending on workload and policy
- the willingness to say local CPU/disk cost and network cost are being traded against each other
- the admission that some edits still collapse changed-piece replay into whole-file resend

Do not clone:

- one `incremental` or `delta` label that hides piece-shift resend cliffs
- edition- or runtime-gated stronger replay without one ordinary page naming the unavailable class
- policy toggles that change replay cost without a review publishing who pays the cost and how

Replacement obligation:

- one replay-class posture page
- one replay-cost review page
- one replay-evidence page
- one replay receipt''')

# Clone veto addendum
prepend('docs/12-resilio-interface-clone-veto-tests-and-page-obligations.md', '''## Revision addendum — clone-veto test after rev0256: `incremental` may not hide replay-class cliffs

If the product can say `only changed parts sync`, `delta`, or `incremental` without also publishing:

1. the active replay class,
2. whether piece-shifting edits still force whole resend,
3. whether stronger diff replay is unavailable by edition/runtime/policy,
4. and what evidence supports the current claim,

it fails the clone-veto test.

AnonSync must instead expose one posture page, one cost review, one evidence page, and one receipt for replay class truth.''')

# Product direction addendum
prepend('docs/20-product-direction.md', '''## Revision addendum — doctrine after rev0256: replay class is public product meaning

`Incremental`, `delta`, and `changed parts only` are not implementation trivia.
They are public product claims about replay class, fallback ceiling, edit-shape sensitivity, and who pays the optimization bill.
A product that hides those facts behind one friendly performance label is still making the operator do transport archaeology.

AnonSync should therefore treat replay class as a first-class inspectable object with posture, review, evidence, and receipt surfaces.''')

# Pattern language addendum
prepend('docs/39-interface-pattern-language.md', '''## Revision addendum — pattern language after rev0256: replay is a class card, not a speed adjective

Another pattern now belongs in the archive:

- when a product describes changed-file transfer, represent it as a **replay class card**, not a speed adjective

Why this matters:

- a speed adjective hides whether the subject replays by pieces, by full resend, or by a stronger diff lane
- a replay class card can keep edit-shape fallback, hash basis, and unavailable stronger class adjacent
- it prevents `incremental` from impersonating `piece-shift safe`''')

# Architecture addendum
prepend('docs/40-architecture-decisions.md', '''## ADR addendum after rev0256 — replay class deserves explicit architecture status

**Decision:** Persist replay class as a first-class computed object, not an inferred transport footnote.

**Why:** Current Resilio docs still show that changed-file replay meaning varies across piecewise resend, piece-shift whole-file fallback, stronger diff-delta lanes, and policy-driven full resend. One performance adjective is therefore not enough.

**Consequence:** any surface that claims `incremental`, `delta`, or `changed parts only` must bind to a replay-class record with fallback ceiling, evidence strength, and unavailable-stronger-class explanation.''')

# Roadmap addendum
prepend('docs/50-roadmap.md', '''## Latest roadmap addendum — promote replay class and full-resend ceilings into the ordinary product core

A further current Resilio pass suggests the roadmap should now reserve one explicit tranche for:

- replay-class posture and fallback visibility
- reviewed replay-cost changes instead of generic performance toggles
- evidence for current changed-file replay claims
- durable receipts for the class actually in force

Why this is next-worthy:

Current official docs still make it too easy for one operator to hear `only changed pieces`, another to discover `whole file re-synced after shift`, and a third to learn that a stronger diff lane was edition- or policy-gated.
AnonSync should lock that down as ordinary product truth rather than FAQ folklore.''')

# Open questions addendum
prepend('docs/64-critical-open-questions.md', '''## Latest open-questions addendum — replay class, edit-shape cliffs, and who should pay the optimization bill after rev0256

Questions now worth keeping explicitly open:

- When should a product be allowed to summarize replay as `incremental` if some common edit shapes still trigger whole resend?
- Should replay class be computed per subject, per seat, per job, or per source-target pair when hash availability differs?
- How much stronger must an unavailable diff lane be before the product must advertise it instead of quietly omitting it?
- When CPU/disk and network costs disagree, should the default bias be `save the network`, `save the workstation`, or `ask with examples`?''')

# Sources addendum
prepend('docs/sources.md', '''## Sources addendum — rev0257 replay class, piece-shift fallback, and differential-sync ceilings

The most load-bearing source set for this pass was another current official Resilio cluster around changed-file replay class, piece-shifting full resend, stronger diff-delta language, and policy-bearing differential-sync choices.

- Resilio's current `When a file changes, does Resilio Sync transfer the entire file again, or just the part that's changed?` article, which still says files are split into pieces from `32 KB` to `2 MB`, that only changed pieces are usually transferred, that piece-shifting edits can still force a whole-file resend, and that Sync Business has diff-delta sync for that case.
- Resilio's current official documentation page `Synchronizing pre-seeded folder`, which still says the `Disable differential sync` parameter chooses between whole-file sync and changed-piece replay once a file needs syncing, and that hash-availability policy materially changes replay behavior.
- Resilio's current official documentation page `Advanced custom parameters`, which still says hashing/differential parameters are coupled and that weak hash availability can make changed-file replay depend on which agent actually has hashes.
- Resilio's current official best-practice pages for VDI / profile-style workloads, which still say slower disks may justify full-file replay while faster disks may justify changed-piece replay and stronger local recheck.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

Reference URLs:

- https://help.resilio.com/hc/en-us/articles/206217095-When-a-file-changes-does-Resilio-Sync-transfer-the-entire-file-again-or-just-the-part-that-s-changed
- https://www.resilio.com/documentation/content/advanced-configuration/best-practices/synchronizing_pre-seeded_folder/
- https://www.resilio.com/documentation/content/advanced-configuration/profiles-and-configuration-parameters/advanced_custom_parameters/
- https://www.resilio.com/documentation/content/advanced-configuration/best-practices/best_practices_for_synchronizing_fslogix_and_vdi_profiles/
- https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log
''')

