from pathlib import Path

root = Path('/mnt/data/rev0311_src')
docs = root / 'docs'


def prepend(path: Path, text: str):
    old = path.read_text()
    path.write_text(text.rstrip() + "\n\n" + old)


def append(path: Path, text: str):
    old = path.read_text()
    if not old.endswith('\n'):
        old += '\n'
    path.write_text(old + '\n' + text.rstrip() + '\n')

new_docs = {
    '1006-resilio-path-identity-canonicalization-and-equivalence-class-fragmentation-evaluation.md': '''# Resilio path identity, canonicalization, and equivalence-class fragmentation evaluation

## Why this pass exists

The archive already had portability repair, invalid-name handling, rename-plane separation, and conflict recovery.
What it still lacked was one direct current Resilio evaluation for another ordinary seam:

> when two paths look similar or identical to a human, which name form actually governs identity, collision, portability, and sync safety across the cohort?

Current official Resilio docs still preserve several real distinctions, but they still make the operator reconstruct the answer from troubleshooting pages, power-user settings, and changelog notes rather than one stable contract page.

## What current Resilio still gets right

Current official docs are still candid that path identity is not only `whatever the current machine accepted locally`.
They still say all of the following:

- `Power user preferences` still exposes `normalize_unicode_paths = true` and describes it as normalizing Unicode filenames into composed/decomposed form.
- `Conflict files in Sync` still says collisions can arise from case-insensitive peers, decomposed UTF symbols, prohibited filesystem symbols, and linked junctions.
- The same conflict guidance still explains that composed and decomposed Unicode names can look the same to a human while still being different at filesystem level.
- `My files don't sync` still says Sync expects UTF-8 naming, flags special-symbol / encoding trouble, and still warns about path-length limits.
- `Unsupported asterisk (*)...` still says one invalid trailing-asterisk family can be interpreted as system data and disrupt syncing.
- The current changelog lineage still records fixes for crashes caused by mixed composed/decomposed filename symbols, invalid symbols in Windows paths, and trailing-dot syncing to Windows peers.

That candor is valuable.
Resilio is not pretending that local acceptance, rendered appearance, and peer-safe canonical identity are always the same truth.

## Why this is still a good reason not to clone them

### 1) Canonicalization policy is still a hidden advanced lever

The product still has a real normalization policy, but the ordinary operator answer to `what counts as the same name here?` is still partly hidden behind a power-user setting and partly implied by conflict outcomes.

### 2) Equivalence-class truth is still learned from failure

Current docs still teach the operator about case collisions, composed/decomposed collisions, and invalid-symbol substitutions mostly through conflict examples, bugfix notes, and repair prose.
That means the product still surfaces identity classes too late.

### 3) Path validity is still local-looking but cohort-shaped

A local filesystem may accept one name form while another peer will rewrite, reject, or collide with it.
Current docs preserve that truth, but the ordinary question `is this rename safe for the whole cohort?` is still scattered across troubleshooting and changelog archaeology.

### 4) Rendered names and byte-level names still collapse too easily

Humans see one filename.
The product reality still depends on codepoint form, case posture, portability restrictions, and symbol-rewrite rules.
AnonSync should not clone any contract where that distinction remains mostly implicit until damage appears.

## What AnonSync should do instead

AnonSync should keep the candor and refuse the fragmentation.
The replacement contract should make path identity first-class:

1. **Path identity contract sheet**
   - rendered label
   - raw name form
   - canonical comparison basis
   - cohort portability horizon

2. **Canonicalization review**
   - case posture
   - Unicode normalization posture
   - forbidden-symbol and rewrite posture
   - strongest safe sentence

3. **Equivalence collision warning**
   - same-looking / different-byte names
   - same-byte / rewritten-peer names
   - local-safe / cohort-unsafe rename plans

4. **Path validity preview**
   - local acceptability
   - peer portability
   - blocked rename/adoption effects
   - safe alternative ladder

5. **Path identity receipt**
   - reviewed canonical basis
   - equivalence verdict
   - portability ceiling
   - blocked stronger sentence

## Sharper non-clone line

So the tighter conclusion for this pass is:

> Resilio is still worth borrowing for its candor that path identity really depends on case posture, Unicode normalization, invalid-symbol rules, and peer portability. But it is not worth cloning the way ordinary answers to `are these two names the same thing, a collision, or a peer-specific rewrite?` still sprawl across power-user preferences, conflict guidance, troubleshooting notes, invalid-name warnings, and changelog archaeology instead of one stable page family.''',

    '1007-path-identity-contract-sheet-page-rendered-name-raw-form-canonical-basis-and-peer-horizon-interface-spec.md': '''# Path identity contract sheet page — rendered name, raw form, canonical basis, and peer horizon

## Purpose

Show, in one durable place, the exact path-identity facts the operator may rely on before renaming, adopting, restoring, or approving a cohort-visible name.

This page exists to answer:

- `what name is the operator seeing?`
- `what exact raw form is being compared?`
- `which canonicalization rules are in force?`
- `is this safe only locally, or across the whole peer horizon?`

## Required sections

### 1. Subject header

Must show:

- subject and current parent path
- rendered basename
- operation lane (`rename`, `adopt`, `restore`, `replay`, `ingress`, `repair`, `other`)
- reviewed peer horizon
- current validity verdict (`safe`, `guarded`, `blocked`, `unknown`)

### 2. Name forms block

Render separate rows for:

- **Rendered name**
- **Raw stored form**
- **Canonical comparison form**
- **Peer-rewritten or substituted form** (when applicable)

Each row must publish:

- current value
- provenance
- whether it is stable across the reviewed horizon
- whether it is sufficient for equality decisions by itself

### 3. Canonical basis block

Must show:

- case-sensitivity posture in the reviewed horizon
- Unicode normalization posture
- invalid-symbol / forbidden-suffix posture
- rewrite or substitution posture
- whether these rules are subject-local, seat-local, or horizon-wide

### 4. Equivalence class block

Must classify the candidate as one of:

- `same rendered and same raw form`
- `same rendered but different raw form`
- `different rendered but canonical collision`
- `local-only valid`
- `peer rewrite expected`
- `blocked due to invalid or unsafe form`

### 5. Horizon safety block

Must distinguish:

- safe on current seat only
- safe across current connected peers
- safe across reviewed intended cohort
- unsafe because at least one peer horizon would rewrite, collide, or reject
- unknown because peer/path facts are incomplete

### 6. Strongest safe sentence

Examples:

- `This rename is safe only on the current seat; the reviewed cohort contains a case-insensitive peer that would collide.`
- `These two names render the same to humans but differ at raw Unicode form.`
- `The current policy would rewrite or reject this path on part of the cohort.`

### 7. Blocked stronger sentence

Examples:

- `The filenames are definitely identical because they look the same.`
- `Local filesystem acceptance means cohort-safe identity.`
- `Rendered name alone is enough to prove safe equality.`

## Interaction rules

- copying/exporting a summary must preserve both rendered and canonical basis fields
- any blocked or guarded verdict must link to a dedicated review page
- cohort horizon must stay visible near the primary action
- this page must not hide normalization or substitution rules under advanced disclosure

## Receipt obligations

Any receipt derived from this page must preserve:

- reviewed name forms
- canonical basis
- horizon safety verdict
- strongest safe sentence
- blocked stronger sentence''',

    '1008-canonicalization-review-page-case-posture-unicode-normalization-invalid-symbol-policy-and-claim-ceiling-interface-spec.md': '''# Canonicalization review page — case posture, Unicode normalization, invalid-symbol policy, and claim ceiling

## Purpose

Review the exact comparison and rewrite rules that will govern a proposed path mutation or adoption.

This page exists to answer:

- `which comparison rules matter here?`
- `what will be normalized, rewritten, or rejected?`
- `what claim about safe identity can the product honestly make?`

## Required sections

### 1. Review trigger

Must show:

- operation being reviewed
- current path and candidate path
- trigger reason (`case collision`, `Unicode ambiguity`, `forbidden symbol`, `portability mismatch`, `unknown horizon`, `other`)

### 2. Comparison rules table

Must show separate rows for:

- case handling
- Unicode normalization
- invalid-symbol replacement or rejection
- trailing-dot / trailing-space / suffix rules when relevant
- length / encoding policy when relevant

Each row must publish:

- current effective rule
- origin of the rule
- affected peers or surfaces
- whether the rule changes equality, visibility, or validity

### 3. Candidate outcomes

Must classify outcomes such as:

- accepted unchanged
- accepted but canonicalized
- accepted locally but peer rewrite expected
- accepted locally but peer collision expected
- blocked before apply
- unknown pending stronger horizon evidence

### 4. Safe alternatives

Must offer the cheapest safe alternatives, such as:

- choose a cohort-safe canonical name
- branch locally instead of cohort rename
- narrow the peer horizon and continue with weaker sentence
- stop and repair conflicting existing names first

### 5. Strongest safe sentence

Examples:

- `The candidate is locally acceptable but not cohort-safe under the reviewed case and Unicode rules.`
- `The product can promise only canonicalized equality, not literal raw-name equality.`

### 6. Blocked stronger sentence

Examples:

- `This path will behave the same everywhere because this seat accepts it.`
- `Normalization differences are cosmetic only.`

## Interaction rules

- the primary apply action must render the winning comparison basis inline
- blocked candidates must not offer a destructive fast path as the primary action
- rewritten outcomes must publish the exact resulting canonical or substituted name before apply

## Receipt obligations

Any receipt derived from this page must preserve:

- reviewed rules
- winning comparison basis
- candidate outcome class
- safe alternative chosen if any
- claim ceiling''',

    '1009-equivalence-collision-warning-page-same-looking-different-byte-names-and-cross-peer-merge-risk-interface-spec.md': '''# Equivalence collision warning page — same-looking different-byte names and cross-peer merge risk

## Purpose

Warn when names that appear separate or identical to humans collapse into one risky equivalence class across the reviewed cohort.

This page exists to answer:

- `which names are colliding?`
- `are they literally equal, canonically equal, or peer-rewritten into equality?`
- `what merge, conflict, or rewrite risk follows if we continue?`

## Required sections

### 1. Collision summary

Must show:

- all candidate names in the collision set
- rendered forms side by side
- raw-form difference indicator
- collision class (`case-only`, `Unicode-form`, `symbol-rewrite`, `length-truncate`, `mixed`)

### 2. Horizon impact

Must publish:

- which peers or surfaces would collide
- whether collision is present now or only on later arrival / reconnect / restore
- whether current peers already contain conflict artifacts or rewritten variants

### 3. Risk ladder

Must distinguish:

- visible `.Conflict` risk
n- silent rewrite risk
- blocked sync risk
- rename replay ambiguity
- archive / restore ambiguity

### 4. Safe resolution options

Must offer:

- choose one surviving canonical name
- export / branch one candidate out of band
- keep both only by widening their visible difference
- defer until missing horizon facts are gathered

### 5. Strongest safe sentence

Examples:

- `These names are not safely distinct across the reviewed cohort.`
- `The candidates differ in raw form, but at least one peer horizon would collapse them into one identity class.`

### 6. Blocked stronger sentence

Examples:

- `Both names can safely coexist because they currently appear separately on this seat.`
- `A visible difference to the human eye guarantees portable distinctness.`

## Interaction rules

- collision members must be copyable/exportable with both rendered and raw-form evidence
- the page must keep the reviewed peer horizon visible while the operator resolves the set
- any destructive resolution path must link to the existing salvage/repair family

## Receipt obligations

Any receipt derived from this page must preserve:

- full collision member set
- collision class
- reviewed horizon
- winning resolution path
- blocked stronger sentence'''.replace('\nn-','\n-'),

    '1010-path-validity-preview-page-local-acceptability-peer-portability-and-blocked-rename-adoption-effects-interface-spec.md': '''# Path validity preview page — local acceptability, peer portability, and blocked rename/adoption effects

## Purpose

Preview the exact consequences of adopting or renaming a path that may be acceptable on one surface but unsafe across the reviewed cohort.

This page exists to answer:

- `will this name be accepted locally?`
- `will peers preserve it, rewrite it, reject it, or collide it?`
- `what downstream effects follow if I continue anyway?`

## Required sections

### 1. Current and candidate paths

Must show:

- current path
- candidate path
- operation type
- reviewed horizon
- immediate local validity verdict

### 2. Portability matrix

Must classify each reviewed peer/surface as:

- preserves candidate unchanged
- canonicalizes candidate
- rewrites or substitutes candidate
- rejects candidate
- unknown

### 3. Downstream effects

Must show the expected effect family:

- no downstream hazard
- future conflict artifact risk
- blocked sync / non-arrival risk
- archive / restore replay ambiguity
- rename divergence across peers
- same-looking duplicate branch risk

### 4. Safer alternatives

Must offer:

- choose cohort-safe name
- keep local alias only
- branch subject locally
- stop and repair existing portability issues first

### 5. Strongest safe sentence

Examples:

- `The candidate is acceptable on the current seat but not portable across the reviewed cohort.`
- `Proceeding would create a rename that cannot be stated honestly as preserved everywhere.`

### 6. Blocked stronger sentence

Examples:

- `This rename will be preserved exactly across all peers.`
- `The only question is whether the current filesystem accepts it.`

## Interaction rules

- the primary action must reflect the actual winning outcome (`Rename locally only`, `Choose new canonical name`, `Stop and repair`, etc.)
- portability matrix entries must be visible without extra drilling when any peer is blocked or rewritten
- this page must preserve action-plane separation from local aliasing and other non-path mutations

## Receipt obligations

Any receipt derived from this page must preserve:

- local validity verdict
- portability matrix summary
- downstream effect family
- chosen action
- blocked stronger sentence''',

    '1011-path-identity-lineage-receipt-page-canonical-basis-equivalence-verdict-and-blocked-stronger-sentences-interface-spec.md': '''# Path identity lineage receipt page — canonical basis, equivalence verdict, and blocked stronger sentences

## Purpose

Provide durable proof of how a path identity question was reviewed, what basis won, and what stronger interpretation was deliberately rejected.

## Required fields

- subject and operation lane
- current path and resulting path
- reviewed peer horizon
- rendered name at decision time
- raw-form or comparison witness retained by the product
- winning canonical basis
- equivalence verdict
- portability verdict
- resulting action
- strongest safe sentence
- blocked stronger sentence
- receipt timestamp and supersession pointer

## Required verdict classes

The receipt must classify at least:

- literal equality vs canonical equality vs collision
- locally valid vs cohort-portable vs blocked
- preserved unchanged vs canonicalized vs rewritten vs rejected

## Interaction rules

- receipts must be exportable in a text-safe form that preserves the winning comparison basis
- later pages must be able to cite the receipt without restating a stronger claim than it actually earned
- if later horizon facts change, the product must supersede rather than silently reinterpret the prior receipt

## Example safe sentences

- `At decision time the candidate was reviewed under the recorded canonical basis and was not safe to claim as literal portable equality.`
- `The resulting path was accepted only with the portability ceiling recorded in this receipt.`

## Example blocked stronger sentences

- `These names were proven identical everywhere.`
- `Local acceptance proved exact cross-peer preservation.`'''
}

for name, content in new_docs.items():
    (docs / name).write_text(content.rstrip() + '\n')

prepend(root / 'README.md', '''## Revision addendum — path identity, canonicalization, and equivalence-class truth

This revision continues directly from `rev0310` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Unicode normalization, case posture, invalid-symbol rules, conflict examples, UTF-8 expectations, and path-name bugfix history**.
2. Tightens the non-clone line again: borrow Resilio's candor that path identity is not just whatever one local filesystem accepts; refuse any contract where the operator still has to reconstruct `are these two names the same thing, a collision, or a peer-specific rewrite?` from several help pages and changelog notes.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio path-identity truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: path identity contract sheet, canonicalization review, equivalence collision warning, path validity preview, and path identity lineage receipt.
5. Makes one hard product decision explicit: **path identity becomes a first-class contract object rather than a side effect of conflict recovery**.
6. Makes another hard product decision explicit: **rendered name, raw form, and canonical comparison basis are separate truths**.
7. Makes a third hard product decision explicit: **local acceptability never by itself proves cohort-safe identity or portable rename semantics**.
8. Packages the result as another continuation archive whose new tranche makes the `path-identity / canonical-basis / equivalence-collision / portability-preview / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present path-identity contract**

This time the reason is especially clear around **hidden Unicode normalization policy, case-sensitive versus case-insensitive peers, same-looking composed/decomposed names, invalid-symbol and trailing-form portability, and bugfix history that proves these are not merely theoretical edge cases**.
Current official materials simultaneously show that:

- the current `Power user preferences` article still exposes `normalize_unicode_paths = true` and describes it as normalizing Unicode filenames into composed/decomposed form.
- the current `Conflict files in Sync` article still says conflicts can arise from case-insensitive peers, decomposed UTF symbols, prohibited filesystem symbols, and linked junctions, and still says operators should keep the same letter case and encoding across devices.
- the current `My files don't sync` article still says Sync expects UTF-8 naming, still flags special-symbol/encoding trouble, and still warns about path-length limits.
- the current `Unsupported asterisk (*)...` article still says one invalid trailing-asterisk family can be interpreted as system data and disrupt syncing.
- the current changelog still records fixes for crashes caused by mixed composed/decomposed symbols in filenames, invalid symbols in Windows paths, and trailing-dot syncing to Windows peers.

That candor is useful.
The path-identity contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether a visible filename, a raw codepoint form, a canonicalized comparison form, and a peer-rewritten path all answer the same equality question.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful path-identity distinctions are real, but the present contract still hides too much meaning across power-user settings, conflict guidance, troubleshooting notes, invalid-name warnings, and changelog archaeology instead of owning path identity as one stable page family.**''')

prepend(docs / '00-status.md', '''## Revision addendum — path identity, canonicalization, and equivalence-class truth

This revision continues directly from `rev0310` and does eight concrete things:

1. Re-checks another current official Resilio cluster around **Unicode normalization, case posture, invalid-symbol rules, conflict examples, UTF-8 expectations, and path-name bugfix history**.
2. Tightens the non-clone line again: borrow Resilio's candor that path identity is not just whatever one local filesystem accepts; refuse any contract where the operator still has to reconstruct `are these two names the same thing, a collision, or a peer-specific rewrite?` from several help pages and changelog notes.
3. Adds one new **Resilio evaluation** document focused on why present-day Resilio path-identity truth is still too fragmented to clone even though the distinctions are useful.
4. Adds five new **interface specs** for the workflow-owned surfaces this pass was still missing: path identity contract sheet, canonicalization review, equivalence collision warning, path validity preview, and path identity lineage receipt.
5. Makes one hard product decision explicit: **path identity becomes a first-class contract object rather than a side effect of conflict recovery**.
6. Makes another hard product decision explicit: **rendered name, raw form, and canonical comparison basis are separate truths**.
7. Makes a third hard product decision explicit: **local acceptability never by itself proves cohort-safe identity or portable rename semantics**.
8. Packages the result as another continuation archive whose new tranche makes the `path-identity / canonical-basis / equivalence-collision / portability-preview / durable-receipt` seam explicit in the reading order and page family.

## Current conclusion, tightened again

Another current official Resilio pass still supports the same overall judgment:

- **borrow Resilio's practical candor**
- **do not clone Resilio's present path-identity contract**

This time the reason is especially clear around **hidden Unicode normalization policy, case-sensitive versus case-insensitive peers, same-looking composed/decomposed names, invalid-symbol and trailing-form portability, and bugfix history that proves these are not merely theoretical edge cases**.
Current official materials simultaneously show that:

- the current `Power user preferences` article still exposes `normalize_unicode_paths = true` and describes it as normalizing Unicode filenames into composed/decomposed form.
- the current `Conflict files in Sync` article still says conflicts can arise from case-insensitive peers, decomposed UTF symbols, prohibited filesystem symbols, and linked junctions, and still says operators should keep the same letter case and encoding across devices.
- the current `My files don't sync` article still says Sync expects UTF-8 naming, still flags special-symbol/encoding trouble, and still warns about path-length limits.
- the current `Unsupported asterisk (*)...` article still says one invalid trailing-asterisk family can be interpreted as system data and disrupt syncing.
- the current changelog still records fixes for crashes caused by mixed composed/decomposed symbols in filenames, invalid symbols in Windows paths, and trailing-dot syncing to Windows peers.

That candor is useful.
The path-identity contract is the problem.
AnonSync should not clone a world where the operator still has to remember whether a visible filename, a raw codepoint form, a canonicalized comparison form, and a peer-rewritten path all answer the same equality question.

So the harder product stance now becomes explicit:

> **AnonSync is not cloning Resilio because the useful path-identity distinctions are real, but the present contract still hides too much meaning across power-user settings, conflict guidance, troubleshooting notes, invalid-name warnings, and changelog archaeology instead of owning path identity as one stable page family.**''')

append(docs / '10-resilio-sync-evaluation.md', '''
## Further current clone-veto seam — path identity, canonicalization, and equivalence-class truth

Another current official Resilio pass produced a tighter no-clone reason around **what it means for two filenames to be the same subject identity across a heterogeneous cohort**.
The useful distinctions are real.
The present contract is still too fragmented.

Current official docs still openly distinguish all of the following:

- `Power user preferences` still exposes `normalize_unicode_paths = true` and describes it as normalizing Unicode names into composed/decomposed form.
- `Conflict files in Sync` still says conflicts can arise from case-insensitive peers, decomposed UTF symbols, prohibited filesystem symbols, and linked junctions, and still tells operators to keep the same letter case and encoding across devices.
- `My files don't sync` still says Sync expects UTF-8 naming, still warns about special symbols and path-length limits, and still treats encoding mismatches as a real cause of non-sync.
- `Unsupported asterisk (*)...` still says some invalid trailing-asterisk names may be interpreted as system data and disrupt syncing.
- the current changelog still records fixes for mixed composed/decomposed filename crashes, invalid symbols in Windows paths, and trailing-dot syncing to Windows peers.

This is good evidence that Resilio is candid about a real seam.
It is also good evidence that AnonSync should not clone the exact page contract.

To answer one ordinary operator question — **`are these two paths literally the same, canonically the same, or cohort-unsafe despite looking fine here?`** — current Resilio still makes the operator combine:

- power-user normalization settings
- conflict examples and cleanup guidance
- generic troubleshooting notes about UTF-8 and path length
- special-case invalid-name warnings
- changelog archaeology proving the class is operationally real

AnonSync should keep the distinctions and refuse the archaeology.
That means:

1. **path identity becomes a first-class contract object**
2. **rendered name, raw form, and canonical comparison basis become separate visible truths**
3. **local acceptability does not imply cohort-safe identity**
4. **same-looking/different-byte and different-looking/canonical-collision cases get a dedicated warning family**
5. **every serious path-identity decision emits a durable receipt with the blocked stronger sentence**

That is the reason for this tranche's page family: path identity contract sheet, canonicalization review, equivalence collision warning, path validity preview, and path identity lineage receipt.''')

append(docs / '11-resilio-borrow-line-and-non-clone-scorecard.md', '''
## Revision addendum — scorecard after rev0310: borrow path-identity candor, reject filename-equivalence archaeology

Another current Resilio pass again strengthens the same split judgment:

- **borrow** the candor that case posture, Unicode normalization, invalid-symbol rules, and peer portability materially change path identity
- **do not clone** the present-day contract where one ordinary operator answer about `is this the same path, a collision, or a peer-specific rewrite?` still spans power-user settings, conflict cleanup, generic troubleshooting, and changelog archaeology

Scorecard change added by this tranche:

| Path identity / canonicalization / equivalence-class truth | Strong candor, fragmented contract | **Adapt** | Current docs preserve the important distinctions, but the ordinary answer still spans normalization settings, conflict guidance, UTF-8/path troubleshooting, invalid-name warnings, and bugfix notes instead of one owned workflow | **Path identity contract sheet**, **Canonicalization review**, **Equivalence collision warning**, **Path validity preview**, and **Path identity lineage receipt** |
''')

append(docs / '12-resilio-interface-clone-veto-tests-and-page-obligations.md', '''
## Revision addendum — clone-veto implication from path-identity fragmentation

Add one more veto test explicitly:

- reject any interface where a visible filename is treated as the whole truth without also publishing the winning canonical comparison basis, the reviewed peer horizon, and whether the name is only locally acceptable versus cohort-portable

New page obligation added by this tranche:

- any rename, restore, adopt, or replay path that may cross case, Unicode, invalid-symbol, or portability boundaries must route through a dedicated path-identity review family rather than relying on later conflict recovery''')

append(docs / '20-product-direction.md', '''
## Revision addendum — product direction from rev0311

AnonSync should make path identity first-class.
That means:

- the product owns a stable notion of **rendered name**, **raw form**, and **canonical comparison basis**
- any operation that changes cohort-visible naming must publish the reviewed **peer horizon** before apply
- local acceptance is intentionally weaker than cohort-safe portability, and the interface must say so directly
- same-looking / different-byte and canonical-collision cases are page families, not troubleshooting folklore''')

append(docs / '30-interface-spec.md', '''
## Revision addendum — interface family added in rev0311

Add a dedicated **path identity** family to the global interface inventory:

- contract sheet for rendered/raw/canonical path truth
- canonicalization review for case / Unicode / invalid-symbol policy
- equivalence collision warning for same-looking and cross-peer collapse cases
- path validity preview for local-acceptability versus cohort-portability
- lineage receipt for the exact winning comparison basis and blocked stronger sentence''')

append(docs / '32-interface-flows.md', '''
## Revision addendum — new flow family from rev0311

A rename, adopt, restore, or replay flow must now branch into **path identity review** whenever any of these are true:

- case posture differs inside the reviewed horizon
- Unicode normalization policy could change equality
- symbol substitution / rejection is possible on any reviewed surface
- the operator is relying on local filesystem acceptance as if it proved cohort-safe identity

The flow must end in a lineage receipt that preserves the winning canonical basis and the portability ceiling.''')

append(docs / '39-interface-pattern-language.md', '''
## Revision addendum — pattern language note from rev0311

Add one more standing pattern:

- **same-looking is not same-subject** — when a product can compare by rendered label, raw bytes/codepoints, and canonicalized identity, the interface must keep those planes distinct and must never let a human-readable name silently stand in for the winning equivalence basis''')

append(docs / '40-architecture-decisions.md', '''
## Revision addendum — architecture decision from rev0311

Decision: **Path identity is modeled explicitly, not inferred only from conflict aftermath.**

Implications:

- subject identity must retain rendered name, raw form witness, and canonical comparison basis where relevant
- peer-horizon portability is part of rename/adoption planning
- receipts and audit surfaces must preserve the exact comparison basis used at decision time''')

append(docs / '50-roadmap.md', '''
## Revision addendum — roadmap note from rev0311

Near-term roadmap addition:

- implement the path-identity review family so all cohort-visible naming actions can publish canonical basis, peer horizon, and portability ceiling before apply instead of relying on later conflict repair''')

append(docs / 'sources.md', '''
## Revision addendum — path identity, canonicalization, and equivalence-class truth after rev0310

This revision again leaned primarily on the comparison archive, but the outside evidence that most directly mattered this time was another cluster of current official Resilio Sync docs about Unicode normalization, filename conflict causes, UTF-8 and path portability, invalid path-name edge cases, and bugfix history proving that these classes are operationally real.
The new questions were:

> where do current official docs most clearly show that Resilio is candid that path identity is not simply `whatever the local filesystem accepted`?

> where do those same current docs still show that the ordinary operator answer about `same name, different raw form, collision, rewrite, or reject?` depends on several pages instead of one stable product-owned page family?

The most load-bearing source set for this pass was:

- Resilio's current `Power user preferences` article, which still exposes `normalize_unicode_paths = true` and describes it as normalizing Unicode names into composed/decomposed form.
- Resilio's current `Conflict files in Sync` article, which still says conflicts can arise from case-insensitive peers, decomposed UTF symbols, prohibited symbols, and linked junctions, and still says operators should keep the same letter case and encoding across devices.
- Resilio's current `My files don't sync` article, which still says Sync expects UTF-8 naming, still flags special-symbol/encoding trouble, and still warns about path-length limits.
- Resilio's current `Unsupported asterisk (*) characters at the end of file/folder names` article, which still says some invalid trailing-asterisk names may be interpreted as system data and disrupt syncing.
- Resilio's current changelog, which still records fixes for crashes caused by mixed composed/decomposed symbols in filenames, invalid symbols in Windows paths, and trailing-dot syncing to Windows peers.

## Additional Resilio official sources emphasized in rev0311

- Power user preferences
  https://help.resilio.com/hc/en-us/articles/207371636-Power-user-preferences

- Conflict files in Sync
  https://help.resilio.com/hc/en-us/articles/204753629-Conflict-files-in-Sync

- My files don't sync
  https://help.resilio.com/hc/en-us/articles/205450355-My-files-don-t-sync

- Unsupported asterisk (*) characters at the end of file/folder names
  https://help.resilio.com/hc/en-us/articles/206214715-Unsupported-asterisk-characters-at-the-end-of-file-folder-names

- Resilio Sync change log
  https://help.resilio.com/hc/en-us/articles/206216855-Resilio-Sync-change-log''')

print('rev0311 content applied')
