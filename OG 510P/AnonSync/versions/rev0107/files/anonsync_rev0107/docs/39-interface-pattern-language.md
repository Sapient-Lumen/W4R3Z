# Interface pattern language

## Purpose

`38-operator-workbench-interface-spec.md` defines the main surfaces.
This document defines the interaction grammar that keeps those surfaces honest.

The question here is not “which tab exists?”
The question is:

> what patterns should repeat across CLI, GUI, TUI, and local web surfaces so AnonSync feels like one inspectable product instead of several partial clients?

`41-report-and-intervention-language.md` now complements this document by specifying how proof-bearing findings render once a page or card decides they matter.

## Core rule

A projection may simplify navigation, but it may not simplify truth.

That means:

- compressed summaries are allowed
- ambiguous verbs are not
- deferred proof panels are allowed
- silent widening of trust or delete scope is not
- view-specific affordances are allowed
- view-specific semantics are not

## Pattern 1 — page skeleton

Every substantial page should follow the same skeleton:

1. **Summary header**
   - object name
   - stable ID or easy copy handle
   - high-signal chips (`Incoming`, `Selective`, `Lease active`, `Blocked`, `Settled`, `Degraded`)
2. **Current answer strip**
   - one-sentence answer to the page's most important operator question
3. **Primary cards**
   - the few cards needed to understand state and take the next step
4. **Proof drawer / explain panel**
   - attached evidence for risky or subtle decisions
5. **Danger zone**
   - destructive or trust-expanding actions kept separate from ordinary work

The summary header should be consistent enough that an operator can move from a share page to a peer page without re-learning the visual grammar.

## Pattern 2 — current answer strip

Every detail page should expose one explicit sentence that answers the dominant question for that object.

Examples:

- share: `Visible here, mounted at /srv/media, currently selective, settled for backup but not yet for cutover.`
- peer: `Trusted collaborator with read-write on 2 shares, no delegation, one future approval record, no active successor handoff.`
- incoming share: `Visible from Alex, not yet adopted, target path is non-empty, same-path divergence exists at 12 paths, reconciliation review required before bind.`
- constellation join: `Keeps its identity, joins personal constellation as appliance, 12 shares become incoming-only, no delegated approvals, mixed-version warning blocks apply.`
- retirement: `Old device revoked locally, successor preview prepared, remote cleanup still pending on 1 offline peer.`
- compromise response: `Suspected theft on laptop-ember, sessions frozen, token revoked, rotation prepared, successor still optional.`

This strip exists because raw chips and counts are not enough.

## Pattern 3 — proof drawer

The proof drawer is the main answer to “show me why”.
It should be attachable from any risky card or action.

The drawer should be able to host at least these proof types:

- `preflight`
- `comparison`
- `preservation`
- `convergence`
- `settlement`
- `exposure`
- `authority-delta`
- `plan-drift`

Rules:

1. Opening the drawer does not mutate state.
2. The drawer must identify the exact subject object and version it is proving.
3. If proof is stale, the drawer should say so plainly and downgrade any apply action.
4. If several proofs matter, the drawer should order them by decision relevance, not by internal type name.

## Pattern 4 — verb vocabulary

The interface should use verbs that keep different scopes distinct.

Preferred verbs:

- `Join constellation` — add a device relationship without implying replacement or owner merge
- `Adopt` — turn visible incoming state into a local mount/binding
- `Bind` / `Rebind` — attach a share to a specific local path
- `Fetch` — materialize bytes locally
- `Evict` — remove local bytes while keeping share state
- `Repair path` — recover continuity of an existing mount at an intended or compared path
- `Detach locally` — release a local binding while keeping share visibility distinct from revocation
- `Delete from share` — replicated delete
- `Restore locally` — historical recovery that does not rewrite shared state
- `Prepare restore to share` — reviewed historical recovery back into replicated state
- `Resolve deviation` — act on a public local-drift case, not on a vague warning
- `Revoke` — remove granted authority
- `Retire` — end a device relationship with cleanup consequences
- `Replace` — bind successor continuity after review
- `Prepare cutover` — preview successor continuity or runtime/state re-home before apply
- `Re-home state root` — move or reopen durable state without implying fresh install or identity takeover
- `Ignore future contact` — durable suppression of new unsolicited contact
- `Snooze` — presentation-only defer of review attention
- `Dismiss` — hide a summary card without resolving the underlying subject

Avoid overloaded verbs like:

- `Connect`
- `Disconnect`
- `Link` when identity continuity, visibility blast radius, or approval widening are not spelled out
- `Remove`
- `Migrate settings` when continuity scope is not spelled out
- `Pause`
- `Fix`

unless the scope is spelled out nearby in plain language.

Good replacements for runtime control include:

- `Suspend downloads`
- `Drain uploads`
- `Throttle Internet transfers`
- `Freeze delete propagation`

These phrases are longer, but they keep the phase truth visible.

## Pattern 5 — action hierarchy

A page should normally offer:

- one primary action
- one or two secondary actions
- separate danger actions

The primary action should be the safest meaningful next step, not the most dramatic one.

Examples:

- incoming share with non-empty target path: primary action is `Prepare claim` or `Compare target`, not `Adopt anyway`
- non-empty target with same-path divergent bytes: primary action is `Review reconciliation`, not `Bind anyway` or `Use latest version`
- degraded convergence: primary action is `Explain blockers`, not `Force rescan`
- stale settlement barrier: primary action is `Refresh proof`, not `Apply anyway`
- successor handoff: primary action is `Preview handoff`, not `Apply replacement`
- state-root/runtime re-home: primary action is `Prepare cutover`, not `Migrate now`
- nested or overlapping path work: primary action is `Review topology`, not `Add anyway`

## Pattern 6 — batch honesty

Batch actions are acceptable only when their semantics are uniform.

Allowed examples:

- snooze three quiet review cards for 2 hours
- dismiss five resolved informational cards
- refresh three stale convergence reports

Guarded examples:

- apply several share adoptions only if all have equivalent preflight class and no outlier warnings
- revoke several grants only if the blast radius is identical and clearly shown per subject

Disallowed examples:

- mix data-destructive and trust-expanding operations in one apply
- mix local-only file actions with share-wide restore/delete under one ambiguous file toolbar action
- batch successor replacement with unrelated peer retirement cleanup
- batch local evictions together with share-wide deletes under one ambiguous `remove`

## Pattern 7 — empty states must teach, not decorate

Empty states should state what is absent and why that absence matters.

Good examples:

- `No items in Now. Nothing is currently blocked, risky, or time-sensitive.`
- `No future approval records. All new share offers from this peer will require fresh review.`
- `No active leases. Current route posture comes only from durable policy.`

Bad empty states are purely decorative or motivational.

## Pattern 8 — review lane promotion and demotion

The same subject may move between `Now`, `Soon`, and `Quiet` without changing its underlying object state.
That movement should follow stable reasons.

Promotion reasons may include:

- newly observed risk
- worsening preservation posture
- proof expiry approaching
- time-bounded lease nearing expiry
- convergence intended for `cutover` still degraded
- settlement barrier for `restore` expired before apply

Demotion reasons may include:

- proof refreshed and still valid
- blocker removed
- only background informational state remains
- operator snooze window active

The interface should explain the lane movement rather than making cards seem random.

## Pattern 9 — timeline condensation

Most pages should expose recent activity as a condensed timeline rather than raw logs.
Each event row should say:

- what changed
- which object changed
- whether it widened trust, changed bytes, or only changed presentation
- which proof or plan it referenced, if any

An operator should be able to jump from the condensed event to full audit details without losing context.

## Pattern 10 — textual parity

The richer GUI/web workbench must not hold exclusive semantics.
CLI and TUI projections should be able to render the same truths as text.

At minimum, textual surfaces should be able to express:

- the summary header
- the current answer strip
- lane placement and reason codes
- attention delivery outcome and acknowledgement posture when a page is the source of a live attention event
- attached proof refs and freshness
- clear action hierarchy labels

This matters because a Linux-first product cannot treat its textual surfaces as second-class explanations.

## Pattern 11 — what Resilio teaches here

Resilio's current docs still show a product with real strengths and real seams.
It has useful linking, selective sync, WebUI, config mode, and operational tuning.
But its docs also show why AnonSync needs a stricter interaction contract:

- configuration mode does not cleanly express the strongest share semantics
- WebUI and desktop flows diverge in meaningful places
- some network-policy outcomes still depend on retained cache and support knowledge
- several important outcomes still have to be reconstructed from mode, platform, or hidden-file context
- file-action meaning can still drift between placeholder state, read-only remediation, and archive ritual unless the interface pins intent explicitly
- conflict meaning can still drift between suffix filenames, path/case folklore, and rollback ritual unless the interface pins adjudication explicitly
- pause/scheduler semantics can still drift between transfer stop, delete propagation, rescans, and LAN-vs-Internet caps unless the interface pins phase truth explicitly

AnonSync should borrow the good lesson — reduce friction — without borrowing the bad lesson — hide the real model behind whichever surface happens to be most complete.

## Resulting standard

A good AnonSync interface should let an operator answer six questions quickly from any surface:

1. What is this object?
2. What is true about it right now?
3. What is the safest next action?
4. What scope would that action touch?
5. What proof supports it?
6. What would remain unresolved afterward?

If a surface cannot answer those six questions, it is not yet a trustworthy projection of the model.


## Pattern 12 — report cards should always look decision-shaped

Whenever a page or queue surfaces a report-backed finding, the card should show five things without click-through:

- report type
- severity
- freshness
- one-sentence current answer
- safest next action

A report card that shows only a scary badge or vague warning text is not good enough.

## Pattern 13 — freshness must be visible before apply

If a report is `aging`, `stale`, `drifted`, or `superseded`, the surface should show that fact before presenting any apply or dangerous action.

The operator should never discover freshness failure only after pressing the button they were invited to trust.

## Pattern 14 — one report drawer grammar, many report types

A `preflight` report and a `preservation` report may prove different things, but they should still open with the same interaction grammar:

1. current answer
2. scope
3. findings/evidence
4. next-safe action
5. unresolved aftermath

This is important because consistency of explanation is itself part of the safety model.

## Pattern 15 — warnings should collapse toward reports, not away from them

If the product accumulates badges, banners, tooltips, hidden-file lore, and special-case dialogs that do not point back to one common report language, it will drift back toward the kind of operator archaeology this archive is trying to escape.

A warning may be brief. It should still be legibly connected to a report-shaped explanation.


## Pattern 16 — operator state must be inspectable before mutation-rich surfaces are trusted

Any first-class surface that can mutate shares, trust, routes, or recovery state should also make it possible to answer one prerequisite question:

> which state root and runtime profile am I actually operating?

This does not mean every page needs a giant banner.
It does mean the product should have a stable path to the answer, and high-signal surfaces should show enough context that the operator is not acting inside a mystery control universe.

A good implementation usually includes:

- a persistent status affordance for active state root / service profile
- a dedicated System State page
- transition receipts when root or profile changes occurred recently
- no background/service/local-web mode that silently swaps semantics or inventory

If a profile switch, attach, or move can make shares appear or disappear without an explicit receipt, the interface has failed this pattern.

## Pattern 16a — execution-seat switches must show reachability and freshness delta before apply

A service-account or runtime-seat change on one host is not merely a startup convenience.
It can change which state root opens, which paths remain reachable, and whether notifications stay native.

Required rules:

- switching user, service seat, maintenance seat, or container seat must say whether the same state root and identity remain active
- any target that becomes unreachable, remapped, or downgraded to reviewed workaround posture must be visible before apply
- freshness/notification downgrade such as `native -> rescan-only` must be shown as semantic fallout, not hidden inside later troubleshooting
- `migrated state`, `same state with rebind`, and `clean-seat start` must remain visibly different outcomes

This matters because a product can define good state-root and service-profile objects on paper and still regress in practice if `run as service`, `switch account`, or `open as system` silently changes the host-local world.

## Pattern 16b — labels and authority continuity must not share one casual rename affordance

A good sync product should let operators fix names.
A trustworthy sync product should also make sure a name edit does not quietly become a trust rewrite.

Required rules:

- local-only relabel, peer-visible relabel, alias history, and authority replacement must remain visibly different actions
- the same label must not be treated as proof of the same authority, and a new label must not be treated as proof of authority rotation
- any action that would replace authority or inherit future approvals must escalate into continuity review rather than save inline from a text field
- peer-visible scope and alias retention must be shown before apply
- successor, compromise, or constellation review escalation must stay obvious when the continuity story stops being cosmetic

This matters because a product can define good subject handles, authority domains, and successor workflows on paper and still regress in practice if `Rename`, `Link`, or `Looks like the same laptop` quietly rewrites the trust story.

## Pattern 17 — transfer cards must answer route, budget, and queue truth

A transfer card is not trustworthy if it shows only:

- bytes done
- current rate
- a peer name
- maybe a relay or direct icon

A mature transfer card should answer five questions without click-through:

1. which route class is currently winning
2. whether a better route exists but is disallowed, degraded, or simply not selected
3. which budget or override is constraining throughput now
4. whether the transfer is running, queued, delayed, suspended, blocked, or source-starved
5. what change would most directly improve it

This matters because throughput confusion is one of the easiest ways for a product to drift back into support-article archaeology.
A relay icon, a speed chart, and a hidden advanced knob do not add up to one honest explanation surface.


## Pattern 18 — channel parity, not channel semantics

A toast, tray bubble, browser banner, webhook, email, or CLI watch line may differ in presentation.
They may not differ in meaning.

Required rules:

- every delivery channel must point back to the same attention event, report, and subject
- channels may truncate, but they may not invent different severity or different recommended actions
- delivery failure must become visible in the workbench and CLI instead of disappearing into logs
- Linux/headless deployments must preserve the same semantics even when no desktop-shell affordances exist

## Pattern 18a — disappearing controls must collapse into server-declared capability state

A browser button, context-menu item, or popover action may fail to render.
That must never become the operator's only explanation.

Required rules:

- every high-signal control action has a server-declared capability record independent of UI rendering
- if one channel cannot render or use the action honestly, the operator sees an explicit denial or degradation reason
- browser incompatibility or content blocking becomes an integrity finding rather than an absent control
- at least one fallback channel is named where the action remains inspectable or performable

This matters because a product can define good access objects on paper and still regress in practice if missing browser chrome changes the perceived feature set.

## Pattern 18b — fallback must preserve review identity, not restart the meaning

Telling an operator to continue in another client is not enough.
An honest fallback path keeps the same reviewed action alive unless the product explicitly reopens broader review.

Required rules:

- a cross-channel handoff keeps the same action, subject, review family, and receipt promise unless stronger review is explicitly required
- degraded channels may emit handoff objects, but they may not invent weaker apply paths than the owning review family allows
- if endpoint, trust, or state-root meaning changes across channels, the product must say that it is reopening review rather than pretending nothing changed
- later audit must be able to prove why the action continued in another channel or why it stopped

This matters because otherwise `try the CLI`, `use another browser`, or `switch to desktop` becomes yet another support ritual instead of a durable operator contract.

## Pattern 18c — auth repair must be side-effect bounded

Regaining control access is not the same as resetting the product.
An honest repair surface should make that obvious.

Required rules:

- ordinary auth repair must say which authority changes and which durable subjects remain untouched
- no repair path may silently reset unrelated preferences, duplicate device identity rows, or switch state roots
- if broader state mutation is actually required, the repair surface must stop and hand off to bring-up or state-root review
- browser trust bypass ritual must never be the only practical way to keep administering the daemon

This matters because a product can define a good safety model on paper and still regress in practice if the real repair path is storage-folder surgery or browser magic.

## Pattern 19 — acknowledgements need receipts, not vibes

`Seen`, `Ack`, `Snooze`, and `Mute` are not cosmetic implementation details.
They are durable interventions that should be inspectable later.

Required rules:

- every acknowledgement-style action emits a receipt or updates a receipt-bearing attention event
- the UI must say whether the action is presentation-only or also resolves a subject workflow elsewhere
- a snoozed card should still expose when and why it will worsen or reassert
- no acknowledgement affordance may silently approve, revoke, apply, or delete the underlying subject


## Pattern 20 — every important value needs an origin chip

If the workbench shows a current value without also showing where it came from, it is only halfway honest.
Important configurable fields should therefore expose a small origin chip such as `default`, `profile`, `pinned`, `override`, `schedule`, `imported`, or `downgraded`.
Opening the chip should reveal the full origin chain, not navigate to a different settings maze.

That keeps “effective policy” legible in the same place where the operator first noticed the value.


## Pattern 21 — temporary exceptions need one common drawer grammar

An operator should not have to remember that one temporary exception lives under `route lease`, another under `diagnostic depth`, and a third under `maintenance override`.
Wherever a temporary exception is rendered, the drawer or card should show the same sequence:

1. baseline posture
2. active temporary effect
3. expiry or exhaustion condition
4. overlap/conflict with other exceptions
5. receipt history

This matters because cleanup memory is not a trustworthy control plane.
A product that wants temporary intent to stay legible must render it with one common interaction grammar even when the underlying domain-specific effects differ.

## Pattern 22 — exit review needs a fixed grammar

Every departure-style review should render the same sections in the same order:

1. intent and scope
2. stops now
3. stays intentionally
4. residue after apply
5. follow-up options
6. receipt promise

This matters because a product can define a good exit object model on paper and still regress in practice if one client turns it into a two-line warning while another exposes the real consequences.

## Pattern 22a — claim and adoption review need a fixed grammar

Every non-trivial way-in review should render the same sections in the same order:

1. source and offer
2. local outcome
3. path and filesystem
4. authority delta
5. blockers and drift
6. receipt promise

This matters because a product can define good incoming-share and claim objects on paper and still regress in practice if one client uses a rich acceptance sheet while another falls back to a path picker called `Connect`.



## Pattern 22b — compromise review needs a fixed grammar

Every non-trivial compromise review should render the same sections in the same order:

1. trigger and scope
2. immediate freeze
3. revocation and rotation
4. continuity and successor
5. residue and observation
6. receipt promise

This matters because a product can define good revoke, rotate, exit, and replacement objects on paper and still regress in practice if one client offers a rich incident sheet while another falls back to a bag of unlink, uninstall, and relink instructions.

## Pattern 22c — dormant-peer re-entry review needs a fixed grammar

Every non-trivial stale-return review should render the same sections in the same order:

1. subject and dormancy
2. chronology and evidence
3. authority and scope
4. divergence and availability
5. admissible actions
6. receipt promise

This matters because a product can define good settlement, rollback, and compromise objects on paper and still regress in practice if one client offers a rich re-entry sheet while another falls back to peer counters, archive warnings, or a generic `Resume syncing` button.

## Pattern 22d — destructive-replay review needs a fixed grammar

Every non-trivial destructive-replay review should render the same sections in the same order:

1. trigger and scope
2. destructive effect summary
3. preservation and recoverability
4. authority and source confidence
5. admissible actions
6. receipt promise

This matters because a product can define good file-intent, rollback, and activity objects on paper and still regress in practice if one client offers a rich delete-wave sheet while another falls back to `Pause`, `Resume syncing`, archive checkboxes, or read-only overwrite lore.

## Pattern 22e — local-derivation review needs a fixed grammar

Every non-trivial same-host derivation review should render the same sections in the same order:

1. source and target
2. topology and loop risk
3. authority and lifecycle coupling
4. materialization and target-tier reality
5. admissible derivations
6. receipt promise

This matters because a product can define good binding, projection, and fidelity objects on paper and still regress in practice if one client offers a rich same-host derivation sheet while another falls back to a path picker plus `Create local copy`.

## Pattern 22f — authority-mutation review needs a fixed grammar

Every non-trivial authority-mutation review should render the same sections in the same order:

1. trigger and current authority
2. desired boundary delta
3. active subject state and coupled dependents
4. authority-substrate and compatibility effects
5. admissible mutations
6. receipt promise

This matters because a product can define good grants, stewardship, and constellation caps on paper and still regress in practice if one client offers a rich access-change sheet while another falls back to `Owner`, `Disconnect`, or `re-share with a different key`.

## Pattern 22g — contention and quiescence review need a fixed grammar

Every non-trivial contention review should render the same sections in the same order:

1. trigger and contested scope
2. writer and lock reality
3. notification and filesystem posture
4. quiesce and propagation effects
5. admissible actions
6. receipt promise

This matters because a product can define good transfer, activity, and fidelity objects on paper and still regress in practice if one client offers a rich coordination sheet while another falls back to a locked-files badge, a retry timer, or `increase delay` folklore.

## Pattern 22h — capacity-fit and scale-admission review need a fixed grammar

Every non-trivial capacity-fit review should render the same sections in the same order:

1. subject and intended local role
2. local capacity and index cost
3. freshness and notification posture
4. portability and path blockers
5. admissible modes and mitigations
6. receipt promise

This matters because a product can define good intake, storage, and fidelity objects on paper and still regress in practice if one client offers a rich host-fit sheet while another falls back to `slow indexing`, `out of memory`, `increase watchers`, or `re-add the folder` folklore.


## Pattern 22i — bring-up and control-entry review need a fixed grammar

Every non-trivial bring-up review should render, in this order:

1. host role and runtime target
2. state and continuity choice
3. identity and relationship posture
4. control access and network posture
5. blockers and bootstrap dependencies
6. receipt promise

This matters because a product can define good state-root, recovery, access-token, and service-profile objects on paper and still regress in practice if one client offers a friendly starter flow while another hides that it attached prior state, retained prior identity, or widened control exposure.
Headless and GUI surfaces need one first-open grammar, not one wizard and one bag of startup flags.



## Pattern 22j — mutation-gate review needs a fixed grammar

Every non-trivial mutation gate should render, in this order:

1. current session and endpoint
2. requested mutation and subject scope
3. required authority and grant scope
4. binding and freshness
5. blockers and fallback
6. receipt promise

This matters because a product can define good access, session, and repair objects on paper and still regress in practice if one client offers a rich reviewed elevation sheet while another falls back to `Confirm password`, `Apply anyway`, or whatever browser session happened to survive.

## Pattern 22k — target-custody and exclusive-bind review need a fixed grammar

Every non-trivial target-custody review should render, in this order:

1. target and discovered markers
2. current custody and lineage
3. requested bind and continuity story
4. collision and corruption risk
5. admissible custody actions
6. receipt promise

This matters because a product can define good state-root, bind, and successor objects on paper and still regress in practice if one client offers a rich custody sheet while another falls back to `folder not empty`, `already managed`, or `delete internal files and retry` folklore.
Headless and GUI surfaces need one host-local ownership grammar, not one path picker and one troubleshooting article.

## Pattern 22l — share-layout and residue review need a fixed grammar

Every non-trivial share-layout review should render, in this order:

1. requested layout and visibility
2. live namespace guarantee
3. annex placement and metadata-carry posture
4. residue/history/cleanup posture
5. admissible actions
6. receipt promise

This matters because a product can define good custody, history, projection, and space objects on paper and still regress in practice if one client offers a rich layout sheet while another falls back to `Show hidden files`, `Open Archive`, `Delete .sync`, or `Clean temp files` folklore.
Headless and GUI surfaces need one layout-separation grammar, not one file-browser ritual and one support article.

## Pattern 22m — semantic downgrade must not hide inside speed language

Every non-trivial optimization review should render, in this order:

1. requested optimization or degraded target
2. semantic guarantees at risk
3. detection/diff/verification posture
4. target and runtime findings
5. admissible actions
6. receipt promise

This matters because a product can define good transfer, fidelity, and capacity objects on paper and still regress in practice if one client says `Performance mode` while another reveals that rename continuity, freshness, or verification actually weakened.
Headless and GUI surfaces need one semantic-fallback grammar, not one speed toggle and one troubleshooting article.


## Pattern 22n — revocation and recall need one fixed retained-copy grammar

Every non-trivial recall review should render, in this order:

1. requested boundary change
2. current authority and byte reality
3. retained-copy and recovery findings
4. recall and observation posture
5. admissible actions
6. receipt promise

This matters because a product can define good exit, authority, and recovery objects on paper and still regress in practice if one client says `Removed` while another reveals that the peer still has bytes, or if one channel preserves encrypted backup truth while another implies ordinary erasure.
Headless and GUI surfaces need one retained-copy grammar, not one remove button and one support article.

## Pattern 23 — dangerous verbs should inherit the reviewed intent label

A reviewed `decommission` plan should not end with a generic `Remove` button.
A reviewed `replace-with-successor` plan should not end with a generic `Apply` button unless the nearby text repeats the real intent prominently.
The final action label should inherit the reviewed verb family so the operator is never asked to trust a generic destructive button for a specific, high-consequence state transition.
A reviewed `compromise` plan should not end with a generic `Remove device` or `Reset` button if the real action is `Apply containment`, `Rotate identity`, or `Prepare clean break`.
A reviewed `reentry` case should not end with a generic `Resume` button if the real action is `Resume read-only`, `Quarantine pending chronology review`, or `Escalate to compromise`.
A reviewed destructive-replay case should not end with a generic `Apply` or `Resume syncing` button if the real action is `Freeze destructive replay`, `Allow non-destructive sync only`, or `Apply narrowed destructive scope`.
A reviewed local-derivation case should not end with a generic `Create` button if the real action is `Create read-only derivative`, `Create cache branch`, or `Reject unsafe self-edge`.
A reviewed authority-mutation case should not end with a generic `Apply` or `Disconnect` button if the real action is `Grant write without delegation`, `Narrow to read-only and preserve bytes`, or `Strip delegation but keep read access`.
A reviewed contention case should not end with a generic `Retry`, `Resume syncing`, or `Increase delay` button if the real action is `Hold uploads and preserve local writes`, `Freeze bidirectional propagation`, or `Escalate to filesystem-fidelity review`.
A reviewed capacity-fit case should not end with a generic `Add folder`, `Connect`, `Retry indexing`, or `Re-add` button if the real action is `Adopt metadata-only on this host`, `Defer and reclaim before full materialization`, or `Escalate to topology/fidelity review`.
A reviewed target-custody case should not end with a generic `Use folder`, `Reconnect`, or `Delete .sync` button if the real action is `Reuse verified same-lineage bind`, `Preserve foreign markers and inspect only`, or `Apply reviewed cleanup after preservation`.
A reviewed share-layout case should not end with a generic `Show hidden files`, `Open Archive`, or `Clean temp files` button if the real action is `Migrate managed bytes to annex`, `Preserve legacy layout and inspect only`, or `Apply reviewed cleanup of metadata-carry residue`.
A reviewed recall case should not end with a generic `Remove`, `Disconnect`, or `Revoke` button if the real action is `Stop future updates and attest retained copies`, `Preserve encrypted backup and freeze future updates`, or `Request remote delete and await observation`.

## Pattern 24 — channel parity is part of the safety model

Resilio's current docs are a useful warning here: Linux WebUI, config mode, and desktop-oriented controls do not always express the same safety affordances or the same feature envelope.
AnonSync should adopt the opposite rule for safety-critical actions.
Rich layout, narrow layout, and textual layout may differ in presentation, but they may not differ in:

- intent class
- scope truth
- residue truth
- continuity truth
- required acknowledgements
- receipt identity

If those differ by channel, the system does not have one trustworthy control surface.



## Pattern 22o — authority rotation needs one fixed epoch grammar

Every non-trivial epoch-rotation review should render, in this order:

1. requested boundary change
2. current epoch map
3. stale-capability fallout
4. derivative and migration obligations
5. convergence and observation posture
6. receipt promise

Headless and GUI surfaces need one epoch grammar, not one `Rotate key` button and one folder-class FAQ.

This matters because a product can define good offers, grants, compromise cases, and recall objects on paper and still regress in practice if one client offers a rich epoch sheet while another falls back to `re-share`, `use a new key`, or `upgrade share` folklore.

A reviewed epoch-rotation case should not end with a generic `Rotate`, `Re-share`, or `Upgrade` button if the real action is `Issue new epoch but old capability remains`, `Quarantine old authority and wait for observation`, or `Upgrade authority class but rebuild derivative/local-share state separately`.


## Pattern 22p — observer/read-only claims need one fixed four-truth grammar

When the product says a subject is `read only`, `observer`, `viewer`, `receive only`, or similar, the review surface should always keep these sections in the same order:

1. requested access posture
2. visibility and materialization reality
3. local-write and repair behavior
4. onward serving and redistribution posture
5. projection, share-class, and runtime limits
6. receipt promise

This matters because the archive already treats `read only` as insufficiently honest on its own. A safer product must show whether the subject sees placeholders or full bytes, whether local edits stall or auto-revert, whether the replica may still serve clean bytes onward, and whether any of that answer only exists because of projection or class-specific ritual.


## Pattern 22q — visible names are not a fetch promise

A path that is visible in the tree, visible as a placeholder, or visible as a selective-materialization stub must not automatically read as `the bytes are safely fetchable later`.
The product should show whether the bytes are locally present, remotely witnessed, only last-seen on an offline source, or no longer honestly retrievable at all.

This matters because Resilio's own docs now make two dangerous states explicit: placeholder-only universes where nobody still has the full file, and ghost announcements where the tree still advertises a file even though no peer now has the bytes.
A safer product must keep namespace visibility, local residency, full-copy witnesses, and fetchability posture as separate truths.



## Pattern 22r — file availability must read like one answer, not a collage of statuses

A serious file/subtree surface should be readable as one sentence-shaped answer.
The operator should not have to scan three cards and a warning tray just to learn whether the thing is visible, local, witnessed elsewhere, fetchable now, or safe to evict.

The default compact order should be:

1. visibility
2. local residency
3. witness summary
4. fetchability posture
5. safest next step

That order matters because it mirrors the actual reasoning chain.
First: can I see the name? Second: do I have bytes here? Third: who else has bytes? Fourth: is a fetch honest right now? Fifth: what is the safest action?

## Pattern 22s — mixed-risk subtree actions must split by safety class before they batch

A subtree that contains both remotely backed files and local-last-copy files must not collapse into one optimistic bulk action.
If the operator asks to evict the subtree, the interface should split the result into at least:

- safe now
- guarded, re-witness first
- stale/ghost visibility

This matters because batch convenience is one of the fastest ways to recreate misleading `remove from device` semantics.

## Pattern 22t — the primary verb must change when the risk class changes

When the current posture is `fetchable-now`, the primary verb may be `Fetch now` or `Evict safe rows`.
When the current posture is `local-last-copy`, the primary verb should change to something like `Pin locally` or `Create another full-copy witness`.
When the current posture is `ghost-risk`, the primary verb should change again to something like `Retire stale announcement` or `Keep visible with warning`.

The point is not wordsmithing.
The point is that the primary verb should expose the real state transition instead of preserving one convenient button label across materially different safety conditions.

## Pattern 22u — a batch bar may only speak for the safe subset it can actually mutate

When a mixed selection contains safe rows, guarded rows, and stale rows, the primary batch label should only name the subset it can truthfully change right now.
A label such as `Evict 24 safe rows` is acceptable.
A label such as `Evict 30 selected rows` is not, if 6 rows still require re-witness, restore, or stale-retirement review.

This matters because overclaiming scope in the action bar is just a more polished form of the same ambiguity that old `remove from device` language created.

## Pattern 22v — history-backed-only must switch the verb from transfer to restore

When no current peer now witnesses the bytes, but local or reviewed history still can restore them, the primary verb should become `Restore from history`.
The product should not keep using `Fetch` merely because the path is still visible in a selectively materialized tree.

This matters because `fetch` implies live source backing, while `restore` implies timeline-backed recovery.
Those are different promises and should not share one optimistic label.

## Pattern 22w — dense and mobile surfaces may compress counts, not risk classes

A dense list row or mobile card may shorten wording and move details behind expansion, but it must still preserve separate cues for:

1. local bytes
2. witness posture or its absence
3. safest next action

If compression merges witness posture and fetchability posture into one vague adjective such as `available`, the surface has crossed from dense into misleading.


## Pattern 22x — the row must keep state, source, and verb adjacent

An operator should be able to scan one row and answer three questions without opening a menu:

1. do I have bytes here
2. what backs recovery or fetch
3. what is the next honest action

If those answers are spread across a state chip, a distant side panel, and a context menu, the row is not honest enough for an operator product.

## Pattern 22y — only safe-now rows get one-click mutation

A row may expose a direct inline mutation when it is clearly `safe-now`.
Once a row becomes guarded, history-backed, stale, or blocked, the visible affordance should pivot into review instead of preserving the same one-click action shell.

This matters because keeping the same button after the risk class changed is just a subtler version of keeping the same verb after the state changed.



## Pattern 22z — announced here is not the same as claimed here

A newly visible share should be allowed to exist on a machine before that machine has chosen a local path, role, or materialization posture.
The surface should therefore preserve separate language for:

- announced here
- deferred here
- claimed here
- bound here
- hidden here only
- withdrawn wider by authority

This matters because linked-device convenience is one of the easiest places to smuggle path-creation and visibility side effects back under one vague `Connect` or `Remove` verb.

## Pattern 22za — local hide and wider withdraw must never share one primary verb

A user who does not want to see a share on this laptop is doing something materially different from an authority holder who wants to retract visibility across a wider constellation.
The interface may place those actions near each other, but it must not collapse them into one generic `Remove` action.

This matters because cross-device convenience easily turns local housekeeping into accidental authority mutation when the scope line is not explicit.

## Pattern 22zb — remembered defaults may prefill review, but may not silently create a claim

The product may remember the preferred path root, local role, or initial materialization posture for this machine.
But remembered defaults should only prefill a review or claim draft.
They should not silently turn a merely announced share into a bound local mount.

This matters because otherwise a personal-constellation convenience feature quietly recreates the same default-location and duplicate-path folklore the archive is trying to avoid.

## Pattern 22zc — approvals must say which seat is speaking and how far the approval travels

A truthful approval surface does not begin with a generic `Approve` verb.
It begins with four adjacent facts: requested subject, acting seat, approval horizon, and next honest action.

At minimum that means:

- `Approve once` stays visibly different from `Approve for reviewed scope`
- switching seats must visibly change the admissible horizon when it matters
- dense/mobile clients may compress wording, but not erase `seat` or `future-reaching` cues
- a receipt must later prove which seat spoke and whether future approval memory was created

If the operator can still approve a request without seeing who is speaking or how far the approval travels, the surface has recreated linked-device owner folklore under a cleaner coat of paint.


## Pattern 22zd — remembered approval may lower friction, but it may not silently complete later local acts

A truthful remembered-trust surface does not begin with `Approved before`, `Auto-connect`, or `No review needed`.
It begins with four adjacent facts: current arrival, matched memory, local outcome now, and next honest action.

That means:

- a standing-approval match may be explicit evidence for skipping identity re-vetting
- it may stage a lower-friction queue outcome such as `claim suggested`
- it may not silently pick a path, create a bind, or materialize bytes
- a receipt must later prove whether the product only recognized prior trust or actually changed local state

If the operator can still watch a matched arrival appear as a live local folder without seeing that claim/bind/materialization were separate later acts, the surface has recreated remembered-trust folklore under a cleaner coat of paint.


## Pattern 22ze — current share posture and future-arrival policy must not share one mode chip

A truthful local-share surface does not begin with `Disconnected`, `Selective`, `Synced`, or any other one-word summary.
It begins with adjacent facts about:

1. whether the share is merely announced here or actually claimed here
2. whether a local bind/path exists here and how that path was chosen
3. whether local bytes are absent, placeholder-backed, partial, or full
4. what this seat will do with later arrivals in the same reviewed scope

If one chip is still answering all four questions, the surface has recreated mode folklore under cleaner styling.

## Pattern 22zf — changing future defaults must visibly spare current posture unless review says otherwise

When an operator changes a seat's future-arrival policy, the interface should explicitly say whether existing shares remain untouched.
Likewise, when an operator changes the current share's bind or byte posture, the interface should explicitly say whether future defaults remain untouched.

This matters because one overloaded `change mode` control is one of the easiest ways to smuggle path relocation, dematerialization, and later-arrival automation back under a single friendly action.


## Pattern 22zg — suggested path is not the same as committed bind

A truthful placement surface does not begin with `Connect`, `Open`, or a default root.
It begins with four adjacent facts:

1. current bind truth
2. suggested candidate path
3. suggestion basis
4. collision class / next honest action

If the operator cannot tell whether the shown path is only a convenience draft or an already committed local bind, the surface has recreated default-location folklore under cleaner styling.

## Pattern 22zh — duplicate-suffix fallback is a reviewed placement outcome, not a harmless cosmetic fix

A suffix such as `(1)` is never merely a prettier filename.
It is evidence that the candidate path collided and that the product chose to preserve convenience over a truthful bind review.

That means:

- any suffix-adjusted candidate must be shown explicitly as a candidate with a reason
- same-lineage adoption, alternate-path choice, and `keep unbound` must remain visible alternatives when admissible
- dense/mobile clients may compress wording, but they may not hide that the original candidate collided
- if the product cannot justify the candidate with reviewed evidence, the honest next action is review, not silent duplicate creation


## Pattern 46 — standing convenience must be edited through its own reviewed object

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


## Pattern 47 — every arrival-worthy subject deserves one why-here explanation

A subject that arrived through linked visibility, remembered approval, standing template, or later placement suggestion should expose one compact explanation surface.
That surface should keep these adjacent:

1. current stage
2. strongest cause
3. strongest non-cause
4. one counterfactual
5. next honest verb

Good compression:

```text
Photos-2026   claim-suggested   matched prior approval + family template   no local bind yet   Explain
```

Bad compression:

```text
Photos-2026   Connected   Open
```

The bad form hides whether the subject is merely announced, lightly admitted, claimed, or bound.
A mature operator surface should not make the user learn that difference from support prose.

## Pattern 47a — every explanation needs at least one explicit non-cause

Whenever a standing memory or default influenced a subject, the surface should say not only what *did* happen, but one important thing that *did not* happen.
Examples:

- `approval memory matched, but no local bind exists yet`
- `template drafted a path, but no claim was auto-applied`
- `placement suggestion exists, but sibling bound shares were untouched`

Without an explicit non-cause, convenience surfaces drift back toward magical interpretation.

## Pattern 47b — counterfactuals are part of trustworthiness, not optional garnish

A useful explanation surface should let the operator see one narrower or broader governing case and how the stage would differ.
Examples:

- `No remembered approval => fresh review required`
- `Announce-only template => no claim suggestion`

This matters because operators do not merely need chronology; they need help judging which governing fact actually mattered.


## Pattern 47c — standing-policy mutation needs effect buckets before apply

A standing-policy edit should not jump from `current values` straight to `Apply`.
It should first show stable effect buckets for:

1. future unseen arrivals
2. announced-unclaimed subjects
3. claimed-unbound subjects
4. bound subjects
5. current bytes
6. approval memory / standing matches

Good compression:

```text
announce-only + new default root   future-only unless drafts refreshed   bound shares unchanged
```

Bad compression:

```text
Save settings
```

The bad form hides retroactivity and asks the operator to remember folklore.
A mature operator surface should not do that.

## Pattern 47d — every standing-policy preview needs one explicit non-effect and one named example

Category prose alone is not enough.
A trustworthy preview should always pair one explicit non-effect with at least one named example subject whenever live subjects exist.

Examples:

- `bound shares unchanged`
- `Invoices-2025 keeps its current bind and current bytes`
- `Photos-2026 keeps its old draft unless refresh is selected`

Without that pairing, previews drift back toward magical interpretation even if the underlying model is sound.



## Pattern 47e — current policy and applied policy must stay visibly separate

When one standing-policy family has changed over time, do not let one `current settings` row pretend to explain every older subject still on the seat.
A truthful compact surface should keep:

- current effective version
- applied version for this subject, or `matches current`
- one explicit attribution label (`grandfathered`, `matches current`, `draft-carried-forward`)
- one next honest action

Good compression:

```text
Photos-2026   current v7 announce-only   applied v6 claim-suggested   grandfathered draft   Explain policy lineage
```

Bad compression:

```text
Photos-2026   Mode: announce-only   Settings
```

The second form is short, but it still asks the operator to infer whether the subject actually followed the current version, an older version, or a partially refreshed draft.



## Pattern 47f — post-lineage drift still needs its own class and action surface

After a policy family has version lineage, do not assume the operator can infer live actionability from lineage alone.
A truthful compact surface should keep:

- current policy summary
- applied policy summary or `matches current`
- one explicit drift class
- one next honest action

Good compression:

```text
Photos-2026   current v8 announce-only   applied v6 claim-suggested   refresh-eligible   Refresh under current policy
```

Also good:

```text
Invoices-2025   current v8 announce-only   applied v6 bound /srv/family   pinned exception   Inspect exception
```

Bad compression:

```text
Photos-2026   Out of date   Update
```

The bad form hides whether the subject is truly safe to refresh, intentionally grandfathered, or actually requires stronger subset review.

## Pattern 47g — mixed drift batches must split before apply

When a selected set contains refresh-eligible drafts, subset-review subjects, and pinned/grandfathered exceptions, do not render one cheerful batch verb.
A trustworthy surface should split the batch into class-specific actions.

Good compression:

```text
Refresh 4 eligible drafts   Review 2 claimed subjects   Keep 3 exceptions
```

Bad compression:

```text
Realign 9 subjects
```

The second form is short, but it still asks the operator to guess which of the nine subjects will actually mutate now.


## Pattern 47h — intentional exceptions need aging state, not immortal rows

After a product can classify drift and pin exceptions, do not assume that is the end of the story.
A truthful compact surface should keep:

- one explicit divergence summary
- one explicit aging class (`healthy`, `due-soon`, `overdue`, `no-expiry-acknowledged`)
- one review-horizon fact or explicit no-expiry acknowledgement
- one next honest action

Good compression:

```text
Invoices-2025   pinned exception vs current v8 announce-only   due-soon   review in 10d   Renew exception
```

Also good:

```text
Family-Archive   kept grandfathered under v6   no-expiry-acknowledged   inspect acknowledgement   Inspect exception
```

Bad compression:

```text
Invoices-2025   Exception   Keep
```

The bad form hides whether the difference is still within review horizon, already overdue, or explicitly allowed to live without expiry.

## Pattern: remembered-trust freshness row

Use this pattern whenever prior approval can still affect later arrivals.
A remembered-trust freshness row should keep five items adjacent:

1. remembered approval subject
2. granted scope summary
3. freshness class
4. strongest cooling reason or freshness evidence
5. next honest action

Good examples:

- `Maya / photos-collab · granted Maya + linked devices / Photos family · cooling · last used 214d ago · Touch-renew`
- `Studio-NAS / backup-read · granted read-only backup scope · frozen · identity epoch changed · Require fresh approval next time`

Bad examples:

- `Approved before`
- `Known peer`
- `Still trusted`
- `Auto-connect ready`

The row exists to explain whether remembered approval is still live enough to matter, not merely that it once existed.


## Pattern: remembered-trust trace row

Use this pattern whenever prior approval still affects later arrivals and the operator may need to know which exact trust act was reused.
A remembered-trust trace row should keep five items adjacent:

1. remembered approval subject
2. current head summary
3. freshness class
4. latest mutation fact
5. next honest action

Good examples:

- `Maya / photos-collab · head narrowed to home-nas/photos-only · cooling · last mutation 21d ago · Show trace`
- `Studio-NAS / backup-read · head frozen after identity epoch change · frozen · last mutation 3d ago · Show trace`

Bad examples:

- `Approved before`
- `Known peer`
- `Auto-connect history`
- `Still trusted`

The row exists to explain which trust lineage is live now and to open one explicit authorization trace when a later subject needs proof.

## Pattern: remembered-trust rebase row

Use this pattern whenever a linked-device or identity mutation means old remembered approval is no longer trivially one family.
A remembered-trust rebase row should keep five items adjacent:

1. remembered approval subject
2. mutation trigger
3. current family posture
4. affected-descendant fact
5. next honest action

Good examples:

- `Maya / photos-collab · certificate takeover 3d ago · split recommended · 2 descendants affected · Rebase trust family`
- `Studio-NAS / backup-read · hidden member reappeared · fresh required for 1 descendant · 1 descendant affected · Rebase trust family`

Bad examples:

- `Linked approval changed`
- `Known peer updated`
- `Trust family needs repair`
- `Keep linked`

The row exists to explain when remembered approval can no longer be treated as one harmless blob after constellation mutation.

## Pattern: remembered-trust descendant-liveness row

Use this pattern whenever a descendant still matters to remembered-trust convenience but current liveness is weaker than family membership.
A descendant-liveness row should keep five items adjacent:

1. descendant identity
2. family / inheritance posture
3. liveness class
4. confidence fact or witness age
5. next honest action

Good examples:

- `tablet-citrine · inherits frozen · hidden awaiting return · low confidence · Freeze reuse until live`
- `desktop-ash · split child family · reappeared awaiting proof · guarded confidence · Require fresh approval on return`
- `home-nas · inherits unchanged · live observed 4m ago · high confidence · Record live observation`

Bad examples:

- `Known device`
- `Available before`
- `Probably online`
- `Connected family`

The row exists to explain when a descendant still belongs to trust history without quietly implying that it is alive enough for current convenience.

## Pattern: remembered-trust descendant-capability row

Use this pattern whenever a descendant still matters to remembered-trust convenience but current role eligibility is weaker than family membership or liveness.
A descendant-capability row should keep five items adjacent:

1. descendant identity
2. governed subject
3. candidate role
4. eligibility class
5. next honest action

Good examples:

- `desktop-ash · incoming:photos-2026 · approval-seat · eligible after proof · Require fresh approval`
- `tablet-citrine · photos/archive/2025 · byte-source · blocked no bytes · Mark explanation only`

Bad examples:

- `Known owner`
- `Available peer`
- `Can approve here`
- `Ready device`

The row exists to explain whether a descendant may actually act for a governed subject now, not merely that the device is linked, remembered, or probably online.


## Pattern: remembered-trust reuse-precedence row

Use this pattern whenever a governed subject may or may not inherit remembered approval convenience.
A reuse-precedence row should keep five items adjacent:

1. governed subject
2. standing reuse candidate
3. subject reuse policy
4. precedence outcome
5. next honest action

Good examples:

- `incoming:photos-2026 · memory match with descendant · fresh approval all peers · fresh approval required · Open approval review`
- `backup:quarterly-ledger · memory match · reuse known peers only · reuse after seat check · Narrow to reviewed seat`

Bad examples:

- `Already approved`
- `Known trusted peer`
- `Will auto-connect`
- `Can skip approval`

The row exists to explain when remembered approval is present but intentionally not decisive for this exact governed subject.


## Pattern: offer trust-promotion row

Use this pattern whenever a portable invitation's own lifetime and any later durable trust outcome could otherwise blur together.
An offer trust-promotion row should keep five items adjacent:

1. artifact posture
2. claim outcome
3. promotion posture
4. later reuse posture
5. next honest action

Good examples:

- `offer consumed · claim applied · subject only · fresh approval next time · Keep this subject only`
- `offer expired · claim applied · family reuse candidate · eligible after seat check · Open trust review`

Bad examples:

- `Invite used`
- `Already trusted now`
- `Known peer for later`
- `One-time link normalised`

The row exists to explain what durable trust, if any, survived the invitation itself, not merely that an old link was clicked successfully once.

## Pattern rule — keep `for`, `redeemed by`, and `trust survived` adjacent

Portable-offer surfaces must not collapse sender intent, actual redeemer, and resulting trust into one vague status chip.
Dense rows, review panes, and CLI summaries should preserve three adjacent labels in that order:

1. `For`
2. `Redeemed by`
3. `Trust survived`

Examples:

- good: `For Noah   Redeemed by tablet-lapis   Subject only   Review mismatch`
- bad: `Accepted   Approved before   Connected`

A surface that can tell who redeemed the offer but not whether that matched sender intent is incomplete.
A surface that can tell the mismatch existed but not what trust survived is also incomplete.


## Pattern 59 — partially consumed offers must render as ledgers, not as generic active links

Portable-offer surfaces must not collapse shared artifact budget and per-redeemer trust into one vague link state.

They should answer, in order:

1. how much budget the artifact had and has left
2. which ordered attempts matter
3. which attempts actually consumed budget
4. what trust survived from each successful attempt
5. whether the safe next action is to reissue instead of stretching the old artifact further

Bad compression:

- `Link active`
- `Used twice`
- `Accepted by 2 peers`

Good compression:

- `2/3 uses consumed`
- `Maya-phone subject only; Noah-laptop broader`
- `Next safe action: reissue new artifact`

## Pattern 60 — familiar redeemer attempts still need explicit slot treatment

Portable-offer surfaces must not collapse `same redeemer`, `same family`, and `same subject` into one vague budget outcome.

They should answer, in order:

1. what budget remains
2. which earlier attempt is the real comparison point
3. what the equivalence class is
4. what the slot effect is
5. whether reissue is safer than stretching the artifact again

Bad compression:

- `Already used by Maya`
- `Known peer`
- `Same person, continue`

Good compression:

- `1/2 consumed`
- `Compare: tablet-lapis #1`
- `Known peer, new subject`
- `Consumes slot 2 if approved`


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


## Revision addendum — received-via / preview / authority adjacency

Portable-offer surfaces should now follow one additional adjacency rule:

- **Received via**
- **Preview said**
- **Authoritative now**

should remain visually adjacent, with **External touch** immediately nearby when any browser, QR, mail, chat, or file-manager surface participated.

Good compression:

- `Browser auto-handoff`
- `Preview only`
- `Landing page saw wrapper only`
- `Locally inspected`

Bad compression:

- `Opened successfully`
- `Trusted link`
- `Verified by browser`


## Pattern 62 — carrier form must not stand in for canonical artifact identity

Portable-offer surfaces must not collapse wrapper URL, protocol URL, QR, copied text, and file wrapper into whichever one was seen most recently.

They should answer, in order:

1. what the canonical artifact is
2. which carrier is being shown now
3. what other aliases are known
4. whether the current carrier is authority-bearing or delivery-only
5. whether the safe next action is `same artifact`, `manual compare`, or `treat as successor`

Bad compression:

- `Same link`
- `Opened via QR`
- `Shared again`

Good compression:

- `Canonical offer off_01J...`
- `Current carrier: wrapper URL`
- `Other alias: protocol URL`
- `Delivery wrapper only`
- `Equivalence: same canonical artifact`
- `Next safe action: inspect canonical offer`


## Pattern 63 — preview familiarity must not masquerade as field authority

Portable-offer surfaces must not collapse `I saw the folder name and size already` into `the important fields are now known`.

They should answer, in order:

1. which facts were merely preview hints
2. which facts stayed sealed until local parse
3. which facts are authoritative now
4. which later actions may rely on those facts
5. what definitely may not be inferred yet

Bad compression:

- `Preview verified`
- `Looks right`
- `Known share`
- `Ready to connect`

Good compression:

- `Preview hint: label, approx size`
- `Sealed until parse: authority-bearing fields`
- `Authoritative now: artifact id, policy fields`
- `Still not enough: approval not yet granted`
- `Claim/budget review cites parsed fields only`


## Pattern 64 — familiar preview must not masquerade as governance sufficiency

Portable-offer surfaces must not collapse `I saw the right label and size` into `I know how this offer is governed`.

They should answer, in order:

1. what the preview showed
2. what governance-bearing facts are still missing
3. what the preview is enough for right now
4. what it is still not enough for
5. what the next honest action is

Bad compression:

- `Looks right`
- `Known share`
- `Ready to open`
- `Safe to continue`

Good compression:

- `Preview: label, approx size`
- `Missing: permissions, expiry`
- `Enough for: recognition`
- `Not enough for: approval`
- `Next: inspect locally`
