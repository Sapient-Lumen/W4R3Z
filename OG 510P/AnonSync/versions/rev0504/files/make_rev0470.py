from pathlib import Path

root = Path('/mnt/data/work_rev0469')
docs = root / 'docs'

new_docs = {
'1960-resilio-remedy-hardening-attestation-executable-mandate-binding-scope-and-execution-routing-fragmentation-evaluation.md': '''# Resilio remedy hardening attestation executable mandate, binding scope, and execution-routing fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that `the verdict looks legitimate`, `the permission looks changed`, `the linked device should now have access`, `the local share should inherit the new posture`, `the service should now behave the same way`, and `the intended change is therefore binding and executed everywhere it matters` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `Sync Private Identity & Linking My Devices` docs still say that once devices are linked, all folders automatically become available on all linked devices, that remote users can auto-approve future sharing across linked devices, and that approvals can be issued from any linked device where the folder is present
- current `Comprehensive guide to syncing (Desktop-Desktop)` docs still say linked devices receive automatic full read-write access while manual sharing is the path where access privileges can be chosen folder by folder
- current `User Management` docs still say Advanced-folder permissions can be changed without disrupting synchronization, and disconnect revokes future updates while leaving already synchronized files in place
- current `How to create a Read Only folder while syncing across linked devices?` docs still say linked devices automatically receive Owner permission and that a read-only result on a linked device requires a Standard-folder Read Only key detour plus manual disconnect and manual re-entry
- current `Sharing a folder locally` docs still say local shares cannot receive Owner permission, Advanced local-share permissions cannot be changed through user management and instead require remove-and-re-share, and reconnecting a source share does not automatically reconnect the local share
- current `Running Sync in configuration mode` docs still say one config can apply settings across many machines at start, but only for Standard folders, and that shared folders declared in config disable WebUI and override folders previously added from WebUI
- current `Sync Service Troubleshooting on Windows` docs still say service-user changes can create a different storage world where old folders are absent and require re-add plus re-share or reconnect, and that some WebUI exposure changes require service restart
- current `Running Sync on schedule` docs still say `Paused` stops uploads and downloads but still allows file deletions to sync and new files to be rescanned and indexed

## Where the current contract still fragments

The problem is not that Resilio lacks execution knobs.
The problem is that it still does not produce one first-class, case-scoped **executable-mandate and execution-routing** object.

Today an operator can often infer only weaker truths such as:

- this linked device should now inherit access automatically
- this manual share path can produce a different access result than the linked-device path
- this permission change is live for one peer class but not for another topology
- this local derivative share must be removed and re-shared instead of mutated in place
- this configuration can shape startup state for Standard folders but not for Advanced folders
- this service world can require restart or even a world fork before the intended effect exists
- this scheduler or pause state still allows some side effects to continue

Those are useful clues.
They are not the same as an explicit answer to `who is now actually bound, through which execution path, by which deadline, with which actuator and fallback, and what stronger execution-complete sentence is still blocked?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the verdict is legitimate`.
It needs to support claims such as:

- the verdict is legitimate, but advisory only because no mandate has been issued yet
- the verdict is binding for a named operator cohort only, not for the entire estate
- the mandate exists, but the chosen actuator is unavailable in this world or topology
- the execution route exists, but manual steps still remain for a read-only detour, re-share, reconnect, or restart
- execution has started, but only a named slice has completed and broader execution remains blocked
- a fallback path is now governing because in-place mutation was unsupported
- the product can justify `mandate issued` or `execution pending`, but not yet `execution complete`

AnonSync therefore needs first-class objects for **binding scope, obligated actor set, required action set, actuator class, chosen execution route, deadline, fallback route, execution witness, execution-failure class, highest honest execution sentence, and blocked stronger sentence** rather than leaving operators to infer execution truth from linked-device defaults, permission toggles, manual detours, restart folklore, or scheduler side effects.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `now that the verdict is legitimate, who is actually bound and has execution really landed?` — only by making the operator combine several partially overlapping mechanics:

- linked-device automatic spread and approval memory
- manual folder-sharing lanes with separate privilege semantics
- live permission changes for some cases and remove-and-re-share replacement for others
- local-share inheritance and non-reconnection behavior
- Standard-only config rollout with WebUI override side effects
- service-user world forks, re-add or reconnect requirements, and restart gates
- paused lanes that still propagate deletions or indexing side effects

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **executable mandate, binding scope, and execution routing** directly.
Its interface family should let the product separate at least these truths:

- legitimate verdict, advisory only
- legitimate verdict, mandate draft pending ratification
- mandate issued for named cohort only
- mandate issued, actuator unavailable
- mandate issued, execution pending within deadline
- deadline missed, fallback required
- partially executed for named slice only
- fully executed for named slice
- broader stronger sentence blocked
''',
'1961-remedy-hardening-attestation-executable-mandate-contract-sheet-page-bound-parties-actuators-deadlines-and-fallbacks-interface-spec.md': '''# Remedy-hardening-attestation executable-mandate contract sheet page — bound parties, actuators, deadlines, and fallbacks

## Purpose

This page is the compact contract for deciding whether a verdict that is already legitimate has become a real mandate that binds named actors and can actually be executed through a known route.
It exists so the product can distinguish `legitimate verdict only`, `mandate issued`, `binding for named cohort only`, `actuator unavailable`, `execution pending`, `fallback governing`, `named-slice execution complete`, and `broader stronger sentence blocked`.

## Core fields

- executable-mandate identifier
- source verdict-legitimacy receipt identifier
- governing verdict sentence
- mandate issuer or authority identifier
- binding scope by actor class, estate slice, world, and topology
- obligated actor set identifier
- required action set identifier
- action deadline or execution window
- primary actuator class
- primary actuator identifier
- manual-step requirement flag
- restart or reconnect requirement flag
- fallback actuator class
- fallback trigger rule
- current executable-mandate class
- highest currently safe execution sentence
- strongest blocked stronger sentence
- next fact that upgrades executable standing now
- next fact that collapses executable standing now

## Executable-mandate classes

The page must model at least these distinct classes:

- legitimate verdict, advisory only
- mandate draft pending issuance
- mandate issued, binding scope ambiguous
- mandate issued for named cohort only
- mandate issued, primary actuator unavailable
- mandate issued, execution pending within deadline
- deadline missed, fallback required
- fallback route governing
- partially executed for named slice only
- execution complete for named slice
- broader stronger sentence blocked

## Actuator classes

The page must support at least these actuator classes:

- in-product automatic mutation
- per-subject manual operator action
- remove-and-recreate route
- disconnect-and-reconnect route
- restart-gated route
- configuration-at-startup route
- out-of-product human procedure

## Fixed rendering order

Every executable-mandate contract sheet must render the same sections in the same order:

1. **Highest currently execution-safe sentence**
2. **Binding scope, obligated actors, and deadline**
3. **Primary actuator, manual steps, and restart requirements**
4. **Fallback route, failure triggers, and current execution class**
5. **Next fact that upgrades or collapses executable standing**

## Hard rules

The contract sheet must never let an operator hide:

- a legitimate verdict behind an unstated `who is actually bound`
- an automatic-looking permission behind an unstated manual detour
- a chosen action behind an unstated restart, reconnect, or re-share requirement
- a partial slice completion behind `execution complete` wording
- a missing actuator behind `policy already landed` wording
''',
'1962-remedy-hardening-attestation-executable-mandate-review-page-is-this-legitimate-verdict-actually-binding-and-executable-here-interface-spec.md': '''# Remedy-hardening-attestation executable-mandate review page — is this legitimate verdict actually binding and executable here?

## Purpose

This page is the operator-facing review that answers the practical execution question after verdict legitimacy is already good enough: given the current legitimate verdict, who must now act, through which route, by when, and what is the strongest execution sentence the product may honestly publish?

## Primary review prompts

The review must answer these prompts in order:

1. **What verdict is now supposed to become action?**
2. **Who is actually bound by that verdict here?**
3. **Which action or state change is required from each bound actor?**
4. **Which actuator or route can execute it in this world and topology?**
5. **Which manual steps, restarts, reconnects, or replacement moves still remain?**
6. **What is the strongest execution sentence the product may honestly say now?**

## Review sections

### 1. Binding-scope board

Show:

- source verdict-legitimacy receipt
- mandate issuer
- actor classes bound
- actor classes explicitly not bound

### 2. Action-and-deadline board

Show:

- required action set
- deadline or execution window
- whether the action is advisory, mandatory, or fallback-triggered

### 3. Route-and-actuator board

Show:

- primary actuator class
- whether the route is automatic, manual, restart-gated, reconnect-gated, or replacement-style
- whether a fallback route exists already

### 4. Execution-witness board

Show:

- what evidence would count as execution
- what evidence would count as execution failure
- what evidence only proves named-slice completion

### 5. Execution-ceiling board

The review must output one and only one primary sentence class such as:

- legitimate verdict, advisory only
- mandate draft pending issuance
- mandate issued, binding scope ambiguous
- mandate issued for named cohort only
- mandate issued, primary actuator unavailable
- mandate issued, execution pending within deadline
- deadline missed, fallback required
- fallback route governing
- partially executed for named slice only
- execution complete for named slice
- broader stronger sentence blocked

## Hard rules

The review must never let an operator hide:

- a legitimate verdict behind `someone will handle it`
- an automatic-looking lane behind unstated manual procedures
- a restart or reconnect dependency behind `already executed`
- a named-slice completion behind estate-wide completion wording
- a fallback trigger behind `the primary route is still fine`
''',
'1963-remedy-hardening-attestation-executable-mandate-proof-page-binding-scope-actuator-coverage-and-execution-ceiling-interface-spec.md': '''# Remedy-hardening-attestation executable-mandate proof page — binding scope, actuator coverage, and execution ceiling

## Purpose

This page is the evidence-heavy proof surface for determining whether a legitimate verdict has actually become a real executable mandate.
It proves the exact ceiling on any sentence that tries to say a verdict is not merely legitimate, but now binding, routed, and executed for the intended actors.

## Required evidence blocks

### 1. Governing verdict basis

Preserve:

- source verdict-legitimacy receipt
- governing verdict sentence
- mandate issuer or issuance basis

### 2. Binding-scope ledger

Preserve:

- actor classes bound
- actor classes excluded
- world, topology, and platform scope
- named-slice-only ceiling if broader binding is unsupported

### 3. Action-and-route ledger

Preserve:

- required action set
- deadline or execution window
- primary actuator class and identifier
- manual-step requirements
- restart, reconnect, or replacement prerequisites
- fallback route and fallback trigger rule

### 4. Execution-witness ledger

Preserve:

- evidence that primary execution started
- evidence that execution completed for a named slice
- evidence that the primary route failed or stalled
- evidence that fallback now governs
- exact blocker for any broader completion sentence

### 5. Claim ceiling

Render:

- highest honest execution sentence now
- highest honest named-slice-only execution sentence now
- strongest blocked broader sentence and exact blocker
- next witness that would raise the ceiling

## Evidence and execution classes

The page must distinguish at least:

- legitimate verdict only
- mandate not yet issued
- binding scope ambiguous
- named-cohort-only binding
- actuator unavailable
- execution pending
- deadline missed
- fallback governing
- named-slice execution complete
- broader stronger sentence blocked

## Hard rules

The proof page must never treat:

- legitimacy as automatic executability
- one permission display as proof that all required actions landed
- manual replacement routes as equivalent to in-place mutation
- one restarted world as proof across sibling worlds
- one completed slice as proof of broader execution
''',
'1964-remedy-hardening-attestation-executable-mandate-timeline-page-order-route-attempt-deadline-failover-and-execute-events-interface-spec.md': '''# Remedy-hardening-attestation executable-mandate timeline page — order, route, attempt, deadline, failover, and execute events

## Purpose

This page is the ordered event view for execution questions after verdict legitimacy is established.
It exists so later operators can see whether the case moved from a legitimate sentence into a binding, routed, and executed mandate, or whether manual detours, missing actuators, missed deadlines, or fallback routes kept the stronger sentence blocked.

## Event classes

The timeline must support at least these events:

- verdict imported as mandate candidate
- mandate draft created
- mandate issued
- binding scope narrowed
- obligated actor set changed
- primary actuator selected
- primary actuator unavailable
- manual step requested
- restart required
- reconnect required
- replacement route required
- execution attempt started
- deadline warning raised
- deadline missed
- fallback route armed
- fallback route governing
- partial named-slice execution confirmed
- execution complete for named slice
- broader stronger sentence blocked
- mandate superseded or withdrawn

## Required columns

- timestamp
- event class
- source evidence or order reference
- resulting executable-mandate class
- stronger execution sentence newly allowed or newly blocked

## Hard rules

The timeline must never collapse:

- legitimate verdict and mandate issuance into one event by default
- mandate issuance and execution start into one event by default
- execution start and execution completion into one event by default
- deadline miss and fallback activation into one event by default
- named-slice completion and broader completion into one event by default
''',
'1965-remedy-hardening-attestation-executable-mandate-lineage-receipt-page-binding-scope-execution-path-and-blocked-stronger-sentences-interface-spec.md': '''# Remedy-hardening-attestation executable-mandate lineage receipt page — binding scope, execution path, and blocked stronger sentences

## Purpose

This page is the durable one-receipt summary for mandate executability after verdict legitimacy review.
It lets a later operator read one artifact and know exactly whether the legitimate verdict remained advisory, became binding, entered a specific execution route, stalled into fallback, or completed only for a named slice while stronger execution-complete language stayed blocked.

## Receipt fields

- receipt identifier
- executable-mandate identifier
- source verdict-legitimacy receipt identifier
- governing verdict sentence
- mandate issuer summary
- binding-scope summary
- obligated actor summary
- action and deadline summary
- primary actuator summary
- fallback summary
- current executable-mandate class
- highest honest execution sentence
- blocked stronger sentence
- evidence references
- issued-at timestamp

## Primary sentence block

The receipt must begin with exactly two lines:

- **Highest honest executable-mandate sentence**
- **Blocked stronger sentence**

## Required sections

1. **Why this verdict is or is not binding here**
2. **Who is obligated to act and by when**
3. **Which execution route, manual steps, and prerequisites govern**
4. **Whether fallback, partial execution, or world-scope limits still matter**
5. **Why the next stronger execution sentence is blocked**

## Hard rules

The receipt must never let:

- `legitimate verdict exists` impersonate `real mandate exists`
- `permission changed somewhere` impersonate `the bound actors executed`
- `automatic linked-device behavior` impersonate `all required topologies are handled`
- `one restarted or reconnected world` impersonate `all relevant worlds executed`
- `one slice completed` impersonate `broader execution complete`
'''
}

readme_addendum = '''## Revision addendum — executable mandate, binding scope, and execution-route truth after rev0469

This tranche locks the next seam around **whether a verdict that is already legitimate has actually become a binding, routed, and executable mandate**.
The key decisions now made explicit in the archive are:

- **verdict-legitimate current conformance is a first-class rung, but it is weaker than executable-mandate current conformance with explicit binding scope and execution routing**
- **legitimate verdict only, mandate draft pending issuance, mandate issued with ambiguous binding scope, mandate issued for named cohort only, primary actuator unavailable, execution pending within deadline, deadline missed with fallback required, fallback route governing, partially executed for named slice only, and broader stronger sentence blocked are different truths**
- **legitimacy is weaker than mandate issuance, mandate issuance is weaker than execution routing, and execution routing is weaker than execution completed for the named bound slice**
- **linked-device auto-spread, live permission toggles, local-share inheritance, restart requirements, config startup behavior, and pause-mode side effects can no longer silently impersonate `the mandate landed`**
- **every serious post-verdict action sentence now needs one receipt that preserves governing verdict, mandate issuer, binding scope, obligated actors, required action set, deadline, primary actuator, fallback route, current execution class, highest honest execution sentence, and the blocked stronger sentence**

New docs added in this tranche:

- `1960-resilio-remedy-hardening-attestation-executable-mandate-binding-scope-and-execution-routing-fragmentation-evaluation.md`
- `1961-remedy-hardening-attestation-executable-mandate-contract-sheet-page-bound-parties-actuators-deadlines-and-fallbacks-interface-spec.md`
- `1962-remedy-hardening-attestation-executable-mandate-review-page-is-this-legitimate-verdict-actually-binding-and-executable-here-interface-spec.md`
- `1963-remedy-hardening-attestation-executable-mandate-proof-page-binding-scope-actuator-coverage-and-execution-ceiling-interface-spec.md`
- `1964-remedy-hardening-attestation-executable-mandate-timeline-page-order-route-attempt-deadline-failover-and-execute-events-interface-spec.md`
- `1965-remedy-hardening-attestation-executable-mandate-lineage-receipt-page-binding-scope-execution-path-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `the verdict is legitimate` can no longer hide whether anyone is actually bound to act
- a permission change or automatic linked-device spread can no longer silently impersonate execution completion
- a manual remove-and-re-share or restart-gated route can no longer hide inside `the system handled it`
- later operators can open one receipt and see exactly who was bound, which actuator was chosen, what fallback governed, which slice completed, and which broader execution sentence stayed blocked


'''

status_addendum = '''## Revision addendum — status shift toward executable mandate, binding scope, and execution-routing governance after rev0469

The next seam after **verdict legitimacy, burden, threshold, and rulebook-version governance** is now explicit:

- the archive can already say whether the trusted current witness set legitimately satisfies the current burden for the sentence the product wants to publish
- it still needed to own the harder truth of **whether that legitimate verdict has actually become a binding mandate for named actors, through a concrete execution route, with explicit actuator and fallback state**, because legitimate verdict, advisory-only verdict, mandate issued, binding for named cohort only, execution pending, fallback required, partial named-slice completion, and broader execution-complete standing are not one consequence class
- current Resilio docs reinforce that gap because linked devices still auto-spread folders with Owner or full read-write consequences, read-only on linked devices still requires a manual Standard-folder detour, Advanced local-share permission changes can still require remove-and-re-share, config mode still applies only to Standard folders and can disable WebUI while overriding prior folders, service-user changes can still create a different storage world and require re-add plus re-share or reconnect, and schedule pause still allows deletions and indexing side effects

This pass turns that gap into a first-class product object: **the remedy-hardening attestation executable-mandate and execution-routing case**.

What is newly true in the archive:

- **verdict-legitimate standing is weaker than executable-mandate standing**
- **legitimate verdict only, mandate draft pending issuance, mandate issued with ambiguous binding scope, named-cohort-only mandate, primary actuator unavailable, execution pending within deadline, deadline missed with fallback required, fallback-governed execution, named-slice execution complete, and broader stronger sentence blocked are separate public truths**
- **a legitimate sentence is weaker than a binding order, a binding order is weaker than an explicit execution route, and an explicit route is weaker than execution actually witnessed for the named bound slice**
- **linked-device spread, live permission changes, local-share inheritance, startup config, service restarts, reconnect recipes, and pause behavior now degrade into execution inputs instead of impersonating the execution verdict**
- **every serious post-verdict action sentence now needs one receipt that preserves mandate issuer, bound actor set, required action set, deadline, actuator class, primary route, fallback route, execution witness, highest honest execution sentence, and the blocked stronger sentence**

What remains intentionally true:

- verdict legitimacy still matters
- observer integrity still matters
- policy conformance, remediation, and affected-party closure still matter
- but none of those may substitute for one explicit answer about whether the verdict is actually binding and whether execution really landed for the actors the product now claims are governed

New docs added in this tranche:

- `1960-resilio-remedy-hardening-attestation-executable-mandate-binding-scope-and-execution-routing-fragmentation-evaluation.md`
- `1961-remedy-hardening-attestation-executable-mandate-contract-sheet-page-bound-parties-actuators-deadlines-and-fallbacks-interface-spec.md`
- `1962-remedy-hardening-attestation-executable-mandate-review-page-is-this-legitimate-verdict-actually-binding-and-executable-here-interface-spec.md`
- `1963-remedy-hardening-attestation-executable-mandate-proof-page-binding-scope-actuator-coverage-and-execution-ceiling-interface-spec.md`
- `1964-remedy-hardening-attestation-executable-mandate-timeline-page-order-route-attempt-deadline-failover-and-execute-events-interface-spec.md`
- `1965-remedy-hardening-attestation-executable-mandate-lineage-receipt-page-binding-scope-execution-path-and-blocked-stronger-sentences-interface-spec.md`

What this tranche contributes to the larger doctrine:

- `the verdict was legitimate` can no longer hide whether anyone was actually obligated to act
- a permission or share-state change can no longer silently impersonate execution of the whole mandate
- restart, reconnect, remove-and-re-share, and fallback routes can no longer hide inside optimistic `the system applied the ruling` language
- later operators can open one receipt and see exactly who was bound, how execution was supposed to happen, whether fallback governed, and why the next stronger execution sentence remained blocked


'''

resilio_eval_addendum = '''## Revision addendum after rev0469 — why remedy hardening attestation executable mandate, binding scope, and execution routing now sit on the non-clone side

Current official Resilio docs are still admirably candid that `the verdict is legitimate`, `this device should now get the folder`, `the permission changed`, `the local share should follow`, `the config should enforce it`, and `the ruling therefore landed everywhere it matters` are not one flat truth.
`Sync Private Identity & Linking My Devices` still says linked devices auto-receive your folders, remote users may auto-approve future linked-device sharing, and approvals can be issued from any linked device where the folder is present.
`Comprehensive guide to syncing (Desktop-Desktop)` still says linked devices get automatic full read-write access while manual sharing is the lane where access privileges are chosen folder by folder.
`User Management` still says Advanced-folder permissions can be changed without disrupting synchronization and that disconnect only suspends future updates while leaving already synchronized files in place.
`How to create a Read Only folder while syncing across linked devices?` still says linked devices automatically receive Owner permission and that achieving read-only on a linked device requires a Standard-folder Read Only key detour with manual disconnect and manual reconnect flow.
`Sharing a folder locally` still says local shares cannot receive Owner permission, Advanced local-share permissions cannot be changed through user management, remove-and-re-share is required, and reconnecting the source share does not automatically reconnect the local share.
`Running Sync in configuration mode` still says one config can apply settings across many machines at startup, but only for Standard folders, and that declaring shared folders in config disables WebUI and overrides previously added WebUI folders.
`Sync Service Troubleshooting on Windows` still says service-user changes can create a different storage world where old added folders are absent and require re-add plus re-share or reconnect, and that some exposure changes require restart.
`Running Sync on schedule` still says paused lanes still propagate deletions and continue rescanning and indexing.

This is strong execution-ingredient candor.
It is also exactly why AnonSync should not clone the present contract.
One ordinary answer to `now that the verdict is legitimate, who is actually bound and has execution truly landed?` still depends on combining linked-device automation, manual sharing detours, live-vs-replacement permission paths, local-share inheritance, Standard-only startup config, service-world forks, restart gates, and scheduler side effects.

So this tranche freezes a stronger replacement line: **legitimate verdict, advisory only, mandate issued, named-cohort-only mandate, actuator unavailable, execution pending, fallback governing, named-slice execution complete, and broader execution-complete sentence blocked become separate modeled truths.**

That is why this revision adds five more first-class pages: **Remedy-hardening-attestation-executable-mandate contract sheet**, **Remedy-hardening-attestation-executable-mandate review**, **Remedy-hardening-attestation-executable-mandate proof**, **Remedy-hardening-attestation-executable-mandate timeline**, and **Remedy-hardening-attestation-executable-mandate lineage receipt**.


'''

sources_addendum = '''## rev0470 source set — remedy hardening attestation executable mandate, binding scope, and execution routing

The most load-bearing source set for this pass was:

- Resilio's current `Sync Private Identity & Linking My Devices` article, which still says linked devices automatically receive folders, approvals can be issued from any linked device where the folder is present, and remote users may auto-approve future linked-device sharing.
- Resilio's current `Comprehensive guide to syncing (Desktop-Desktop)` article, which still says linked-device mode grants automatic full read-write access while manual sharing is the lane where access privileges are chosen per folder.
- Resilio's current `User Management` article, which still says Advanced-folder permissions can be changed without disrupting synchronization and that disconnect suspends future updates while leaving already synchronized files in place.
- Resilio's current `How to create a Read Only folder while syncing across linked devices?` article, which still says linked devices automatically receive Owner permission and that creating a read-only result requires a manual Standard-folder key detour.
- Resilio's current `Sharing a folder locally` article, which still says local shares cannot get Owner permission, some Advanced permission changes require remove-and-re-share, and source reconnection does not automatically reconnect the local share.
- Resilio's current `Running Sync in configuration mode` article, which still says one config can apply settings across many machines at startup but only for Standard folders, and that config-defined shares disable WebUI while overriding prior WebUI folders.
- Resilio's current `Sync Service Troubleshooting on Windows` article, which still says service-user changes can create a different storage world and require re-add plus re-share or reconnect, and that some changes require restart.
- Resilio's current `Running Sync on schedule` article, which still says paused lanes still propagate deletions and continue rescanning and indexing.

Those sources were enough to tighten the line again:

- current Resilio still deserves credit for candid execution ingredients
- but current Resilio still answers `who is actually bound and has execution really landed?` too diffusely
- AnonSync should therefore prefer explicit remedy-hardening-attestation-executable-mandate sheets, executable-mandate reviews, executable-mandate proofs, executable-mandate timelines, and durable executable-mandate lineage receipts over overloaded linked-device defaults, permission toggles, manual detours, config side effects, service-world forks, and pause semantics

Primary sources:

- Sync Private Identity & Linking My Devices
  https://help.resilio.com/hc/en-us/articles/205457815-Sync-Private-Identity-Linking-My-Devices

- Comprehensive guide to syncing (Desktop-Desktop)
  https://help.resilio.com/hc/en-us/articles/204754939-Comprehensive-guide-to-syncing-Desktop-Desktop

- User Management
  https://help.resilio.com/hc/en-us/articles/205471375-User-Management

- How to create a Read Only folder while syncing across linked devices?
  https://help.resilio.com/hc/en-us/articles/206216565-How-to-create-a-Read-Only-folder-while-syncing-across-linked-devices

- Sharing a folder locally
  https://help.resilio.com/hc/en-us/articles/360011582500-Sharing-a-folder-locally

- Running Sync in configuration mode
  https://help.resilio.com/hc/en-us/articles/206178884-Running-Sync-in-configuration-mode

- Sync Service Troubleshooting on Windows
  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows

- Running Sync on schedule
  https://help.resilio.com/hc/en-us/articles/210783266-Running-Sync-on-schedule


'''

for name, content in new_docs.items():
    (docs / name).write_text(content, encoding='utf-8')

# prepend addenda
readme = (root / 'README.md').read_text(encoding='utf-8')
(root / 'README.md').write_text(readme_addendum + readme, encoding='utf-8')

status = (docs / '00-status.md').read_text(encoding='utf-8')
(docs / '00-status.md').write_text(status_addendum + status, encoding='utf-8')

resilio_eval = (docs / '10-resilio-sync-evaluation.md').read_text(encoding='utf-8')
(docs / '10-resilio-sync-evaluation.md').write_text(resilio_eval_addendum + resilio_eval, encoding='utf-8')

sources = (docs / 'sources.md').read_text(encoding='utf-8')
(docs / 'sources.md').write_text(sources_addendum + sources, encoding='utf-8')

apply_script = root / 'apply_rev0470.py'
apply_script.write_text('''from pathlib import Path\nimport runpy\n\nROOT = Path(__file__).resolve().parent\nrunpy.run_path(str(ROOT / "make_rev0470.py"), run_name="__main__")\n''', encoding='utf-8')

print('wrote', len(new_docs), 'new docs and updated top-level files')
