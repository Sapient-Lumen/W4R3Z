from pathlib import Path
import re

root = Path('/mnt/data/anonsync_rev0087')

def read(rel):
    return (root / rel).read_text()

def write(rel, text):
    (root / rel).write_text(text)

# Metadata
rev = 'rev0087'
ts = '2026.03.18.02.52'
codename = 'arrivaltemplategovernanceharbor'

# New doc content
new_doc = '''# Standing arrival-template and default-root review interface spec

The archive already separates announcement from claim, claim from bind, current-share posture from future-arrival policy, and one-share placement review from broader defaults.
This document answers the narrower standing-policy seam that still remains after `98-share-local-presence-and-mode-decomposition-interface-spec.md` and `99-arrival-placement-suggestion-and-collision-review-interface-spec.md`:

> how should AnonSync let an operator edit the **standing seat template** that governs later arrivals, without turning one-share placement, reconnect ritual, or mobile `Simple mode` folklore back into the hidden source of future behavior?

This is the governance companion to `58-policy-origin-defaults-and-precedence-spec.md`, the per-seat posture companion to `98-share-local-presence-and-mode-decomposition-interface-spec.md`, and the per-arrival placement companion to `99-arrival-placement-suggestion-and-collision-review-interface-spec.md`.

## Why this needs its own spec

Resilio's current docs still make this seam unusually concrete.
`Sync Private Identity & Linking My Devices`, `Synchronization Modes`, `How to manually set the location of the folders synced across linked devices?`, `Folders are duplicating with an index (i) in their name.`, and `Settings on mobile platforms` still show that a seat's standing defaults are carried by a mix of `Disconnected / Selective Sync / Synced`, default folder location, and Android `Simple mode`.
That means the same knobs still decide, in one place or another:

- whether later arrivals announce only or connect immediately
- whether a default root/path is drafted before per-arrival review
- whether mobile shares auto-land in one default location
- whether same-name collisions fall back to indexed duplicates
- whether changing one seat's convenience setting will later surprise the operator when unrelated arrivals behave differently

Those are useful conveniences.
They are not yet one truthful **standing policy contract**.

The practical consequence is that the operator can still change a device default and only later discover that they also changed:

- how future arrivals are admitted
- where future binds are drafted
- which open arrivals inherit the new template
- whether duplicate fallback remains possible
- whether any current bound shares were supposed to stay untouched

AnonSync should therefore promote the standing arrival template into an explicit reviewed object rather than letting it hide behind connect/disconnect ritual, default-folder toggles, or `Simple mode`.

## Core rule

A **standing seat template** is a durable policy object.
It is not the same thing as:

- the current share's local posture
- the current share's committed bind
- a one-share placement review
- a one-time collision override

Every serious edit to that template should therefore render as its own reviewed change with explicit effect buckets.

## Vocabulary

### Standing seat template

A durable policy object governing later arrivals for one reviewed seat and one reviewed scope.

Suggested fields:

- arrival admission posture (`announce-only`, `review-required`, `claim-suggested`, `reviewed-auto-claim`)
- path-template or default-root draft
- collision default (`always-review`, `allow-same-lineage-adopt-suggestion`, `propose-alternate`, never silent suffix)
- initial byte suggestion (`names-only`, `placeholders`, `materialize-after-review`)
- scope (`family-arrivals`, `camera-backup`, `trusted-contact:Maya`, etc.)
- precedence / policy origin

### Template-governance review

A reviewed change to a standing seat template, including effect preview for future unseen arrivals and for already-visible but still-uncommitted arrivals.

### Effect bucket

A stable preview class saying what the template change will and will not touch.

Required buckets:

- **future unseen arrivals**
- **currently announced but unclaimed arrivals**
- **currently claimed but unbound arrivals**
- **currently bound shares**

### Template receipt

A durable record proving which standing template changed, what scope it governs, what effect buckets were reviewed, and whether any currently visible drafts were refreshed.

## Fixed review order

Every standing-template change should render the same sections in the same order:

1. **Reviewed seat and governed scope**
2. **Current standing template**
3. **Proposed standing template**
4. **Effect buckets**
5. **Exceptions and pinned subjects**
6. **Admissible actions**
7. **Receipt promise**

### 1) Reviewed seat and governed scope

This section should show:

- which seat is being changed
- what reviewed scope is governed
- which policy origin currently supplies the template
- whether the scope is seat-wide, share-class-wide, contact-scoped, or more limited

The operator must be able to answer: **which future arrivals am I actually governing here?**

### 2) Current standing template

This section should show the current values for:

- arrival admission posture
- path-template / default-root
- collision default
- initial byte suggestion
- provenance / origin

The operator must be able to answer: **what exactly is this seat currently set to do next time?**

### 3) Proposed standing template

This section should show the proposed replacement or delta.
It should preserve unchanged fields explicitly instead of making the operator infer them.

The operator must be able to answer: **what future behavior changes, and what stays the same?**

### 4) Effect buckets

This section should show a stable four-bucket preview.

#### Future unseen arrivals

Always show the new default behavior.

#### Currently announced but unclaimed arrivals

The product may offer two explicit policies:

- `refresh suggestion drafts to new template`
- `leave existing drafts unchanged`

The default should be conservative: **leave existing drafts unchanged unless the operator explicitly refreshes them**.

#### Currently claimed but unbound arrivals

These should ordinarily remain unchanged.
If the product ever allows draft-path refresh here, it must require a stronger review and explicit subject list.

#### Currently bound shares

These must remain unchanged by standing-template edits.
A standing-template review must never silently relocate or dematerialize already bound shares.

The operator must be able to answer: **what future and draft subjects change, and which real subjects definitely do not?**

### 5) Exceptions and pinned subjects

This section should show:

- subjects pinned away from inheritance
- per-share template overrides
- old drafts that would remain under prior template values
- any conflict with policy precedence or safety policy

The operator must be able to answer: **what will not follow this new template even though it seems in scope?**

### 6) Admissible actions

This section should allow verbs such as:

- `Change standing template for future arrivals`
- `Also refresh unclaimed drafts`
- `Keep current template`
- `Open narrower scope review`
- `Pin one subject away from inheritance`

It must not collapse these into `Save defaults` or `Change mode` when that wording would hide scope/effect differences.

### 7) Receipt promise

This section should show:

- acting seat and governed scope
- old template summary and new template summary
- which effect buckets were reviewed
- whether existing drafts were refreshed
- which subject classes were guaranteed unchanged

The operator must be able to answer: **what later evidence will prove that I changed standing policy rather than current share state?**

## Row and card contract

A truthful compact row should keep these facts in stable order:

1. seat + scope
2. admission posture
3. path-template/default-root
4. draft-refresh posture
5. next honest action

Example:

```text
Home-NAS / family arrivals   announce-only   /tank/family/{{share_name}}   drafts unchanged   Review template
```

A details card should also surface pinned exceptions and currently bound-share non-effects.

## What must never be implied

The interface must never imply that:

- changing the standing template relocates already bound shares
- changing the default root automatically refreshes all open arrivals
- `Simple mode`-style convenience is harmless enough to skip an effect preview
- silent duplicate suffixing is an acceptable collision default for future arrivals
- a per-arrival placement decision has rewritten the standing template unless the receipt says so

## Dense/mobile rule

Dense/mobile clients may compress wording, but they must still preserve separate cues for:

- governed seat/scope
- admission posture
- path template / default root
- whether existing drafts refresh
- which subjects stay untouched

A small client may shorten `currently bound shares unchanged` to `bound shares unchanged`, but it may not omit that guarantee entirely.

## CLI contract

Minimal commands:

```text
anonsync arrival-template list --seat self
anonsync arrival-template show --seat self --scope family-arrivals
anonsync arrival-template review prepare --seat self --scope family-arrivals \
  --admission announce-only \
  --path-template /tank/family/{{share_name}} \
  --collision-default always-review \
  --draft-refresh unchanged \
  --plan
anonsync arrival-template review show atr_01J...
anonsync arrival-template apply atr_01J...
anonsync arrival-template receipt show atc_01J...
```

## Why this matters

A weaker product shape would let per-seat defaults hide in a mode selector, a default-folder field, or a mobile simplification toggle and then ask the operator to remember what future arrivals will now do.
This spec rejects that shape.

The rule is:

> standing convenience must be its own reviewed object, with explicit effect buckets, so future-arrival behavior can improve without silently rewriting current share truth.
'''
write('docs/100-standing-arrival-template-and-default-root-review-interface-spec.md', new_doc)

# README
text = read('README.md')
text = re.sub(r'- Revision: `rev\d+`', f'- Revision: `{rev}`', text)
text = re.sub(r'- Timestamp: `[^`]+` \(America/New_York\)', f'- Timestamp: `{ts}` (America/New_York)', text)
text = re.sub(r'- Codename: `[^`]+`', f'- Codename: `{codename}`', text)
text = re.sub(r'## What changed in this revision\n\nThis revision continues directly from `rev0085` and does six things:\n\n1\.[\s\S]*?## Current conclusion', '''## What changed in this revision

This revision continues directly from `rev0086` and does six things:

1. Re-checks **Resilio Sync** again, this time around standing arrival defaults rather than only one-share placement: current docs still say linked devices expose three standing synchronization modes, newly added folders on linked devices still follow those defaults, custom placement still requires switching to `Disconnected` and later using `Connect`, and Android `Simple mode` plus `Default folder location` still drive where new shares land and whether same-name duplicates pick up `(1)`.
2. Adds a dedicated **standing arrival-template and default-root review interface spec** so the archive no longer tolerates one mode toggle, one default-folder field, or one mobile simplification toggle standing in for admission posture, drafted root, collision default, and draft-refresh scope.
3. Tightens the **evaluation** so the non-clone case against Resilio gets sharper again: the issue is not that standing defaults exist, but that current docs still let future-arrival behavior hide in a scattered mode/default/simple-mode story instead of one reviewed seat policy object.
4. Extends the **object model and daemon/API contract** with explicit standing-template policy, template review, and effect-bucket preview resources so clients do not infer future-arrival behavior from unrelated current-share actions.
5. Adds an additional **canonical interface flow** showing the split the archive now wants: an operator can change a seat's future family-arrival root/template and keep already bound shares untouched, while explicitly choosing whether any currently unclaimed drafts should refresh.
6. Refreshes the **workbench, pattern language, ADRs, roadmap, open questions, status, source notes, and reading order** so future revisions keep **standing template governance** central wherever convenience defaults and truthful seat policy meet.

## Current conclusion''', text, count=1)
text = text.replace('- a first-class arrival-placement suggestion / collision / placement-receipt surface so remembered roots stay helpful without silently becoming path commitments or duplicate `(1)` fallbacks\n', '- a first-class arrival-placement suggestion / collision / placement-receipt surface so remembered roots stay helpful without silently becoming path commitments or duplicate `(1)` fallbacks\n- a first-class standing arrival-template / default-root / effect-bucket surface so seat-level convenience remains reviewable policy instead of scattered mode/default/simple-mode folklore\n')
write('README.md', text)

# Status rewrite fully for coherence
status = f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0086`, driven by the current request:

- continue researching and tightening the archive without letting it sprawl
- evaluate Resilio Sync further so the non-clone case stays evidence-based rather than rhetorical
- spend more time on interface specs, especially where standing defaults or convenience toggles still hide future-arrival behavior
- keep Linux-first, overlay-first, and least-privilege assumptions intact unless the evidence actually breaks them
- preserve the useful parts of Resilio's convenience model without inheriting silent template mutation, silent duplicate-suffix fallback, or current-share actions that secretly rewrite future seat defaults
- make sure the archive can answer not only `what happens to this share now?` but also `what will this seat do with the next matching arrival, why, and what existing subjects definitely remain untouched?`

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- a fairer Resilio comparison that explicitly grants current strengths — maintained Sync v3, 2025 feature polish such as file-download priority, strong selective materialization, useful linked-device convenience, and practical mobile defaults — while still naming the sharper reason not to clone its standing-default story wholesale
- a new **standing arrival-template and default-root review interface spec** that defines how one seat should render admission posture, drafted root/template, collision default, effect buckets, and draft-refresh choice without collapsing them into one mode/default/simple-mode ritual
- stronger interface and daemon/API requirements so standing template policy, template review, and effect-bucket previews become explicit public objects rather than hidden consequences of one mode/default-location setting
- stronger workbench and pattern-language rules so `future only`, `refresh unclaimed drafts`, `bound shares unchanged`, `pinned away from inheritance`, and `collision default: always review` remain visibly different across dense and full surfaces
- an additional canonical flow showing the core governance split the archive now wants: a seat's future arrival template can change without moving current bound shares, and any refresh of open drafts must be explicit
- README, roadmap, ADR, open-question, status, and source-note updates so future revisions keep **standing template governance** central wherever machine-local convenience and truthful future-arrival policy meet

## The main shift

`rev0086` proved that one-share path suggestion and placement review need their own explicit contract.

`rev0087` tightens the standing-policy problem one level up:

> it is not enough to separate current share posture from future-arrival policy in principle. A serious operator product must also specify how a seat's standing future-arrival template is inspected, edited, previewed, and receipted without quietly mutating current shares or open drafts.

That changes the archive in five specific ways:

- `Disconnected / Selective Sync / Synced`, `Default folder location`, and Android `Simple mode` are now treated as cautionary product shapes, not a model to copy forward
- standing future-arrival policy now has its own first-class review object with explicit effect buckets
- open unclaimed drafts may be refreshed only by explicit choice; they do not silently inherit a new template just because the seat default changed
- currently bound shares are now an explicit guaranteed non-effect bucket for template-governance review
- the non-clone case against Resilio gets tighter again: the missing piece is not standing defaults, but the absence of one explicit contract that says what the default governs, what it never rewrites, and what later receipt proves that boundary

## What still remains unresolved

This revision intentionally still leaves important questions open, including:

- how aggressive reviewed auto-claim may ever become before it starts feeling magical again
- whether currently claimed-but-unbound subjects should ever be eligible for template refresh in v1
- how much remembered scope or role state can be reused before `claim` quietly degenerates back into `Connect`
- how dense/mobile clients should expose `drafts unchanged` versus `refresh drafts now` without recreating hidden defaults
- how broad one reviewed mutation grant may be in v1 before explicit authority becomes either too reusable or too noisy
- when long-offline or clock-uncertain peers should be allowed to resume writable participation without first-class re-entry review
- when remote delete or overwrite waves should always force destructive-replay review instead of ordinary sync progress
- how aggressive default compromise freezes should be before the product starts turning suspicion into disruptive magic
- how aggressive the default review queue should be before it becomes noisy

## Files added in this revision

- `docs/100-standing-arrival-template-and-default-root-review-interface-spec.md`
- `update_rev0087.py`

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
- `docs/100-standing-arrival-template-and-default-root-review-interface-spec.md`
- `docs/sources.md`
'''
write('docs/00-status.md', status)

# Evaluation append new section before sharper conclusion
text = read('docs/10-resilio-sync-evaluation.md')
insert = '''\n## 16ak) Standing arrival defaults still hide future behavior behind scattered mode/default/simple-mode ritual

Resilio's current docs still make this seam unusually concrete.
`Sync Private Identity & Linking My Devices` and `Synchronization Modes` still present `Disconnected`, `Selective Sync`, and `Synced` as standing linked-device defaults.
`How to manually set the location of the folders synced across linked devices?` and `Folders are duplicating with an index (i) in their name.` still say that when `Selective Sync` or `Synced` are in force, new linked-device arrivals go to the default folder, and that custom placement requires switching the device to `Disconnected` and later using `Connect`.
`Settings on mobile platforms` still says that when Android `Simple mode` is enabled, all new shares go to the default folder location and same-name collisions pick up `(1)`.

Those are useful conveniences.
They are also evidence that one seat's standing future-arrival behavior is still spread across several knobs rather than one reviewed policy object.

The practical consequence is that the operator can still change a standing device default and only later discover that they also changed:

- whether later arrivals announce only or connect immediately
- which drafted root or default path later arrivals will propose
- whether same-name collisions may silently drift toward duplicate suffix fallback
- whether mobile behavior differs only because one simplification toggle stayed on
- whether any currently visible but still-unclaimed arrivals now inherit the new template

AnonSync should therefore not let standing future-arrival behavior hide inside a mode selector, a default-folder field, or a mobile simplification toggle.
It should instead publish one explicit standing-template policy with one explicit governance review that previews effect buckets for:

- future unseen arrivals
- currently announced but unclaimed arrivals
- currently claimed but unbound arrivals
- currently bound shares

And it should make one conservative choice explicit:

- changing the standing template should not refresh existing drafts unless the operator explicitly asks for that outcome
- changing the standing template must never silently relocate already bound shares

### Requirement 74 — standing future-arrival templates must be explicit reviewed seat policy, not scattered convenience toggles

If the operator still has to combine mode lore, default-folder settings, mobile `Simple mode`, reconnect ritual, and duplicate-index folklore to answer `what will this seat do with the next matching arrival, and what existing subjects definitely stay untouched?`, the product has not actually exposed its standing default contract.

AnonSync should instead publish one public model with:

- an explicit standing seat-template object naming admission posture, drafted root/path template, collision default, byte suggestion, and governed scope
- an explicit template-governance review showing effect buckets and pinned exceptions
- explicit draft-refresh choice for currently announced but unclaimed arrivals
- durable receipts proving which standing policy changed and which current subjects were guaranteed unchanged
\n'''
text = text.replace('\n## Sharper conclusion from this pass\n', insert + '## Sharper conclusion from this pass\n', 1)
text = text.replace('What AnonSync should not copy is the way *path suggestion*, *path commitment*, and *collision fallback* still live inside one convenience story.\n', 'What AnonSync should not copy is the way *path suggestion*, *path commitment*, *collision fallback*, and *standing future-arrival defaults* still live inside one convenience story.\n')
text = text.replace('- any review surface that makes operators use `disconnect`/`connect` folklore to explain where a share really belongs\n', '- any review surface that makes operators use `disconnect`/`connect` folklore to explain where a share really belongs\n- any standing seat-default story that makes operators infer future-arrival behavior from scattered mode, default-root, or `Simple mode` toggles instead of one reviewed policy object\n')
write('docs/10-resilio-sync-evaluation.md', text)

# Interface spec append new section
text = read('docs/30-interface-spec.md')
append = '''\n\n## Standing arrival-template governance surfaces

Use one explicit family for seat-level future-arrival templates instead of letting `mode`, `default folder`, or `Simple mode` stand in for durable policy.

```text
anonsync arrival-template list --seat self
anonsync arrival-template show --seat self --scope family-arrivals
anonsync arrival-template review prepare --seat self --scope family-arrivals --admission announce-only --path-template /tank/family/{{share_name}} --collision-default always-review --draft-refresh unchanged --plan
anonsync arrival-template review prepare --seat self --scope family-arrivals --admission claim-suggested --path-template /srv/family/{{share_name}} --collision-default propose-alternate --draft-refresh refresh-unclaimed --plan
anonsync arrival-template review show <arrival_template_review_id>
anonsync arrival-template apply <arrival_template_review_id>
anonsync arrival-template receipt show <arrival_template_receipt_id>
```

Rules:

- a standing arrival template must render as its own seat-scoped policy object, not as a hidden consequence of current-share placement or bind actions
- every review must show one fixed group order: `reviewed seat and governed scope`, `current standing template`, `proposed standing template`, `effect buckets`, `exceptions and pinned subjects`, `admissible actions`, `receipt promise`
- effect buckets must at least distinguish `future unseen arrivals`, `currently announced but unclaimed arrivals`, `currently claimed but unbound arrivals`, and `currently bound shares`
- the conservative default is `drafts unchanged`; refreshing existing unclaimed drafts to a new template must be explicit
- currently bound shares must never be moved, dematerialized, or re-bound by a standing-template change
- dense/mobile surfaces may compress wording, but they may not hide which governed scope changed or which current subjects stayed untouched
- the apply verb in rich or textual surfaces should inherit the reviewed intent label (`Change standing template`, `Also refresh unclaimed drafts`, `Keep current template`) instead of collapsing back to generic `Save defaults`
'''
if '## Standing arrival-template governance surfaces' not in text:
    text += append
write('docs/30-interface-spec.md', text)

# Daemon API append object model/endpoints/events
text = read('docs/31-daemon-api-spec.md')
append = '''\n\n## Standing arrival-template governance additions

### `arrival_template_policy`

A durable seat-scoped policy object describing how later arrivals should be admitted and drafted.

Suggested fields:

- `id`
- `seat_id`
- `governed_scope`
- `admission_posture` — `announce-only`, `review-required`, `claim-suggested`, `reviewed-auto-claim`
- `path_template`
- `collision_default` — `always-review`, `allow-same-lineage-adopt-suggestion`, `propose-alternate`
- `initial_byte_suggestion` — `names-only`, `placeholders`, `materialize-after-review`
- `origin_kind`
- `pinned_subject_count`
- `created_at`
- `updated_at`

### `arrival_template_effect_preview`

A stable preview of what a proposed standing-template change will and will not touch.

Suggested fields:

- `id`
- `policy_id`
- `future_unseen_effect`
- `unclaimed_draft_effect` — `unchanged`, `refresh-to-new-template`, `explicit-subset-only`
- `claimed_unbound_effect` — `unchanged`, `blocked`, `explicit-subset-review-required`
- `bound_share_effect` — must normally be `unchanged`
- `pinned_subject_ids[]`
- `notes[]`
- `created_at`

### `arrival_template_review`

A reviewed standing-template change for one seat and one governed scope.

Suggested fields:

- `id`
- `seat_id`
- `governed_scope`
- `current_policy_id`
- `proposed_policy_delta`
- `effect_preview_id`
- `selected_draft_refresh_mode` — `unchanged`, `refresh-unclaimed`
- `receipt_promise`
- `created_at`

### Endpoints

```text
GET  /v1/seats/{seat_id}/arrival-templates
GET  /v1/arrival-templates/{policy_id}
POST /v1/arrival-templates/reviews
GET  /v1/arrival-templates/reviews/{review_id}
POST /v1/arrival-templates/reviews/{review_id}/apply
GET  /v1/arrival-templates/receipts/{receipt_id}
```

### Event additions

- `arrival_template.policy_changed`
- `arrival_template.effect_preview_created`
- `arrival_template.review_opened`
- `arrival_template.unclaimed_drafts_refreshed`
- `arrival_template.receipt_emitted`
'''
if '## Standing arrival-template governance additions' not in text:
    text += append
write('docs/31-daemon-api-spec.md', text)

# Flows append flow 146
text = read('docs/32-interface-flows.md')
flow = '''\n\n## Flow 146 — change a seat's future arrival root without moving current shares or silently refreshing old drafts

**Intent:** prove that AnonSync can improve standing seat convenience without inheriting Resilio-style default-folder / simple-mode semantics that quietly change future behavior and leave the operator guessing what else moved.

### Situation

- `Home-NAS` governs `family-arrivals` with standing template:
  - admission: `claim-suggested`
  - path template: `/srv/family/{{share_name}}`
  - collision default: `always-review`
- current bound share `Photos-2026` lives at `/srv/family/Photos-2026`
- current bound share `Scans-2026` lives at `/srv/family/Scans-2026`
- one still-unclaimed announced arrival `Videos-2026` already has a draft suggestion under the old template
- the operator wants future family arrivals to draft under `/tank/family/{{share_name}}`
- the operator does **not** want already bound shares moved and does **not** want the old `Videos-2026` draft silently rewritten

### Workbench path

1. `Seat templates` shows:

```text
Home-NAS / family arrivals   claim-suggested   /srv/family/{{share_name}}   drafts unchanged   Review template
```

2. Opening review shows, in order:

   - reviewed seat and governed scope
   - current standing template
   - proposed standing template
   - effect buckets
   - exceptions and pinned subjects
   - admissible actions
   - receipt promise

3. The pane makes these facts explicit:

   - future unseen family arrivals will draft under `/tank/family/{{share_name}}`
   - currently announced-but-unclaimed `Videos-2026` can either keep its old draft or be explicitly refreshed
   - currently bound shares `Photos-2026` and `Scans-2026` remain unchanged
   - no current bytes, binds, or path provenance on bound shares are touched by this review

4. The operator sees three honest verbs:

   - `Change standing template`
   - `Change standing template and refresh unclaimed drafts`
   - `Keep current template`

5. The operator chooses `Change standing template`.

6. Apply emits a receipt proving:

   - acting seat: `Home-NAS`
   - governed scope: `family-arrivals`
   - old path template: `/srv/family/{{share_name}}`
   - new path template: `/tank/family/{{share_name}}`
   - unclaimed drafts: unchanged
   - bound shares: unchanged

### CLI sketch

```text
anonsync arrival-template show --seat home-nas --scope family-arrivals
anonsync arrival-template review prepare --seat home-nas --scope family-arrivals \
  --path-template /tank/family/{{share_name}} \
  --draft-refresh unchanged \
  --plan
anonsync arrival-template review show atr_01J...
anonsync arrival-template apply atr_01J...
anonsync arrival-template receipt show atc_01J...
```

### Why this matters

A weaker product shape would have changed one seat default and left the operator guessing whether that meant:

- future arrivals go somewhere else
- open drafts already changed too
- current bound shares would later reconnect somewhere new
- or all of the above

This flow proves the archive wants a different contract:

- standing template edits are their own reviewed object
- open drafts refresh only by explicit choice
- current bound shares stay untouched
- later receipts prove that boundary
'''
if '## Flow 146 — change a seat\'s future arrival root without moving current shares or silently refreshing old drafts' not in text:
    text += flow
write('docs/32-interface-flows.md', text)

# Workbench spec append
text = read('docs/38-operator-workbench-interface-spec.md')
append = '''\n\n## Seat templates view

The workbench should expose a first-class `Seat templates` view for standing future-arrival policy.
This view exists so operators do not have to infer durable future behavior from one current share card, one mode selector, or one mobile simplification toggle.

### Required columns

- seat + governed scope
- admission posture
- path template / default root
- collision default
- draft-refresh posture
- pinned exception count
- next honest action

### Review-pane rule

Opening one row should preserve the fixed standing-template order from `100-standing-arrival-template-and-default-root-review-interface-spec.md`:

1. reviewed seat and governed scope
2. current standing template
3. proposed standing template
4. effect buckets
5. exceptions and pinned subjects
6. admissible actions
7. receipt promise

### Compact-row example

```text
Home-NAS / family arrivals   announce-only   /tank/family/{{share_name}}   always-review   drafts unchanged   Review template
```
'''
if '## Seat templates view' not in text:
    text += append
write('docs/38-operator-workbench-interface-spec.md', text)

# Pattern language append
text = read('docs/39-interface-pattern-language.md')
append = '''\n\n## Pattern 46 — standing convenience must be edited through its own reviewed object

When a product offers seat-level convenience for later arrivals, do not hide that convenience inside a mode selector, default-folder field, or simplification toggle.
Turn it into one explicit reviewed object with:

- a governed seat/scope
- a current template
- a proposed template
- effect buckets
- pinned exceptions
- a receipt promise

Good compression:

```text
Home-NAS / family arrivals   announce-only   /tank/family/{{share_name}}   drafts unchanged   Review template
```

Bad compression:

```text
Mode: Selective Sync
Default folder: /tank/family
```

The second form may be short, but it still asks the operator to remember what future arrivals will do, whether open drafts changed, and whether current shares remain untouched.
A mature AnonSync surface should not require that folklore.
'''
if '## Pattern 46 — standing convenience must be edited through its own reviewed object' not in text:
    text += append
write('docs/39-interface-pattern-language.md', text)

# ADR append
text = read('docs/40-architecture-decisions.md')
append = '''\n\n## ADR-100 — standing future-arrival defaults need one reviewed template-governance contract, not scattered mode/default/simple-mode folklore

### Status
Accepted

### Context

The archive already separates current share posture from future-arrival policy and one-share placement review from broader defaults.
Current Resilio docs still show standing future-arrival behavior spread across linked-device modes, default-folder settings, custom-location reconnect ritual, and Android `Simple mode`.
That is practical convenience, but it still leaves operators reconstructing one seat's future behavior from several scattered knobs.

### Decision

AnonSync will model standing future-arrival behavior as an explicit seat-template policy with explicit governance review, explicit effect buckets, explicit pinned exceptions, and explicit receipts.
Changing this template will never silently relocate already bound shares.
Refreshing existing unclaimed drafts will require its own explicit choice.

### Consequences

- clients gain one public object for standing convenience instead of inferring it from current-share actions
- policy changes can preview future unseen arrivals separately from open drafts and bound shares
- mobile/dense clients may compress wording, but they must still preserve governed scope and unchanged-subject guarantees
- the product avoids recreating `change mode` / `default folder` folklore as a hidden control plane for future arrivals
'''
if '## ADR-100' not in text:
    text += append
write('docs/40-architecture-decisions.md', text)

# Roadmap append bullet and exit criterion in phase 2
text = read('docs/50-roadmap.md')
text = text.replace('- explicit standing-approval / matched-arrival guardrail contract so remembered approval can recognize later arrivals without silently turning them into connected local paths\n', '- explicit standing-approval / matched-arrival guardrail contract so remembered approval can recognize later arrivals without silently turning them into connected local paths\n- explicit standing arrival-template / default-root governance contract so seat-level convenience remains reviewable policy rather than scattered mode/default/simple-mode behavior\n')
text = text.replace('- operators can always tell whether a share is merely visible here, already claimed here, bound here, hidden here only, or withdrawn more widely\n', '- operators can always tell whether a share is merely visible here, already claimed here, bound here, hidden here only, or withdrawn more widely\n- operators can always tell what one seat will do with the next matching arrival, whether old drafts were refreshed, and which currently bound shares stayed untouched when standing defaults changed\n')
write('docs/50-roadmap.md', text)

# Open questions append new item maybe after 18 or before 19
text = read('docs/64-critical-open-questions.md')
q = '''\n\n## 20) How much standing-template refresh power is safe before seat defaults start mutating live work too quietly?

The archive is now clearer that standing future-arrival templates need their own reviewed object, but one policy seam is still open:

- should unclaimed draft arrivals stay unchanged by default forever, or only until some freshness boundary
- should claimed-but-unbound arrivals ever be eligible for standing-template refresh in v1
- how much scope preview is enough before a seat-template edit becomes too noisy to use
- when should changing a drafted root require stronger review because many open drafts would be affected

This matters because too little refresh power recreates stale draft clutter, while too much refresh power recreates the very hidden default-mutation problem the archive is trying to avoid.
'''
if '## 20) How much standing-template refresh power is safe before seat defaults start mutating live work too quietly?' not in text:
    text += q
write('docs/64-critical-open-questions.md', text)

# sources note prepend and maybe ensure relevant source listed (already mostly). Add syncing mobile if missing? sources has settings and manual path. We'll update top note.
text = read('docs/sources.md')
text = text.replace('The newest pass especially reused the linked-device approval/owner, linked-arrival, disconnected/remove, and duplicate-index articles to keep the non-clone case about current product semantics rather than dated folklore.\n', 'The newest pass especially reused the linked-device mode/default-path, manual-location, duplicate-index, and mobile simple-mode articles to keep the non-clone case about current product semantics rather than dated folklore.\n')
if 'Syncing between a desktop computer and a mobile device' not in text:
    marker = '- Settings on mobile platforms  \n  https://help.resilio.com/hc/en-us/articles/205458145-Settings-on-mobile-platforms\n'
    insert = marker + '\n- Syncing between a desktop computer and a mobile device  \n  https://help.resilio.com/hc/en-us/articles/205451165-Syncing-between-a-desktop-computer-and-a-mobile-device\n'
    text = text.replace(marker, insert)
write('docs/sources.md', text)

print('updated rev0087 files')
