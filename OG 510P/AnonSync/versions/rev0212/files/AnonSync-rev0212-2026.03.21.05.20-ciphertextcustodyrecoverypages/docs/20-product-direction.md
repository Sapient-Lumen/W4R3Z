## Revision addendum — make opaque custody product-owned, not article-owned, after rev0211

The product direction should now treat ciphertext-only custody as another place where AnonSync must be **more explicit than Resilio, not less candid than Resilio**.

Near-term direction pressure:

- publish one ordinary admission page before landing ciphertext on a target root
- publish one ordinary custody page that states the hard capability ceiling of an opaque node
- publish one ordinary recovery page that ranks real recovery lanes by saved-material proof and database continuity
- publish one ordinary history-limit page that states when encrypted Archive is evidence only instead of live replay authority

Do not let `encrypted backup` collapse into optimistic folklore.
It is only trustworthy when target hygiene, capability ceiling, recovery prerequisites, and replay limits all remain explicit.

## Revision addendum — product direction after rev0210: target volume truth must be public product state

A serious sync product cannot treat filesystem and volume capability as hidden implementation trivia.
If shell/materialization affordances, metadata fidelity, or bundle semantics depend on NTFS versus FAT32, native xattrs versus fallback stubs, or stronger-versus-weaker target classes, that truth belongs on first-class product pages.

AnonSync should therefore publish:

- the current target volume class
- the strongest native primitives it actually supports
- whether metadata fidelity is native or fallback-backed
- whether a missing action reflects posture, client health, or a real target ceiling
- whether the honest next step is to keep degraded semantics, migrate the subject, or reformat the target

This is how the product avoids making operators learn storage truth from hidden `.sync` artifacts and support folklore.

## Revision addendum — product direction after rev0201: publication readiness must be first-class, not inferred

AnonSync should now commit to one more product-direction line:

- `Publish ready` is a first-class verdict, not a spinner the operator has to interpret.
- `Delay active` means the product states the rule, its origin, and the remaining countdown.
- `Manual repair suggested` means the product states whether bytes are unchanged and chronology would be advanced.
- `Priority active` means the product states whether order is inherited, frozen locally, constrained by the active queue, or only cosmetically misrendered.

This is a substantive product-shape decision, not wording polish.
The product should reserve explicit pages and compact-row chips for readiness and urgency instead of forcing the operator to infer them from support notes.

## Revision addendum — product direction after rev0199: capability posture must be first-class, not inferred

AnonSync should now commit to one more product-direction line:

- `Capability available` is a first-class verdict, not a button that merely happens to be visible.
- `Entitlement basis` means the operator can see whether a right is self-held, owner-inherited, shared-seat, family-scoped, or line-default.
- `Action gated` means the product states the exact blocking rule rather than hiding behind omission.
- `Pro-function lost` means the product states what narrowed, what live work is affected, and what bytes still survive.

This is a substantive product-shape decision, not wording polish.
The product should reserve explicit pages and compact-row chips for capability posture instead of forcing the operator to infer it from repeated feature footnotes or missing controls.


## Revision addendum — product direction after rev0192: verbs for byte presence must stay typed

AnonSync should now commit to one more product-direction line:

- `Fetch` means materialize bytes here under an explicit future-arrival policy.
- `Evict local copy` means reduce only this seat's byte presence while proving another full-copy floor still exists.
- `Detach subject` means stop local participation without pretending bytes were globally deleted.
- `Delete everywhere` means a reviewed authority-bearing mutation and must never hide behind a generic local delete gesture.
- `Restore from retained history` means a chronology-bearing replay decision, not merely browsing a hidden folder.

This is a substantive product-shape decision, not wording polish.
The product should reserve different verbs for different scopes even when another tool would collapse them into one context menu.

## Revision addendum — seat continuity and reset-impact truth after rev0191

Near-term product direction should now explicitly prefer:

- one exact answer for whether a seat is the same one, a reviewed successor, a foreign seat, or only stale roster residue
- one exact destructive review page whenever linking or repair would actually replace a certificate-bearing seat identity
- one exact roster page that distinguishes hidden-returnable rows, offline linked rows, duplicate reset artifacts, and retireable residue
- one exact reset-impact page that states what survives, what resets, and whether the operator is staying in the same storage world or entering a new one

The product should not let seat names, duplicate rows, or clean-install folklore partially own continuity truth.

## Revision addendum — approval visibility and approver-locus truth after rev0190

Near-term product direction should now explicitly prefer:

- one exact answer for whether a claimant is still pending because approval is outstanding, because the approver never saw the request, or because remembered trust should have auto-approved later
- one exact inspection page that states identity proof, fingerprint, claim lane, and resulting right before approval is granted
- one exact approver-locus page that names which linked seats may approve and what subject-presence floor makes that true
- one exact approval-memory page that states remembered-trust scope, reprompt triggers, and how to tighten the policy deliberately

The product should not let pending-folder icons, silent remembered certificates, or linked-seat folklore partially own approval truth.

## Revision addendum — grant-lifecycle truth after rev0189

Near-term product direction should now explicitly prefer:

- one exact answer for whether a requested access change is a true in-place mutation or a successor-grant epoch
- one exact register of live access-bearing artifacts and their current governance drift
- one exact revocation page that separates direct effect, descendant blast radius, and landed-byte residue
- one exact reissue plan whenever `remove and re-share` would otherwise hide a governance replacement ritual

The product should not let subject class, derivative lineage, or artifact-flow trivia partially own grant-lifecycle truth.

## Revision addendum — carrier-independent authority truth after rev0188

Near-term product direction should now explicitly prefer:

- one exact answer for what right a seat will gain before the seat joins
- one exact linked-family page that distinguishes `relationship` from `merged owner domain`
- one exact shareability page that distinguishes subject-class cliffs from current-seat ceilings
- one exact comparison page whenever lanes that look similar differ in approval, budget, or browser dependence

The product should not let linked-seat convenience, subject family, or carrier choice partially own authority truth.

## Revision addendum — current-surface action truth after rev0187

Near-term product direction should now explicitly prefer:

- one exact answer for whether an action is fully supported here, inspect-only here, handoffable here, or genuinely blocked here
- one exact diagnosis page whenever browser/app mismatch, hidden affordance, or direct-link failure could otherwise look like a policy denial
- one explicit reviewed handoff object whenever the safest continuation is in another channel
- one explicit resume page proving whether the target channel continued the same reviewed action or reopened broader review

The product should not let browser behavior, extension state, or missing buttons partially own action truth.

# Product direction

## One-sentence thesis

AnonSync is an **inspectable, scriptable, peer-to-peer sync system** for people who want strong control over trust, materialization, discovery, topology exposure, provenance, decision traces, projection policy, convergence evidence, diagnostic evidence, and recovery state.

## The product should feel like

- the clarity of a good Unix tool
- the practicality of a modern sync app
- the privacy posture of an encrypted replica system
- the predictability of an operator-friendly daemon
- a Linux-first headless system that does not apologize for knowing its primary environment

## The product should not feel like

- a black box that “usually works” until it doesn't
- a consumer cloud clone with P2P underneath
- a premature enterprise control plane
- a trust-expanding convenience layer that hides real authority changes

## Primary use cases

### 1) Personal device mesh

A user has desktop, laptop, phone, maybe a small server.
They want:

- easy linking
- on-demand files on constrained devices
- explicit local-vs-remote state
- simple troubleshooting
- explicit policy for whether linking implies future auto-grants
- the ability to keep one device read-only, mirrored, or cache-only without dropping into a second-class share model

### 2) Encrypted intermediary

A user wants to use an untrusted VPS, NAS, or borrowed machine as a transit/cache node that stores ciphertext only.

### 3) Small trusted team share

A small group wants a shared working set with controlled permissions and understandable sync policy, without adopting a central SaaS file platform.

### 4) Privacy-routed sync mesh

A user wants the default WAN posture to prefer privacy-preserving paths.
They want:

- Tor and I2P to be first-class supported route classes
- one delivered package that already contains the required transport components
- clear inspection of which path is active and why
- the option to mix overlay paths with LAN or approved direct paths deliberately, with route classes exposed by name
- faster clearnet direct as a manual override, not a silent default

### 5) LAN-only or known-host sync mesh

A user wants peer-to-peer sync that can be pinned to:

- local-network only
- a specific set of known hosts
- no relay use
- no tracker use

This should be a normal first-class policy choice, not a power-user scavenger hunt.

## The real product differentiator

Not merely:

- “open source Resilio”
- “private Syncthing”
- “yet another sync app”

But specifically:

> a sync system where trust, discovery, materialization, grants, provenance, recovery, and release compatibility are explicit objects with explicit policies and explicit diagnostics.

## The counter-model

The archive is now converging on a clearer counter-model to convenience-first sync tools:

- **linking** forms relationships, not mergers
- **profiles** install explicit policies, not hidden side effects
- **plans** preview mutations before they are committed
- **preflight reports** surface compatibility and downgrade risks before commitment
- **claims** separate visibility and offers from actual local acceptance
- **recovery bundles** make encrypted recovery prerequisites explicit and verifiable
- **diagnostic incidents and evidence bundles** make supportability scope, redaction posture, and export history explicit instead of hiding them in daemon folders
- **remembered trust** is a visible scope object with recall controls, not a convenience checkbox whose future consequences are discovered later
- **absent rows** declare return posture and removal scope explicitly instead of collapsing hidden, disconnected, offline, and removed into one visual class
- **control recovery** preserves runtime identity by default instead of equating lost credentials with settings reset or duplicate-seat side effects
- **control trust** distinguishes local bootstrap, temporary browser exception, trusted certificate, and remote exposure instead of outsourcing the meaning to browser warnings
- **artifact handoff** treats browser-open as an accelerator over one typed manual import lane, not as the only honest intake path
- **rate policy** lives on one effective ledger that names WAN caps, LAN exceptions, schedule windows, and non-rate side effects
- **installation receipts** separate package trust, elevation/network consent, runtime start, and control reachability instead of collapsing them into one “installed” event
- **repair ladders** expose ordered rungs and copy-safety truth instead of sending operators through restart/reconnect/re-add folklore
- **release posture** keeps version, channel, edition family, schema epoch, and rollback truth explicit instead of scattering them across update pages and release notes
- **incoming shares** become visible before they are adopted into local paths
- **seat capability floors** make storage class, background posture, and removable-storage ceilings explicit before constrained-seat bind
- **external edits** become explicit branch-and-return workflows, not copy ritual hidden under `open in another app` language
- **shell projections** accelerate actions but never become the sole semantic home of materialize/evict/share capability
- **suspended seats** rejoin through chronology-confidence review rather than silently carrying late-return precedence
- **path choice** is a per-share workflow, not a device-global linked-folder mode trick
- **path binding and relocation** are compared actions, not loose filesystem side effects
- **target preflight** classifies same-subject reuse, stale residue, and illegal duplicate bind before any local path mutation
- **file actions** distinguish fetch, local eviction, and share-wide delete
- **history and restore** are supported control surfaces, not hidden archive rituals
- **ignore rules, conflicts, and projection policies** are supported objects, not hidden control files, placeholder folklore, or magic filenames
- **portability contracts** make pathname, metadata, notification, and network-share fidelity explicit over time, not only at bind time
- **convergence reports** distinguish completion, degraded health, and settlement confidence instead of bundling them into one vague status line
- **recovery** is a normal workflow, not a support exception
- **device roles** preserve least privilege inside convenient personal meshes
- **status, explain, and audit** are product surfaces, not afterthoughts
- **decision traces** are supported objects, not inferences from icons, peer counts, or old troubleshooting notes
- **transport runtimes** are inspectable supported objects, not magical bundled background helpers
- **retirement records** distinguish hide, ignore, revoke, replace, and rotate instead of bundling them into one device-disconnect ritual
- **UI/CLI/API** are views of one model, not separate product tiers
- **same-machine derivation** is a first-class lineage model, not a local-share exception page
- **route narrowing** is a reviewed mutation with residue truth, not a toggle followed by cleanup folklore
- **capability uplift** is a reviewed kind migration, not remove-and-readd folklore
- **rights editing** is topology-aware and ceiling-aware, not a dropdown with unexplained missing options
- **path rehome** is a classified continuity workflow, not `Folder not found` followed by reconnect ritual
- **empty states after seat changes** are attributed local-world states, not automatic first-run assumptions
- **incident response and device retirement** are reviewed trust workflows, not unlink/regenerate/reinstall/reshare ritual
- **restore and reintroduction** keep candidate bytes, authorship, and blast radius together instead of splitting them across hidden archive folders and separate history lookup
- **membership presence** is a ledger with explicit live, hidden, retired, revoked, and successor states, not peer-count folklore plus list hygiene
- **snapshot send** is a bounded delivery subject, not a caveat-driven mini-share
- **storage pressure** is a filesystem-scoped ledger, not a warning pinned vaguely to a default arrival root
- **identity health** is a salvageable control-plane object, not unlink-or-reinstall folklore around hidden storage folders
- **host custody** is a visible path-claim contract, not a same-host collision discovered only after hidden service-state damage
- **compatibility gates** distinguish safe joins from reviewed migrations and blocked unsafe merges before any control plane is replaced


- **control listeners** are survivable exposure objects, not process-death traps bound to one interface by accident
- **same-host multi-instance runs** are reviewed namespaces, not extra processes that happen to remember different ports
- **capability envelopes** move by explicit entitlement review, not as side effects that silently starve another seat
- **headless artifact intake** is typed before action, not one generic `paste key or link` funnel
- **attention** is a graded delivery contract with recovery, not a bell plus OS-specific luck
- **entitlement changes** are reviewed capability-floor transitions, not silent workflow cliffs
- **upgrades** are visible cohort moves with known installability and restart cost, not startup-check folklore
- **diagnostics** are reviewed exports with redaction and destination mode, not hidden-log scavenger hunts

## Latest doctrine additions

### Latest addition — control exposure is not daemon identity

Widening or relocating a control listener may change who can reach the daemon.
It should not silently change whether the daemon is allowed to keep syncing if one network interface disappears.

### Latest addition — simultaneous runtimes need explicit namespaces

Running two live seats on one host is not just a convenience flag.
Ports, storage roots, identity roots, and local subject custody must be reserved and provable up front.

### Latest addition — feature entitlement is not subject authority

A capability owner transfer, premium-seat reassignment, or other entitlement move should never masquerade as subject trust repair, data revocation, or owner-domain mutation.

### Latest addition — imported artifacts must be typed before action

A pasted token, a protocol URL, a seat grant, and a subject offer may all arrive as strings or files.
The product should classify them first, then route them into the correct reviewed lane.

### Latest addition — attention is a graded delivery contract

An event existing in the model does not prove it reached a person.
Attention should state delivery grade, suppression factors, and missed-event recovery explicitly instead of hiding that truth behind bells, trays, and OS-specific notification behavior.

### Latest addition — entitlement loss is a reviewed capability-floor change

Trial, license, or seat changes may narrow what a runtime can actively do.
They should not silently rewrite subject history or leave live workflows to fail without one continuity review.

### Latest addition — upgrade truth belongs on one seat-local page

A seat should be able to see whether a newer compatible build exists, whether it is actually eligible to receive it here, and what restart/re-entry cost applies.
The product should not require desktop-only checks, website lore, or WebUI omissions to answer that question.

### Latest addition — diagnostics are reviewed exports, not hidden-file ritual

Troubleshooting evidence should be collectible, redactable, and exportable from the product itself.
Operators should not have to discover support boundaries and hidden storage paths before they can create a useful evidence packet.

### Latest addition — support packets are frozen disclosures, not live evidence

A reviewed local evidence store and a recipient-specific outbound packet are different objects with different authority.
AnonSync should normalize `held-unsent` state and require one frozen manifest, one redaction pass, and one disclosure receipt before anything leaves the machine.

### Latest addition — outside blockers need follow-up handles and return proof

When the next honest step leaves the product for a browser page, OS dialog, shell, vendor queue, or admin console, that detour must become a tracked object.
AnonSync should publish what was delegated outward, what return is expected, and what proof shows the operator actually came back with the blocker resolved or still pending.

### Latest addition — live external sources are not frozen review basis

A help-center URL, forum thread, ticket permalink, or teammate paste may remain the convenience entry point for follow-up.
It should not be the thing local review and translation actually point at.
AnonSync should preserve the live locator, the fetched snapshot, the exact frozen basis excerpts, and later drift checks as separate objects so mutable outside text never rewrites what the operator really approved.

### Latest addition — reviewed intent is scoped to its expected basis

A reviewed draft, packet, queue-worthy action, or apply-ready mutation is not generic approval for whatever later became current.
AnonSync should preserve the expected basis rows, current comparison, stale-attempt truth, and explicit reissue path so later drift never turns older review into ambient latestness.

### Latest addition — recipient target is part of reviewed basis when the action is target-scoped

A reviewed recipient-specific packet issue, offer issue, or refresh note is not generic permission for whatever later destination the operator happens to pick.
AnonSync should preserve expected-target rows, current target comparison, stale-target truth, and explicit retarget reissue so later recipient drift never turns older review into ambient send authority.

### Latest addition — current shareable head is not the same object as the current outward surface

A newer frozen head may already be ready for reuse, and a queued send may already exist, while an older issued artifact is still the one a recipient or audience should be assumed to have right now.
AnonSync should preserve current shareable head, queued issue item, executed issue event, current issued head, and later delivery witness as separate objects so `ready` or `queued` never impersonates `currently outwardly in force`.

### Latest addition — same-thread continuity is not exact acknowledgment

An imported reply, ticket comment, or read/open signal may prove that someone responded in the right conversational lane.
It should not silently prove which exact artifact, correction notice, or replacement artifact they acknowledged.
AnonSync should preserve sender match, conversation continuity, acknowledged object kind, and stronger same-product proof separately so `recipient acknowledged` stops being one mushy status chip.

### Latest addition — latest reply in the lane is not automatically the current operative answer

Once imported reply truth can already classify object exactness, actor scope, authorship, stance, and referent coverage, the product still needs one compact answer to which reply is currently operative now.
AnonSync should preserve latest arrival, current whole-artifact head, current subset heads, superseded older replies, and contradiction warnings separately so the bottom-most message in a thread never impersonates current whole-packet meaning by accident.


## Product boundaries

### What AnonSync is willing to optimize for

- operator comprehension
- explicit security/trust boundaries
- automation-friendly surfaces
- personal and small-team workflows
- reversible, inspectable state changes

### What AnonSync is not trying to optimize for first

- maximum invisible convenience at any semantic cost
- central control-plane features for fleets
- “just clone every Resilio behavior” parity work
- every platform integration before the core model is stable

## Product doctrine

### Doctrine 1 — visible states matter

Resilio is right that users need to see whether a device/share is detached, selective, or full.
That insight stays.

### Doctrine 2 — explicit trust beats implicit trust expansion

Linking devices should make relationships easier.
It should not silently imply that every linked device now has owner-equivalent power or universal share visibility.

### Doctrine 3 — network behavior is policy

Tracker use, relay use, LAN multicast, known-host pinning, endpoint caching, and address publication are not implementation trivia.
They are user-relevant policy and must be inspectable.

### Doctrine 4 — recovery is a product feature

Replacing hardware, moving state, exporting backups, rotating identity, or repairing trust graphs should be explicit supported workflows.

### Doctrine 5 — UI is downstream of the control surface

A future web UI or TUI should sit on top of the same object model, APIs, and event stream used by the CLI.
If the CLI cannot explain something, the UI should not hide that fact.

### Doctrine 6 — convenience must be decomposable

If AnonSync offers “easy mode” behaviors such as linking, auto-grants, or default selective mounts, those must compile down to explicit policy objects the user can inspect, revoke, and script.

### Doctrine 7 — observability is not optional

A serious sync product must expose:

- why a peer is unreachable
- why a file is blocked
- what transport path is in use
- whether only encrypted copies exist
- what policy or recovery event changed the current state

Otherwise operators will reinvent the missing model in guesswork.

### Doctrine 8 — provenance is part of usability

For high-signal state, users should be able to ask not just “what is true now?” but also “why is it true now?”
That means plans, policies, grants, recovery actions, and route changes should all leave durable explanatory traces.

### Doctrine 9 — visibility and path adoption are separate

A share becoming visible through linking or policy should not automatically create a folder in some default location.
Visibility should land in an explicit incoming/adoption surface where the operator can:

- inspect provenance
- choose a path
- choose a mount/materialization mode
- reject or defer adoption

### Doctrine 10 — local eviction and replicated delete are different actions

Materialization controls save space; replicated delete changes shared state.
Those must not collapse into one ambiguous action.
If the product supports both, the interface should make scope explicit.

### Doctrine 11 — restore should be a normal operator workflow

A sync product already owns replicated state, deletion semantics, and recovery metadata.
So earlier versions and deleted copies should not be recoverable only by browsing hidden directories and copying files around by hand.
Operators should be able to:

- inspect candidate file versions
- restore locally without affecting the share
- intentionally restore back into the share with explicit scope
- see audit and event records for the restore action

### Doctrine 12 — capability uplift must preserve continuity honestly

Stronger subject kinds or richer governance features may exist.
They should arrive through reviewed kind migration that says exactly what continuity survives, not through remove-and-readd ritual.

### Doctrine 13 — rights editors must explain ceilings, not merely hide blocked options

If a subject cannot receive a stronger right because of topology, substrate, or acting-seat limits, the product should say so directly and show dependent fallout.

### Doctrine 14 — path movement is continuity work, not just filesystem work

Rename, same-root move, cross-root rehome, and broken-path repair are different truths.
The interface should classify them before claiming continuity.

### Doctrine 15 — empty state must be attributed before it is acted on

A local web or service seat that looks empty may be opening a different root, an unreachable root, or a true empty root.
The product should classify that before inviting new setup.

### Doctrine 16 — hidden service files are implementation detail, not product contract

Ignore lists, archive/version stores, and other service artifacts may exist internally, but operators should not have to edit or protect hidden control files just to use the product safely.
The product surface should expose:

- effective ignore rules
- drift and consistency state
- service-file damage as health findings
- repair paths when internal metadata is missing or unhealthy

### Doctrine 13 — bind preflight should classify collision before mutation

Path selection is not a boring file-picker detail.
A target can mean `safe empty path`, `same-subject reuse`, `other-subject collision`, `stale residue`, or `illegal recursive overlap`.
The product should classify those cases before bind instead of throwing one generic duplicate error afterward.

### Doctrine 14 — conflicts should be explicit cases, not magic filenames

Conflicts are normal events in a replicated system.
They should be inspectable and resolvable through supported object surfaces with stable IDs, visible candidates, explicit blast radius, and audit records.
A user should never need to memorize which special filename is safe or unsafe to delete just to resolve an ordinary sync conflict.



### Doctrine 15 — same-machine convenience must preserve lineage truth

If the product supports local same-machine derivatives, it should show:

- source versus child identity
- rights ceiling versus local materialization
- loop safety
- reattach versus recreate

It should not rely on grayed-out options or exception docs to teach those rules.

### Doctrine 16 — convenience must preserve least privilege

A personal-device mesh should not force a binary choice between:

- convenience linking with owner-like power everywhere
- manual weak-mode workarounds just to keep one device read-only

AnonSync should support convenient linking plus explicit per-device/per-share roles inside one coherent model.

### Doctrine 15 — compatibility is part of the trust boundary

Version-family mismatch, capability mismatch, feature downgrade, or policy incompatibility are not mere installation details.
They are part of whether an operation is safe to accept.
So link/share/adopt flows should expose supported preflight reports before commitment.

### Doctrine 16 — visibility, offer, and claim are distinct states

A share or device relationship can become visible before it is locally accepted.
An invite can be inspected before it is claimed.
A claim can be reviewed before it mutates paths, grants, or linked-group membership.

AnonSync should therefore keep these states separate:

- visible / offered
- claimed / reviewed
- adopted / applied

### Doctrine 17 — “my devices” is a convenience boundary, not an authority merger

A personal constellation may share defaults, discovery convenience, and reviewed approval ergonomics.
It should not silently mean that every member sees every share the same way, has owner-like mutation or re-share power, or can widen future approvals across the whole constellation without an explicit authority-domain record.

That yields a more legible audit trail and avoids collapsing awareness into authority.

### Doctrine 16b — delivery encoding must not stand in for authority semantics

A QR code, copied link, saved file, or local handoff may be convenient delivery forms, but they should not silently alter what authority is being offered.
Operators should be able to inspect one normalized offer manifest and one later claim receipt regardless of encoding.

That means the product should expose:

- one offer-artifact object model across file / URI / QR / clipboard delivery
- explicit expiry, redemption budget, and redelegation policy
- explicit peer pinning and approval posture
- durable receipts for later offer consumption or revocation

### Doctrine 17 — recovery readiness should be inspectable before disaster

A sync product should not wait for failure before revealing that its encrypted-recovery story depends on hidden state.
Operators should be able to export, inspect, and verify recovery material ahead of time.

That means the product should expose:

- recovery bundles with clear contents and scope
- sufficiency checks for offline decrypt and device replacement workflows
- explicit warnings when recovery posture has degraded
- ordinary audit/event records when recovery material is exported or rotated
- explicit custody and invalidation posture so operators can tell whether a bundle is portable, split-secret, or still daemon-bound
- durable receipts when recovery material is exported, re-verified, invalidated, or consumed

### Doctrine 18 — approval memory must be explicit, scoped, and revocable

“Approve once” can be a good convenience feature, but only if it compiles down to explicit supported state rather than sticky folklore.
Operators should be able to inspect:

- who is pre-approved
- for what future shares or share classes
- which local devices may exercise that approval
- what maximum role or permission the approval can imply
- when it expires, was consumed, or was revoked

That is how AnonSync keeps convenience without inheriting remembered ambient trust.

### Doctrine 19 — share identity and local path binding are separate things

A share label, a share ID, and a local directory path are related, but they are not the same object.
Operators should be able to:

- rename a local mount path without pretending the share itself changed name everywhere
- inspect whether a target path is already bound to this share, another share, or no share at all
- compare a non-empty target path before adopting or relocating a mount into it
- review collision policy instead of inheriting timestamp-win folklore

That means path adoption and relocation should be explicit compared actions, not implicit filesystem rituals.

### Doctrine 20 — publication and routing are separate decisions

A route policy that says only “tracker on/off, relay on/off, LAN on/off” is not explicit enough.
Operators need to distinguish at least:

- what this device will publish about reachability
- which infrastructure may learn that publication
- which targets the daemon may dial proactively
- which fallback steps are allowed if the preferred path fails

Otherwise privacy-relevant metadata disclosure remains bundled inside convenience routing.

### Doctrine 20a — disclosure needs audience, fact-class, and residue truth

A serious disclosure surface should answer more than `LAN on/off` or `tracker on/off`.
Operators should be able to inspect:

- which audience classes can currently learn anything
- whether the learned fact is identity, share-membership, endpoint, or relay-reachability information
- which mechanisms produce that disclosure
- whether a narrowing change only stops future publication or also clears old residue

That is how AnonSync avoids turning disclosure into tracker/relay folklore.

### Doctrine 21 — temporary overrides are leases, not silent policy edits

Operators need short-lived control for maintenance, metered links, shutdown drains, and incident response.
That does **not** mean the product should silently rewrite long-lived share or route policy.

A good control surface should make it obvious:

- which behavior comes from durable policy
- which behavior comes from an active temporary override
- what the override changes exactly
- when it expires automatically
- what baseline state returns after expiry

That is how AnonSync keeps maintenance intent legible without turning every pause button into hidden configuration drift.

### Doctrine 22 — destructive mutations need preservation reports

A user deciding between evicting local bytes, removing a local copy, deleting from the share, or restoring back into shared state should not have to infer recoverability from menu wording, hidden archives, or power-user toggles.

A good interface should make visible before apply:

- what will remain locally after the action
- whether any known plaintext replicas remain elsewhere
- whether the remaining copies are only encrypted replicas
- whether history/versioning can recover the path and with what retention limits
- whether the system considers the action low-risk, guarded, high-risk, or blocked

That is how AnonSync keeps destructive intent explicit without requiring users to memorize product folklore.

### Doctrine 23 — retirement is trust state, not list hygiene

A sync mesh accumulates dead laptops, renamed phones, reinstalled servers, stolen devices, and old identities.
A serious product should not treat all of those as variants of “remove this thing from the list.”

AnonSync should make distinct and inspectable:

- cosmetic hiding
- ignored future contact
- trust revocation
- successor replacement
- identity rotation

That is how the product stays clear about what continuity survives and what authority is truly gone.

### Doctrine 24 — share governance is a first-class contract

A serious sync product should not hide share stewardship inside one overloaded permission bit.
Data mutation, grant authority, delegation bounds, and succession should be inspectable as separate state.
That means operators should be able to review who can hand a share off, under what conditions, and with what surviving limits.


### Doctrine 25 — permission, propagation, and local-deviation remediation are separate decisions

A serious sync product should not hide read-only behavior behind one overloaded checkbox or share-type special case.
Whether a device may authoritatively write, whether its local edits propagate, and what happens after accidental local edits are three different questions.

AnonSync should therefore expose local-deviation policy explicitly for non-authoritative roles and mounts.
Operators should be able to choose and inspect whether accidental local adds, edits, and deletes are preserved, quarantined, auto-reverted, or blocked pending review.
That is how the product avoids forcing users to learn a matrix of share-type caveats just to answer “what happens if someone edits the read-only copy?”


### Doctrine 26 — filesystem semantics are part of share compatibility

A share is not actually compatible with a mount target unless pathname and metadata semantics are understood.
Operators should be able to inspect at least:

- case-sensitivity posture
- Unicode normalization posture
- prohibited-name or prohibited-character risk
- symlink / junction / special-file handling
- xattr / ACL / permission fidelity
- timestamp and clock-safety findings relevant to sync correctness

That means filesystem compatibility cannot remain a support-only topic or a bag of hidden advanced toggles.
It belongs in preflight, explain, doctor, and effective-state surfaces.

### Doctrine 27 — namespace projection is distinct from ignore and materialization

A path can be:

- part of the share namespace peers learn about
- suppressed from share announcement
- visible on one mount as a placeholder or metadata-only entry
- omitted from another mount entirely
- already materialized locally even after tighter rules are proposed

Those are different outcomes and they should not collapse into one overloaded “ignore” concept.
Operators should be able to inspect:

- whether a rule changes share-wide namespace announcement or only a local mount view
- whether a matched path is omitted, placeholder-visible, metadata-only, or fully materialized locally
- whether tightening a rule later leaves already-indexed structure visible until review
- whether existing local bytes are preserved, evicted safely, or blocked pending review

That is how AnonSync avoids a model where “ignore later stops bytes but not structure” remains support-article knowledge.

### Doctrine 28 — settlement confidence is distinct from completion

A sync product should not make operators infer "safe to trust as settled" from one overloaded status view.
A share may have no currently queued bytes and still be untrustworthy as a cutover point because:

- source peers are missing
- watcher exhaustion means new local changes are only discovered on periodic rescan
- excessive clock skew blocks freshness comparison
- hidden merge / hash / dedup work is still in progress
- local or remote state is only partially known

AnonSync should therefore expose convergence as first-class supported state.
Operators should be able to inspect:

- transfer completion
- source availability
- scan / watcher health
- clock-confidence findings
- whether the daemon considers the share merely idle, fully converged, or converged with degraded confidence
- what readiness rule is being applied for cutover, backup, restore, or maintenance, and whether that rule is satisfied, waiting, stale, or blocked
- whether a later action receipt can prove which readiness answer was accepted

That is how the product avoids turning cutover, backup, and recovery readiness into status-column guesswork.


### Doctrine 29 — anonymity transports are first-class engines, not proxy afterthoughts

If Tor and I2P matter to the product thesis, they cannot live only as “configure an external proxy somehow.”
AnonSync should treat them as supported transport engines with:

- explicit runtime state
- explicit route-class participation
- explicit health and bootstrap reporting
- explicit policy/fallback semantics

That is how the product stays honest about what privacy-routed operation actually means.

### Doctrine 30 — clearnet direct is a manual speed override, not the default WAN path

Direct IP-to-IP can be useful.
It can also silently widen exposure if it is the default path whenever it happens to work.

AnonSync should therefore make a sharp distinction between:

- normal LAN direct allowed by local policy
- overlay-first WAN routing through Tor and/or I2P
- deliberately enabled clearnet direct for a trusted peer, share, or maintenance window

The interface should say clearly when the operator has chosen speed over overlay privacy.

### Doctrine 31 — Linux is the first-class operating environment

The project does not need to pretend every desktop OS is equally important on day one.
A serious v1 can be Linux-first on purpose.

That means design quality should center on:

- headless daemon operation
- Linux watcher and service-manager realities
- common Linux filesystem semantics
- explicit support tiers for ext4, xfs, and btrfs before broader platform spread
- correctness on Linux before convenience parity elsewhere

Other platforms can remain future work instead of distorting the primary model too early.

### Doctrine 32 — bundled privacy transports still need public runtime contracts

Shipping Tor and I2P inside the product does not excuse hiding them.
If the daemon bundles those capabilities, the operator should still be able to inspect:

- which runtime is present
- how it was activated
- where ephemeral runtime state lives
- whether current routes depend on long-lived transport sessions
- why the daemon considered an engine ready, degraded, or unavailable

That is how AnonSync avoids replacing “external proxy folklore” with “embedded binary folklore.”

### Doctrine 33 — Linux filesystem support must be tiered, not implied

“Linux-first” should not mean “we hope the usual filesystems work.”
It should mean the project publishes which environments are:

- first-class and strongly supported
- acceptable with warnings
- best effort only
- blocked for sensitive workflows

That lets operators reason about correctness before adoption instead of after conflicts or metadata surprise.


### Doctrine 34 — bundled privacy runtimes need inspectable provenance

If AnonSync ships Tor or I2P support inside the product artifact, operators should still be able to inspect:

- which implementation is present
- whether it is compiled in or carried as an embedded payload
- which version, digest, and signer/provenance facts the daemon believes
- where persistent router/runtime state lives
- whether runtime updates arrive only through daemon releases or through some other channel

That keeps bundled privacy support from turning into a black box.

### Doctrine 35 — temporary speed wins must remain visibly temporary

There are real cases where a user will want faster clearnet direct transport for a trusted bulk transfer.
That does **not** justify making public direct the ambient WAN default.

AnonSync should therefore treat speed exceptions as leased overrides with:

- explicit scope
- explicit reason
- explicit expiry
- explicit visibility in status, route, audit, and explain surfaces

That is how the product can acknowledge practical speed pressure without quietly abandoning its default privacy posture.

### Doctrine 36 — Linux-only v1 is a respectable product decision

The project does not need to burn time pretending v1 is cross-platform if the serious operator contract is still stabilizing.
For now, the archive should be comfortable saying:

- Linux is the real v1 platform
- Windows/macOS are deferred work, not hidden promises
- Unix-style local control surfaces are the primary administration path
- other platforms should not distort route, path, metadata, or daemon-lifecycle design before Linux semantics are solid

### Doctrine 37 — filesystem portability is a durable contract

A preflight warning is not enough if the mount will live for months and later drift under it.
Filesystem semantics should therefore stay visible as an ongoing contract:

- each important mount should publish a fidelity contract
- portable-subset rewrite/drop behavior should be explicit policy, not silent accommodation
- weakened notification posture, network-share backing, permission loss, or filesystem-type drift should surface as drift against that contract
- accepted downgrade should emit a receipt that later audit can show plainly

That is how AnonSync avoids a model where SMB caveats, symlink rules, xattr control files, and repair rituals stay trapped in support lore instead of product state.

### Doctrine 38 — storage pressure is a budget contract

A low-disk warning is not enough if the operator still cannot tell whether the problem is materialized bytes, retention growth, temp remnants, or daemon/service state.
Storage semantics should therefore stay visible as an ongoing budget contract:

- each important device, state root, share, and mount should publish a space ledger by byte class
- pressure thresholds and automatic trim behavior should be explicit policy, not hidden power-user folklore
- reclaim should stay visibly separate from replicated delete and from retention trimming
- accepted reclaim or retention tradeoffs should emit receipts that later audit can show plainly

That is how AnonSync avoids a model where placeholder lore, hidden Archive growth, storage-folder cleanup, and temp-remnant repair steps stay trapped in support articles instead of product state.

### Doctrine 39 — transfer speed should be an explainable budget, not a mixture of charts and hidden knobs

Operators will absolutely care about throughput.
What they should not need to do is triangulate among a peer icon, a speed chart, a relay help page, a LAN-only caveat, a priority setting, and a hidden delay file just to answer why one transfer is slow or suspended.

AnonSync should therefore treat transfer behavior as an explicit contract with:

- visible route class and preferred alternatives
- visible durable transfer policy versus temporary throughput budget
- visible queue lane, fairness posture, and suspension cause
- visible relay-cost posture and metered exemptions
- receipts for temporary budget changes and scheduled caps

That is how the product can acknowledge real throughput needs without making “speed tuning” a second hidden control plane.

### Doctrine 40 — attention is a contract, not a mixture of badges, logs, and client-specific notifications

A serious control surface should not make operators reconstruct urgency from whichever channel happened to surface first.
A report is semantic truth.
A review lane is workbench placement.
A toast, system notification, webhook, or browser prompt is only delivery.
An acknowledgement or snooze is a separate durable intervention that should not silently resolve the underlying subject.

So the product should expose:

- explicit attention policy that maps report classes and severities into lane and delivery choices
- durable attention events that say what was delivered where and why
- acknowledgement and snooze receipts that distinguish presentation-only change from subject resolution
- headless-safe delivery parity so Linux-first deployments do not lose meaning just because they lack a tray or desktop shell
- visible delivery failure and deduplication state instead of one best-effort notification illusion

That is how the product can stay quiet without becoming vague, and multi-surface without becoming several different products.

## Product conclusion

AnonSync should be **narrower than Resilio**, **more explicit than most GUI-first sync tools**, **overlay-first by default on WAN links**, **honest about bundled privacy runtimes, temporary direct-speed leases, durable filesystem-fidelity contracts, durable storage-budget contracts, and durable transfer-budget contracts, durable attention-policy contracts, and durable policy-origin contracts**, and **Linux-only for v1 in a concrete filesystem-aware way**.
That is a credible reason for the project to exist.

## Platform scope reminder

Linux is the first-class operating environment for v1.
Windows and macOS parity are explicitly out of scope until the Linux control-plane, filesystem, and bundled-transport contract feel boringly solid.


### Doctrine 41 — control-plane access is a contract, not a mixture of bind addresses, browser warnings, and cookie ritual

A Linux-first product that expects serious daemon use cannot let “who can control me right now?” dissolve into WebUI listen settings, config-file passwords, self-signed-browser prompts, or reverse-proxy folklore.

AnonSync should therefore publish endpoint exposure, token issuance, session scope, proxy posture, and access revocation as first-class inspectable state.
Local IPC should remain the primary administrative surface.
Leaving localhost should be a reviewed exposure change with explicit receipts, not a casual bind tweak.


### Doctrine 42 — release truth is a product surface, not package-manager folklore

A serious sync product cannot leave upgrade safety to “a newer build exists” plus release-note archaeology.
Operators should be able to inspect:

- current version, edition family, channel, and schema epoch
- whether a peer constellation is uniform or carries meaningful skew
- what a proposed upgrade would preserve, block, or narrow
- whether rollback is supported, guarded, or explicitly not promised

That does not mean AnonSync needs to own every installation path.
It does mean the compatibility boundary must be first-class in the shared model.


### Doctrine 43 — effective policy is a contract, not settings-layer archaeology

A serious sync product cannot leave effective behavior trapped inside one global preferences page, one per-share preferences page, one power-user JSON table, one startup config file, and one remembered “I reset that once” superstition.
Operators should be able to inspect:

- which defaults profile or policy binding governs this subject now
- which fields are inheriting versus intentionally pinned
- whether a temporary override or schedule is affecting only the current effective value
- what a defaults/profile change would actually touch before apply
- which receipt proves that a subject returned to inheritance or detached from it

That does not mean every knob should become equally prominent.
It does mean precedence, origin, and reset semantics have to be first-class in the shared model.


### Doctrine 44 — temporary exceptions are leases, not cleanup folklore

A serious sync product cannot leave short-lived risky posture trapped inside scheduler cells, debug toggles, power-user keys, config edits, or remembered “set this back later” ritual.
Operators should be able to inspect:

- what baseline a temporary exception is modifying
- what effect is active now
- what ends the exception (time, byte budget, success, or explicit cancel)
- whether overlapping exceptions interact in surprising ways
- which receipt proves the exception expired, exhausted, renewed, or became durable policy

That does not mean every convenience action needs ceremony.
It does mean temporary intent has to be first-class in the shared model instead of hiding inside cleanup memory.


### Doctrine 45 — exit is a contract, not removal folklore

If entry, trust, route policy, recovery, and disclosure are explicit but departure is still one overloaded family of `remove` buttons, the product is not actually honest.

AnonSync should make every removal-style action answer five questions:

- what authority ends
- what visibility/publication ends
- what bytes or retained history remain
- what continuity is preserved intentionally
- what residue still remains and why

That means `hide`, `detach`, `ignore`, `revoke`, `replace`, `decommission`, and `erase-local-residue` should remain distinct intents even when the UI chooses to present them from the same page.

The operator should never have to learn from support lore that one action merely cleaned up a list, another revoked future trust, a third preserved recovery bundles, and a fourth deleted local archive bytes while leaving remote copies intact.


### Doctrine 16 — interface shell is part of the trust boundary

A shell that loses subject, proof, or queue context at the wrong moment is not just awkward.
It changes operator judgment.
So the persistent frame, subject header, proof panel, and action tray are part of the product's safety model, not decorative layout.

### Doctrine 17 — every effective value must explain its source

A displayed value is only half an answer.
For non-trivial policy and runtime state, the product should also show:

- whether the value is inheriting
- what baseline or parent it inherits from
- whether a local pin, exception, temporary lease, or copied-static profile broke inheritance
- what would happen if the baseline changed tomorrow
- how to rejoin baseline cleanly

### Doctrine 18 — speed features must preserve reviewable scope

Search, command palette, shortcuts, and bulk actions are welcome.
But if they allow trust-expanding, destructive, or topology-changing work, they must still compile into reviewable objects with explicit scope, proof, and receipts.
Fast access is good.
Hidden apply is not.


### Doctrine 19 — edit intent must choose an instrument before it chooses a value

A serious sync product cannot let `change this` silently mean any one of: edit the baseline, pin this subject, create a temporary override, create a durable exception, or restore inheritance.
Those are different acts with different future consequences.
Operators should be able to inspect:

- what source state they are changing away from
- what mutation instrument they are choosing
- what scope that instrument touches now
- what future parent changes will or will not flow through afterward
- what receipt or review object will prove the resulting posture

That does not mean every trivial low-risk local tweak needs ceremony.
It does mean semantic edits need an intent-first editor instead of raw field mutation.

### Doctrine 20 — projection parity is part of the product contract

A Linux-first sync product cannot treat local web, CLI, TUI, and richer GUI as separate semantic worlds.
Operators should not need support ritual to learn that one projection can explain a subject, another can create a draft, and a third is the only place where apply is visible.
The product should be able to say clearly:

- what every projection can read
- what every projection can explain
- what every projection can draft
- what a given projection can or cannot apply and why
- what handoff preserves continuity when execution really must continue elsewhere

That does not require identical visuals.
It does require one capability contract.

### Doctrine 46 — reviewed drafts still need a reviewed commit barrier

A good draft is necessary but not sufficient.
The last step before apply must still answer:

- what will change right now
- what becomes hard to undo
- what continuity claim the product will make afterward
- what receipts or successor objects will exist immediately after apply

Otherwise the product still hides too much meaning in a final button press.

### Doctrine 47 — reconnect and repair should preserve path continuity honestly

When a share reappears, that does not automatically answer:

- whether it should bind again at the old path
- whether the old path still exists
- whether current bytes there are the right bytes
- whether a new path would create a duplicate namespace

So reconnect, adopt, rebind, and path repair should be reviewed comparison workflows, not default-location ritual.

### Doctrine 48 — Linux-first means local web is primary, not merely available

If Linux and service installs commonly begin in a local browser, then first-run auth, empty-state teaching, draft review, explanation, and apply quality must already be first-class there.
A reachable web page is not enough.

### Doctrine 49 — narrow surfaces may compress layout, not provenance

A dense table, narrow pane, or mobile-width screen may hide secondary ornament.
It may not hide:

- source of truth
- scope of effect
- future baseline behavior
- blocker reason
- draft/apply consequence

Compression is acceptable.
Semantic erosion is not.

### Doctrine 50 — reconnect, claim, and bind should stay separate truths

A share may be visible here, claimable here, remembered here, or safely bindable here without those all being the same fact.
The interface should therefore keep distinct answers for:

- visible here
- claimed here
- remembered path here
- safe bind here now
- continuity restored here

If those truths collapse into one overloaded `Connect` affordance, the product will recreate exactly the path folklore it is trying to escape.


### Doctrine 51 — delivery encoding is not authority semantics

A file, URI, QR code, or clipboard payload is only the wrapper.
The operator should first be able to see the offered capability, redelegation posture, approval rules, and expiry semantics before picking how that capability is delivered.

### Doctrine 52 — browser preview is not local acceptance

Opening a link or scanning a QR code may preview a portable artifact.
It must not be the only semantic boundary standing between `I inspected something` and `this machine accepted something`.

### Doctrine 53 — one property deserves one effective-truth surface

If a value can be influenced by subject policy, seat defaults, machine defaults, rollout config, and temporary override, the product should still expose one canonical layer stack rather than send the operator through several settings families.

### Doctrine 54 — standing defaults may suggest, not silently bind

Machine or seat defaults may group, prioritize, pre-stage, or suggest paths for future arrivals.
They must not become the hidden explanation for why one specific share bound where it did or why a whole-device mode had to change before one share could be placed safely.


### Doctrine 32 — compromise response is trust-boundary work, not reinstall folklore

A sync product should not wait until a device is stolen to reveal that the practical response is `unlink everything, regenerate identity, reinstall, and reshare`.
Operators should be able to inspect and choose among:

- cosmetic hide
- operational quarantine
- trust revocation
- successor replacement
- authority rotation
- full continuity rebuild

That is how AnonSync keeps incident response legible without flattening every risky device event into teardown ritual.

### Doctrine 33 — restore must keep bytes, provenance, and blast radius together

Recovery is not complete when the product can point at hidden historical bytes.
A serious product should keep three answers together on one restore surface:

- which candidate bytes exist
- who or what last changed the path, when known
- whether reintroduction is local-only, forked, or share-visible

That is how AnonSync avoids a model where successful restore still depends on hidden service folders and remembered support caveats.

### Doctrine 34 — membership presence is not list hygiene

A member can be reachable, offline, hidden, retired, revoked, or replaced, and those are not cosmetic variants of one state.
A serious product should keep presence, trust, and visibility separate enough that a returning device is a classified event instead of a surprise contradiction of what `hidden` seemed to mean.

### Doctrine 35 — snapshot transfer is not a live share in miniature

Fast one-time delivery is worth supporting.
But a snapshot send is not a shared subject with ongoing source continuity.
The product should say explicitly:

- which bytes were captured
- what expiry and redemption budget govern the artifact
- whether downstream resharing is allowed and how lineage is preserved
- whether removing UI state also removes local bytes

That is how AnonSync keeps convenience handoffs honest without turning them into ambiguous semi-shares.
### Doctrine 55 — hidden service state must not be the public contract

Hidden folders, marker files, stream allowlists, and other daemon artifacts may exist internally.
They must never be the only place where operator-meaningful policy, identity, or repair truth lives.
A serious product should surface those meanings on one visible rule/service-state ledger and classify whether repair preserved or forked continuity.

### Doctrine 56 — warning-tier targets need steady-state truth, not setup-time warnings

If a target is allowed but weaker — for example because notifications degrade, outsider writers can bypass coordination, or some entry classes are blocked — the product should keep that weakness visible after bind day.
The operator should be able to answer what semantics are promised here now, what drift has occurred, and what is merely tolerated.

### Doctrine 57 — nested subtree sharing is a graph decision, not an ordinary publish action

A child subtree inside a parent subject changes propagation, transit, indexing cost, and admissibility.
The product should therefore review nested topology explicitly instead of teaching it through side effects and support caveats.

### Doctrine 58 — one-way rights, local divergence, and relay role are separate truths

A member that may not write upstream can still have local edits, local forks, restore policy, and even some relay/seeding capability.
The product should not compress those into one overloaded `Read only` badge.

### Doctrine 59 — portability collisions are not filename trivia

Case-folding, normalization, invalid-symbol, reserved-name, and path-length failures are part of the subject contract on a target path.
The product should review them explicitly instead of letting `.Conflict` suffixes stand in for the operator model.

### Doctrine 60 — one subject may have several honest names, but each needs a declared plane

Subject title, local mount label, disk basename, peer alias, and portable-artifact label may diverge.
That is acceptable only when the interface shows which plane is changing and which audiences will observe it.

### Doctrine 61 — `rename` must publish continuity class and byte cost

A rename can be local-only, mount-continuous, share-continuous, rehome-like, or effectively replay-heavy.
The product should say which class applies before the operator commits to it.

### Doctrine 62 — placeholders are visibility, not proof of surviving bytes

A visible placeholder proves that a path is known.
It does not by itself prove that any durable full copy still exists elsewhere.
The product should guard byte-evicting actions with witness and horizon truth, not with faith.

## Revision addendum — four tighter doctrine choices

This revision adds four doctrine-level decisions that make the interface stricter without making the product broader:

### 1) Ciphertext-only custody is a named role

An untrusted backup or transit peer is not merely `read only`.
If it can hold bytes, seed bytes, but never render plaintext, that must be visible as an explicit opaque-replica role with explicit recovery prerequisites.

### 2) Liveness claims must name their detection class

`Watching` is not enough.
The product must say whether discovery is event-driven, hybrid, periodic-only, or manual-only, and what latency promise follows from that.

### 3) Names and bytes are separate truths

A visible name or placeholder is not proof that any byte witness still exists.
Announcement state, byte witness state, and chronology certainty must be separate first-class facts.

### 4) Broad roots are admitted only after service-root review

A user-visible tree is not automatically a valid subject root if it already contains daemon storage, identity material, logs, or other volatile control state.
The product must review that boundary before bind.



### Doctrine 63 — chronology claims require visible clock confidence

`Latest`, `newer`, `stale`, and `safe to restore` are only honest when the product also shows whether peer clocks and timezones are trustworthy enough to support those claims.

### Doctrine 64 — publication should distinguish writer pressure from quiescent completion

A file under active editor control is not merely `changed`.
The product should show whether it is lock-blocked, delay-buffered, or truly quiescent enough to publish.

### Doctrine 65 — alias edges are topology, not decoration

Symlinks, junctions, hard links, and similar filesystem indirections alter subject scope.
The product should review whether it is preserving the edge, expanding the target, or crossing a boundary.

### Doctrine 66 — pause must publish which signal classes still move

A pause that still allows deletes, indexing, or one-way upload is not false, but it is incomplete.
The product should show a signal matrix instead of hiding several semantics behind one adjective.


### Doctrine 17 — exclusion policy should be public policy

If the product excludes files, directories, or patterns, operators should not have to inspect hidden service files to know why.
The product should expose:

- effective include/exclude rules
- provenance of each rule
- peer agreement or drift
- whether edits are future-only or retroactive-review work

### Doctrine 18 — metadata fidelity must be stated, not implied

A file being present is not enough if metadata channels materially affect usability or object shape.
The product should state whether metadata are:

- preserved natively
- tunneled indirectly
- reduced in fidelity
- blocked entirely

and should explain any visible consequences such as bundle decomposition.

### Doctrine 19 — staged transfer state is part of user truth

`Arrived`, `visible`, and `final` are different truths.
If bytes are still staged, verifying, or cleanup-optional, that must be explicit before the operator deletes residue or assumes continuity.

### Doctrine 20 — capture-to-sink retention is its own subject kind

A personal ingest workflow is not the same thing as collaboration and not merely read-only sync.
If the product offers phone-to-desktop or other capture sinks, it should expose:

- source and sink roles
- foreground/background runtime caveats
- retention floor after source-side deletion
- disconnect semantics for landed bytes versus future capture


### Doctrine 67 — visible progress requires typed work phases, not one busy state

A sync product that scans, hashes, merges, reuses local blocks, writes, and verifies cannot honestly compress all of that into `working` or `internal tasks`.
AnonSync should publish typed work phases, bottleneck class, and next proof point so patience and repair both rest on visible truth.

### Doctrine 68 — local reuse is a proof claim, not a vibe

`Already have these files` is not honest enough.
AnonSync should expose witness strength, reuse class, fallback boundary, and local-resource bill whenever it claims it can avoid re-fetching bytes.

### Doctrine 69 — repair must climb a typed ladder before it mutates continuity

Restart, reindex, rebuild local state, repair bind, and recreate a subject are not the same repair.
AnonSync should require one typed ladder that publishes layer, blast radius, reversibility, and continuity effect before stronger steps are applied.

### Doctrine 70 — departure actions must publish full scope, not familiar verbs

Disconnect, evict local bytes, hide placeholders, retire here, and delete everywhere may all feel adjacent in a UI while having radically different consequences.
AnonSync should publish a full local/shared/reconnect scope matrix before any weakening action can commit.


### Doctrine 71 — power policy must publish participation cadence and absence meaning

A battery-managed seat is not merely `offline` when the product itself chose a wake cadence, charging override, or low-battery stop floor.
AnonSync should publish power policy as part of the public liveness contract.

### Doctrine 72 — transfer ledgers are not payload truth

A history row, a still-live offer window, and local bytes on disk are separate truths.
AnonSync should never let one visible row stand in for all three.

### Doctrine 73 — ingress verbs must declare subject kind and authority shape

`Create`, `adopt`, `send`, `attach capture source`, and `claim incoming` may all begin with user-selected files or folders, but they do not create the same kind of thing.
AnonSync should declare the resulting subject kind before bytes move.

### Doctrine 74 — local reclaim must publish byte class, placeholder effect, and recovery floor

Clearing receipt payloads, evicting materialized copies, reverting to placeholders, and disconnecting a subject are different actions.
AnonSync should publish a reclaim scope matrix instead of hiding those differences behind `clear` or `remove`.

## Revision addendum — four more doctrine choices

This revision adds four doctrine-level decisions that make the interface stricter without making the product broader:

### 1) Power-saving is part of participation truth

If the product chooses to sleep, wake periodically, or stop below a charge floor, that is no longer merely local device preference.
It is part of what other peers can honestly expect about freshness.

### 2) Snapshot history is still not the payload

A retained row can be useful evidence after expiry or local cleanup.
That evidence should survive without pretending the payload still exists.

### 3) Entry verbs teach the product model

Users learn the product from its first verbs.
If those verbs blur live subjects, adopted folders, bounded sends, and capture sources, the whole product model becomes harder to recover later.

### 4) Cleanup is a scoped residency decision

A serious sync product should let operators reclaim local space without guessing whether they just removed cache, names, bytes, or membership.


## Revision addendum — service worlds, declaration branches, and closure receipts

This revision settles four tighter product decisions that current official Resilio docs still leave too distributed:

- **daemonization is a reviewed seat promotion, not an install-mode checkbox**
- **target admission publishes path class and detection grade, not merely reachability**
- **declarative rollout is a declaration branch, not a silent override of live interactive state**
- **program removal compiles to a closure plan and receipt, not a generic uninstall verb**

These decisions intentionally make AnonSync heavier than convenience folklore at the moment the operator changes runtime world, tolerates rescan-bound storage, activates a declaration, or retires a node.
That extra explicitness is the point.


## Revision addendum — doctrine after rev0139

The next doctrinal hardening after this pass is now clearer:

1. discovery bootstrap is not implementation scaffolding; it is an operator-visible authority chain with freshness, fallback, and receipts
2. egress-only seats are not merely slower seats; they are a separate reachability class that must change pairwise route expectations explicitly
3. runtime memory pressure is not permission to discard subject continuity casually; it must route through one ordered relief ladder
4. weaker posture on one self-owned seat is still one subject inside one owner-domain and should therefore behave like an in-place rights edit, not a disguised rejoin


## Revision addendum — relabel salvage, title-plane truth, transfer explanation, and typed search

This revision narrows four more doctrine choices.

### 1) Label edits are not authority rotation by default

A user-visible rename must start as a label problem, not an authority problem.
If authority replacement is actually required, the interface must say so and surface salvage fallout before apply.

### 2) Visible share title is never one anonymous field

The product must keep separate, inspectable planes for:

- subject title
- local title override
- disk basename
- one-off artifact alias

A reset path must always point back to an explicit baseline.

### 3) Slow-transfer explanation is a first-class surface

The product should not force operators to triangulate peer icons, graphs, and settings pages just to answer why a transfer is slow.
Route class, directness, latency, disk pressure, and policy caps should converge in one explanation pane.

### 4) Search is typed navigation, not a page-local filter

Search should span live objects and historical receipts in one surface.
Results must say what kind of object matched, whether it is current or historical, and whether opening it preserves current proof context.

### Additional doctrine bullets this pass stabilizes

- **identity relabel** is a reviewed salvage decision, not a bare text-field edit
- **share-title override** is local decoration unless explicitly promoted
- **artifact alias issuance** is a one-off outward label unless explicitly turned into standing title state
- **transfer explanation** precedes tuning knobs
- **global search** is allowed to move between live objects and receipts, but it must say when proof context is preserved or left behind

### Doctrine 75 — diagnostics must preserve live tie sets before they sell confidence

Two or more explanations can remain honestly alive after evidence review.
AnonSync should publish the current recommendation, the still-live rival set, the arbitration rule, and the abstention budget instead of pretending ambiguity disappeared because one row was sorted first.

### Doctrine 76 — every visible fact needs an authorship bucket before it earns authority

A local observation, a peer declaration, an operator-entered value, a browser-observed event, a config default, and a derived verdict are not the same truth.
AnonSync should publish who authored a visible fact and forbid silent upcasts from weaker buckets into stronger authority.

### Doctrine 77 — local-web history is continuity truth, not action proof

Back, forward, refresh, and deep-link navigation describe session continuity, not whether an action was applied.
AnonSync should make browser-history behavior explicit and receipted instead of letting router accidents masquerade as product law.

### Doctrine 78 — transient cues may accelerate understanding but may not own it

A toast, snackbar, badge glow, or live-region update can announce a change.
It must never become the only durable place where the operator can recover what changed, what is now true, or what next action is required.

## Revision addendum — comparative synthesis after rev0144

Cross-reading the companion datacubes sharpened four doctrine choices that AnonSync should now treat as settled:

### 1) Preserve ambiguity honestly when several explanations survive

The product should not force one diagnostic winner simply because several candidates fit.
Tie sets, near-ties, fallback baselines, and abstention thresholds are part of operator truth.

### 2) Separate truth by authorship before you separate it by confidence

Who authored a visible fact matters before how much confidence a derived row assigns to it.
Peer-declared, browser-observed, operator-entered, and locally measured facts must keep distinct public lanes.

### 3) Browser navigation deserves product law

Local-web projection is now important enough that push-vs-replace, back-forward continuity, and typed miss handling should be deliberate parts of the interface contract rather than implementation leftovers.

### 4) Delivery layers are not outcome layers

Transient notifications can help but must remain secondary to durable inline outcome state, stable receipts, and unobscured target landing.



### Doctrine 79 — local evidence and outbound packets must never collapse into one object

A log bundle, trace set, crash dump, or evidence timeline kept under local custody is not yet a disclosure act.
AnonSync should keep private evidence stores, frozen recipient-specific packets, and send receipts separate so operators never have to guess whether help was merely prepared or actually shared.

The same law should apply one step earlier to outside instructions themselves: the live page or ticket link may stay reachable for convenience, but the actual local review basis should be one frozen fetched snapshot plus one explicit excerpt set.

### Doctrine 80 — outside-surface blockers must re-enter through typed proof

A browser exception, firewall rule, vendor reply, admin-console change, or shell-side repair can unblock progress without happening inside the product.
AnonSync should represent that detour as a first-class handoff with follow-up state, stale-return truth, and an explicit proof row when the operator comes back.

## Revision addendum — comparative synthesis after rev0145

A second pass through the companion datacubes only produced one genuinely worthy cluster of imports, but it was strong enough to matter:

### 1) Private evidence is not public packet

An operator may need to gather richer local evidence before deciding whether anything should leave the machine.
AnonSync should therefore separate sealed local evidence, reviewed outbound packet composition, and final disclosure receipts instead of treating `export` as a disguised `send`.

### 2) `No-send` must be an honest normal state

Support preparation is often real work even when nothing has been transmitted yet.
`Held-unsent`, `ready for review`, and `packet frozen but undisclosed` are legitimate operator outcomes, not awkward transitional failure states.

### 3) Outside blockers deserve typed handles

The next honest step may live in a browser warning page, OS trust prompt, shell command, vendor ticket, or admin console.
That detour should become a tracked handoff with target class, promised return, and stale-followup behavior rather than a sentence in helper copy.

### 4) Return proof is part of operator truth

It is not enough to say `go fix this elsewhere` and hope context survives.
The product should record what the operator was asked to do outside, what came back, and whether the blocker was actually cleared, still pending, superseded, or abandoned.


## Revision addendum — comparative synthesis after rev0146

A further comparative pass only produced two additions worth keeping, but both are load-bearing:

### 1) Remembered trust is perishable by trigger, not only by age

A remembered approval can remain recent and still stop deserving lower-friction reuse because the basis changed underneath it.
Identity epoch change, linked-device growth, scope widening, proof contradiction, or overdue periodic review should reopen trust explicitly instead of floating forward on convenience.

### 2) `Non-material` still needs a receipt

If the operator decides a trigger did not justify changed reuse, that judgment should be recorded.
Silent carry-forward is exactly the folklore this archive is trying to remove.

### 3) Retained shareable artifacts need a current-head register

Once several packets, offers, or bundles exist in one family, the product should expose one tiny answer to which retained object is the latest working tip and which frozen object is the current shareable head.
`Latest`, `current`, and `shareable` are not synonyms.

### 4) Ambiguity should survive as warning surface, not editorial cleanup

If the latest tip is not frozen, the audience no longer matches, or several tips branch, the product should preserve that ambiguity openly rather than guessing which artifact the operator probably meant.


### Doctrine 81 — approval-seat relevance is not the same thing as a live current ask

A seat may remain eligible to approve while no current request is open, and a completed review may remain historically relevant without binding a newer basis.
AnonSync should therefore separate seat-roster continuity, active request state, reviewed-current state, and rerequest-needed state instead of letting one reviewer/approver badge answer all four questions.

## Revision addendum — doctrine after rev0148

Cross-reading the companion datacubes again sharpened one more doctrine choice that AnonSync should now treat as settled:

1. **Seat continuity and live coordination are different truths.** Approval-capable seats should remain visible as roster facts even after one review completes, but later basis drift must surface `rerequest-needed` until a fresh explicit request targets the current basis. Eligibility is not a live ask, and older review is not evergreen approval coordination.

### Doctrine 82 — lightweight status must publish its own proof ceiling

An operator should be able to ask an everyday question like `is this seat basically ready?` without opening a full incident dossier.
But that convenience only remains honest if the lightweight bridge also states what it does **not** yet prove.
A machine-readable bridge verdict, a few supporting probe rows, and an explicit escalation boundary are better than either a vague health badge or a forced jump into raw host archaeology.

### Doctrine 83 — outside progress is not whole repair until effect and follow-through survive reread

A requested step, an observed source-side change, an observed product-side effect, and a whole-fix claim are different truths.
AnonSync should keep them separate so partial outside progress never launders itself into `resolved`, and so remaining cleanup, residue, rereview, or verification work stays visible after the first promising sign.

## Revision addendum — doctrine after rev0150

Cross-reading the companion datacubes again sharpened two more doctrine choices that AnonSync should now treat as settled:

1. **Everyday operator status deserves its own proof scale.** The product should expose one compact runtime-status bridge before it escalates to a full incident or support dossier, and that bridge should say both what it knows and where its claim ceiling stops.
2. **Partial outside fixes need follow-through coverage, not optimism.** The product should preserve the difference between requested step, source-side execution, product-side effect, and final claim-ready repair so that one observed sub-step does not impersonate a whole restored world.

### Doctrine 84 — outbound channel completion must publish its claim ceiling

A frozen shareable artifact is not yet a delivered artifact.
A clipboard update, browser download, share-sheet invocation, target-pass event, and recipient acknowledgment are different truths with different ceilings.

AnonSync should therefore expose one outbound channel-execution lane that publishes:

- which exact frozen artifact was current
- which channel was used
- what exact local completion was observed
- what stronger witness, if any, now exists beyond that
- which stronger labels remain forbidden until later proof arrives

That is how AnonSync avoids a model where `Copy`, `Share`, `Download`, or `Open mail client` quietly launder themselves into `Sent` or `Delivered`.


### Doctrine 85 — current head, change ledger, and visible refresh note are different objects

A newer shareable head does not, by itself, explain what changed since the previously shared artifact.
A hash or version marker may prove non-identity, but it does not tell the operator whether the older artifact still stands unchanged, refreshes in place, must be replaced, or needs full reopen.

AnonSync should therefore preserve three separate surfaces:

- **current head** — which artifact is current for sharing now
- **delta ledger** — which field families changed and which guarantees stayed explicitly unchanged
- **visible refresh note** — the smallest honest audience-safe summary of what changed since the comparison basis

That is how AnonSync avoids a product where recipients and operators must reverse-engineer semantic change from lineage, hashes, or delivery receipts.

## Revision addendum — doctrine after rev0151

Cross-reading the companion datacubes again sharpened one more doctrine choice that AnonSync should now treat as settled:

1. **Retained-artifact continuity needs its own refresh grammar.** Head registers answer which artifact is current, and outbound-channel receipts answer what movement or receipt was observed, but neither one replaces a compact carryforward verdict and refresh note saying whether the older artifact still stands, what changed, and when terse carryforward is forbidden.


### Doctrine 86 — install receipt, service continuity, and startup ownership are different truths

A node can be installed cleanly, promoted into a continuity-correct service seat, and be healthy right now, yet still have the wrong background-start story for tomorrow.
One host may have no effective startup owner, another may have two, and another may have a generated or conditional owner whose meaning is not the same as ordinary explicit enablement.

AnonSync should therefore preserve:

- **requested startup posture** — what the operator reviewed and intended
- **candidate owner lanes** — which startup mechanisms still claim the node now
- **effective owner** — which lane, if any, actually owns startup at the moment
- **runtime correlation** — whether the current daemon actually came from that owner
- **drift history** — whether startup truth is stable, newly broken, recently repaired, or flapping

That is how AnonSync avoids a product where `install finished`, `service enabled`, or `healthy now` quietly impersonate `this exact node will come back correctly after reboot/login`.

## Revision addendum — doctrine after rev0152

Cross-reading the companion datacubes again sharpened one more doctrine choice that AnonSync should now treat as settled:

1. **Startup ownership needs its own receipt-bearing truth surface.** Install attestation answers what was trusted, service promotion answers whether the same node survived a move into background life, and runtime status answers how healthy the node looks now; none of those objects, by themselves, answer who actually owns automatic return on this host or whether that ownership recently drifted.


### Doctrine 87 — reviewed actions should remember the basis they expected

A reviewed draft, packet, notice, or apply-ready action can remain visible long enough for the world around it to change.
A newer head, newer approval basis, newer policy version, or newer shareable artifact should not quietly inherit the older review.

AnonSync should therefore preserve:

- **reviewed action** — the thing the operator already reviewed
- **expected basis rows** — the exact heads / versions / basis objects that action expected to remain current
- **current basis comparison** — what still matches and what drifted
- **stale-attempt truth** — a durable record when a click was refused against stale basis
- **explicit reissue** — the newer reviewed action that replaced the older one

That is how AnonSync avoids a product where `reviewed`, `ready`, or `queued` quietly impersonate `safe to execute against whatever is current now`.

### Doctrine 88 — recipient-scoped review should remember the target it expected

A reviewed recipient-specific action can remain visible long enough for the intended destination to change.
A new mailbox, wider audience, public posting class, or different support target should not quietly inherit the older review.

AnonSync should therefore preserve:

- **reviewed action** — the thing the operator already reviewed
- **expected target rows** — the exact recipient, audience, or destination set that action expected
- **current target comparison** — what still matches and what changed
- **stale-target truth** — a durable record when a send or issue was refused against a different target
- **explicit retarget reissue** — the newer reviewed action that replaced the older one on the new destination

That is how AnonSync avoids a product where `reviewed packet` quietly impersonates `approved for this new recipient too`.

### Doctrine 89 — current shareable head, queued issue, and current issued surface are different objects

A family may already have a newer frozen shareable head and even a prepared or queued send while an older issued artifact is still the one currently in force outwardly for one recipient or audience.
Those are adjacent truths, but they are not the same object.

AnonSync should therefore preserve:

- **current shareable head** — the artifact that is current for new reuse or issue now
- **queued issue item** — the reviewed or scheduled outward act that may later move one head toward one target
- **executed issue event** — the transition proving one queued or immediate outward act actually ran
- **current issued head** — the artifact currently outwardly in force for one target or audience after execution
- **current outward-surface snapshot** — the frozen public/recipient-facing wrapper corresponding to that current issued head
- **later delivery witness** — any stronger proof beyond issue execution itself

That is how AnonSync avoids a product where `frozen`, `ready`, or `queued` quietly impersonate `this is what the other side currently has`.

### Doctrine 90 — already-issued outward artifacts need explicit correction state

Once an artifact was already issued outwardly, a later internal decision, a newer replacement artifact, or even a newly current issued head is not automatically the same thing as the recipient understanding the older artifact as withdrawn or superseded.

AnonSync should therefore preserve:

- **older issued artifact** — the outward artifact whose interpretation is being corrected
- **active correction notice** — the outward-facing note that now tells one target how to interpret that older artifact
- **replacement-issued state** — whether a newer artifact exists and whether it was actually issued yet
- **residual reliance posture** — why older copies may still circulate or matter
- **stronger acknowledgment** — recipient or same-product proof that upgrades the correction claim ceiling

That is how AnonSync avoids a product where `we fixed it locally` quietly impersonates `they now know the old thing is obsolete`.

### Doctrine 91 — exact acknowledged object and represented audience scope are different truths

A reply can be exact about the correction notice or replacement artifact while still being only one actor's response inside a broader mailbox, alias, group, or support lane.
That is useful evidence, but it is not the same thing as whole-target or whole-audience acknowledgment.

AnonSync should therefore preserve:

- **raw actor** — the concrete person, operator, or process that produced the reply if known
- **visible reply lane** — the mailbox, group, ticket, or same-product lane the acknowledgment arrived through
- **relation to expected target** — whether that actor is the exact target, one audience member, a delegate of the lane, or only loosely related
- **delegation evidence** — what actually proves the actor may speak through that lane
- **scope ceiling** — whether the current truth is actor-only, target-lane, one-audience-member, or genuinely audience-wide

That is how AnonSync avoids a product where `one correct reply in the right thread` quietly impersonates `everyone who matters now acknowledged it`.



### Doctrine 92 — reply-shaped traffic still needs explicit human-proof classification

A reply can bind exactly to the right correction notice or replacement artifact and can even arrive through the exact target lane while still being only an automatic out-of-office response, a ticket auto-create notice, a rule-authored comment, or some other machine-authored reaction.
That is still useful evidence, but it is not the same thing as human review.

AnonSync should therefore preserve:

- **authorship class** — human-authored, automation-authored, mixed, receipt-only, or unknown
- **automation kind** — vacation reply, ticket auto-create, rule-authored comment, gateway challenge, delivery-failure notice, or similar machine shape
- **human material presence** — whether any explicit human-authored text is actually visible in the imported evidence
- **human-proof strength** — none, weak hint, manual classification, structural proof, or same-product proof
- **authorship ceiling** — machine-lane reaction only, lane ingestion probable, ticket opened or routed, human response probable, or human response exact

That is how AnonSync avoids a product where `the mailbox reacted` or `the ticket system spoke` quietly impersonates `a human actually reviewed and replied`.


### Doctrine 93 — human reply stance is not the same thing as acceptance

A human-authored reply can be exact about the right artifact and can even arrive through the right target lane while still only asking for clarification, requesting a changed artifact, redirecting the operator to a different lane, conditionally accepting once one further step is completed, or declining the request entirely.
That is still useful evidence, but it is not the same thing as `accepted current request`.

AnonSync should therefore preserve:

- **reply stance** — machine-operational-only, receipt-only, understands, clarification requested, artifact change requested, redirected, conditional, declined, ambiguous, or unknown
- **blocking effect** — whether the current claim may continue as-is, needs follow-up, must redirect, is currently blocked, or has ended in terminal decline
- **smallest honest follow-up** — answer question, issue corrected artifact, rechannel/repackage, retarget lane, provide stronger proof, record decline and stop, or none
- **accepted-scope ceiling** — what the reply currently justifies saying: receipt only, understanding only, conditional pending step, accepted current request, redirect only, declined, or unknown
- **stronger reply needed** — the exact kind of later reply or proof that would strengthen the stance

That is how AnonSync avoids a product where `human replied in the right place` quietly impersonates `the current packet was accepted and no follow-up remains`.


### Doctrine 94 — exact reply object is not the same thing as exact covered portion

A human-authored or machine-authored reply can bind exactly to the right outward artifact family and still only speak about one quoted paragraph, one diff range, one attachment, one named request item, or one corrected field inside that larger artifact.
That is useful evidence, but it is not the same thing as whole-artifact or whole-request acceptance.

AnonSync should therefore preserve:

- **referent slice** — whether the reply referred to the whole artifact, one named subobject, one quoted excerpt, one line/range, one attachment, one named request item, a visible subset, or an unclear subset
- **coverage ceiling** — whether the current reply covers one slice only, a named subset, all explicit request items, or the whole outward artifact
- **remainder posture** — whether the untouched remainder is unmentioned, explicitly left open, explicitly rejected, or actually closed
- **promotion requirement** — what stronger proof would justify upgrading subset truth into whole-artifact acceptance
- **subset-safe next move** — what the operator may honestly say or reissue now without overstating the rest

That is how AnonSync avoids a product where `they replied about the right packet` quietly impersonates `they accepted the whole packet`.


## Revision addendum — doctrine after rev0162

Cross-reading the companion datacubes again sharpened one more doctrine choice that AnonSync should now treat as settled:

1. **Artifact exactness and covered portion are orthogonal.** `259` can already answer what exact outward artifact a reply bound to and `262` can already answer what that reply meant, but neither one alone answers whether the reply spoke about the whole packet or only one quoted/requested slice. AnonSync should therefore preserve referent-slice and request-coverage truth explicitly instead of letting one line-range comment, one attachment note, or one quoted paragraph silently stand in for whole-artifact acceptance.

## Revision addendum — doctrine after rev0161

Cross-reading the companion datacubes again sharpened one more doctrine choice that AnonSync should now treat as settled:

1. **Human-proof and semantic acceptance are orthogonal.** `261` can already answer whether a human probably replied, but that still does not tell the operator whether the reply accepted the current request, asked for clarification, redirected the request, or declined it. AnonSync should therefore preserve reply stance and smallest-sufficient follow-up explicitly instead of letting every human reply inherit acceptance meaning by accident.

## Revision addendum — doctrine after rev0160

Cross-reading the companion datacubes again sharpened one more doctrine choice that AnonSync should now treat as settled:

1. **Object exactness, represented scope, and human-proof are orthogonal.** `259` can already answer what exact object was acknowledged and `260` can already answer who that reply can speak for, but neither one alone answers whether the reply was human-authored; AnonSync should therefore preserve automation kind and human-proof ceilings explicitly instead of letting ticket auto-create or out-of-office traffic inherit human meaning by accident.

## Revision addendum — doctrine after rev0159

Cross-reading the companion datacubes again sharpened one more doctrine choice that AnonSync should now treat as settled:

1. **Exact object binding and represented audience scope are orthogonal.** `259` now answers what exact object was acknowledged, but it still cannot by itself answer who that reply counts for. AnonSync should therefore preserve actor, visible reply lane, delegation evidence, and scope ceiling separately instead of letting one member reply or one delegated operator reply silently count for the whole target audience.

## Revision addendum — doctrine after rev0156

Cross-reading the companion datacubes again sharpened one more doctrine choice that AnonSync should now treat as settled:

1. **Outward correction needs its own register.** Disclosure registers answer what is currently in force outwardly, carryforward notes answer what changed since an older disclosed artifact, and delivery ceilings answer what a channel or witness proved; none of those objects alone answers which notice now controls interpretation of an older already-issued artifact or what residual stale-copy posture still remains.

## Revision addendum — doctrine after rev0155

Cross-reading the companion datacubes again sharpened one more doctrine choice that AnonSync should now treat as settled:

1. **Current outward surface needs its own register.** Head registers answer what is current for reuse, carryforward notes answer what changed since an older disclosed artifact, and delivery ceilings answer what a channel or witness proved; none of those objects alone answers what artifact is currently outwardly in force for one recipient or audience when newer frozen or queued artifacts also exist.

## Revision addendum — doctrine after rev0154

Cross-reading the companion datacubes again sharpened one more doctrine choice that AnonSync should now treat as settled:

1. **Reviewed intent needs an expected-basis guard.** Current heads, approval clocks, and carryforward ledgers already explain adjacent truths, but they do not by themselves answer whether an older reviewed action still honestly binds right now; the product should therefore preserve match, stale-attempt, and explicit reissue truth instead of silent inheritance.
2. **Recipient-scoped review needs an expected-target guard.** Recipient-specific packet and offer rules already explain who a thing is for, but they did not yet answer whether an older reviewed action still honestly points at the same destination after recipient or audience drift; the product should therefore preserve match, stale-target, and explicit retarget reissue truth instead of silent retargeting.

## Revision addendum — borrow boldly, fuse less

This revision adds two doctrine choices that should survive beyond the immediate Resilio pass.

### Convenience selectors must decompose into inspectable truths

A useful convenience selector may still exist.
But if one selector silently decides:

- visibility
- local adoption
- materialization
- authority widening
- future default behavior

then the selector is too strong.
AnonSync should let convenience survive only after those consequences compile into separately inspectable public objects.

### Everyday lists are semantic surfaces, not decorative indexes

Share list, Transfers, History / Restore, and Conflict pages are not secondary browse views.
They are where most operators will actually decide what to do next.
So list rows must preserve proof-bearing truth, not just ornament, counts, and status color.

## Revision addendum — doctrine after rev0165

Cross-reading the Resilio material again sharpens one more doctrine choice that AnonSync should now treat as settled:

1. **Every non-clone boundary needs a page-shaped replacement.** It is no longer enough for the archive to say that current products fuse truths or scatter them across too many surfaces. If AnonSync refuses the clone, it should be able to point at one concrete replacement page that answers the same operator question with stronger truth contracts. That is why control trust, artifact intake, effective rate truth, and finish-setup bringup now each get their own fixed page contract instead of remaining general doctrine only.

2. **A degraded state must advertise its own upgrade ladder.** Browser warning, failed handoff, scheduled pause, and installed-but-not-ready are not merely statuses. They are incomplete states that should each name the next stronger reachable state and the exact mutation needed to get there.

## Revision addendum — second-wave Resilio replacement pages after rev0166

The product direction now becomes slightly more opinionated.
It is no longer enough to say that AnonSync will keep orthogonal truths separate.
The archive now commits to four additional ordinary pages whenever the product exposes selective materialization, ciphertext-only custody, same-host derivation, or Archive-style recovery:

1. **Byte posture** instead of one fused mode selector
2. **Encrypted custody** instead of ciphertext recovery folklore
3. **Same-host lineage** instead of local-share caveat memory
4. **Fetchability** instead of `available on demand` optimism

This is now part of the product thesis, not side commentary.


## Revision addendum — third-wave Resilio replacement pages after rev0167

The product direction now commits to four more ordinary pages whenever the product exposes identity-family joins, non-empty target intake, mutable delegation, or multiple live naming planes:

1. **Identity join** instead of one ambiguous `link device` story
2. **Existing bytes intake** instead of reconnect-and-duplicate repair ritual
3. **Delegation** instead of grayed-out rights ceilings and caveat memory
4. **Name planes** instead of one overloaded `folder name` field

This is now part of the product thesis, not side commentary.


## Revision addendum — fourth-wave Resilio replacement pages after rev0168

The product direction now commits to four more ordinary pages whenever the product exposes hidden service material, exclusion rules, file-class delay policy, or non-trivial download prioritization:

1. **Service material page** — because identity-bearing runtime material, Archive continuity, partial residue, and rebind-vs-repair truth should not surface mainly through hidden directories and corruption warnings
2. **Exclusion policy page** — because `not indexed`, `not transferred`, and `not counted` are product semantics that need scope, matching, and accounting truth on one page
3. **Mutation delay page** — because file-class batching and lock-avoidance timing should be inspectable and reviewable without storage-folder JSON ritual
4. **Download queue page** — because visible browse order, effective execution order, inherited defaults, frozen local overrides, and preemption exceptions must remain one inspectable answer

This revision therefore settles four more doctrine choices that should survive beyond the immediate Resilio comparison:

- hidden runtime material may exist, but it may not be the only public semantic home of continuity truth
- exclusion policy is governance, not merely advanced syntax
- delayed shipment is a first-class chronology policy, not just a tuning file
- queue order is product truth only when the visible surface can explain the effective execution order honestly


## Revision addendum — fifth-wave Resilio replacement pages after rev0169

The product direction now commits to four more ordinary pages whenever the product exposes shell acceleration, byte-presence mutation, retained history, or risky filesystem shapes:

1. **Shell capability page** — because file-manager shortcuts and extensions may accelerate the work without becoming the only semantic home of it
2. **Byte action review page** — because local evict, placeholder reversion, disconnect, and delete-everywhere are materially different actions that need one explicit review grammar
3. **History access page** — because retention, seat access parity, candidate ordering, and restore consequences should not depend on hidden Archive browsing or platform folklore
4. **Filesystem shape audit page** — because link nodes, metadata channels, invalid names, and bundle cohesion should roll up into one ordinary fidelity verdict before trouble starts

This revision therefore settles four more doctrine choices that should survive beyond the immediate Resilio comparison:

- shell integration is an accelerator, not an authority boundary
- byte-presence mutation and object destruction may never share one unlabeled `remove` story
- restore parity is part of continuity truth, not an afterthought of hidden retention storage
- filesystem shape fidelity needs one operator rollup page before specialist drill-ins


## Revision addendum — observer-boundary and state-root continuity after rev0170

This revision tightened two quieter but still load-bearing doctrines.

1. **Outside infrastructure deserves one observer matrix, not reassurance prose.** It is not enough for the product to say `your data stays on your devices` or `relay cannot read files` if the operator still has to reconstruct tracker facts, landing-page click counts, telemetry fields, update checks, and account touch points from separate articles. The product should show one matrix of observer classes, fact classes, plaintext ceilings, and narrowing paths.

2. **Local state roots are ordinary product state, not troubleshooting leftovers.** If runtime principal, config mode, or storage-path choice can silently land the operator in a different local world, then state root is not an implementation detail. The product should expose which world is active, why that path won, what identity/inventory belong to it, and whether clone/shadow/snapshot ambiguity is present before any meaningful mutation proceeds.

3. **`Cloning is unsupported` is not enough.** A serious product still owes reviewed answers for same-world attach, successor import, stale-backup quarantine, clean branch creation, and clone-risk block. Unsupported opaque copying can remain true while the product still supports reviewed continuity transitions.

4. **Disablement should preserve capability truth.** Narrowing tracker, relay, landing-page, update, telemetry, or account reliance should state both the privacy gain and the exact convenience/reachability cost instead of collapsing into generic `off`.

This tranche therefore treats infrastructure visibility, service role, state root, and attach state as ordinary pages rather than advanced annexes.



## Revision addendum — helper-policy and host-cadence contracts after rev0171

This revision intentionally tightens the product doctrine in four further ways:

1. **Helper policy deserves one scope stack, not scattered toggles.** It is not enough to have tracker, relay, LAN, pinned-host, and proxy controls if the operator still has to reconstruct the effective posture from separate subject, seat, host, and troubleshooting surfaces. The product should show one stack with precedence, blockers, and counterfactual route effects.

2. **Bootstrap provenance is public state, not background trivia.** If a seat learns helper locations or peer addresses from a vendor catalog, a private catalog, manual pins, or cached residue, that is part of the trust and narrowing story. The product should show which source is active, how fresh it is, and what older knowledge still survives.

3. **Pairwise helper dependence deserves one ordinary explanation page.** It is not enough to say `relay`, `direct`, or `blocked`. The product should state which helper is actually needed now, which blocker prevents the cleaner path, and what exact change would remove the dependence.

4. **Host cadence is a reviewable freshness contract.** If notifications, periodic rescan, helper refresh, settings-save cadence, or logging keep a host awake or make it stale, that is not merely tuning. The product should show the current loops, the wake/freshness tradeoff, and the before/after effect of quiet-host changes.

This tranche therefore treats helper policy, bootstrap source, helper dependence, and host cadence as ordinary pages rather than advanced annexes.

## Revision addendum — capability provenance, compatibility gates, alert delivery, and kind choice after rev0172

The product direction now also needs four more ordinary truths to stay first-class:

- **right-to-run is provenance, not a badge** — capability should publish whether it is purely local, locally activated, remotely dependent, expiring, or blocked
- **compatibility is a gate, not a yes/no icon** — sync-safe, join-safe, update-safe, and storage-safe must remain separate answers
- **alerts are delivery pipelines, not bell icons** — event origin, carrier, permission gate, suppression, and missed-event recovery must remain explicit
- **creation is a kind decision, not only a path decision** — `sync`, `backup`, `send`, `ciphertext custody`, and `same-host derivation` must compare on one chooser page before commitment

## Revision addendum — health and repair pages after rev0173

The product direction now owes four more explicit ordinary surfaces:

- **Issue home** so a broken-looking system starts with one family verdict and one first safe action rather than a bag of hints
- **Environment conflict** so lock pressure, foreign-writer risk, and weak change detection stay distinct and actionable
- **Repair plan** so least-destructive recovery is ordered by copy-safety proof instead of folklore
- **Crash capture** so evidence origin, restart/reproduction needs, and disclosure boundaries become product-owned rather than hidden-path ritual


## Revision addendum — path continuity and relocation pages after rev0174

The product direction now owes four more explicit ordinary surfaces:

- **Share path** so every local bind publishes current path, storage/volume facts, and relocation eligibility instead of leaving those truths implicit
- **Relocate review** so same-domain moves, cross-domain rebinds, path repair, and peer-continuity fallout stay distinguishable
- **Disconnected share** so pathless known-subject presence can publish what still exists, what reconnect choices remain, and what removal scope would be accepted
- **Rename / move explanation** so local disk changes, peer-visible consequences, and archive/history dependence become product-owned rather than FAQ-shaped


## Revision addendum — surface parity, save-back, background freshness, and mobile storage after rev0175

The product direction now owes four more explicit ordinary surfaces:

- **Surface capability** so every surface can publish its real verbs, its missing verbs, and the winning reason for each gap
- **External edit review** so copy-based editing, explicit save-back, replacement, and sibling-risk stay visible before launch
- **Background delivery** so `continuous`, `conditional`, `foreground-only`, and `stopped` remain first-class operational answers rather than folklore
- **Mobile storage** so sandbox facts, app-versus-user-data accounting, cleanup scope, and reacquireability stay adjacent

## Revision addendum — capture-only ingest needs source/sink/landing/cleanup separation after rev0176

Near-term direction should now keep four new truths separate whenever a phone or constrained seat acts as a capture source:

1. **Source scope is not sink promise.** `Camera backup`, `custom Android folder`, and `provider-scoped subtree` are different source contracts. The product should publish exactly what source domain is attached instead of implying that all ingest workflows watch an equally broad tree.
2. **Sink membership is not durability.** A linked-device list, a delivered backup link, and a platform-default destination are not the same as a sink that currently counts toward the durability threshold for safe source cleanup.
3. **Landing is not the same thing as progress.** `Seen`, `queued`, `in flight`, and `landed on enough sinks to satisfy policy` must remain visibly distinct so operators never delete from the source because a progress row looked optimistic.
4. **Source cleanup is not relationship teardown.** Deleting from the source, pausing capture, disconnecting capture, and clearing local previews are materially different acts. The product should keep their consequences explicit instead of overloading them into one `stop backup` family.


## Revision addendum — execution principal and host-authority pages after rev0177

The product direction now owes four more explicit ordinary surfaces:

- **Execution principal** so every seat can publish which OS principal is acting, why that principal won, and how much real disk authority it currently has
- **Filesystem grant** so path writability is grounded in one exact owner/group/ACL/provider proof instead of generic `permission denied` folklore
- **Principal switch review** so switching between current user, service account, package user, system account, or storage root is treated as a reviewed continuity event rather than a harmless toggle
- **Blocked-path repair** so least-destructive grant repair stays separate from stronger world-changing escalations

Near-term direction should keep four doctrine choices explicit:

1. **runtime authorship is product truth** — the brand name is not enough; the acting OS principal must be public state
2. **grant proof is not the same thing as path presence** — a visible path is not a writable path, and file versus directory proof must remain distinct
3. **authority widening is not world continuity** — a stronger service account may widen reach while still creating a successor local world
4. **repair ladders must prefer in-place grant repair over world replacement** — the product should not jump straight from `permission blocked` to `switch principal` without showing safer rungs first


### Latest addition — configured reachability is not proved route truth

A listening port, helper toggle, or manual endpoint pin may be necessary input, but it is not the same thing as proved ingress, current pairwise route, or safe repair order. AnonSync should publish one listener page, one pairwise route-proof page, one least-destructive repair ladder, and one endpoint-claim review so `configured`, `advertised`, `reachable`, and `trusted enough to pin` stop collapsing into the same story.

## Revision addendum — chronology authority, offline replay, mtime fidelity, and restore timing after rev0179

The product direction now owes four more explicit ordinary surfaces:

- **Clock authority** so time-zone and clock-validity truth does not remain warning-only knowledge
- **Offline replay review** so returning-offline edits cannot silently masquerade as clean chronology
- **Mtime integrity** so database-only timestamp truth and filesystem-visible timestamp truth remain visibly distinct
- **Restore replay review** so `restore`, `export`, `make live`, and `share-wide replay` stop collapsing into one verb

Near-term direction should keep four doctrine choices explicit:

1. **chronology trust is product state** — peer clock validity and chronology confidence must be public, not inferred
2. **coming back online is not the same thing as being newer** — authored time and return time must remain separate truths
3. **filesystem time is not always authority** — if the engine's database is the stronger timestamp source, the product must say so directly
4. **restore timing is part of restore meaning** — runtime liveness and watch freshness must remain first-class preconditions for live replay


## Revision addendum — semantic-tradeoff and hidden-optimization pages after rev0180

The product direction now owes four more explicit ordinary surfaces:

- **Read-only divergence** so suspension, overwrite posture, and added-file fate stop living in FAQ folklore
- **Placeholder removal** so local eviction, global delete, and delete-guard remapping remain visibly distinct
- **Hash readiness** so scanned, hashed, semantically ready, and preseed-held remain separate truths
- **Transfer method** so speed/resume/resource tradeoffs are inspectable instead of hidden behind adaptive behavior or advanced toggles

Near-term direction should keep four doctrine choices explicit:

1. **read-only does not mean semantically quiet** — local drift, suspension, and destructive overwrite risk must stay public
2. **removal intent and destruction scope are separate truths** — placeholder eviction must never masquerade as object destruction or vice versa
3. **visibility is not readiness** — seeing names or progress is not the same as having enough hash/index evidence for semantic operations
4. **speed is not free** — fastpath transfer choices must publish their interruption and recovery cost


## Revision addendum — doctrine 75: counted bytes, resident bytes, and hidden bytes are separate truths

A product that shows one number and one `present/empty` badge for a subject is lying by compression whenever the following can all be true at once:

- some names are only placeholders
- some bytes are excluded from the visible metric
- some managed/history/temp bytes remain on the seat
- some structure is known before payload verification is complete

From this revision onward, AnonSync doctrine requires that **metric contract**, **resident footprint**, **completeness confidence**, and **service residue** are separate inspectable truths.
A subject row may stay compact, but the answer must exist.

## Revision addendum — topology and media fit should be product-owned, not caveat-owned

AnonSync should treat target topology and media/provider fit as first-class product meaning.
A path choice is not enough.
The product direction now explicitly prefers:

- reviewed admission of parent/child/disjoint/duplicate graph relations before bind
- same-host edges that say `self-routed dependent edge` rather than pretending to be ordinary peers
- removable/provider-backed targets that prove grant scope separately from folder choice
- return flows that distinguish `same target resumed`, `safe rebind`, and `new target with merge risk`

This is part of the broader refusal to let convenience verbs stand in for real continuity semantics.


## Revision addendum — capability artifacts, requester review, and mutable grants after rev0183

The product direction now owes four more explicit ordinary surfaces:

- **Share capability** so artifact family, carrier, approval posture, and rights ceiling stop collapsing into one `Share` moment
- **Incoming share request** so requester proof, remembered-policy reuse, and durable consequence become reviewable before approval
- **Member access** so grant origin, editability fence, and future-update revocation stay inspectable after sharing
- **Manual claim** so paste/scan/import paths stop acting like one generic intake box

Near-term direction should keep four doctrine choices explicit:

1. **artifact family is product state** — raw capability material, reviewed claim artifacts, and delivery wrappers are different truths
2. **approval is not ornamental** — requester proof and remembered-policy reuse must stay public
3. **grant editability is not universal** — subject kind and operator role can narrow what later mutations are honest
4. **revocation is scoped** — stopping future updates is not the same thing as reclaiming already-landed bytes


## Revision addendum — subject-class cliffs and successor cutover after rev0184

Another current Resilio pass keeps pointing at the same doctrinal gap from a different angle:

- subject class is not just a badge; it changes identity proof, peer aggregation, mutable rights, and onward-share meaning
- `upgrade` cannot be allowed to hide successor-epoch truth when governance class actually changes
- per-seat exceptions inside a broad owner family must declare whether they remain in-family or break out into a separate subject
- peer rows must declare whether they are rows of verified members, descendant seats, or merely devices the current class cannot prove belong together

AnonSync should therefore keep class identity, class cliffs, successor cutover, and row-grouping meaning visible as first-class page contracts rather than as folklore reconstructed from missing buttons.

## Revision addendum — performance truth should be product-owned, not graph-owned

AnonSync should treat performance visibility as a first-class meaning surface, not a decorative telemetry layer.
A chart alone is not an answer.
The product direction now explicitly prefers:

- graph windows that name scope, sample basis, and confidence instead of implying certainty by motion
- peer tables that explain route, RTT, asymmetric upload ceilings, and why a given peer is or is not the present bottleneck
- disk-pressure surfaces that separate Sync-created queue from host-wide contention and offer a safe relief ladder
- throughput explanations that distinguish network ceiling from workload-shape ceiling, especially for many-small-file and relay-heavy work

This is part of the broader refusal to let `looks live` impersonate `already explained`.


## Revision addendum — evidence custody should be product-owned, not support-owned

AnonSync should treat diagnostics as a first-class product meaning surface, not an afterthought owned by troubleshooting prose.
A toggle alone is not an answer.
The product direction now explicitly prefers:

- telemetry surfaces that distinguish low-grade statistics from deeper incident capture
- capture reviews that declare purpose, restart gate, and expected local artifact cost before profiling begins
- outbound evidence sends that preview bundle membership and emit a receipt rather than silently uploading
- retention pages that enumerate hidden/local artifacts and can attest what still remains after cleanup

This is part of the broader refusal to let `there is a support article for that` impersonate `the product itself already owns the answer`.



### Latest addition — control entry is a product surface, not browser luck

Opening control in a browser, from an installer, or from a deep link is not mere launch trivia.
The product should tell the operator which surface answered, which runtime owns it, what endpoint was reached, and what convenience paths are unavailable from here.

### Latest addition — exposure is a declared audience, not a bind-string side effect

Loopback-only, LAN-reachable, proxied, and remote control are different audience states.
The product should name them directly instead of expecting the operator to reconstruct them from `127.0.0.1`, `0.0.0.0`, or browser reachability.

### Latest addition — browser distrust is typed product state

A browser warning is not the explanation.
The explanation is whether this is expected local bootstrap, stale browser residue, hostname/certificate drift, or a genuinely unexpected endpoint.
The product should own that distinction.

### Latest addition — control recovery preserves seat continuity by default

Losing a control secret should not silently widen into duplicate-seat appearance, global-preference reset, or unclear session invalidation.
State-preserving recovery is the normal path; broader reset is a reviewed escalation.

## Revision addendum — namespace-blockage and portability-repair pages after rev0193

The product direction now owes four more explicit ordinary surfaces:

- **Namespace blockage** so delayed, auto-repaired, conflicted, portability-blocked, unsupported, and share-stalling states stop collapsing into one vague warning row
- **Conflict evidence** so `.Conflict` artifacts stop masquerading as disposable clutter instead of live counterpart-bearing data
- **Unsupported entry** so link/junction fidelity and target-byte inclusion stop hiding inside platform caveats
- **Portability repair** so rename/normalization/split/move plans become reviewed scope decisions instead of support ritual

Near-term direction should keep four doctrine choices explicit:

1. **namespace diagnosis is product state** — the product must publish whether it rewrote, conflicted, blocked, excluded, or merely delayed
2. **conflict artifacts are evidence-bearing objects** — suffixes must not replace counterpart proof or delete-scope warning
3. **unsupported entry classes are consequence-bearing** — link fidelity and target inclusion are first-class product meaning
4. **portability repair is a scoped plan, not a generic suggestion** — rename, split, move, and block all carry different continuity promises
## Revision addendum — freshness-basis and rescan-review pages after rev0194

The product direction now owes four more explicit ordinary surfaces:

- **Freshness basis** so `up to date` stops hiding whether that claim rests on live notifications, periodic scan, startup rediscovery, or manual intervention
- **Detection downgrade** so watcher exhaustion, path-class weakness, disabled notifications, and service-path downgrade stop collapsing into one vague `sync is slow` story
- **Rescan review** so `Rescan` becomes a reviewed proof-uplift action with explicit non-effects instead of a generic troubleshooting ritual
- **Change publication** so a changed object's journey from local detection to remote landed proof stays visible as one chain rather than status/history/queue folklore

Near-term direction should keep four doctrine choices explicit:

1. **freshness claims need a basis** — the product must publish what mechanism currently supports `current enough`
2. **downgrade is product state** — losing near-real-time detection is not mere implementation detail
3. **repair verbs need non-effects** — `Rescan` must say what it will not fix
4. **publication is staged truth** — detected, indexed, announced, fetchable, and landed are different public facts
## Revision addendum — transport-path truth should be product-owned, not preference-owned

AnonSync should treat peer discovery, route class, and disclosure change as first-class meaning surfaces, not as incidental byproducts of networking toggles.
A checked box alone is not an answer.
The product direction now explicitly prefers:

- reachability pages that say whether current discovery depends on tracker, LAN, known host, remembered residue, or none of the above
- pair-route pages that explain how a specific peer pair found each other, what path is actually carrying traffic, and why stronger directness failed
- repair ladders that begin with the narrowest route or listener fix before widening observer scope
- widening reviews that publish who newly learns what and whether later rollback still requires restart or cache clearance

This is part of the broader refusal to let `Use tracker`, `Use relay`, or `connected` impersonate `already explained`.

## Revision addendum — effective motion and quiet truth after rev0196

The product direction should now treat **motion truth** as separate from both **freshness truth** and **route truth**.
That means the product must publish, in one place:

- whether apparent quiet means `no work`, `hidden work`, `source absence`, `runtime absence`, `policy suppression`, or `bottleneck elsewhere`
- whether a quiet window zeros transfer only or also freezes deletes, indexing, announcement, and serving
- whether slowness is primarily route-shaped, source-shaped, disk-shaped, workload-shaped, or host-interference-shaped
- whether resume should honestly create catch-up, only renewed waiting, or explicit residual risk

A product that says `Paused`, `slow`, `running in background`, or `will sync later` without these decompositions is still making the operator do systems archaeology instead of product use.


## Revision addendum — hidden subject spine and sidecar truth after rev0197

Product direction should now explicitly require that AnonSync never treat hidden service namespace as mere implementation detail.

The product should instead make three distinctions public everywhere:

- **payload bytes vs managed service bytes**
- **continuity-bearing spine vs seat-local sidecar policy**
- **safe observation vs safe mutation**

That means every ordinary subject surface should be able to answer:

- what managed families exist under this subject
- which ones are identity/continuity-bearing
- which ones are local policy or metadata-carriage sidecars
- whether a move, repair, or cleanup preserves the current subject epoch or creates a successor epoch

A privacy-respecting sync product that hides these distinctions behind a hidden folder is still under-explaining itself.

## Revision addendum — install eligibility and cohort cutover truth after rev0198

Product direction should now explicitly require that AnonSync never let `download`, `install`, or `update available` impersonate release truth.

The product should instead make four distinctions public everywhere:

- **host-role support vs mere executability**
- **usage-class support vs license possession**
- **bytes preserved vs configuration preserved**
- **current package lane vs future maintenance owner**

That means every ordinary seat surface should be able to answer:

- whether this line belongs on this host at all
- whether this linked cohort must move together to stay honest
- whether a boundary crossing is a same-line update, supported cutover, redirect, or blocked transition
- whether updates here are owned by a package manager, app installer, vendor package, or explicit operator ritual

A privacy-respecting sync product that hides these distinctions behind requirements tables and install notes is still under-explaining itself.


## Revision addendum — hidden advanced overrides and precedence truth after rev0200

Product direction should now explicitly require that AnonSync never let advanced settings or config files function as a shadow government for ordinary operator truth.

The product should instead make four distinctions public everywhere:

- **visible preference vs hidden override**
- **interactive source vs declared source**
- **immediate effect vs restart / clearance effect**
- **targeted benefit vs side-effect budget**

That means every ordinary seat or subject surface should be able to answer:

- which hidden overrides are currently active here
- which visible controls are being shadowed or ignored
- which change will actually take effect now versus later
- what safety, retention, discovery, or runtime cost the current bias buys

A privacy-respecting sync product that hides these distinctions behind an advanced-preferences table is still under-explaining itself.


## Revision addendum — external-recipe provenance and postcondition truth after rev0202

Another current Resilio pass sharpens a more operational requirement for AnonSync:

- external guidance and remediation are not enough on their own
- the product must also preserve recipe class, target tuple, precondition proof, lane witness, and postcondition reread

So the next design posture should stay firm on five points:

1. every outside-the-product act must remain a named object, not improvised prose
2. target scope must be normalized enough to distinguish seat, runtime, path, process, browser trust store, and hidden service state
3. execution witness must stay separate from repaired product truth
4. destructive reset and continuity recreation must be named honestly
5. follow-on verification must be mandatory rather than optional

This revision's four new pages are therefore not merely troubleshooting notes.
They are part of the product's ordinary truth-telling surface.

## Revision addendum — warning ownership and repair-rung truth after rev0203

Product direction should now explicitly require that AnonSync never let warning strings function as the true home of degraded-state meaning.

The product should instead make four distinctions public everywhere:

- **warning class vs mere alert delivery**
- **blast radius vs generic severity color**
- **safe next rung vs loudest available recipe**
- **acknowledgement visibility change vs proof-backed repair**

That means every ordinary warning surface should be able to answer:

- what class of problem this is
- what scope is actually affected and what still works normally
- what least-destructive next step is justified now
- whether the warning was solved, accepted with residue, or merely hidden

A privacy-respecting sync product that hides these distinctions behind footer strings and related-article prose is still under-explaining itself.

## Revision addendum — mobile capture-source and path-class truth after rev0204

Product direction should now explicitly require that AnonSync never let mobile subject truth collapse into whichever platform article or picker flow the operator happened to remember.

The product should instead make four distinctions public everywhere:

- **source class vs generic mobile share**
- **path class vs generic chosen folder**
- **durable-copy sink vs collaborative peer**
- **reacquire path vs generic available later promise**

That means every ordinary mobile surface should be able to answer:

- what exact source kind is under review
- what storage/path class is actually writable or source-only here
- whether the chosen destination is storage-only or collaborative
- what local clearing leaves behind and how bytes can honestly return later

A privacy-respecting sync product that hides these distinctions behind mobile help articles is still under-explaining itself.

## Revision addendum — compromised-seat containment and rebuild truth after rev0205

Product direction should now explicitly require that AnonSync never let compromise response collapse into whichever unlink, reinstall, relink, or support article the operator happened to remember.

The product should instead make four distinctions public everywhere:

- **at-rest protection posture vs live authority posture**
- **narrow subject-local cutoff vs broader cohort rotation**
- **trusted-survivor rebuild vs generic start-over ritual**
- **residual possession vs residual live authority**

That means every serious incident surface should be able to answer:

- what the suspect seat can still do right now
- what the narrowest believable cutoff is
- when broader identity or authority rotation is actually required
- what possession, exposure, and proof gaps remain afterward

A privacy-respecting sync product that hides these distinctions behind support prose is still under-explaining itself.

## Revision addendum — bounded handoff, receive ownership, and cleanup residue after rev0206

The archive should now explicitly preserve four more truths as first-class doctrine:

- **bounded handoff** so file-send issuance never masquerades as live shared-subject creation
- **redemption lane** so open-link claim power, expiry non-powers, and collision results stay adjacent
- **receive inbox** so landing-root ownership is visible instead of scattered across settings and deployment lore
- **transfer history** so row cleanup, local-byte cleanup, expired-row retention, and reissue need stay visibly separate

The guiding rules are now:

1. **Convenient send verbs are not enough.** `Share file`, `Send file`, and `Scan QR` must compile to bounded-handoff truth instead of lightweight share folklore.
2. **Open-link audience is real authority.** If possession of the link is the actual claim basis, the product should say so directly.
3. **Landing roots need an owner.** Desktop defaults, config-owned defaults, and fixed mobile inboxes are different contracts and should remain visible as such.
4. **History residue is not the same thing as bytes or live claim.** Cleanup and expiry should never flatten those three objects into one cheerful `clear` action.


## Revision addendum — support lane, capture depth, and crash custody after rev0207

Another current Resilio pass sharpens the product direction again.

The next ordinary surfaces should not leave support/disclosure truth trapped inside help-center articles, hidden debug files, attachment limits, or NAS shell rituals.
A serious sync product should publish four adjacent answers:

- **Support lane** so private staffed escalation, self-serve forum help, and local-only evidence preservation stop collapsing into one `contact support` story
- **Log capture window** so the product can state what capture family is active, whether restart is still pending, how long evidence must still run, and what local residue is accumulating
- **Report send** so packet membership, send route, size ceilings, and fallback upload lanes remain explicit before commitment
- **Crash artifact** so minidumps, crash reports, and core dumps stop hiding in platform-specific storage and out-of-product rituals

The design goal stays the same: copy Resilio's candor about diagnostic reality, refuse its scattered article ownership of ordinary support truth.


## Revision addendum — space pressure and reclaim proof after rev0208

Product direction should now explicitly require that AnonSync never let storage truth collapse into warning strings, cleanup buttons, or path-lore about hidden folders.

The product should instead make four distinctions public everywhere:

- **pressure floor vs generic low-space mood**
- **byte-class ownership vs generic used space**
- **reviewed reclaim vs generic cleanup**
- **postcondition proof vs generic cleanup complete**

That means every ordinary storage surface should be able to answer:

- what exact floor is active here now
- what byte classes are actually consuming local storage
- what least-destructive reclaim action exists before continuity weakens
- what exact bytes and guarantees changed after apply

A privacy-respecting sync product that hides these distinctions behind warning articles and cleanup folklore is still under-explaining itself.


## Revision addendum — network paths and protocol discipline after rev0209

Product direction should now explicitly require that AnonSync never flatten remote storage into a generic `folder` abstraction.

The product should instead make four distinctions public everywhere:

- **path class vs generic location picking**
- **authoritative mutation lane vs generic multi-app access**
- **detection grade vs vague freshness optimism**
- **admission fitness vs best-effort bind success**

A serious sync product should publish four adjacent answers:

- **Network path class** so local folders, mounted network shares, and UNC-under-service workarounds stop sharing one dishonest folder story
- **Protocol discipline** so mixed direct-plus-Samba mutation risk is reviewed before corruption teaches the lesson
- **Detection grade** so operators know whether this namespace is live-watched, rescan-only, or restart-sensitive
- **Network subject admission** so permission fitness, lock assumptions, and service-identity fallout are reviewed before a bind is accepted

The design goal stays the same: copy Resilio's candor about remote-path reality, refuse its scattered article ownership of ordinary network-path truth.
