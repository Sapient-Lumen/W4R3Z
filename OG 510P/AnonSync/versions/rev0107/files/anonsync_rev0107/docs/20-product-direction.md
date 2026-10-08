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
- **release posture** keeps version, channel, edition family, schema epoch, and rollback truth explicit instead of scattering them across update pages and release notes
- **incoming shares** become visible before they are adopted into local paths
- **path choice** is a per-share workflow, not a device-global linked-folder mode trick
- **path binding and relocation** are compared actions, not loose filesystem side effects
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

### Doctrine 12 — hidden service files are implementation detail, not product contract

Ignore lists, archive/version stores, and other service artifacts may exist internally, but operators should not have to edit or protect hidden control files just to use the product safely.
The product surface should expose:

- effective ignore rules
- drift and consistency state
- service-file damage as health findings
- repair paths when internal metadata is missing or unhealthy

### Doctrine 13 — conflicts should be explicit cases, not magic filenames

Conflicts are normal events in a replicated system.
They should be inspectable and resolvable through supported object surfaces with stable IDs, visible candidates, explicit blast radius, and audit records.
A user should never need to memorize which special filename is safe or unsafe to delete just to resolve an ordinary sync conflict.



### Doctrine 14 — convenience must preserve least privilege

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
