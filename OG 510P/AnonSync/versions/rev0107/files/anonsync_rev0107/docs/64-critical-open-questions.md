# Critical open questions

## 0) How aggressive should standing-policy simulation be before previews become too noisy or expensive?

The archive now requires effect buckets, named example subjects, and explicit non-effects for standing-policy edits.
What remains unresolved is the preview budget:

- how many example subjects should appear by default
- when subject-level simulation should be cached versus recomputed live
- whether some very large scopes should show sampled examples first and open a fuller subject list on demand
- how stale a preview may become before apply must force recomputation

This matters because too little simulation recreates folklore, while too much can make ordinary settings review feel heavy and slow.


This file is intentionally short.
It exists so future revisions do not forget the biggest remaining design seams while chasing feature surface.


## 0a) How quickly should remembered approval cool, freeze, or demand touch renewal?

The archive now requires visible freshness classes and cooling reasons for remembered trust.
What remains unresolved is the actual cooling budget:

- how much weight to give `last used` versus `last explicitly reviewed`
- when linked-device-set growth should cool trust faster than simple inactivity
- whether some scope classes should auto-freeze after identity-epoch change instead of merely becoming `stale`
- how much repeated ignored-arrival evidence should matter before future shortcut reuse is blocked

This matters because slow cooling recreates immortal trust memory, while over-aggressive cooling recreates needless approval friction and turns healthy convenience into constant ceremony.


## 0b) How aggressive should subject-level fresh-approval overrides be before share security becomes hidden policy folklore?

The archive now requires a first-class subject-level approval-reuse precedence layer.
What remains unresolved is the actual policy budget:

- when a share/offer should default to `reuse-known-peers-only` versus `fresh-approval-all-peers`
- whether some share templates should inherit a standing reuse preference or always force an explicit per-subject choice
- when a stricter subject-level override should remain one-subject-only versus teaching a broader arrival template
- how much dense/mobile surfaces may compress these override choices before operators stop understanding why old approval was or was not reused

This matters because weak override defaults recreate immortal convenience memory, while over-aggressive fresh-approval rules can make ordinary resharing feel punitive and ceremonial.

## 1) Which I2P router implementation should ship first behind the stable contract?

The archive is clearer that the operator surface should stay runtime-implementation-neutral.
What remains unresolved is which actual I2P helper/router should back v1 first on Linux:

- a Java router bundle behind SAM
- an i2pd-style helper behind SAM or an equivalent stable boundary
- some phased validation strategy that tests both before one becomes the default

This matters for memory footprint, operability, persistence layout, shutdown behavior, and upgrade friction.

## 2) How should transport identities and overlay publication be scoped?

A device may have:

- a durable AnonSync identity
- LAN addresses
- approved clearnet known-host addresses
- a Tor onion identity
- an I2P destination / session identity

The archive still needs to decide how much of that is device-wide, share-scoped, or policy-scoped, and which of those identifiers should ever be published automatically.

## 2a) How much intake review can be compressed before the product recreates `Connect` folklore?

The archive is now clearer that non-trivial claims and adoptions should use one fixed intake grammar, but a sharp ergonomics question remains:

- when may a low-risk incoming share be adopted from one review card without a fuller claim page
- whether portable offer inspection and linked incoming visibility should always create the same explicit claim object or only converge once risk rises
- how much target-path memory or defaults can be reused before the product starts hiding acceptance meaning again
- whether any auto-adopt posture should be allowed for populated paths or authority-changing outcomes

This matters because too much review can make convenience feel ceremonial, while too little recreates exactly the reconnect/custom-path folklore the archive is trying to escape.


## 2b) How pathless may announced shares remain before convenience turns into ambiguity?

The archive is now clearer that `visible here`, `claimed here`, and `bound here` should stay separate.
What remains unresolved is the ergonomics edge:

- how long an announced share should remain prominent before the product assumes the operator really does not want it on this machine
- whether `hide on this machine` should be a quiet presentation rule or a stronger durable local policy
- whether some low-risk constellations may allow one-click claim from the inbox card while still preserving honest path/bind review
- how much remembered path or role state is safe before the product silently recreates default-location ritual

This matters because too little persistence recreates ambient path creation, while too much pathless visibility can make the inbox turn into a second forgotten namespace.

## 3) What is the exact safety model for peer-pinned direct paths and direct-speed leases?

The archive now has known-host records and route leases as first-class concepts.
What remains unresolved is the stricter policy detail:

- should time-bounded direct leases also require byte caps by default or only optionally
- when a stale known-host record should warn versus block
- whether some direct exceptions should require a reviewed plan instead of an immediate lease
- how much remembered endpoint state may survive after a narrowing change before the daemon forces a clear

## 4) How strict should metadata fidelity be for first-class Linux support?

The archive now names support tiers, but there is still real policy work left around:

- which xattr namespaces are required
- how much ACL fidelity is mandatory
- what the default symlink / hardlink / special-file contract should be
- when downgrade should warn versus block

## 5) How should overlay scheduling differ from clearnet scheduling?

Tor and I2P are not just slower versions of direct TCP/UDP.
The daemon may need different behavior for:

- chunk sizing
- prefetch windows
- retry cadence
- concurrency limits
- settlement expectations

## 6) When, if ever, should bundled transport payloads update independently of daemon releases?

This archive still chooses a conservative v1 default: bundled transport updates should ordinarily ride AnonSync releases.
What remains unresolved is the later threshold for changing that rule.

## 7) Should bounded introductions ever auto-link, or should all new peers always stop in pending state?

This revision makes introduction policy explicit, but it does not settle the strongest convenience question:

- should any trusted constellation be allowed to auto-link peers at all
- should introduction always stop in a pending queue
- if limited auto-link exists, what scopes and maximum roles are still safe

## 8) What should survive successor replacement by default: contacts, approvals, grants, or almost nothing?

The archive now treats succession as reviewed continuity, but the default carry-forward policy is still unresolved:

- which remembered contacts should normally survive
- whether future-approval grants should freeze by default
- whether known-host direct paths should always require re-verification on the successor


## 9) How aggressive should the review queue be before it becomes noise?

This revision makes derived review items and a workbench home surface first-class, but one important design choice remains open:

- should the default home view be very strict and surface nearly every degraded or reviewable state
- should it stay quieter and risk operators missing subtle but important conditions
- which findings deserve `now` versus `soon` versus quiet background placement

The right answer matters because a noisy review surface recreates alert blindness, while an over-quiet one recreates hidden-state surprises.

## 10) How much batch power can the workbench safely expose before it starts hiding scope?

This revision makes the batch-action question more explicit, but it is still unresolved:

- which operations can safely batch under one preview/apply step
- when per-subject proof must force a batch to split
- whether the default interface should be conservative enough that advanced operators sometimes find it annoyingly slow

This matters because bulk convenience is one of the fastest ways for a careful interface to regress back into ambiguous `remove`, `approve`, or `apply anyway` behavior.



## 11) How much report surface is enough before the workbench becomes its own kind of noise?

This revision strengthens the idea that many findings should collapse into one shared report language.
What remains unresolved is the balance point:

- how many active reports should be visible by default
- when a report should stay attached to a page versus also appearing in the global report shelf
- whether some low-risk findings should collapse into quiet background summaries instead of standalone reports

The answer matters because too few report surfaces recreates hidden-state surprises, while too many recreates a different kind of operator fatigue.

## 12) Which state-root operations deserve first-class product verbs in v1?

The archive is now clearer that storage root, identity root, and service profile are important operator state, and it now specifies explicit surfaces for them.
What remains unresolved is how much of that should become first-class in v1:

- inspect only
- inspect plus export/import
- inspect plus supported move/attach
- full replacement / re-home workflows at day one

This matters because invisible state roots produce some of the worst recovery surprises, but exposing them poorly could also overcomplicate the early product.

## 13) How online should state-root transition workflows be allowed to remain?

The new state-root spec still leaves one sharp operational question open:

- should move-root always force a maintenance/quiesce boundary
- should some attach/switch actions be allowed live when integrity can be proven
- how much automatic restart or handle-drain behavior is acceptable before the model becomes magical

This matters because fully online transitions are convenient, but they are also one of the easiest ways to blur together “same state moved safely” and “different state happened to become active”.

## 14) How much preservation state should v1 keep by default before it becomes too weak or too heavy?

This revision makes binding repair and preservation posture more explicit, but one policy seam remains open:

- how much local history should exist by default for ordinary repair and restore workflows
- whether peer-origin-only history is acceptable for some roles but too weak for others
- when size caps or retention caps should merely warn versus block risky cleanup or repair
- how much preservation metadata should survive detach or rebinding

This matters because too little retained history recreates hidden surprises, while too much retention can turn ordinary mounts into unexpectedly heavy local state.


## 15) When should share-scope restore or delete always force plan/apply?

The archive is now much clearer about file intent and local deviation, but one threshold still needs product judgment:

- when a share-scope delete should always require review even if preservation looks healthy
- when a share-scope restore can be direct versus plan-bearing
- whether some path classes (for example top-level or widely-shared paths) should always require stronger confirmation
- how much settlement degradation should block restorative or destructive share-wide actions outright

This matters because making these actions too direct recreates silent scope mistakes, while making all of them plan-bearing could make ordinary recovery feel punitive.


## 16) How much recurring-schedule power is safe before presets start hiding too much?

The archive now treats runtime activity truth and recurring windows as first-class state, but one design seam remains open:

- how many presets should exist before they become shorthand for hidden behavior
- whether `maintenance-freeze` should always require plan/apply
- how much delete-propagation control is safe to expose on recurring windows
- whether some route-class scopes should be disallowed or heavily warned by default

This matters because recurring windows are useful, but they can easily turn back into opaque scheduler folklore if they stop showing their real phase effects.

## 17) What should projection tightening guarantee once names were already announced or bytes already materialized?

The archive is now clearer that projection needs receipts and effect reports, but one policy seam remains open:

- when should the product promise future suppression only versus reviewed remote retraction
- whether some namespace-tightening actions should wait for stronger settlement confidence before claiming success
- how much local byte eviction may be bundled into a local-view tighten by default
- whether child-path suppression under already-shared parents should force stronger review automatically

This matters because promising too much would lie about past visibility, while promising too little recreates exactly the placeholder and ignore folklore the archive is trying to replace.


## 18) How strict should settlement witness sets, quiet windows, and receipt reuse be for each action class?

The archive is now clearer that settlement needs policy, barriers, and receipts, but the sharp policy detail is still open:

- which actions really need all writable peers versus a smaller witness set
- how long a satisfied barrier may remain reusable before apply must refresh proof
- whether `degraded-satisfied` should ever be allowed for share-wide destructive actions
- how much quiet-window delay is necessary before cutover, restore, or maintenance can honestly claim readiness

This matters because weak defaults recreate status folklore, while overly strict defaults could make ordinary maintenance feel needlessly punitive.


## 19) How much rollback provenance and conflict detail must v1 retain locally before receipts become too weak?

The archive is now clearer that history entries, conflict cases, and rollback receipts are first-class state, but one policy seam remains open:

- how much per-path provenance should survive after ordinary retention cleanup
- whether source-peer identity and capture-cause should always survive even after bytes age out
- when low-confidence or derived-remote history should warn versus block share-scope restore
- how much loser-handling detail a rollback receipt must keep before later audit becomes misleading

This matters because weak retention recreates support-article archaeology, while excessive retention can make ordinary shares unexpectedly heavy and privacy-hostile.


## 20) How aggressive should portable-subset rewrite/drop defaults be before fidelity stops being honest?

The archive is now clearer that portability needs a durable fidelity contract, but one policy seam remains open:

- when should normalization rewrite, metadata drop, or link blocking be allowed under reviewed warning posture versus blocked outright
- whether the default should prefer strict-native correctness even when that rejects common mixed-path workflows
- how much automatic portable-subset behavior is acceptable before the product starts hiding real semantic loss behind convenience
- which downgrade classes always require a fidelity receipt and which are low-risk enough to batch

This matters because an over-strict product becomes impractical, while an over-flexible one recreates exactly the semantics folklore the archive is trying to replace.

## 21) When should warning-tier network-share targets be allowed at all in v1?

This revision makes reviewed network-share posture more explicit, but one boundary still needs product judgment:

- should SMB/NAS-backed targets ever be allowed for ordinary writable mounts in v1
- whether degraded notifications plus periodic rescan can be acceptable for some intents but always blocked for others
- when mixed local/direct access risk should merely warn versus hard-block
- whether a mount that drifts from local-native to network-reviewed should auto-block high-signal actions until a new fidelity receipt exists

This matters because local-first correctness is part of the project thesis, but real operators will still ask for NAS convenience. The product needs an honest answer rather than an accidental one.


## 22) How aggressive should default pressure and retention policies be before storage honesty turns punitive or too loose?

The archive is now clearer that storage pressure needs a first-class budget model, but one policy seam remains open:

- how high the default soft and hard thresholds should be before new materialization, restore, or large incoming adoption is guarded or blocked
- whether logs/temp remnants should auto-trim by default while history/archive always stays review-required
- when reclaim should prefer evicting cold local materialized bytes versus trimming retained rollback history
- how much storage accounting detail must stay visible before the product becomes noisy rather than honest

This matters because weak defaults recreate low-space folklore, while overly aggressive defaults could make ordinary use feel like constant budget babysitting.


## 23) How much bearer-style power should any portable offer artifact ever have before stronger pinning or claim review becomes mandatory?

The archive is now clearer that delivery encoding should not stand in for authority semantics, but one policy seam remains open:

- when should one-time or short-lived offers still require peer pinning by default
- whether some offer kinds may ever auto-claim into visibility-only state without explicit review
- how much redelegation should be allowed before the artifact stops feeling least-privilege
- whether some high-signal offer classes should always require plan/apply rather than direct issue

This matters because portable convenience is useful, but bearer-like artifacts are one of the easiest ways for a careful model to regress back into “copied the link, therefore authority happened.”


## 24) How aggressive should default transfer fairness, relay-cost posture, and metered budgets be before throughput truth becomes either too magical or too manual?

The archive is now clearer that transfer speed needs a first-class policy and budget model, but one policy seam remains open:

- how much interactive reserve should exist by default before background work becomes starved
- when relay use should merely warn versus spend from an explicit budget versus block outright
- how much automatic LAN exemption is acceptable before “same budget everywhere” stops being legible
- whether per-share and per-peer fairness should be stronger by default than raw throughput maximization

This matters because a weak default recreates speed folklore, while an over-specified one could make ordinary sync feel like constant traffic engineering.


## 25) How aggressively should attention leave the workbench before the product becomes noisy or client-specific?

The archive is now clearer that reports, review lanes, delivery channels, and acknowledgement receipts are separate public state, but one policy seam remains open:

- which severities should stay workbench-only by default versus also leaving through toast, webhook, browser, or other channels
- how much deduplication and quiet-hour suppression is safe before operators miss important time-bounded conditions
- whether delivery failure should itself escalate or merely remain visible in the Attention center
- how much richer clients may optimize presentation before Linux/headless parity starts to erode

This matters because weak defaults recreate badge-lore and missed action, while aggressive defaults recreate alert fatigue and client-specific semantics.


## 26) How broad may one reviewed mutation grant be in v1 before explicit authority becomes either too reusable or too noisy?

The archive now makes a firmer decision that browser/workbench inspection should not automatically imply mutation power, but one product seam remains open:

- which low-risk mutations, if any, can proceed without a fresh grant while still keeping inspect-versus-mutate honesty intact
- whether one grant should normally cover only one reviewed apply, one bounded batch, or a short reusable window
- when stronger user-presence proof should be required for compromise, successor, or destructive-replay actions
- how aggressively endpoint, state-root, or integrity drift should invalidate grants that are still within TTL

This matters because weak defaults recreate ambient browser authority, while overly strict defaults could make ordinary careful administration feel like repeated ceremony.


## 27) How much recovery material may remain daemon-bound before the product becomes either dishonest or too cumbersome?

The archive is now clearer that recovery posture, custody class, invalidation, and continuity claims need first-class public state, but one policy seam remains open:

- when should v1 insist that a workflow be fully portable rather than merely verifiable while the daemon is healthy
- how much split-secret or daemon-bound posture is acceptable before export starts to feel misleading
- whether high-signal device-replacement bundles should require stronger freshness, escrow, or dual-control options by default
- how aggressively rotation, retirement, or state-root drift should invalidate older recovery bundles versus merely downgrade them to warning state

This matters because weak defaults recreate “thought we had recovery” folklore, while overly strict defaults could make ordinary preparation for disaster feel like ceremony instead of support.

## 28) How strict should default channel pinning and mixed-constellation skew rules be before release truth becomes either noisy or too magical?

The archive is now clearer that release posture needs a first-class model, but one policy seam remains open:

- when should mixed-version or mixed-channel constellations merely warn versus block linking, upgrade apply, or high-signal workflow entry
- how aggressively stable should be the default versus candidate or pinned tracks for Linux-first operators
- when should rollback posture downgrade from guarded to unsupported because schema or runtime-bundle drift has moved too far
- how much release-check noise is acceptable before operators stop trusting the surface

This matters because weak defaults recreate upgrade folklore, while overly strict defaults could make ordinary maintenance feel ceremonial instead of trustworthy.



## 29) How aggressive should defaults/profile inheritance be before effective-policy surfaces become either too magical or too manual?

The archive is now clearer that effective policy needs first-class defaults profiles, bindings, origin chains, and receipts, but one policy seam remains open:

- how many subjects should inherit by default before the system starts feeling ambient rather than explicit
- when should a field-level pin be preferred over a domain-level pin, and when should that be considered too fiddly for ordinary operators
- whether `return to inheritance` should normally target one field, one domain, or the whole subject unless the operator narrows it
- how much origin detail should stay visible by default before the interface becomes a wall of provenance chips instead of a working control surface

This matters because weak defaults recreate settings archaeology, while overly elaborate inheritance could make routine policy work feel like programming the product rather than operating it.


## 30) How much diagnostic depth, redaction automation, and evidence retention is safe before supportability becomes either leaky or ceremonial?

The archive is now clearer that diagnostics should use first-class incidents, reviewed evidence bundles, redaction posture, and evidence receipts, but one policy seam remains open:

- how much temporary debug-depth escalation should be allowed before routine troubleshooting starts collecting too much unrelated state by default
- which bundle classes should be exportable automatically versus always requiring explicit redaction review and sealing
- how aggressively secrets, peer identifiers, paths, and local filenames should be auto-redacted before the bundle stops being useful for serious diagnosis
- how long sealed evidence bundles and their local staging material should survive before retention starts conflicting with privacy and storage honesty

This matters because weak defaults recreate hidden-log archaeology and support ritual, while overly strict defaults could make real troubleshooting slow, opaque, or impossible when the system is already under stress.


## 31) How strict should temporary-exception defaults be before the system becomes either sticky or too ceremonial?

The archive is now clearer that temporary exceptions should use first-class override leases, expiry/exhaustion semantics, and override receipts, but one policy seam remains open:

- when should `no expiry` be allowed at all without a stronger review or dual acknowledgement
- how much automatic renewal is acceptable before temporary intent starts drifting into ambient durable state
- which lease families should allow budget exhaustion instead of time-only expiry by default
- how aggressively overlapping exceptions should escalate before the system becomes noisy rather than honest

This matters because weak defaults recreate cleanup-memory folklore, while overly strict defaults could make ordinary maintenance and troubleshooting feel ceremonial instead of trustworthy.


## 32) How much authority convenience should a personal constellation get before it stops being least-privilege?

The archive is now clearer that a convenience-linked set of devices needs its own explicit constellation and authority-domain model, but one policy seam remains open:

- which member classes should exist by default versus only by advanced review
- whether some classes may approve future claims or successor actions across the constellation at all
- how strict the default visibility posture should be for newly offered shares on phones, appliances, and recovery-only members
- when a local disconnect or cleanup action should automatically stop and demand a stronger scope review because the same share is present across many members

This matters because personal-device convenience is valuable, but it is also one of the fastest ways for a sync product to quietly collapse membership, visibility, and owner power back into ambient identity magic.


## 33) How strong should publication-narrowing guarantees be before disclosure truth becomes noisy or dishonest?

The archive is now clearer that disclosure needs first-class audience/fact matrices, residual-disclosure findings, and disclosure receipts, but one policy seam remains open:

- when should the product be allowed to claim “effectively private again” versus only “future publication stopped”
- how much cache/provider/peer residue detail should remain visible by default before the disclosure surface becomes too noisy
- whether some narrowing actions should require endpoint or artifact rotation by default rather than only cache clear or quiet-window wait
- how much constellation/share-scoped fact separation is necessary before disclosure previews stop being hand-wavy

This matters because weak defaults recreate tracker/LAN folklore, while overly elaborate residue reporting could make ordinary route changes feel more ceremonial than legible.


## 34) How strict should default exit semantics be before departure truth becomes either noisy or too magical?

The archive is now clearer that exit intent should use first-class exit plans, residue findings, and exit receipts, but one policy seam remains open:

- when should `decommission` be allowed to preserve recovery material by default versus forcing explicit keep/discard choices
- how much unresolved remote or time-bound residue is acceptable before an exit may still be called “complete” rather than “applied with residue”
- whether some exit classes should always force follow-up review when offline peers or remote providers could still retain disclosure or byte residue
- how much ergonomics may stay in domain-specific verbs before the unified exit contract starts disappearing behind aliases again

This matters because weak defaults recreate uninstall and remove folklore, while overly ceremonial defaults could make ordinary cleanup feel harder than the risk actually warrants.


## 35) How much one-click automation is safe in exit and replacement flows before the interface starts hiding scope?

The archive is now clearer that exit needs a fixed review grammar and channel parity, but one product seam remains open:

- when may follow-up actions such as token rotation, successor binding, reclaim-plan creation, or route cleanup be bundled into one reviewed apply step versus remaining separate
- how much automation is acceptable when some residue is purely time-bound but other residue still depends on offline-peer observation
- whether the default should strongly prefer one exit intent per review, even when experienced operators want a faster compound workflow
- how much batching is safe for multi-device retirement or replacement waves before the workbench starts hiding outliers behind one reassuring summary

This matters because weak defaults recreate remove/uninstall folklore, while overly strict defaults could make obvious, repetitive decommission work feel ceremonial instead of trustworthy.


## 36) How lightweight may personal-device joins become before the product starts hiding blast radius again?

The archive is now clearer that device joining should use a fixed reviewed join grammar, but one product seam remains open:

- when may a clearly low-risk fresh device join skip a full review and use a compressed path instead
- how much automatic member-class suggestion is acceptable before class/default decisions start feeling ambient rather than chosen
- whether some joins should always be diverted into migration or replacement workflows once existing identity or share state is detected
- how much immediate visibility summary is enough before the join surface becomes either too noisy or too hand-wavy

This matters because weak defaults recreate `link device` folklore, while overly strict defaults could make obviously safe same-person joins feel ceremonial instead of trustworthy.


## 37) When should successor cutover and state-root re-home share one workflow versus branch early?

The archive is now clearer that both actions need one fixed cutover review grammar, but one product seam remains open:

- when may a same-root runtime/profile re-home use a safely compressed cutover path instead of the full successor ceremony
- when should detected existing state on the candidate force predecessor/candidate comparison rather than ordinary attach/import
- how much residue and revocation truth must remain visible when the predecessor is already dead or permanently offline
- whether verified recovery bundles should be mandatory for some successor classes or only for higher-signal continuity claims

This matters because weak defaults recreate migration/install folklore, while over-unifying every root move and hardware replacement could make small, honest re-home work feel more ceremonial than trustworthy.


## 38) How aggressive should default compromise containment be before safety turns into disruptive magic?

The archive is now clearer that trust incidents need one fixed containment grammar, but one policy seam remains open:

- when should a newly opened case auto-freeze sessions, route leases, portable offers, or future approvals before the operator reviews it
- whether suspected theft should default toward continuity-preserving successor preparation, clean-break posture, or neutral freeze-first posture
- how much local or remote residue uncertainty is acceptable before the receipt must stay explicitly provisional
- when repeated stale-device reappearance should escalate from visibility annoyance to mandatory containment review

This matters because weak defaults recreate emergency support ritual, while overly aggressive defaults could turn suspicion or false alarms into self-inflicted outages.


## 39) How conservative should stale-return defaults be before re-entry honesty turns punitive or too magical?

The archive is now clearer that long-offline or chronology-uncertain return should use first-class re-entry cases and receipts, but one policy seam remains open:

- how long dormancy or how much evidence drift should automatically force reviewed re-entry instead of ordinary status recovery
- when should chronology uncertainty downgrade a subject to read-only observation by default versus blocking it outright
- how much divergence/source-availability fallout should be acceptable before the product must divert into merge review, successor cutover, or compromise handling
- whether repeated hide/reappear patterns should automatically strengthen suspicion posture or remain a low-grade nuisance until other evidence appears

This matters because weak defaults recreate peer-counter and archive folklore, while overly strict defaults could make harmless laptop wakeups or long-trip returns feel ceremonial instead of trustworthy.


## 40) How aggressive should destructive-replay review defaults be before consent honesty becomes either noisy or too magical?

The archive is now clearer that high-signal remote delete, overwrite, or revert waves should use first-class destructive-replay cases and receipts, but one policy seam remains open:

- what delete or overwrite thresholds should automatically force reviewed destructive-replay handling instead of ordinary sync progress
- when preserved history is strong enough that a wave may use a safely compressed review versus a full danger sheet
- whether protected paths, custody-tagged shares, or weak source confidence should always block destructive apply until stronger witness exists
- how much batching is safe when one review covers many directories or many peers without hiding dangerous outliers

This matters because weak defaults recreate pause/archive folklore, while overly aggressive defaults could make routine mirror maintenance or legitimate cleanup waves feel ceremonial instead of trustworthy.


## 41) How much low-risk conflict automation is safe before adjudication honesty becomes either noisy or too magical?

The archive is now clearer that non-trivial conflicts should use first-class reviewed adjudication and receipts, but one policy seam remains open:

- when ordinary content-concurrency conflicts may use a safely compressed review versus always opening the full adjudication sheet
- whether some semantic classes such as delete-vs-modify, case/unicode collision, or capability mismatch should always block one-click resolution
- how much automatic loser preservation should be mandatory before the product may offer a faster resolve path
- when repeated path/collision conflicts on warning-tier filesystems should automatically divert into portability repair instead of letting operators keep resolving symptoms

This matters because weak defaults recreate suffix and cleanup folklore, while overly strict defaults could make harmless collaborative conflicts feel ceremonial instead of trustworthy.


## 42) How much same-host derivation convenience is safe before topology and lifecycle honesty become too magical?

The archive is now clearer that non-trivial same-host derivations should use first-class reviewed local-derivation cases and receipts, but one policy seam remains open:

- when an obviously disjoint local-native target may use a safely compressed review versus always opening the full local-derivation sheet
- whether warning-tier targets such as removable or network-reviewed paths should always block writable derivatives by default
- how much source-materialization weakness is acceptable before a derivative must narrow to cache-only or wait for fuller byte availability
- when multi-target fanout from one source should automatically strengthen topology review instead of feeling like repeated low-risk convenience

This matters because weak defaults recreate local-share and path-picker folklore, while overly strict defaults could make harmless same-machine branching feel ceremonial instead of trustworthy.

## 43) How much low-risk access-change automation is safe before authority-boundary honesty becomes either noisy or too magical?

The archive is now clearer that non-trivial live permission changes should use first-class reviewed authority-mutation cases and receipts, but one policy seam remains open:

- when an obviously local boundary change such as `rw` to `ro` with no delegation fallout may use a safely compressed review versus always opening the full authority-mutation sheet
- whether widening write access should always force stronger review when the subject belongs to a personal constellation, has dependent local derivations, or sits on warning-tier targets
- how much dependent fallout may auto-apply before the product must split follow-up review items instead of hiding them behind one reassuring summary
- when imported or legacy authority substrates should block mutation outright until migration is reviewed rather than trying to coerce the request into the nearest available class

This matters because weak defaults recreate owner, disconnect, and remove/re-share folklore, while overly strict defaults could make harmless day-to-day access tuning feel ceremonial instead of trustworthy.


## 44) How much low-risk topology convenience is safe before graph honesty becomes either noisy or too magical?

The archive is now clearer that non-trivial nested, overlapping, moved, or root-boundary-sensitive graph relationships should use first-class reviewed topology cases and receipts, but one policy seam remains open:

- when an obviously disjoint or same-root path change may use a safely compressed review versus always opening the full topology sheet
- whether any child-inside-parent or overlap relation should always force full review even when the operator is intentionally building it
- how much propagation-shape automation is acceptable before the product starts hiding double-indexing, piggyback, or re-download consequences behind reassuring summaries
- when allowed-root or whitelist expansion should be reviewed as ordinary topology work versus escalated into stronger filesystem or policy review

This matters because weak defaults recreate nested-share, loop-warning, and reconnect folklore, while overly strict defaults could make harmless path organization feel ceremonial instead of trustworthy.


## 45) How much low-risk contention automation is safe before coordination honesty becomes either noisy or too magical?

The archive is now clearer that non-trivial lock pressure, burst-save delay, mixed external-writer risk, and quiesce actions should use first-class reviewed contention cases and receipts, but one policy seam remains open:

- when an obviously local-native burst-save delay may use a safely compressed review versus always opening the full contention sheet
- whether warning-tier network-reviewed mounts with mixed SMB access should always force stronger quiesce or fidelity escalation by default
- how much automatic release is acceptable once locks clear before the product starts hiding meaningful resume conditions
- when repeated contested writes should escalate from coordination nuisance to destructive-replay, topology, or compromise-adjacent review because the writer story has stopped being honest enough

This matters because weak defaults recreate locked-file, retry, and SMB folklore, while overly strict defaults could make harmless editor save bursts feel ceremonial instead of trustworthy.


## 46) How much low-risk host-fit automation is safe before scale honesty becomes either noisy or too magical?

The archive is now clearer that non-trivial RAM pressure, watcher ceilings, indexing cost, storage headroom, and path blockers should use first-class reviewed capacity-fit cases and receipts, but one policy seam remains open:

- when an obviously comfortable host and modest share may use a safely compressed review versus always opening the full capacity-fit sheet
- whether degraded-freshness outcomes such as metadata-only or periodic-rescan admission should always force stronger acknowledgement when the original request was full materialization
- how much automatic narrowing is acceptable before the product starts hiding meaningful local-role change behind reassuring `Connect` or `Add` language
- when repeated fit failures on one host should divert into topology, storage, or device-placement guidance instead of keeping the operator inside a host-local warning loop

This matters because weak defaults recreate out-of-memory, watcher, and re-add folklore, while overly strict defaults could make harmless moderate-size admissions feel ceremonial instead of trustworthy.


## 47) How much low-risk bring-up automation is safe before continuity and control-entry honesty become either noisy or too magical?

This revision makes reviewed bring-up explicit, but one threshold still needs product judgment:

- when a fresh local-only `init` may stay direct
- when discovered prior state should always force full bring-up review instead of a friendly reopen
- whether reviewed LAN/proxy exposure may ever be bundled with first attach
- how much recover/import shortcutting is safe before startup drifts back into install/config folklore

This matters because too much compression recreates installer, config-mode, and bind-address magic, while too much ceremony makes obvious fresh starts feel heavier than their real risk.


## 48) How much low-risk control repair can stay compressed before browser-independent honesty becomes either noisy or too magical?

This revision makes browser/control degradation and auth repair much more explicit, but one threshold still needs product judgment:

- when an obviously expired browser session may use a safely compressed repair versus always opening the full auth-repair sheet
- whether self-signed or local-only trust bootstrap may ever be streamlined without normalizing unsafe browser ritual
- how much automatic client-fallback is acceptable before the product starts hiding meaningful channel or trust changes behind reassuring summaries
- when repeated browser/client degradation should escalate into broader bring-up, state-root, or compromise review because the problem has stopped being ordinary access maintenance

This matters because weak defaults recreate missing-button, click-through, and settings-file folklore, while overly strict defaults could make harmless session refresh feel ceremonial instead of trustworthy.


## 49) How much low-risk target-custody automation is safe before host-local ownership honesty becomes either noisy or too magical?

This revision makes target custody, foreign-marker inspection, and exclusive-bind review more explicit, but one threshold still needs product judgment:

- when an obviously same-lineage local target may use a safely compressed review versus always opening the full custody sheet
- whether removable-media reuse should ever auto-narrow into inspect-only or always stop for explicit operator choice
- how much cleanup automation is acceptable once markers look stale before the product starts hiding meaningful evidence loss behind reassuring retry language
- when repeated target collisions on one host should escalate into broader state-root, successor, or compromise review because the ownership story has stopped being ordinary path management

This matters because weak defaults recreate hidden-marker, duplicate-instance, and delete-and-re-add folklore, while overly strict defaults could make harmless same-lineage reuse feel ceremonial instead of trustworthy.


## 50) How much low-risk cross-channel handoff can stay compressed before channel-parity honesty becomes either noisy or too magical?

This revision makes safety-critical channel parity and review handoff much more explicit, but one threshold still needs product judgment:

- when an obviously degraded browser/workbench action may offer a one-step `Continue in CLI` handoff versus always opening the full parity sheet
- whether some inspect-only channel shifts can stay nearly invisible without training operators to miss meaningful trust or endpoint changes
- how much grant or gate continuity may survive a channel change before the product starts hiding real differences in user presence, trust bootstrap, or endpoint binding
- when repeated channel degradation should escalate into broader bring-up, compromise, or support-mode review because the problem has stopped being ordinary client variance

This matters because weak defaults recreate `use another browser`, `try the desktop app`, and `switch to CLI` folklore, while overly strict defaults could make harmless channel changes feel ceremonial instead of trustworthy.


## 51) How much low-risk runtime-seat switching can stay compressed before continuity/reachability honesty becomes either noisy or too magical?

The archive is now clearer that current-user, service-style, Local System, maintenance, and similar execution seats should use first-class reviewed seat-switch cases and receipts, but one policy seam remains open:

- when should a same-root runtime switch be allowed to stay compressed because no reachable targets or freshness guarantees change
- whether any target loss should always force full seat-switch review instead of a lighter acknowledgement
- when rescan-only or other degraded workaround posture is acceptable versus always blocked for the requested intent
- how much automatic rebind help is safe before the product starts hiding the difference between continuity and a different host-local world

This matters because weak defaults recreate service-account, mapped-drive, and UNC folklore, while overly strict defaults could make harmless backgrounding or maintenance-seat changes feel ceremonial instead of trustworthy.

## 52) How much low-risk relabeling can stay compressed before naming honesty becomes either noisy or too magical?

The archive is now clearer that mutable labels, stable subject handles, and cryptographic authority should use first-class continuity reviews and receipts, but one policy seam remains open:

- when should an obvious typo fix be allowed to apply from inline UI versus always opening the full continuity sheet
- how much alias history should remain peer-visible by default versus local-only for audit and search
- whether some same-authority relabels may safely preserve future-approval memory without re-showing broader blast radius every time
- when repeated same-person continuity claims should escalate into successor or compromise review because the naming story has stopped being ordinary hygiene

This matters because weak defaults recreate `rename means unlink`, `same name means same device`, and convenience-link folklore, while overly strict defaults could make harmless label cleanup feel ceremonial instead of trustworthy.



## 53) How much low-risk layout cleanup or annex migration can stay compressed before data/control-separation honesty becomes either noisy or too magical?

The archive is now clearer that live namespace, managed annex bytes, rollback/history state, metadata-carry sidecars, and temp-transfer residue should use first-class layout reviews and receipts, but one policy seam remains open:

- when should an obviously clean external-annex migration be allowed to apply from inline UI versus always opening the full layout sheet
- whether some temp-transfer cleanup may stay one-step while history or metadata-carry cleanup always forces full preservation-aware review
- how much explicit in-tree managed visibility is acceptable for advanced users before the product starts normalizing hidden-control-state clutter again
- when repeated mixed-managed layouts should escalate into broader custody, fidelity, or support review because the share is no longer in an ordinary operating posture

This matters because weak defaults recreate hidden-dotfolder, archive-browsing, and temp-file folklore, while overly strict defaults could make harmless annex hygiene feel ceremonial instead of trustworthy.


## 54) How much low-risk semantic optimization can stay compressed before guarantee honesty becomes either noisy or too magical?

The archive is now clearer that detection freshness, rename continuity, diff behavior, verification posture, and degraded-target accommodations should use first-class semantic-runtime reviews and receipts, but one policy seam remains open:

- when should an obviously semantic-neutral tuning change stay inline versus always opening the full optimization sheet
- whether some temporary degraded-target acceptances may stay one-step while others always force full reviewed downgrade
- how much automatic restoration to a stronger profile is safe before the product starts hiding meaningful catch-up or re-verification work
- when repeated semantic downgrades should escalate into broader fidelity, capacity-fit, or support review because the subject is no longer in an ordinary operating posture

This matters because weak defaults recreate advanced-toggle, watcher-warning, and SMB-folklore ergonomics, while overly strict defaults could make harmless tuning feel ceremonial instead of trustworthy.



## 55) How much low-risk recall or retained-copy attestation can stay compressed before recall honesty becomes either noisy or too magical?

The archive is now clearer that future authority stop, retained-copy reality, encrypted-backup usefulness, and stronger recall claims should use first-class retained-replica reviews and receipts, but one policy seam remains open:

- when should an obvious `future updates stop only` case stay inline versus always opening the full recall sheet
- whether some encrypted-backup preservation actions may stay one-step while any remote-delete request always forces full reviewed recall
- how much automatic observation update is safe before the product starts hiding meaningful uncertainty about what peers still retain
- when repeated revoke/remove churn should escalate into broader authority, exit, or stewardship review because the share is no longer in an ordinary operating posture

This matters because weak defaults recreate disconnect/remove folklore, while overly strict defaults could make harmless collaborator offboarding feel ceremonial instead of trustworthy.


## 56) How much low-risk epoch rotation can stay compressed before authority-convergence honesty becomes either noisy or too magical?

The archive is now clearer that new share authority issuance, stale capability residue, derivative/local-share migration, and mixed-epoch convergence should use first-class epoch-rotation reviews and receipts, but one policy seam remains open:

- when should an obvious same-class reissue stay inline versus always opening the full epoch sheet
- whether any stale-capability residue should always force full review or whether artifact-only residue may stay lightly compressed
- how much automatic derivative/local-share migration help is safe before the product starts hiding meaningful rebuild or reissue obligations
- when repeated mixed-epoch drift should escalate into broader compromise, recall, or stewardship review because the share is no longer in an ordinary operating posture

This matters because weak defaults recreate key-change, re-share, and folder-class folklore, while overly strict defaults could make harmless bounded reissue feel ceremonial instead of trustworthy.


## 57) How much low-risk observer/read-only compression can stay inline before observer honesty becomes either noisy or too magical?

The archive is now clearer that `observer`, `read only`, `viewer`, and similar labels should use first-class observer-posture reviews and receipts, but one policy seam remains open:

- when should an obviously safe posture relabel stay inline versus always opening the full observer sheet
- whether some path-revert repairs may stay one-step while any projection/class-limited repair always forces full reviewed explanation
- how much automatic serve-rights inference is safe before the product starts hiding meaningful differences between non-authoritative writing and non-serving replicas
- when repeated observer/read-only drift should escalate into broader authority, derivation, or semantic-runtime review because the subject is no longer in an ordinary operating posture

This matters because weak defaults recreate permission-label folklore, while overly strict defaults could make harmless bounded viewer changes feel ceremonial instead of trustworthy.


## 58) How much low-risk non-empty-target reconciliation can stay inline before merge honesty becomes either noisy or too magical?

The archive is now clearer that pre-existing local material, target lineage, same-path divergence, chronology posture, and encrypted-target reuse should use first-class reconciliation reviews and receipts, but one policy seam remains open:

- when should an obviously same-lineage, all-identical rebind stay inline versus always opening the full reconciliation sheet
- whether any same-path divergent bytes should always force full review or whether some guarded low-risk classes may stay lightly compressed
- how much timestamp or mtime evidence may auto-rank candidates before the product starts hiding weak chronology or weak authority posture behind convenience
- whether encrypted-target reuse can ever be one-step or whether it should always force a preservation-aware full review

This matters because weak defaults recreate `Folder not empty`, reconnect, and pre-populated-folder folklore, while overly strict defaults could make harmless same-lineage rebinds feel ceremonial instead of trustworthy.


## 59) How much low-risk fetchability review can stay inline before on-demand honesty becomes either noisy or too magical?

The archive is now clearer that placeholder-visible or selectively materialized paths should use first-class fetchability reviews and receipts, but one policy seam remains open:

- when should an obviously multi-witness, online-backed path show inline fetchability chips versus always opening the full fetchability sheet
- whether evicting a path that is currently the only confirmed full copy should always force full review or whether any bounded exceptions are safe
- how much last-seen/offline witness evidence may count before the product starts hiding real local-last-copy risk behind `available later` language
- when ghost/stale-announcement handling should stay one-step versus always forcing preserve, re-witness, or retirement review

This matters because weak defaults recreate placeholder folklore and ghost-file warnings, while overly strict defaults could make harmless fetch/pin/evict work feel ceremonial instead of trustworthy.



## 22) How much file-availability compression is safe in dense views and small clients?

This revision makes the concrete availability surface much sharper, but one design seam remains open:

- how many of the five answer-strip truths can collapse into one dense list row before last-copy risk becomes too easy to miss
- whether small/mobile clients may compress witness posture and fetchability posture together, or whether that recreates exactly the misleading `available on demand` story the archive is trying to avoid
- how much mixed-risk subtree batching may stay one action in low-risk contexts before the product starts hiding guarded rows again

This matters because a too-dense interface becomes misleading, while a too-expanded one becomes noisy and ceremonial.

## 60) When may the product offer one-step restore from history instead of a fuller timeline review?

This revision makes history-backed-only availability more explicit, but one policy seam remains open:

- when a local history candidate is strong enough that `Restore from history` may stay inline
- when provenance gaps or stale retention evidence should force a fuller rollback/timeline sheet first
- whether restoring from history into a still-visible placeholder path should automatically require settlement or collision checks
- how much restore convenience is safe before the product starts hiding that the swarm no longer backs the bytes

This matters because weak defaults recreate optimistic on-demand folklore, while overly strict defaults could make obviously safe local recovery feel ceremonial instead of trustworthy.


## 61) How many row-level availability actions may stay one-click before the interface starts hiding too much review?

This revision makes the row/review split much sharper, but one product seam remains open:

- which `safe-now` actions may stay direct with only lightweight confirmation
- when `restore-from-history` is strong enough to remain nearly inline versus always opening the full review pane
- whether stale-visibility retirement can ever stay one-step in dense/mobile clients without becoming accidental cleanup
- how much authority or receipt scope one row-level action may reuse before the product starts feeling magically stateful again

This matters because too many one-click actions recreate hidden-risk convenience, while too few turn an otherwise legible operator product into needless ritual.

## 62) How much low-risk approval convenience can stay inline before seat and blast-radius honesty becomes either noisy or too magical?

The archive is now clearer that pending requests, acting seats, one-subject approval, and future approval memory should use first-class approval reviews and receipts, but one policy seam remains open:

- when should an obviously narrow `approve once` path stay inline versus always opening the full acting-seat sheet
- whether any creation of future approval memory should always force full review or whether some tightly bounded cases may stay lightly compressed
- how much seat reuse is safe before the product starts hiding meaningful differences between `this member spoke` and `the constellation now remembers this` 
- when repeated wider-scope approvals should escalate into broader constellation or trust-boundary review because the product is no longer in an ordinary approval posture

This matters because weak defaults recreate linked-device owner folklore and remembered-approval magic, while overly strict defaults could make obviously narrow collaborator approval feel ceremonial instead of trustworthy.


## 23) How much standing approval should survive, auto-match, and auto-admit by default before remembered trust becomes magical again?

The archive is now clearer that approval memory needs explicit match objects and guarded outcomes, but one policy seam remains open:

- how long standing approval should live by default before expiry or renewed review is required
- whether last-use age should narrow a match from `claim-suggested` back to `fresh-review`
- when a remembered approval may admit only identity trust versus also stage a claim suggestion
- whether some share classes should categorically refuse remembered-trust reuse even when identity matches cleanly

This matters because too little remembered trust recreates needless friction, while too much recreates the very `approved before therefore connected here now` magic the archive is trying to avoid.


## 63) How much future-arrival automation is safe before seat-level convenience becomes magical mode-switching again?

The archive is now clearer that current share posture and future-arrival policy should be separate public objects, but one product seam remains open:

- when should a reviewed seat be allowed to auto-claim later arrivals versus only queue them as announced or claim-suggested
- whether any path template may ever auto-bind without a fresh local check, or whether that would immediately recreate default-location folklore
- how much collision handling may stay automatic before the product starts hiding path-provenance truth behind `helpful` suffixing or relocation
- when a seat-level automation profile should be considered strong enough that changing it always forces a full review instead of an inline default flip

This matters because too little automation recreates needless per-arrival ceremony, while too much recreates the very `change one mode and hope the right thing happens` magic the archive is trying to avoid.


## 2c) How aggressively may remembered roots and path templates prefill placement before the product recreates duplicate-folder folklore?

The archive is now clearer that a suggested path is not yet a bind and that collision classes need explicit review.
What remains unresolved is the ergonomics edge:

- when should the product rank one default-root candidate above another remembered candidate
- whether `same-lineage likely` may ever enable one-click adopt on a small trusted seat, or whether compare/adopt review should always remain explicit
- whether a template may propose a suffix-adjusted candidate at all, or whether any suffix proposal should always open full placement review
- how much collision evidence is enough to keep a suggestion card compact instead of immediately escalating into the larger custody/compare surface

This matters because too little suggestion memory recreates repetitive path picking, while too much suggestion authority recreates exactly the duplicate-path and reconnect folklore the archive is trying to escape.


## 20) How much standing-template refresh power is safe before seat defaults start mutating live work too quietly?

The archive is now clearer that standing future-arrival templates need their own reviewed object, but one policy seam is still open:

- should unclaimed draft arrivals stay unchanged by default forever, or only until some freshness boundary
- should claimed-but-unbound arrivals ever be eligible for standing-template refresh in v1
- how much scope preview is enough before a seat-template edit becomes too noisy to use
- when should changing a drafted root require stronger review because many open drafts would be affected

This matters because too little refresh power recreates stale draft clutter, while too much refresh power recreates the very hidden default-mutation problem the archive is trying to avoid.


## 64) How much arrival-causality detail should be visible by default before explanation surfaces become either noisy or too magical?

The archive is now clearer that later-arrival subjects need first-class explanation surfaces with causes, non-causes, counterfactuals, and proofs, but one policy seam remains open:

- how many causal steps should render by default before the drawer becomes a miniature audit log instead of a working explanation
- when should counterfactuals stay lightweight versus opening the fuller policy-origin or approval-memory sheet
- how aggressively should the product highlight `what did not happen` before expert users start treating it as repetitive chrome
- how much explanation caching is acceptable before policy mutation or later local acts require recomputation

This matters because weak defaults recreate exactly the state-archeology problem the archive is trying to escape, while overly exhaustive defaults could turn every simple arrival card into a wall of provenance.



## 65) How much standing-policy lineage should stay visible by default before history becomes noisy?

The archive is now clearer that standing-policy families need explicit version lineage and per-subject attribution, but one design seam remains open:

- how many superseded versions should render inline before dense/mobile clients collapse them behind `more history`
- when should subject attribution be live-recomputed versus cached with periodic invalidation
- how aggressively should the product label subjects as `grandfathered` before mature installations become visually noisy
- whether one semantic compare is enough by default or whether field-level diffs should always stay one click away

This matters because too little lineage recreates settings archaeology, while too much lineage could make ordinary arrival surfaces feel like audit consoles.



## 66) How much post-lineage drift should be surfaced by default before realignment queues become noisy?

The archive is now clearer that standing-policy families need explicit drift classification and reviewed realignment, but one design seam remains open:

- how aggressively should the product surface `refresh-eligible` rows before mature seats feel permanently in cleanup mode
- when should `keep grandfathered` remain a lightweight reviewed choice versus always creating a durable exception pin
- how much split-batch actioning is enough before the queue becomes too fragmented to use comfortably
- whether older intentional exceptions should expire into re-review automatically or remain durable until manually revisited

This matters because too little drift surfacing recreates policy archaeology, while too much could make ordinary operator work feel like perpetual inbox triage.


## 22) How aggressively should intentional exceptions age back into attention before the queue becomes noisy?

The archive now makes exception aging and re-review first-class, but one policy seam remains open:

- what the default review horizon should be for kept-grandfathered outcomes versus pinned exceptions
- when `due soon` should merely raise attention versus block adjacent batch mutations
- whether some scopes should forbid `no expiry` entirely while others allow it with stronger acknowledgement
- how much automatic grouping by seat, scope, or subject kind is necessary before mature installations become noisy

This matters because weak horizons recreate silent forever-policy, while overly aggressive re-review can turn every careful exception into recurring friction.


## 17) How much approval-memory lineage detail should dense/mobile surfaces keep visible by default?

The archive now requires remembered approval to be both fresh and attributable.
What remains unresolved is how much of that provenance should stay visible without opening a full trace pane:

- should dense rows show only current head + latest mutation, or also origin seat/horizon chips
- when should a later subject automatically open the authorization-trace compare instead of a simpler arrival explanation
- how aggressively should the product collapse older lineage nodes on mobile without hiding the difference between `origin`, `renewed`, `narrowed`, and `frozen`
- when should missing origin proof force immediate `unknown` prominence versus a quieter degraded badge

This matters because too little provenance recreates `approved before` folklore, while too much visible history can overwhelm the very surfaces meant to make standing trust legible.

## 18) How aggressively should remembered-trust families split when the underlying constellation changes?

The archive is now clearer that remembered approval needs explicit rebase after certificate takeover, hidden-device return, re-link, or other linked-device mutation, but one policy seam remains open:

- when should same-person continuity be strong enough to keep one family head instead of forcing child-family creation
- whether hidden-device return should merely cool descendant reuse, require fresh approval immediately, or depend on dormancy/risk class
- how much descendant churn can stay compressed in one rebase review before the product must split into several smaller trust-family reviews
- when historical explanation should remain visible after future descendant reuse is frozen or revoked

This matters because too little splitting recreates silent trust carry-forward, while overly aggressive splitting could make harmless constellation maintenance feel like identity surgery.

## 19) How much present-tense proof should descendant liveness require before convenience returns?

The archive is now clearer that remembered-trust family membership is not the same thing as current liveness, but one policy seam remains open:

- when should `recently-live` be enough to count a descendant as a byte source again, and when should direct live proof be mandatory
- whether approval-seat liveness should require stronger proof than byte-source liveness for the same descendant
- how aggressively stale-hidden descendants should disappear from routine lists versus staying visible as cautionary history
- when a reappeared descendant should remain `guarded` versus dropping all the way to `unknown`

This matters because too little proof recreates `known device = currently safe convenience`, while too much proof could make ordinary peer churn feel like a constant demand for re-attestation.

## 20) How much proof should descendant action eligibility require before live convenience turns back on?

The archive is now clearer that remembered-trust family membership and descendant liveness are still weaker than per-subject role eligibility, but one policy seam remains open:

- when should byte-source eligibility be allowed on `recently-live` evidence versus requiring direct fresh byte proof
- whether approval-seat eligibility should always require stronger proof than byte-source eligibility for the same descendant and subject
- how aggressively `eligible-after-proof` rows should stay visible before mature installations become noisy
- when a descendant should remain explanation-only for one subject even while it is fully eligible for another

This matters because too little proof recreates `known live device = can act here now`, while too much proof could make ordinary trusted meshes feel like every later arrival requires a miniature ceremony.


## 26) When should a successful invitation promote durable remembered approval beyond its first subject by default?

The archive now separates offer-artifact lifetime from durable trust promotion, but one product seam still needs real judgment:

- should most invitation artifacts default to `subject only` unless an operator explicitly promotes them
- whether some personal-constellation or tightly-scoped collaboration templates may safely default to `reviewed seat only` or `family reuse candidate`
- how strongly single-use or expiring invitations should bias the product against broader promotion even after a successful first claim
- when an operator should be nudged to freeze broad promotion back down to `subject only` after long dormancy or drift

This matters because promoting too eagerly recreates silent convenience-memory sprawl, while promoting too reluctantly could make ordinary trusted collaboration feel unnecessarily repetitive.

## 27) When should sender intent be strong enough to block a successful redeemer mismatch by default?

The archive now separates portable-offer lifetime, actual redeemer identity, and durable trust promotion, but one policy seam still needs real judgment:

- should most offers default to weak `named human hint` posture unless a stronger reviewed-seat expectation is explicitly chosen
- when should `unexpected redeemer` be hard-blocked versus allowed to continue into `accept subject only` review
- how strongly one-time or expiring offers should bias the product against accepting a mismatched redeemer even when approval proof is strong
- whether some trusted personal-constellation templates may safely default to `family expected`, while sensitive collaboration templates should default to `reviewed seat expected`

This matters because weak sender-intent defaults recreate `whoever got the link is close enough`, while overly strict defaults could make ordinary secure collaboration feel fragile or ceremonial.


## 28) When should a partially consumed portable artifact default to reissue instead of staying live?

The archive now separates sender intent, actual redeemer identity, shared artifact budget, and per-attempt trust fanout, but one policy seam still needs real judgment:

- after one or two successful redemptions, when should the product start recommending `reissue new artifact` by default
- should suspicious or unexpected failed attempts increase that pressure even if they did not consume budget
- when is it acceptable to keep using a partially consumed artifact because all successful attempts remained narrow and well-explained
- should some templates auto-freeze broader promotion once a second distinct redeemer has already consumed the same artifact

## 29) When should familiar redemption attempts collapse into old slots versus consume fresh ones?

The archive now separates raw artifact budget from redemption-equivalence judgment, but one policy seam still needs real judgment:

- when should `same reviewed seat` collapse by default versus still consume a fresh slot for a genuinely new governed subject
- whether `same reviewed family` should ever collapse automatically, or always force stronger review than same-seat repeats
- how much weak human-hint overlap should matter before the product stops recommending `require new artifact`
- when suspicious failed attempts should cool the remaining-budget policy even if they consumed no slot

This matters because collapsing too aggressively recreates `already approved = budget-free forever`, while consuming too aggressively could make bounded-use offers feel wasteful and brittle.


## 30) When should a successor artifact be forced to start as a fresh budget island?

The archive now separates raw offer recreation from explicit predecessor/successor lineage, but one policy seam still needs real judgment:

- when should `same governed subject` still default to `fresh budget island` instead of any shared budget family
- whether some tightly controlled templates should ever allow `carried cap with review`, or whether that is always too reconstructive
- how strongly old mismatch, broader-than-ideal redemption, or suspicious failed attempts should bias the product toward `narrowed successor`
- when `delivery-only-encoding` should be allowed at all instead of forcing full successor review

This matters because too much carry-forward recreates `new link, same hidden story`, while too little carry-forward could make ordinary safe reissue feel heavier than it needs to be.


## 31) How much delivery provenance should lightweight intake surfaces keep visible before they become noisy?

The archive now makes delivery provenance and preview-authority first-class, but one policy seam still needs real judgment:

- when should dense/mobile intake rows show only `Received via` + `Authoritative now`, and when must `External touch` stay visible too
- whether browser auto-handoff should always trigger at least one expanded explanation surface before claim prep begins
- how aggressively old delivery events should remain visible after local inspect, claim, or supersession has already happened
- when a `landing-page hit, fragment stayed local` posture is still sensitive enough to bias the product toward re-delivery through a narrower channel

This matters because too little visibility recreates `opened link = trusted enough`, while too much visibility could make routine safe intake feel like a networking seminar.


## 32) How aggressively should the product auto-collapse carrier aliases into one canonical artifact?

The archive now makes delivery provenance and carrier identity first-class, but one policy seam still needs real judgment:

- when should wrapper URL and protocol URL auto-collapse without review, and when should the product still ask for manual compare
- whether QR payloads should default to `same canonical artifact` only when full normalization succeeds, or whether some lighter alias evidence is enough
- how much carrier-only drift should still count as delivery-only versus forcing `cannot prove yet`
- when a familiar-looking new wrapper should bias toward `treat as successor` because expiry, policy, or intended-recipient posture may have changed under the hood

This matters because too much auto-collapse recreates `looks like the same link, therefore it is`, while too little auto-collapse could make ordinary safe multi-carrier delivery feel heavier than it needs to be.


## 33) How much preview metadata should policy allow before recognition hints become too revealing?

The archive now makes field partition first-class, but one policy seam still needs real judgment:

- which hint classes should default to allowed because they help safe human recognition
- whether some senders or subjects should suppress label/size-style hints entirely even when delivery remains portable
- how strongly repeated preview exposure without claim should bias the product toward reissue through a narrower carrier
- when a client should auto-escalate from `hint only` to `require local inspect before showing anything more`

This matters because too much preview recreates `the browser already told me enough`, while too little preview could make ordinary safe intake feel blind and brittle.


## 34) How much omission detail should a preview show before omission-awareness becomes noisy?

The archive now makes preview sufficiency first-class, but one policy seam still needs real judgment:

- when should dense/mobile rows name only one or two missing governance fields versus a fuller omission list
- whether some environments should suppress omission detail until the operator asks `Why not enough yet`
- how strongly repeated preview exposure should bias the product toward narrower delivery or stricter sender-policy defaults
- when a preview can safely say `routing sufficient` without encouraging users to over-read that as claim or trust readiness

This matters because too little omission detail recreates `looks right = probably safe`, while too much omission detail could make ordinary safe intake feel like every preview needs a miniature audit report.
