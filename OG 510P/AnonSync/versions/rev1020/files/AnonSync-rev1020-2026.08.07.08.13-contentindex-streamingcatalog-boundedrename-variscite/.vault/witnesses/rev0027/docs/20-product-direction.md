# Product direction

## One-sentence thesis

AnonSync is an **inspectable, scriptable, peer-to-peer sync system** for people who want strong control over trust, materialization, discovery, topology exposure, provenance, decision traces, projection policy, convergence evidence, and recovery state.

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

> a sync system where trust, discovery, materialization, grants, provenance, and recovery are explicit objects with explicit policies and explicit diagnostics.

## The counter-model

The archive is now converging on a clearer counter-model to convenience-first sync tools:

- **linking** forms relationships, not mergers
- **profiles** install explicit policies, not hidden side effects
- **plans** preview mutations before they are committed
- **preflight reports** surface compatibility and downgrade risks before commitment
- **claims** separate visibility and offers from actual local acceptance
- **recovery bundles** make encrypted recovery prerequisites explicit and verifiable
- **incoming shares** become visible before they are adopted into local paths
- **path choice** is a per-share workflow, not a device-global linked-folder mode trick
- **path binding and relocation** are compared actions, not loose filesystem side effects
- **file actions** distinguish fetch, local eviction, and share-wide delete
- **history and restore** are supported control surfaces, not hidden archive rituals
- **ignore rules, conflicts, and projection policies** are supported objects, not hidden control files, placeholder folklore, or magic filenames
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

That yields a more legible audit trail and avoids collapsing awareness into authority.

### Doctrine 17 — recovery readiness should be inspectable before disaster

A sync product should not wait for failure before revealing that its encrypted-recovery story depends on hidden state.
Operators should be able to export, inspect, and verify recovery material ahead of time.

That means the product should expose:

- recovery bundles with clear contents and scope
- sufficiency checks for offline decrypt and device replacement workflows
- explicit warnings when recovery posture has degraded
- ordinary audit/event records when recovery material is exported or rotated

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

## Product conclusion

AnonSync should be **narrower than Resilio**, **more explicit than most GUI-first sync tools**, **overlay-first by default on WAN links**, **honest about bundled privacy runtimes and temporary direct-speed leases**, and **Linux-only for v1 in a concrete filesystem-aware way**.
That is a credible reason for the project to exist.


## Platform scope reminder

Linux is the first-class operating environment for v1.
Windows and macOS parity are explicitly out of scope until the Linux control-plane, filesystem, and bundled-transport contract feel boringly solid.
