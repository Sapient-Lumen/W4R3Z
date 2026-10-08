from pathlib import Path
from textwrap import dedent

def prepend(path: Path, text: str):
    old = path.read_text()
    path.write_text(text.rstrip() + "\n\n" + old)

base = Path(__file__).resolve().parent

docs = base / 'docs'
rev = 'rev0254'
ts = '2026.03.21.23.59'
codename = 'indirectiontargetceiling'
prev = 'rev0253'

readme_header = dedent(f'''
# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{rev}`
- Timestamp: `{ts}` (America/New_York)
- Codename: `{codename}`

## What changed in this revision

This revision continues directly from `{prev}` and does seven concrete things:

1. Re-checks another current official Resilio Sync cluster around **soft links, hard links, symbolic links, junction-driven `.Conflict` fallout, platform split, and target non-transitivity**.
2. Sharpens the non-clone line again: borrow Resilio's candor that indirection objects are real and dangerous, while refusing any contract where an ordinary file-or-folder row hides whether the object itself survives, whether target bytes are included, and whether conflicts are expected on this seat family.
3. Adds one new **Resilio evaluation** document focused on how current Resilio still spreads one ordinary operator answer about `is this entry itself syncing, is its target syncing, or is this just a conflict generator here?` across link docs, conflict docs, and troubleshooting folklore.
4. Adds four new **interface page specs** for the missing workflow-owned surfaces in this pass: indirection posture, indirection action review, target transitivity proof, and indirection receipt.
5. Extends the interface/workbench doctrine so every serious alias-edge object now publishes **entry kind, platform lane, object fate, target scope, transitivity verdict, conflict hazard, and strongest safe sentence** before commit.
6. Refreshes status-bearing doctrine documents — status, evaluation, scorecard, clone-veto tests, product direction, roadmap, open questions, daemon API, sources, and README — so the new tranche is integrated rather than bolted on.
7. Packages the result as another continuation archive whose new tranche makes the `entry object / target bytes / platform split / conflict hazard` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's indirection-object contract**

This time the evidence is especially clear around **Windows treating soft links, hard links, junctions, and symbolic links as unsupported and conflict-prone, Unix preserving symbolic links while excluding target folders unless separately added, and conflict guidance still naming linked junctions as a direct conflict cause**.

Current official docs still openly distinguish real facts such as:

- Windows still not supporting soft links, junctions, hard links, or symbolic links in Sync, with `.Conflict` fallout still called out for each affected entry
- Unix still being able to synchronize symbolic links as links while target folders are still not synchronized unless added separately
- current conflict guidance still naming linked junctions as a concrete cause of `.Conflict` files or folders
- the live Sync v3 line still appearing through `3.1.2.1076`

That candor is good.
The non-clone problem is still workflow ownership.
Ordinary operators can still be pushed into several help pages before the product fully owns these questions:

- whether this row is an ordinary file/folder or an indirection object with a different fidelity contract
- whether the entry object itself survives, is flattened, is blocked, or is conflict-prone on this seat family
- whether target bytes are included now, excluded entirely, or require explicit separate admission
- whether following the target would widen the sync graph beyond what the current share already means
- what later receipt can prove the exact entry-kind and target-transitivity verdict that was applied

AnonSync should therefore make **indirection posture** and **target transitivity proof** first-class product objects.
Every serious alias-edge path should render entry kind, platform lane, object fate, target scope, transitivity verdict, conflict hazard, safe substitution ladder, and receipt language before the product treats the row as just another ordinary file or folder.

## Legacy revision notes preserved below
''').strip()

status_add = dedent('''
## Latest addendum — indirection objects, target non-transitivity, and junction-driven conflict fallout after rev0253

Another current Resilio pass now sharpens one more reason to **adapt, not clone**:

- **indirection posture / indirection action review / target transitivity proof / indirection receipt**

Current official Resilio docs still say Windows does not support soft links, hard links, symbolic links, or junctions in Sync and that using such links may lead to `.Conflict` files for each affected entry. Separate current docs still say Unix can synchronize symbolic links as links while target folders are not synchronized unless separately added. Separate current conflict guidance still names files or folders located in linked junctions as a direct cause of `.Conflict` artifacts.
That candor is useful.
The non-clone problem is still indirection ownership.

Ordinary operators can still be pushed into several official docs before the product fully owns these questions:

- whether the row is an ordinary file/folder or an indirection object
- whether the entry object itself is preserved, flattened, blocked, or likely to create conflict residue on this seat family
- whether target bytes are in scope now, out of scope now, or require separate admission
- whether following the target widens the graph beyond the current share contract
- what later receipt can prove the applied fidelity and transitivity verdict

AnonSync should therefore make **indirection posture** and **target transitivity proof** first-class product objects.
Every serious alias-edge path should render entry kind, platform lane, object fate, target scope, transitivity verdict, conflict hazard, safe substitution ladder, and receipt language before the product treats the row as just another ordinary file or folder.
''').strip()

eval_add = dedent('''
## Revision addendum — indirection objects, platform split, and target non-transitivity after rev0253

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about soft links, hard links, symbolic links, junction fallout, and `.Conflict` generation.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that a path row can be an indirection object with a materially different fidelity contract than an ordinary file or folder?

> where do those same current docs still show that the ordinary operator answer about `is this object syncing, is its target syncing, or is this just a conflict generator here?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Soft links, hard links and symbolic links` article, which still says Windows does not support these link classes and that they may create `.Conflict` entries, while Unix can synchronize symbolic links as links but not automatically synchronize the target folders.
- Resilio's current `Conflict files in Sync` article, which still names linked junctions as a concrete cause of `.Conflict` files or folders.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

That is useful candor.
The non-clone problem is workflow ownership.
Current Resilio still lets one ordinary answer about `what exactly is syncing here — the indirection object, the target bytes, both, or neither?` leak across a link article and conflict troubleshooting.

The archive now owes four more first-class pages:

- **Indirection posture**
- **Indirection action review**
- **Target transitivity proof**
- **Indirection receipt**

These pages are required whenever an entry that looks file-like or folder-like could otherwise hide platform-dependent object survival, target exclusion, conflict hazard, or graph-widening side effects.
''').strip()

scorecard_add = dedent('''
## Revision addendum — scorecard after rev0253: borrow indirection candor, reject object/target ambiguity

Another current Resilio pass improves the scorecard in one more narrow place.

### Borrow

Keep borrowing these traits:

- admitting that indirection objects are materially different from ordinary files or folders
- admitting that platform family changes whether a link object is supported at all
- admitting that target folders behind Unix symbolic links are not implicitly brought into scope
- admitting that some unsupported link/junction shapes can materialize as `.Conflict` fallout instead of quiet success

### Refuse to clone

Do not clone these traits:

- letting a normal-looking row hide whether the entry object itself survives here
- making the operator infer target inclusion from separate support articles instead of one page-owned verdict
- scattering the answer between link docs and conflict docs
- treating target-following as an invisible widening of the current subject graph

### Stronger replacement

AnonSync should publish four first-class surfaces instead:

- **Indirection posture**
- **Indirection action review**
- **Target transitivity proof**
- **Indirection receipt**

The governing rule is simple:

> if a path row is actually an indirection object, the product must state whether the object survives, whether target bytes are in scope, and whether following the target widens the graph before the operator commits to any repair or adoption step.
''').strip()

clone_veto_add = dedent('''
## Revision addendum — clone-veto after rev0253: indirection objects cannot masquerade as ordinary rows

The interface clone-veto now adds another family.

If the operator still has to merge link docs and conflict troubleshooting to answer any of the following, the clone-veto still fails:

1. **What exact entry class is this: ordinary file, ordinary folder, symbolic link, hard link, junction, or unresolved indirection?**
2. **Does this seat family preserve the entry object, flatten it, block it, or turn it into conflict-prone residue?**
3. **Are the target bytes in scope now, explicitly excluded, or only obtainable through separate admission?**
4. **Would following the target widen the sync graph beyond the current subject contract?**
5. **What later receipt proves the applied object-fate and target-transitivity verdict?**

Required page family for passing this veto:

- **Indirection posture**
- **Indirection action review**
- **Target transitivity proof**
- **Indirection receipt**
''').strip()

product_add = dedent('''
## Revision addendum — product direction after rev0253: alias-edge rows must publish object fate and target scope

The product direction should now be explicit on one more point:

- `looks like a folder` is not the same answer as `is an ordinary folder`
- `looks like a file` is not the same answer as `syncs like an ordinary file`
- `symlink preserved` is not the same answer as `target bytes are in scope`
- `unsupported here` is not the same answer as `harmless to leave alone`
- `follow target` is not the same answer as `no graph widening occurred`

So AnonSync should publish serious alias-edge work as a first-class indirection object.
Every meaningful indirection surface should show entry kind, platform lane, object fate, target scope, transitivity verdict, conflict hazard, safe substitution ladder, and strongest safe sentence before the product treats the row as ordinary content.
''').strip()

roadmap_add = dedent('''
## Revision addendum — roadmap after rev0253: schedule an indirection-object tranche before broader portability polish

The roadmap should now explicitly include one indirection-object tranche before any broad portability or filesystem-shape polish is treated as complete.

That tranche should deliver:

- one compiled server-side indirection-object record
- one operator-facing indirection posture page
- one indirection action review page
- one target transitivity proof page
- one indirection receipt
- one compact workbench lane for current entry-kind, target scope, and graph-widening risk

This should land before any effort that merely beautifies path warnings, because the semantic gap is still more important than the visual gap.
''').strip()

openq_add = dedent('''
## 0f) When should following an indirection target be exposed as a new subject-admission act instead of a convenience repair?

The archive now requires a first-class indirection review whenever an entry-looking row could also widen the graph by following another path.
What remains unresolved is the ergonomics budget:

- should `follow target` always be rendered as a graph-widening act rather than a silent repair
- when the target is inside the current subject, is automatic proof enough or should the operator still confirm coupling
- when the target is outside the current subject, should the default be block, separate admission, or local-only preservation
- how much conflict-prone unsupported-entry residue should the product tolerate before it escalates from warning to hard block

The archive should keep preferring explicit transitivity proof over convenience when object/target meaning could diverge.
''').strip()

interface_add = dedent('''
## Revision addendum — interface family after rev0253: indirection posture and target transitivity proof

Add four first-class objects to the interface grammar:

- `indirection_posture`
- `indirection_action_review`
- `target_transitivity_proof`
- `indirection_receipt`

These objects exist so `symlink`, `junction`, `looks like folder`, and `unsupported here` stop collapsing entry kind, object fate, target scope, graph widening, and conflict hazard into one vague answer.
''').strip()

daemon_add = dedent('''
## Revision addendum — daemon API after rev0253: indirection object state must be machine-readable

The daemon now owes one more class of structured record.
Any serious path inspection result should be able to expose:

- `entry_kind` (`ordinary-file`, `ordinary-folder`, `symbolic-link`, `hard-link`, `junction`, `alias-like`, `unknown-indirection`)
- `entry_object_fate` (`preserve`, `flatten`, `block`, `unsupported-conflict-prone`, `unknown`)
- `target_scope` (`inside-subject`, `outside-subject`, `unresolved`, `none`, `unknown`)
- `target_transitivity_verdict` (`included-now`, `excluded-now`, `separate-admission-required`, `cannot-prove`, `not-applicable`)
- `graph_widening_risk` (`none`, `inside-coupling-only`, `outside-subject-widening`, `unknown`)
- `conflict_hazard` (`none-known`, `possible`, `likely`, `observed`)

This exists so local UI, CLI, and receipts do not have to infer indirection truth from unstructured warnings or troubleshooting residue.
''').strip()

sources_add = dedent('''
## Revision addendum — indirection objects, target non-transitivity, and conflict fallout after rev0253

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about symbolic links, hard links, directory junctions, unsupported-entry consequences, and `.Conflict` fallout.
The new questions were:

> where do current official docs most clearly show that Resilio is actually fairly candid that a normal-looking path row may be an indirection object with a materially different fidelity contract?

> where do those same current docs still show that the ordinary operator answer about `is this object syncing, is its target syncing, or is this a conflict generator here?` still depends on several documents instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Soft links, hard links and symbolic links` article, which still says Windows does not support these classes and that `.Conflict` fallout may result, while Unix can synchronize symbolic links as links but not automatically synchronize the target folders.
- Resilio's current `Conflict files in Sync` article, which still names linked junctions as a direct cause of `.Conflict` artifacts.
- Resilio's current `Resilio Sync 3.0 change log`, which still shows the active v3 line through `3.1.2.1076`.

## Additional Resilio official sources emphasized in rev0254

- Soft links, hard links and symbolic links
  https://help.resilio.com/hc/en-us/articles/205504529-Soft-links-hard-links-and-symbolic-links

- Conflict files in Sync
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- Resilio Sync 3.0 change log
  https://help.resilio.com/hc/en-us/articles/31386579044755-Resilio-Sync-3-0-change-log
''').strip()

prepend(base / 'README.md', readme_header)
prepend(docs / '00-status.md', status_add)
prepend(docs / '10-resilio-sync-evaluation.md', eval_add)
prepend(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', scorecard_add)
prepend(docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md', clone_veto_add)
prepend(docs / '20-product-direction.md', product_add)
prepend(docs / '50-roadmap.md', roadmap_add)
prepend(docs / '64-critical-open-questions.md', openq_add)
prepend(docs / '30-interface-spec.md', interface_add)
prepend(docs / '31-daemon-api-spec.md', daemon_add)
prepend(docs / 'sources.md', sources_add)

new_docs = {
    '696-resilio-indirection-object-platform-split-and-target-nontransitivity-evaluation.md': dedent('''
        # Resilio indirection-object platform split and target non-transitivity evaluation

        ## Why this seam matters now

        Earlier archive work already noticed unsupported links and filesystem-shape risk.
        This revision promotes that hint into its own family because current official Resilio docs are still unusually candid about a deeper truth:

        > a path row that looks like an ordinary file or folder can actually be an indirection object, and the contract differs by platform family, by entry class, and by whether you mean the object itself or the bytes behind its target.

        That is exactly the kind of seam AnonSync must own directly rather than inherit as folklore.

        ## Current official Resilio candor

        Current official Resilio docs still say:

        - on Windows, Sync does not support soft links, junctions, hard links, or symbolic links
        - use of those entries may lead to `.Conflict` files for each affected file or folder
        - on Unix, symbolic links may be synchronized as links
        - but the target folders referenced by those links are not synchronized unless added separately
        - conflict guidance still names linked junctions as a concrete cause of `.Conflict` artifacts
        - the active Sync v3 line is still visible through `3.1.2.1076`

        That is strong candor.
        Resilio is not pretending these edge classes do not exist.

        ## Why not clone the contract

        The non-clone problem is not honesty.
        The non-clone problem is that one ordinary operator answer still has to be reconstructed from more than one place:

        - what class of entry was actually found
        - whether this seat preserves the object or rejects it
        - whether the target bytes are already in scope
        - whether following the target would widen the graph
        - whether the likely outcome is preservation, flattening, block, or `.Conflict` residue

        A serious sync product should not make operators infer that by stitching together a link article and a conflict article.

        ## Product lesson for AnonSync

        AnonSync should treat these as first-class **indirection objects**, not merely as odd path names.
        Every indirection object should expose two separate truths at once:

        1. **entry-object truth** — what happens to the link/junction object itself on this seat family
        2. **target-transitivity truth** — whether the bytes behind the target are already included, explicitly excluded, or require a separate admission act

        These truths should never collapse into one vague sentence like `supported`, `unsupported`, or `syncs as link`.

        ## Required replacement pages

        This revision therefore adds four page families:

        - `697` **Indirection posture**
        - `698` **Indirection action review**
        - `699` **Target transitivity proof**
        - `700` **Indirection receipt**

        ## Tightened design rule

        > if a row is actually an indirection object, the product must separately publish object fate and target scope before any preservation, flattening, follow-target, or repair action can be described as safe.

        ## Non-clone conclusion

        Keep the Resilio candor.
        Refuse the page contract.
        A path row should not look ordinary while its object fate, target scope, and conflict hazard are still support-article knowledge.
    ''').strip() + '\n',
    '697-indirection-posture-page-entry-kind-platform-lane-and-object-fate-interface-spec.md': dedent('''
        # Indirection posture page: entry kind, platform lane, and object fate interface spec

        ## Purpose

        This page exists to answer one ordinary operator question:

        > what kind of path row is this really, and what exactly survives on this seat — the object, the target, both, or neither?

        ## Core decision

        Every serious sync product must own one first-class **Indirection posture** page whenever a row that looks like a file or folder is actually an indirection object.

        ## Fixed page order

        1. identity strip
        2. entry-class card
        3. object-fate card
        4. target-scope card
        5. graph-widening card
        6. receipts and next action

        ### 1) Identity strip

        Show:

        - subject and seat
        - entry path
        - current display name
        - detected entry kind (`ordinary-file`, `ordinary-folder`, `symbolic-link`, `hard-link`, `junction`, `alias-like`, `unknown-indirection`)
        - current summary verdict (`ordinary`, `preserved-as-object`, `target-excluded`, `separate-admission-needed`, `blocked`, `conflict-prone`)

        ### 2) Entry-class card

        Show:

        - detection basis used for classification
        - seat family / filesystem lane used for interpretation
        - whether this platform lane supports the entry object natively
        - whether the object is being treated as entry, payload, or unsupported control residue

        ### 3) Object-fate card

        Show:

        - `entry_object_fate` (`preserve`, `flatten`, `block`, `unsupported-conflict-prone`, `unknown`)
        - strongest safe sentence
        - stronger forbidden sentence
        - whether a mismatch already produced warnings or conflicts

        ### 4) Target-scope card

        Show:

        - whether the entry has a resolvable target
        - target scope (`inside-subject`, `outside-subject`, `unresolved`, `none`, `unknown`)
        - whether target bytes are in scope now
        - whether target inclusion would require a separate admission act
        - whether target inspection is safe from this page

        ### 5) Graph-widening card

        Show:

        - `graph_widening_risk` (`none`, `inside-coupling-only`, `outside-subject-widening`, `unknown`)
        - whether follow-target would widen the current subject contract
        - whether later drift remains coupled if the operator keeps the object only
        - safest next action (`leave-local`, `preserve-object`, `follow-target`, `branch-bytes`, `block`, `inspect-only`)

        ### 6) Receipts and next action

        Show:

        - latest indirection receipt
        - latest target transitivity proof
        - any conflict evidence linked to this object
        - next honest action

        ## Public objects

        ### Indirection posture page

        Fields:

        - `indirection_posture_page_id`
        - `subject_ref`
        - `seat_ref`
        - `entry_path`
        - `entry_kind`
        - `platform_lane`
        - `entry_object_fate`
        - `target_scope`
        - `target_transitivity_verdict`
        - `graph_widening_risk`
        - `conflict_hazard`
        - `receipt_refs[]`
        - `next_honest_action`

        ## Guardrails

        The page must never:

        - imply that preserving a symbolic link automatically preserves target bytes
        - imply that an unsupported entry is harmless when conflict fallout is possible
        - silently widen the graph by following a target
        - flatten object fate and target scope into one badge

        ## Success criteria

        The page is successful only when an operator can answer:

        1. what entry kind was actually found
        2. what happens to the object on this seat family
        3. whether target bytes are in scope now
        4. whether following the target widens the graph
        5. what the safest next action is
    ''').strip() + '\n',
    '698-indirection-action-review-page-preserve-follow-target-branch-or-block-interface-spec.md': dedent('''
        # Indirection action review page: preserve, follow target, branch, or block interface spec

        ## Purpose

        This page exists to stop indirection repair from being treated as a casual path tweak.

        The operator should be able to review one exact choice:

        > do I preserve the object, follow its target, branch ordinary bytes, or block this row on this seat?

        ## Allowed reviewed actions

        - `preserve-object`
        - `follow-target-inside-subject`
        - `follow-target-as-separate-subject`
        - `branch-ordinary-bytes`
        - `keep-local-only`
        - `block-on-this-seat`

        ## Required review columns

        Every action row must preview:

        - object fate after apply
        - target transitivity after apply
        - graph widening delta
        - expected parity across seat families
        - conflict hazard delta
        - reversibility class

        ## Fixed page order

        1. current posture strip
        2. proposed action rows
        3. widening and coupling review
        4. parity and conflict review
        5. commit guardrail language

        ### 1) Current posture strip

        Show:

        - current entry kind
        - current object fate
        - current target-scope verdict
        - current conflict hazard

        ### 2) Proposed action rows

        Each row must show:

        - action label
        - one-sentence effect
        - whether the entry object survives
        - whether target bytes become in scope
        - whether a new subject admission is minted
        - whether bytes are branched into ordinary content

        ### 3) Widening and coupling review

        Show:

        - whether the action widens the current subject graph
        - whether target drift remains coupled later
        - whether inside-subject following merely formalizes existing scope or changes it
        - what evidence is missing if proof is incomplete

        ### 4) Parity and conflict review

        Show:

        - cross-seat parity delta
        - unsupported-seat fallout still expected after apply
        - whether current or future `.Conflict` residue remains possible
        - whether the action improves clarity at the cost of semantic fidelity

        ### 5) Commit guardrail language

        Before commit, publish:

        - strongest safe sentence
        - strongest forbidden sentence
        - exact receipt that will be generated

        ## Public objects

        ### Indirection action review

        Fields:

        - `indirection_action_review_id`
        - `indirection_posture_ref`
        - `candidate_actions[]`
        - `selected_action`
        - `graph_widening_delta`
        - `parity_delta`
        - `conflict_delta`
        - `reversibility_grade`
        - `receipt_preview`

        ## Success criteria

        The page is successful only when an operator can compare preservation, follow-target, branching, and block as separate semantic acts rather than as one blurry repair button.
    ''').strip() + '\n',
    '699-target-transitivity-proof-page-object-target-scope-and-graph-widening-interface-spec.md': dedent('''
        # Target transitivity proof page: object, target scope, and graph widening interface spec

        ## Purpose

        This page exists to prove whether target bytes are already in scope, still out of scope, or only obtainable through a new admission act.

        ## Core rule

        A product must never let `symlink preserved` or `junction found` stand in for a target-inclusion answer.
        Target transitivity must be proven separately.

        ## Fixed page order

        1. entry proof strip
        2. target resolution card
        3. in-scope / out-of-scope verdict
        4. graph-widening proof
        5. receipts and counterfactuals

        ### 1) Entry proof strip

        Show:

        - entry path
        - entry kind
        - proof confidence for the entry classification
        - whether the object currently survives on this seat

        ### 2) Target resolution card

        Show:

        - target path or unresolved state
        - target scope relative to current subject
        - whether target resolution is stable, broken, or ambiguous
        - whether the target can be inspected safely now

        ### 3) In-scope / out-of-scope verdict

        Show exactly one verdict:

        - `target already in scope`
        - `target outside current scope`
        - `target requires separate admission`
        - `cannot prove target scope yet`
        - `not applicable`

        Also show the strongest sentence explaining why.

        ### 4) Graph-widening proof

        Show:

        - whether follow-target changes the set of governed bytes
        - whether the change is merely coupling within current scope or a true outward widening
        - what new subject or approval object would be minted if widening occurs
        - what later receipt proves that widening did or did not happen

        ### 5) Receipts and counterfactuals

        Show:

        - last target transitivity proof receipt
        - counterfactual sentence for `preserve object only`
        - counterfactual sentence for `follow target`
        - counterfactual sentence for `branch ordinary bytes`

        ## Public objects

        ### Target transitivity proof

        Fields:

        - `target_transitivity_proof_id`
        - `entry_ref`
        - `target_path` nullable
        - `target_scope`
        - `target_transitivity_verdict`
        - `graph_widening_risk`
        - `proof_confidence`
        - `counterfactual_rows[]`
        - `receipt_refs[]`

        ## Guardrails

        The page must never:

        - claim target inclusion because the object itself is visible
        - claim no graph widening when the target is outside current scope
        - bury target ambiguity behind `unsupported` alone
        - force operators to infer counterfactual outcomes from troubleshooting prose
    ''').strip() + '\n',
    '700-indirection-receipt-page-entry-kind-target-verdict-and-fidelity-ceiling-interface-spec.md': dedent('''
        # Indirection receipt page: entry kind, target verdict, and fidelity ceiling interface spec

        ## Purpose

        This receipt proves what the product concluded about an indirection object and what action was actually taken.

        ## Receipt questions

        The receipt must let a later reader answer:

        1. what entry kind was found
        2. what platform lane interpreted it
        3. what happened to the entry object
        4. whether target bytes were in scope
        5. whether graph widening occurred
        6. what fidelity ceiling remains after the action

        ## Required fields

        - `indirection_receipt_id`
        - `subject_ref`
        - `seat_ref`
        - `entry_path`
        - `entry_kind`
        - `platform_lane`
        - `entry_object_fate`
        - `target_scope`
        - `target_transitivity_verdict`
        - `graph_widening_result`
        - `selected_action`
        - `conflict_hazard_after_apply`
        - `fidelity_ceiling`
        - `strongest_safe_sentence`
        - `forbidden_overclaim_sentence`
        - `issued_at`

        ## Presentation order

        1. summary strip
        2. object-fate section
        3. target-transitivity section
        4. widening result section
        5. remaining ceiling section

        ## Receipt language rules

        The receipt must explicitly distinguish:

        - `object preserved` from `target included`
        - `target out of scope` from `target unresolved`
        - `graph widened` from `coupling stayed inside current scope`
        - `unsupported here` from `blocked by policy`

        ## Success criteria

        The receipt is successful only when a later operator does not need to reopen support prose to know whether this indirection object stayed as an object, became ordinary bytes, widened the graph, or still carries a fidelity ceiling.
    ''').strip() + '\n',
}

for name, content in new_docs.items():
    (docs / name).write_text(content)

