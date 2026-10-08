from pathlib import Path

root = Path('.')
docs = root / 'docs'

new_docs = {
    '880-resilio-policy-origin-sticky-override-and-config-plane-fragmentation-evaluation.md': '''# Resilio policy-origin, sticky-override, and config-plane fragmentation evaluation

## Why this pass exists

The archive already had strong work on authority, artifact families, destructive actions, residency, transport, and maintenance semantics.
What it still lacked was one explicit evaluation of a narrower but highly consequential seam:

> when an operator asks `what settings actually govern this subject right now, where did those settings come from, and what will happen if I try to change or reset them?`, how many present-day Resilio planes do they still have to remember?

Current official Resilio docs are still useful because they are candid about real policy sources.
They still openly say that:

- **Folder Preferences** own per-share controls such as Archive, read-only overwrite behavior, relay usage, tracker usage, LAN search, predefined hosts, and file download priority.
- **Power user preferences** publish standing defaults and switches such as `disable_remove_from_all_devices`, and some of those still have platform caveats such as `Ignored in Linux WebUI`.
- **File download priority** now has both a per-share control and a global `folder_defaults.transfer_priority` default, while a share whose priority was manually changed stops inheriting later global changes even if manually set back to `None`.
- **Selective Sync** and **Synchronization Modes** still say mode can be chosen when first connecting, after connection, and when a folder arrives automatically from linked devices.
- **Sync Private Identity & Linking My Devices** still says linked devices auto-receive folders and are prompted with a default folder location plus Disconnected / Selective Sync / Synced posture.
- **Running Sync in configuration mode** still says advanced preferences can be injected through `sync.conf`, that only Standard folders can be set up there, and that if shared folders are specified in configuration then WebUI is disabled and those configured directories override folders previously added from WebUI.

That is good candor.
It is also strong evidence that AnonSync should not clone the exact contract.

## What current Resilio still gets right

### 1) Effective settings really do come from more than one place

Resilio is right that some settings are per-share, some are standing defaults, some are link-time choices, and some are boot-time or configuration-plane choices.
Pretending there is only one policy plane would be dishonest.

### 2) Defaults matter across future arrivals

Resilio is also right that connected-device defaults and folder defaults can affect later arrivals and later created shares.
Those defaults are not cosmetic.

### 3) Config-plane ownership is materially different from casual UI edits

Resilio is right that startup configuration can override previously added folders and even suppress WebUI in some cases.
That is not just another checkbox.
It is a different control plane.

## Why AnonSync still should not clone it

### 1) One ordinary question still leaks across too many policy planes

Current Resilio still makes the ordinary operator answer depend on remembering whether the active setting came from:

- share preferences
- a global power-user default
- a linked-device connect default
- a connect-time choice
- a startup configuration file
- a platform/runtime caveat such as Linux WebUI behavior

Those are real distinctions, but the product should own them in one provenance grammar rather than forcing article archaeology.

### 2) `Return to default` is not honest enough if inheritance does not really rejoin

The current file-priority docs are especially revealing.
A manually changed share priority stops inheriting later global changes even if it is later set back to `None`.
That means `neutral` can still secretly mean `sticky local exception` rather than `rejoined inheritance`.
AnonSync should refuse that ambiguity.

### 3) Config-plane supremacy is still too easy to miss

Current configuration-mode docs still say configured shared directories override folders previously added from WebUI and disable WebUI when the config explicitly defines shared folders.
That is a strong control-plane boundary, but it still mostly lives in setup prose.
A serious product should publish when an effective policy is config-owned and when the UI is no longer the source of truth.

### 4) Blast radius is still hard to inspect before edits

Changing a share preference, changing a standing default, changing a linked-device mode default, and changing a config template do not have the same scope.
Operators deserve a first-class preview of whether they are editing one subject, all inheriting subjects, future arrivals only, or a configuration-owned cohort.

### 5) Drift and exception truth are still too hidden

Once settings can come from several planes, a fleet accumulates exceptions.
Current Resilio reveals pieces of that truth, but the product still does not own a durable `why this share differs from the expected default` page family.
AnonSync should.

## Hard decisions now locked for AnonSync

1. **Every effective policy field carries provenance.** Value alone is never enough.
2. **`Return to default` means rejoin inheritance for real.** It cannot leave a dormant sticky override behind.
3. **Config-plane ownership must stay visible.** A config-owned subject cannot pretend to be UI-owned.
4. **Policy changes preview their plane and blast radius.** Share-local edits, standing-default edits, and config edits are different verbs.
5. **Drift is a first-class object.** Exceptions, legacy overrides, and policy forks get their own review surface and receipt.
6. **Receipts preserve source-of-truth lineage.** Later operators must be able to tell not only what the value became, but also which plane won.

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Effective policy sheet**
- **Policy change preview**
- **Inheritance return review**
- **Policy drift watch**
- **Policy provenance receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still right that defaults, overrides, per-share settings, linked-device mode choices, and config-plane inputs are genuinely different sources of truth. But it still makes the operator reconstruct effective policy from several planes, and it still tolerates sticky local exceptions that do not clearly return to inheritance. AnonSync should keep the candor and refuse the fragmented policy-origin contract.
''',
    '881-effective-policy-sheet-page-origin-precedence-and-current-force-interface-spec.md': '''# Effective policy sheet page: origin, precedence, and current-force interface spec

## Purpose

This page answers one ordinary question:

> what rules are actually in force for this subject right now, which plane supplied each one, and which stronger or weaker planes were overridden?

The page exists because a resolved value without provenance is not enough.

## Core decision

Every serious subject that can inherit defaults, carry local overrides, or be config-owned must render one first-class **Effective policy sheet** page.
That page owns:

- resolved field values
- origin plane
- precedence result
- mutability from the current surface
- nearby competing defaults
- strongest safe sentence

## Fixed page order

1. subject strip
2. effective fields table
3. plane stack card
4. exception and drift card
5. future-arrivals card
6. source-of-truth rail

### 1) Subject strip

Show:

- subject label
- subject family
- scope class
- current policy posture summary
- strongest next-safe action

Scope classes must include at minimum:

- `subject-local only`
- `inherits standing default`
- `local override active`
- `future-arrivals default`
- `config-owned`
- `derived from parent cohort`

### 2) Effective fields table

For each serious field, show a row with at least:

- field name
- current value
- origin plane
- winning precedence reason
- mutable from here? yes/no
- if changed here, expected blast radius

Fields worth supporting include at minimum:

- residency / sync mode
- arrival-placement policy
- archive-bearing posture
- destructive-heal posture
- relay / tracker / LAN / known-host posture
- queue / priority posture
- any standing cohort default relevant to this subject

### 3) Plane stack card

Publish the planes in precedence order, for example:

- configuration-plane declaration
- standing cohort default
- linked-device or seat default
- subject-local override
- temporary reviewed exception

The page must say which planes were present, which plane won, and which lower plane values were superseded.

### 4) Exception and drift card

Show:

- whether this subject differs from its cohort expectation
- whether the difference is reviewed, inherited, legacy, or accidental
- who last changed it
- whether the exception is aging, expected, or ready for rejoin review

### 5) Future-arrivals card

If the current field also shapes future arrivals or future subjects, publish that separately.
The page must not let a future-arrivals default impersonate a current-subject guarantee, or vice versa.

### 6) Source-of-truth rail

Link to the latest policy-change preview, inheritance return review, drift receipt, or config ownership receipt when available.

## Rules

### Rule 1 — effective value must never appear without origin

A naked `ON`, `OFF`, `Synced`, or `Use relay` value is insufficient.
The operator must be able to see where the value came from.

### Rule 2 — precedence must be inspectable

The page must show not only the winning value, but why another plausible source lost.

### Rule 3 — config-owned subjects publish that fact loudly

If the current subject is governed by a configuration-plane declaration, the page must say so before offering UI edits that would imply local ownership.

### Rule 4 — blast radius must stay adjacent to editable fields

Any row that can be changed from this page must say whether the result applies here only, to inheriting siblings, or to future arrivals.

## Acceptance criteria

A later operator can:

- tell which value is currently in force
- tell where that value came from
- tell which competing default or override lost
- tell whether a change here is local, cohort-wide, or future-only
- tell whether the subject is UI-owned or config-owned
''',
    '882-policy-change-preview-page-scope-plane-and-propagation-interface-spec.md': '''# Policy change preview page: scope, plane, and propagation interface spec

## Purpose

This page answers one ordinary question:

> if I change this policy now, which control plane am I editing, what cohort will feel it, and which subjects remain explicit exceptions?

The page exists because changing a share-local value, a standing default, and a config-owned rule are not the same action.

## Core decision

Any serious policy edit must pass through a first-class **Policy change preview** page before commit.
The preview owns:

- target field family
- target control plane
- blast radius
- exception handling
- supersession effect
- strongest safe sentence after commit

## Fixed page order

1. requested-change strip
2. target-plane card
3. propagation card
4. exception-preservation card
5. conflict / lock card
6. commit boundary card

### 1) Requested-change strip

Show:

- current effective value
- requested new value
- target subject or cohort
- current source plane
- strongest next-safe action

### 2) Target-plane card

One of the following must be selected explicitly:

- `subject-local override`
- `standing default edit`
- `future-arrivals default edit`
- `configuration-plane edit`
- `temporary reviewed exception`
- `blocked from this surface`

This card must explain why the chosen plane is the real one being edited.

### 3) Propagation card

Publish the exact blast radius:

- this subject only
- all currently inheriting subjects
- future arrivals only
- config-owned cohort on next activation
- explicit exceptions unaffected
- siblings requiring separate review

The operator must see examples of affected and unaffected subjects before commit.

### 4) Exception-preservation card

Show whether the change will:

- create a new exception
- clear an existing exception
- leave legacy exceptions in place
- force drift review because the cohort will still diverge afterward

### 5) Conflict / lock card

Publish blockers such as:

- config-owned lock
- narrower derivative ceiling
- reviewed danger barrier required
- stale receipt / freshness expiry
- blocked because current surface is read-only for this plane

### 6) Commit boundary card

End with one clear outcome:

- `change this subject`
- `change inheriting cohort`
- `change future default`
- `open config-plane workflow`
- `review drift first`
- `blocked`

## Rules

### Rule 1 — preview the plane, not just the value delta

`Turn relay off` or `Set Synced` is insufficient.
The operator must know which plane is actually being edited.

### Rule 2 — propagation must be concrete

The preview must name touched subjects, untouched exceptions, and future-only effects before commit.

### Rule 3 — locks must explain source-of-truth ownership

A config-owned or derivative-locked field cannot merely say `unavailable`.
It must say which stronger plane owns the truth.

## Acceptance criteria

A later operator can:

- tell which control plane is being changed
- tell which subjects change now and which do not
- tell whether the action creates or clears drift
- tell whether a different workflow is required because this surface is not the source of truth
''',
    '883-inheritance-return-review-page-sticky-override-and-default-rejoin-interface-spec.md': '''# Inheritance return review page: sticky override refusal and default rejoin interface spec

## Purpose

This page answers one ordinary question:

> when I say `return to default`, am I really rejoining inheritance, or am I leaving behind a hidden local exception that merely looks neutral?

The page exists because `None`, `Auto`, or `Default` is not automatically the same thing as true inheritance.

## Core decision

Whenever a subject leaves an explicit override and claims to return to a parent/default rule, the product must render a first-class **Inheritance return review** page.

## Fixed page order

1. return strip
2. parent-rule card
3. sticky-exception test card
4. future-reaction card
5. rejoin receipt preview
6. commit boundary

### 1) Return strip

Show:

- current explicit override
- claimed destination default
- source cohort or parent
- strongest next-safe action

### 2) Parent-rule card

Publish the exact parent/default rule that will be inherited after rejoin, including:

- current inherited value
- owning plane
- when it last changed
- nearby pending changes already known

### 3) Sticky-exception test card

This card must answer explicitly:

- will any local exception remain after this action?
- will later parent changes affect this subject again?
- does any hidden remembered value survive behind the scenes?

Allowed verdicts:

- `true rejoin`
- `partial rejoin with remaining exception`
- `cannot rejoin from this surface`
- `blocked until config / cohort review`

### 4) Future-reaction card

Show one concrete simulation:

- if the parent default changes tomorrow, what happens to this subject?
- if the cohort splits, does this subject follow the parent or stay pinned?

### 5) Rejoin receipt preview

Preview the receipt sentence that will survive:

- `this subject now truly inherits`
- `this subject still carries a local exception`
- `this subject is pinned by a stronger plane`

### 6) Commit boundary

End with one clear action:

- `rejoin inheritance`
- `keep explicit override`
- `review stronger plane`
- `blocked`

## Rules

### Rule 1 — neutral labels must not lie

`Default`, `Auto`, `None`, or a cleared field must not imply inheritance unless future parent changes will truly flow through.

### Rule 2 — future reaction must be demonstrated

The page must simulate at least one future parent change to prove whether inheritance has really resumed.

### Rule 3 — hidden remembered overrides are forbidden

AnonSync must not preserve a dormant local exception that still wins later while pretending the subject returned to default.

## Acceptance criteria

A later operator can:

- tell whether the subject truly rejoined inheritance
- tell whether a hidden local exception remains
- tell how a later parent change will affect the subject
- preserve a receipt proving that `return to default` really meant what it said
''',
    '884-policy-drift-watch-page-share-divergence-exception-lineage-and-remediation-interface-spec.md': '''# Policy drift watch page: share divergence, exception lineage, and remediation interface spec

## Purpose

This page answers one ordinary question:

> which related subjects no longer follow the same policy, why do they differ, and what is the cheapest honest way to bring them back into a readable cohort?

The page exists because multi-plane policy produces exceptions over time, and exceptions should not remain invisible folklore.

## Core decision

Any cohort with meaningful shared defaults or expected common posture must render a first-class **Policy drift watch** page whenever divergence appears.

## Fixed page order

1. cohort strip
2. divergence matrix
3. exception lineage card
4. remediation ladder
5. safety / blast-radius card
6. drift receipt rail

### 1) Cohort strip

Show:

- cohort name
- governing default or expected posture
- number of conforming subjects
- number of exceptions
- strongest next-safe action

### 2) Divergence matrix

List the key subjects and policy fields with at least:

- effective value
- expected value
- origin plane
- difference class
- age of divergence

Difference classes should include at minimum:

- `reviewed exception`
- `legacy override`
- `config-owned split`
- `temporary divergence`
- `accidental drift`
- `blocked from convergence`

### 3) Exception lineage card

For the selected divergent subject, publish:

- first divergence event
- last reviewed change
- source-of-truth plane
- whether the exception is still justified
- whether newer cohort defaults have bypassed it

### 4) Remediation ladder

Offer ordered repair verbs such as:

- keep exception and receipt it
- rejoin inheritance
- promote to new cohort default
- split into separate cohort
- open config-plane review

### 5) Safety / blast-radius card

Before any convergence action, show:

- which subjects will change
- which dangerous or destructive implications follow
- which reviewed exceptions must be preserved
- which receipts will be superseded

### 6) Drift receipt rail

Link to latest change preview, inheritance rejoin receipt, config review receipt, or drift classification receipt.

## Rules

### Rule 1 — drift must be named, not merely implied

A divergent subject cannot hide inside a quiet settings page.
The product must show that it differs from expectation.

### Rule 2 — expected value must be visible beside actual value

The operator should not have to remember the cohort default from another page.

### Rule 3 — remediation must preserve legitimate exceptions

Convergence tools must not steamroll reviewed, necessary deviations.

## Acceptance criteria

A later operator can:

- tell which subjects are exceptions
- tell why each one differs
- tell whether the difference is justified, legacy, or accidental
- choose an honest convergence or split action without guessing blast radius
''',
    '885-policy-provenance-receipt-page-effective-state-origin-and-supersession-boundary-interface-spec.md': '''# Policy provenance receipt page: effective state, origin lineage, and supersession boundary interface spec

## Purpose

This receipt answers one ordinary question:

> after a policy change, reset, or drift review, what value is in force now, which plane owns it, and what older assumption did this receipt supersede?

The receipt exists because later operators should not have to reconstruct policy origin from memory.

## Core decision

Every serious policy mutation, inheritance rejoin, or drift classification emits a first-class **Policy provenance receipt**.

## Receipt body

The receipt must preserve at minimum:

- subject or cohort scope
- field family changed or reviewed
- resulting effective value
- winning source plane
- losing competing plane if relevant
- blast radius
- exception status after action
- future-arrivals effect if any
- superseded receipt or assumption
- reopen triggers

## Receipt sections

### 1) Result sentence

One durable sentence such as:

- `This subject now inherits residency policy from cohort default.`
- `This share now carries a reviewed local override for relay posture.`
- `This cohort default changed, but listed exceptions remain pinned.`
- `This subject is config-owned; UI-local edits do not own its truth.`

### 2) Provenance block

Show:

- winning plane
- previous plane
- precedence reason
- whether the outcome was mutation, rejoin, classification, or lock acknowledgment

### 3) Scope block

Show:

- touched current subjects
- untouched exceptions
- future subjects affected or unaffected

### 4) Supersession block

Publish what older assumption is no longer safe to reuse.
Examples:

- `previous local override receipt superseded`
- `cohort-default assumption invalidated for listed exceptions`
- `config-plane lock replaced earlier UI-owned assumption`

### 5) Reopen block

Publish triggers such as:

- parent default changes again
- config plane changes
- subject leaves cohort
- exception ages out
- drift appears elsewhere in the cohort

## Rules

### Rule 1 — receipts preserve origin, not just value

`Relay disabled` or `Selective Sync on` is insufficient.
The receipt must say who now owns that truth.

### Rule 2 — supersession must be explicit

A newer provenance receipt must name the older receipt or assumption it weakened or replaced.

### Rule 3 — future-only effects stay distinct from current-subject effects

The receipt must separate `what changed here now` from `what later arrivals will inherit`.

## Acceptance criteria

A later operator can:

- tell the current effective value
- tell which plane owns it
- tell what older policy belief is no longer safe
- know exactly when to reopen the policy question
''',
}

for name, content in new_docs.items():
    (docs / name).write_text(content.strip() + '\n', encoding='utf-8')


def prepend(path_str: str, content: str):
    path = Path(path_str)
    old = path.read_text(encoding='utf-8')
    path.write_text(content.strip() + '\n\n' + old, encoding='utf-8')


def append(path_str: str, content: str):
    path = Path(path_str)
    old = path.read_text(encoding='utf-8')
    if not old.endswith('\n'):
        old += '\n'
    path.write_text(old + '\n' + content.strip() + '\n', encoding='utf-8')

readme_addendum = '''## Revision addendum — effective policy provenance, sticky-override refusal, and config-plane ownership

This revision continues directly from `rev0289` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **per-share Folder Preferences, Power user standing defaults, file-priority inheritance behavior, linked-device default connect modes, and configuration-mode ownership / override semantics**.
2. Tightens the non-clone line again: borrow Resilio's candor that effective policy can come from several real planes; refuse any contract where the operator still has to reconstruct current truth from share preferences, defaults, config files, and sticky exceptions.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio policy-origin truth is still too fragmented to clone even though the underlying distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: effective policy sheet, policy change preview, inheritance return review, policy drift watch, and policy provenance receipt.
5. Makes one hard product decision explicit: **every effective policy field carries provenance**. A resolved value without origin is not enough.
6. Makes another hard product decision explicit: **`return to default` must really rejoin inheritance**. AnonSync will not keep a hidden sticky override behind a neutral label.
7. Makes a third hard product decision explicit: **config-plane ownership stays visible**. A config-owned subject cannot pretend to be UI-owned truth.
8. Packages the result as another continuation archive whose new tranche makes the `effective policy / origin plane / drift / true rejoin` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present policy-origin contract**

This time the reason is especially clear around **per-share preferences, standing defaults, link-time modes, and configuration-plane ownership**.
Current official materials simultaneously show that:

- `Folder Preferences` still owns per-share controls such as Archive, read-only overwrite behavior, relay, tracker, LAN search, predefined hosts, and file download priority.
- `Power user preferences` still publishes standing defaults and switches such as `disable_remove_from_all_devices`, including platform caveats like `Ignored in Linux WebUI`.
- `File download priority` still says a global `folder_defaults.transfer_priority` can apply to existing and new shares, while a share with a manually changed priority stops inheriting later global changes even if manually set back to `None`.
- `Selective Sync`, `Synchronization Modes`, and `Sync Private Identity & Linking My Devices` still spread mode truth across connect-time choice, post-connect change, and linked-device defaults.
- `Running Sync in configuration mode` still says advanced preferences can be injected through config, that only Standard folders can be set up there, and that configured shared folders override previously added WebUI folders while disabling WebUI for that case.

That candor is useful.
The policy-origin contract is the problem.
AnonSync should not clone a world where the operator still has to reconstruct, from several planes and caveats, whether a field is inherited, locally overridden, config-owned, future-only, or merely pretending to have returned to default.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful truths are real, but the present-day policy contract still hides too much source-of-truth meaning inside separate preference planes, startup configuration, and sticky exceptions instead of owning effective policy as one stable page family.**

## New documents in rev0290

- `880` Resilio policy-origin, sticky-override, and config-plane fragmentation evaluation
- `881` Effective policy sheet page
- `882` Policy change preview page
- `883` Inheritance return review page
- `884` Policy drift watch page
- `885` Policy provenance receipt page
'''

status_addendum = '''## Latest addendum — effective policy provenance, sticky overrides, and config-plane ownership after rev0289

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **effective policy answers still depend too much on separate planes such as per-share preferences, standing defaults, linked-device defaults, and startup configuration**
- **`return to default` can still fail to mean true rejoin, because current Resilio documents at least one sticky override behavior that stops inheriting later changes even after appearing neutral again**
- **config-plane ownership is real but still too easy to miss when configured shares override earlier WebUI additions and suppress that UI path**

Hard decisions made in this tranche:

1. **Every effective policy field carries provenance.** AnonSync never shows resolved value without origin plane.
2. **`Return to default` means true inheritance rejoin.** AnonSync will not preserve a hidden dormant override behind a neutral label.
3. **Config-plane ownership stays visible.** A config-owned subject cannot pretend that the current UI is the source of truth.
4. **Policy edits preview plane and blast radius.** Share-local change, cohort-default change, future-arrivals default change, and config change are different verbs.
5. **Drift is a first-class object.** Exceptions, legacy overrides, and policy forks get their own review surface and durable receipt.

That yields five more ordinary product-owned pages:

- **Effective policy sheet page**
- **Policy change preview page**
- **Inheritance return review page**
- **Policy drift watch page**
- **Policy provenance receipt page**

This tranche closes a real gap between earlier residency / authority work and the ordinary operator question `what is actually governing this thing right now, who set it, and did my reset really put it back under the parent rule?`.
'''

append(docs / '10-resilio-sync-evaluation.md', '''## Revision addendum — evaluation after rev0289: borrow policy-plane candor, reject provenance folklore

Another current Resilio pass improves the evaluation in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that effective settings can genuinely come from different planes such as per-share controls, standing defaults, linked-device defaults, and configuration files
- admitting that some settings affect current subjects while others affect future arrivals or later-created shares
- admitting that configuration-mode startup can be a stronger control plane than casual UI edits
- admitting that platform/runtime caveats can change whether a visible option actually governs behavior from a given surface

### Refuse to clone

Do not clone these traits:

- making the operator merge Folder Preferences, Power user preferences, link-time mode prompts, and configuration-mode notes just to answer `what governs this right now?`
- letting `default` or `None` sound like true inheritance when a sticky local exception may still survive behind the scenes
- hiding config-plane supremacy inside setup prose when configured shares override earlier WebUI ownership
- leaving no durable page that says which plane won, which lower plane lost, and what blast radius a policy edit really has

### Stronger replacement

AnonSync should publish five first-class surfaces instead:

- **Effective policy sheet**
- **Policy change preview**
- **Inheritance return review**
- **Policy drift watch**
- **Policy provenance receipt**

The governing rule is simple:

> if the product is strong enough to show a policy value, it must also own where that value came from, whether it truly inherits, what stronger plane could override it, and which cohort will feel a change.
''')

append(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', '''## Revision addendum — scorecard after rev0289: borrow multi-plane candor, reject hidden source-of-truth answers

Another current Resilio pass improves the scorecard in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that policy can come from more than one legitimate plane
- admitting that standing defaults and future-arrivals behavior are real contracts, not cosmetic convenience
- admitting that configuration-plane startup can outrank interactive UI changes
- admitting that some platform surfaces still have caveats that materially affect policy ownership

### Refuse to clone

Do not clone these traits:

- making the ordinary policy answer depend on separately remembered share prefs, power-user defaults, linked-device mode defaults, and config files
- allowing `return to default` to leave a hidden sticky exception behind
- letting config-owned truth impersonate UI-owned truth
- leaving no durable receipt of which plane won and which older assumption was superseded

### Stronger replacement

AnonSync should publish five first-class surfaces instead:

- **Effective policy sheet**
- **Policy change preview**
- **Inheritance return review**
- **Policy drift watch**
- **Policy provenance receipt**

The governing rule is simple:

> if the product is strong enough to say `this setting is in force`, it must also say which plane owns that truth, whether the subject truly inherits, and what blast radius a change would carry.
''')

append(docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md', '''## Revision addendum — clone-veto after rev0289: effective policy may not hide its origin plane or fake a return to default

The interface clone-veto now adds another family.

If the operator still has to merge share preferences, power-user defaults, link-time mode prompts, configuration-mode notes, and remembered sticky exceptions to answer any of the following, the clone-veto still fails:

1. **Which control plane currently owns this field?**
2. **Is the visible value inherited, a local override, a future-arrivals default, or a config-owned declaration?**
3. **If I choose `return to default`, will this subject truly rejoin inheritance or keep a hidden local exception?**
4. **What exact cohort feels this change now, and which exceptions remain pinned afterward?**
5. **What durable receipt proves which plane won and which older assumption was superseded?**

Required page family for passing this veto:

- **Effective policy sheet**
- **Policy change preview**
- **Inheritance return review**
- **Policy drift watch**
- **Policy provenance receipt**
''')

append(docs / '20-product-direction.md', '''## Revision addendum — product direction after rev0289: effective policy needs visible provenance and true inheritance rejoin

The product direction should now be explicit on one more point:

- an effective setting is not self-explanatory without origin
- `default` is not honest enough unless future parent changes really flow through again
- share-local change, cohort-default change, future-arrivals change, and config-plane change are not the same verb
- config-owned truth must stay visible when it outranks interactive UI ownership
- exceptions and drift need durable lineage rather than folklore

So AnonSync should publish effective policy as a first-class provenance object.
Every serious sync-mode, residency, relay, archive, overwrite, arrival-placement, and cohort-default surface should show current value, winning plane, competing lower plane, blast radius, drift status, and reopen conditions before the product treats a visible value as the whole truth.
''')

append(docs / '39-interface-pattern-language.md', '''## Revision addendum — new pattern: origin before effective value

Pattern name: **Origin before effective value**

Use when:

- the same visible field can be supplied by more than one policy plane
- a default may be overridden locally or by configuration
- a `reset` or `return to default` action could otherwise overclaim true inheritance

Rules:

- never show a resolved setting without its origin plane
- keep the losing competing plane visible when that comparison matters
- show future-arrivals effects separately from current-subject effects
- do not let `Default`, `Auto`, or `None` imply inheritance unless later parent changes will truly flow through again

## Revision addendum — new pattern: reset must prove rejoin

Pattern name: **Reset proves rejoin**

Use when:

- a surface claims to return to default
- sticky exceptions or pinned locals are possible
- later parent changes are the real test of whether inheritance resumed

Rules:

- simulate a later parent change before calling the result `default` again
- forbid hidden dormant overrides behind neutral labels
- issue a receipt that says whether the subject truly inherits or still carries an exception
- keep config-plane locks visible when they prevent real rejoin
''')

append(docs / '40-architecture-decisions.md', '''## Revision addendum — architecture decision after rev0289: compile effective policy with provenance and precedence

The archive now needs one more explicit architecture rule:

- every serious policy field must compile into a provenance-bearing effective-state object, not just a resolved value cached on the client

At minimum the system should preserve:

- subject or cohort scope
- field family
- winning effective value
- winning source plane
- losing competing plane when relevant
- precedence reason
- blast radius of edits on that plane
- exception / drift status
- superseded receipt or assumption
- reopen triggers

A visible value may still be enough for quick scanning, but it must not silently stand in for source-of-truth ownership or inheritance state.
''')

append(docs / '50-roadmap.md', '''## Revision addendum — roadmap after rev0289: policy provenance, drift watch, and true-default rejoin tranche

Near-term work newly justified by this pass:

1. Add effective-policy object model for field family, winning plane, competing lower planes, and blast radius.
2. Build policy change preview before any serious value edit is allowed to read as a single-plane toggle.
3. Add inheritance-return review so `default` can prove real rejoin rather than sticky exception theater.
4. Add drift-watch views that distinguish reviewed exceptions, legacy overrides, config-owned splits, and accidental divergence.
5. Emit policy provenance receipts with winning plane, superseded assumption, and reopen triggers so source-of-truth lineage never disappears.
''')

sources_addendum = '''## Revision addendum — policy provenance, sticky override, and config-plane ownership after rev0289

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about per-share Folder Preferences, Power user defaults, file-priority inheritance behavior, linked-device mode defaults, and configuration-mode ownership.
The new questions were:

> where do current official docs most clearly show that `what policy is in force right now?` is still answered across several control planes rather than one stable product-owned surface?

> where do those same current docs still show that `return to default` and `who owns this setting?` are not one stable operator grammar today because standing defaults, local overrides, linked-device defaults, and config-plane declarations can all compete?

The most load-bearing source set for this pass was:

- Resilio's current `Folder Preferences` article, which still publishes per-share controls for Archive, overwrite, relay, tracker, LAN search, predefined hosts, and file download priority.
- Resilio's current `Power user preferences` article, which still publishes standing defaults and switches such as `disable_remove_from_all_devices`, and still notes platform caveats like `Ignored in Linux WebUI`.
- Resilio's current `File download priority` article, which still says `folder_defaults.transfer_priority` can affect existing and new shares while a share whose priority was manually changed stops inheriting later global changes even if set back to `None`.
- Resilio's current `Selective Sync` article, which still says sync mode can be chosen at first connect, after connect, and when a folder is automatically added from linked devices.
- Resilio's current `Synchronization Modes` and `Sync Private Identity & Linking My Devices` articles, which still spread mode/default-path truth across linked-device defaults, current-subject modes, and future automatic arrivals.
- Resilio's current `Running Sync in configuration mode` article, which still says advanced preferences can be injected through config, that only Standard folders can be set up there, and that configured shared folders override previously added WebUI folders while disabling WebUI for that case.

## Additional Resilio official sources emphasized in rev0290

- Folder Preferences  
  https://help.resilio.com/hc/en-us/articles/205458125-Folder-Preferences

- Power user preferences  
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- File download priority  
  https://help.resilio.com/hc/en-us/articles/42328167759251-File-download-priority

- Selective Sync  
  https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync

- Synchronization Modes  
  https://help.resilio.com/hc/en-us/articles/205457775-Synchronization-Modes

- Sync Private Identity & Linking My Devices  
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Running Sync in configuration mode  
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode
'''

prepend('README.md', readme_addendum)
prepend(docs / '00-status.md', status_addendum)
append(docs / 'sources.md', sources_addendum)

