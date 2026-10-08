from pathlib import Path
import shutil

src = Path('/mnt/data/anonsync_rev0139/anonsync_rev0139')
dst_root = Path('/mnt/data/anonsync_rev0140')
if dst_root.exists():
    shutil.rmtree(dst_root)
shutil.copytree(src, dst_root)
ROOT = dst_root
DOCS = ROOT / 'docs'

rev = 'rev0140'
timestamp = '2026.03.19.23.11'
codename = 'listenerseatintakewaypoint'
zipname = f'AnonSync-{rev}-{timestamp}-{codename}.zip'

# New docs
(DOCS / '221-control-listener-binding-loss-and-safe-exposure-interface-spec.md').write_text('''# Control-listener binding loss and safe-exposure interface spec

## Purpose

The archive already has bringup, control-access, and service-promotion language.
What it still lacked was one explicit contract for a narrower but very real seam:

> when the local web or other control listener is widened, rebound to a specific interface, or loses that interface later, what page tells the operator whether only the control surface changed, whether background sync work is still alive, and whether the correct next step is degrade, withdraw, or intentionally hard-fail?

Current official Resilio docs make this seam vivid.
They still say Linux/headless defaults the WebUI to `127.0.0.1`, that widening reachability can use `0.0.0.0` or a specific interface, and that if Sync is forced to bind the WebUI to a specific interface that later is unavailable, Sync will shut down immediately.
A current Windows service troubleshooting page still says widening WebUI reachability from localhost requires either a preference change or config edit plus a service restart.

That is not just a transport detail.
It means control exposure, listener binding, and daemon liveness are still coupled more tightly than they should be.

AnonSync should therefore treat listener binding as one reviewed exposure object with an explicit survivability policy.

## Core decision

A control listener is not the same thing as the engine's right to keep syncing.
AnonSync should therefore separate three truths that weaker products blur together:

1. **control endpoint exposure**
2. **listener dependency on a concrete interface/address family**
3. **engine survivability if that endpoint disappears**

The default should be:

> losing a widened control listener narrows control access before it kills sync work.

An operator may still choose a stricter `hard-fail-on-bind-loss` posture, but that must be explicit and reviewable.

## Fixed review order

Every non-trivial listener change or listener-loss event should render the same sections in the same order:

1. **Current control endpoint set**
2. **Requested exposure and bind dependency**
3. **Failure behavior if bind disappears**
4. **Receipt and rollback**

### 1) Current control endpoint set

This section should show:

- active endpoint classes (`loopback-web`, `lan-web`, `unix-socket`, `named-pipe`, `other`)
- current bind targets
- current auth posture
- whether restart is required
- whether another endpoint already exists as a fallback

The operator must be able to answer: **what control surfaces exist right now, and where are they listening?**

### 2) Requested exposure and bind dependency

This section should show:

- requested exposure target (`loopback only`, `all interfaces`, `specific interface`, `specific address family`, `disable listener`, `other`)
- whether the target is stable, ephemeral, or currently absent
- whether the request widens control reachability or only relocates it
- whether the request couples control reachability to one DHCP/network event

The operator must be able to answer: **am I merely widening control reachability, or making daemon control depend on one fragile interface?**

### 3) Failure behavior if bind disappears

This section should show one explicit survivability policy:

- `degrade to remaining endpoint`
- `withdraw remote endpoint, preserve local control`
- `preserve engine, mark control partially unavailable`
- `block change because no acceptable fallback exists`
- `hard fail engine on bind loss` (only by explicit choice)

The operator must be able to answer: **if that interface vanishes, does sync continue, does control fall back, or does the engine stop?**

### 4) Receipt and rollback

This section should show:

- previous endpoint set
- resulting endpoint set
- restart or live-rebind requirement
- survivability policy before/after
- rollback endpoint and rollback prerequisites

The operator must be able to answer: **what later proves that I changed control exposure without accidentally changing engine-liveness semantics?**

## Public objects

### `control_listener_review`

Fields:

- `control_listener_review_id`
- `seat_ref`
- `current_endpoint_refs[]`
- `requested_endpoint_shape`
- `bind_dependency_class`
- `survivability_policy`
- `restart_requirement`
- `fallback_endpoint_refs[]`
- `risk_findings[]`
- `generated_at`

### `control_listener_receipt`

Fields:

- `control_listener_receipt_id`
- `review_ref`
- `seat_ref`
- `before_summary`
- `after_summary`
- `survivability_delta_summary`
- `restart_performed`
- `rollback_hint`
- `created_at`

## Main surface

A compact row should read like one of these:

- `loopback control only · engine independent`
- `LAN control widened · restart required · fallback loopback kept`
- `specific-interface bind blocked · no safe fallback`
- `remote control withdrawn after bind loss · sync still running`

## CLI shape

```text
anonsync control listener show
anonsync control listener review --listen 0.0.0.0:4747
anonsync control listener review --listen if:enp3s0:4747 --survivability degrade
anonsync control listener apply <review>
anonsync control listener receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- a specific-interface control bind can disappear and the operator learns only after the engine has already died
- a localhost-to-LAN change still feels like a hidden config tweak plus restart ritual
- listener loss and engine death are inseparable by default
- the operator cannot prove whether a restart changed only reachability or also continuity/liveness semantics

## Non-clone reason

Current Resilio docs still let WebUI bind choice, exposure widening, restart ritual, and even process shutdown on interface loss live inside startup-flag lore and troubleshooting pages.
AnonSync should instead make listener dependency, exposure scope, and survivability policy first-class reviewed state.
''')

(DOCS / '222-same-host-multi-instance-port-storage-and-state-world-review-interface-spec.md').write_text('''# Same-host multi-instance port, storage, and state-world review interface spec

## Purpose

The archive already has execution-seat switching, host-custody claims, and same-host collision language.
What it still lacked was one explicit contract for a different same-host case:

> when one operator wants two live runtimes on the same host at the same time, what page proves that ports, storage, identity, and subject ownership are actually isolated instead of hoping manual flags are enough?

Current official Resilio docs make this seam vivid.
They still say Linux can run multiple instances, but that the second and later instances require manual transmission/reception port assignment.
The same Linux guide still says that if `--storage` is not defined, a default `.sync` storage folder is created in the current directory.
A current error page still says two instances of Sync on the same computer, or one external drive used as storage for two instances, can corrupt the former instance's internal `.sync` files if the same folder is added twice.

That is not just an advanced-user footnote.
It means multi-instance operation still depends on manually keeping namespaces apart.

AnonSync should therefore treat same-host multi-instance bringup as one reviewed namespace allocation and custody problem.

## Core decision

Every live runtime on the same host must belong to an explicit **instance namespace** that proves four separations together:

1. transport/listener ports
2. control endpoint identifiers
3. storage and identity roots
4. subject ownership claims for local paths

The product must never normalize a second live runtime into `just start another process`.

## Fixed review order

Every same-host multi-instance review should render the same sections in the same order:

1. **Existing runtimes on this host**
2. **Requested new instance namespace**
3. **Collision and corruption risks**
4. **Receipt and branch proof**

### 1) Existing runtimes on this host

This section should show:

- each currently running instance
- its control endpoint(s)
- transport/listener ports it owns
- storage/identity root it owns
- whether it already claims any overlapping local subject paths

The operator must be able to answer: **what already lives on this host, and which namespaces are already occupied?**

### 2) Requested new instance namespace

This section should show:

- proposed instance name
- proposed control endpoint(s)
- proposed transport/listener ports
- proposed storage root and identity root
- whether the new runtime is a sibling, branch, scratch lab, or reviewed migration target

The operator must be able to answer: **what exact namespace will this new runtime own?**

### 3) Collision and corruption risks

This section should show:

- port collisions
- storage-root overlap
- same-subject local-path overlap
- external-disk/shared-root reuse risk
- whether the new instance would read or write another instance's service state

The operator must be able to answer: **is this truly a separate runtime, or am I about to split one state world across two processes?**

### 4) Receipt and branch proof

This section should show:

- resulting instance namespace handle
- namespace reservations created
- blocked overlaps if any
- branch/migration relation to older runtimes
- teardown rule for later retirement

The operator must be able to answer: **what later proves that these runtimes were intentionally separated rather than accidentally colliding?**

## Public objects

### `instance_namespace_review`

Fields:

- `instance_namespace_review_id`
- `host_ref`
- `existing_instance_refs[]`
- `requested_instance_name`
- `requested_port_set[]`
- `requested_control_endpoint_set[]`
- `requested_storage_root`
- `requested_identity_root`
- `requested_branch_class`
- `collision_findings[]`
- `generated_at`

### `instance_namespace_receipt`

Fields:

- `instance_namespace_receipt_id`
- `review_ref`
- `host_ref`
- `instance_ref`
- `reserved_port_set[]`
- `reserved_control_endpoint_set[]`
- `storage_root`
- `identity_root`
- `branch_summary`
- `created_at`

## Main surface

A compact row should read like one of these:

- `second runtime admitted · isolated ports and storage`
- `blocked · storage root overlaps active runtime`
- `blocked · same subject path already claimed by sibling runtime`
- `lab branch admitted · no subject custody overlap`

## CLI shape

```text
anonsync instance list --host this
anonsync instance review --host this --name lab-b --storage /srv/anonsync-lab-b --port-set 41000-41002
anonsync instance apply <review>
anonsync instance receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- multiple live runtimes still depend on manual port memory alone
- a second instance can silently reuse another instance's storage or service state
- same-path subject ownership is discovered only after corruption or suspension
- the operator cannot prove later whether a second process was a reviewed branch, migration helper, or accidental duplicate

## Non-clone reason

Current Resilio docs still make same-host multi-instance operation depend on manual port assignment, implicit storage-root discipline, and later corruption warnings when two instances touch the same subject path.
AnonSync should instead require one explicit namespace review before a second live runtime starts.
''')

(DOCS / '223-capability-owner-transfer-and-seat-starvation-boundary-interface-spec.md').write_text('''# Capability-owner transfer and seat-starvation boundary interface spec

## Purpose

The archive already has subject authority, compromise response, and owner-domain language.
What it still lacked was one explicit contract for a different ownership seam:

> when a feature-capability or entitlement owner moves from one seat to another, what page proves that only capability ownership moved, who loses access if seat budget is exhausted, and what did **not** change about subject/data authority?

Current official Resilio docs make this seam vivid.
They still say applying the license key on a new device transfers license ownership to that device, that the older owner becomes a user if spare seats exist, and that if all seats are already shared one user may lose access.
A current stolen-device page still says the owner is the peer that activated the license most recently, that re-adding the license overrides the previous activation, and that the thief's instance will later revert to Free if it comes online.

That is not just billing trivia.
It means capability ownership can jump seats as a side effect of activation, while data/trust recovery is handled elsewhere.

AnonSync should therefore keep capability-envelope ownership separate from subject/data authority and render transfer/starvation explicitly.

## Core decision

Any capability-envelope transfer must be reviewed as its own mutation class.
The product must separate three questions that weaker products blur together:

1. **who owns the capability envelope now**
2. **which seats currently consume limited seats within that envelope**
3. **what subject/data/control authority is entirely unaffected by this transfer**

The product must never let `apply capability on another seat` silently mean `some other seat lost power`.

## Fixed review order

Every capability-owner transfer should render the same sections in the same order:

1. **Current capability graph**
2. **Requested owner transfer**
3. **Seat-budget impact and starvation simulation**
4. **Receipt and unaffected authority statement**

### 1) Current capability graph

This section should show:

- current capability owner seat
- all seats currently consuming the capability envelope
- total seat budget and free headroom
- any seats already in grace, degraded, or pending removal state

The operator must be able to answer: **who owns this capability envelope now, and how full is it?**

### 2) Requested owner transfer

This section should show:

- proposed new owner seat
- whether the transfer is routine, incident-driven, or stolen-seat containment
- whether the old owner remains a user, becomes unentitled, or enters grace
- whether the transfer implies any credential/token retirement

The operator must be able to answer: **what changes hands, and is this a normal move or an emergency override?**

### 3) Seat-budget impact and starvation simulation

This section should show:

- resulting seat allocation if the transfer succeeds
- which seat(s), if any, would lose capability because the budget is exhausted
- whether those seats lose premium capability immediately, after grace, or only on next contact
- alternative transfers that avoid starvation

The operator must be able to answer: **who loses access if I do this, and can I avoid that?**

### 4) Receipt and unaffected authority statement

This section should show:

- capability owner before/after
- seat-budget before/after
- seats downgraded or spared
- explicit statement of what subject/data/control authority did **not** change
- follow-up actions still needed for incident containment or subject trust repair

The operator must be able to answer: **what later proves this was a capability move, not a hidden subject-authority rewrite?**

## Public objects

### `capability_owner_transfer_review`

Fields:

- `capability_owner_transfer_review_id`
- `capability_envelope_ref`
- `current_owner_seat_ref`
- `requested_owner_seat_ref`
- `transfer_reason`
- `current_consumer_seat_refs[]`
- `seat_budget_summary`
- `starvation_findings[]`
- `unaffected_authority_statement`
- `generated_at`

### `capability_owner_transfer_receipt`

Fields:

- `capability_owner_transfer_receipt_id`
- `review_ref`
- `capability_envelope_ref`
- `before_summary`
- `after_summary`
- `downgraded_seat_refs[]`
- `retired_token_refs[]`
- `followup_refs[]`
- `created_at`

## Main surface

A compact row should read like one of these:

- `capability owner moved · no seat starvation`
- `incident override applied · old owner downgraded on next contact`
- `blocked · transfer would starve 1 seat`
- `owner moved · subject authority unchanged`

## CLI shape

```text
anonsync capability owner show --envelope family-pro
anonsync capability owner review --envelope family-pro --to seat:laptop-ember
anonsync capability owner apply <review>
anonsync capability owner receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- reapplying capability on a new seat can silently demote another seat
- incident-driven owner override still requires the operator to infer which other seats will lose access
- capability transfer is mistaken for subject-authority repair
- the operator cannot later prove whether an access loss came from budget starvation or deliberate subject revocation

## Non-clone reason

Current Resilio docs still let capability ownership jump to the most recently activated seat and explicitly warn that another seat may lose access if the budget is full.
AnonSync should instead review capability-owner transfer, starvation risk, and unaffected subject authority as one explicit receipt-bearing action.
''')

(DOCS / '224-headless-artifact-intake-typing-and-action-routing-interface-spec.md').write_text('''# Headless artifact intake, typing, and action-routing interface spec

## Purpose

The archive already has offer artifacts, redemption lineage, and bringup contracts.
What it still lacked was one explicit contract for a narrower but very real headless seam:

> when a user pastes or imports something on a headless/Linux seat, what page proves whether it is a subject offer, a member grant, a capability seat, a license file, or another artifact class **before** the product takes action?

Current official Resilio docs make this seam vivid.
They still say Linux routes shared-folder links, license-seat links, and license activation through the same `Enter a key or link` entry path in WebUI.
A separate license-application guide still says headless use first creates identity, then applies the license file, while other docs route share offers and seat links through ordinary manual-connection style intake.

That is not just a cosmetic shortcut.
It means materially different artifact classes still converge on one generic intake verb.

AnonSync should therefore type imported artifacts before action and route each kind through a named reviewed lane.

## Core decision

Every imported string/file/QR/protocol artifact must pass through a two-step contract:

1. **artifact typing** — what kind of thing is this?
2. **action routing** — which reviewed lane does that kind belong to?

The product must never let one generic `enter key or link` control become the semantic home for unrelated actions.

## Fixed review order

Every headless artifact-intake surface should render the same sections in the same order:

1. **Artifact classification**
2. **Required prerequisites**
3. **Routed action lane**
4. **Receipt and audit trail**

### 1) Artifact classification

This section should show:

- source form (`text`, `file`, `qr`, `protocol-url`, `clipboard`, `other`)
- detected artifact class (`subject-offer`, `member-introduction`, `capability-seat`, `capability-file`, `identity-bootstrap`, `unknown`)
- confidence level
- any ambiguous interpretations

The operator must be able to answer: **what did I paste or import?**

### 2) Required prerequisites

This section should show:

- whether local identity already exists
- whether a capability envelope or control session is needed
- whether this artifact can be inspected without mutating anything
- which missing prerequisites block apply

The operator must be able to answer: **what must already exist before this artifact can honestly do anything?**

### 3) Routed action lane

This section should show:

- target lane (`inspect offer`, `claim subject`, `approve seat`, `apply capability`, `bootstrap identity`, `reject/hold`)
- whether the next step is local-only or remote-approval-based
- whether the artifact widens authority, consumes a seat budget, or merely reveals an offer
- what receipt type will be emitted if applied

The operator must be able to answer: **which workflow am I actually entering?**

### 4) Receipt and audit trail

This section should show:

- artifact fingerprint
- classification decision
- action lane chosen
- whether the operator inspected only or applied
- successor receipt, if any

The operator must be able to answer: **what later proves what this imported artifact really was and what I did with it?**

## Public objects

### `artifact_intake_review`

Fields:

- `artifact_intake_review_id`
- `seat_ref`
- `source_form`
- `artifact_fingerprint`
- `classification_candidates[]`
- `chosen_class`
- `prerequisite_findings[]`
- `routed_action_lane`
- `apply_blockers[]`
- `generated_at`

### `artifact_intake_receipt`

Fields:

- `artifact_intake_receipt_id`
- `review_ref`
- `seat_ref`
- `artifact_fingerprint`
- `chosen_class`
- `action_taken` (`inspect-only`, `hold`, `apply`, `reject`)
- `successor_ref` nullable
- `created_at`

## Main surface

A compact row should read like one of these:

- `subject offer detected · inspect before claim`
- `capability file detected · identity required before apply`
- `seat grant detected · remote approval lane`
- `ambiguous artifact · hold for typed review`

## CLI shape

```text
anonsync artifact intake inspect --from clipboard
anonsync artifact intake inspect --file ~/Downloads/token.asf
anonsync artifact intake route <review>
anonsync artifact intake receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- share offers, seat grants, and capability files still enter through one generic verb with no typed preview
- headless intake requires the operator to remember product lore about which artifact needs identity first
- import history cannot later prove whether the user inspected or actually applied the artifact
- a single pasted string can widen authority or consume seat budget without a typed action lane

## Non-clone reason

Current Resilio docs still route multiple materially different artifact classes through one generic `Enter a key or link` path on Linux/headless seats.
AnonSync should instead type imported artifacts first and route each one into a named reviewed workflow.
''')

# README rewrite
(ROOT / 'README.md').write_text(f'''# AnonSync

A tight planning archive for a privacy-respecting, inspectable, peer-to-peer sync product that learns from Resilio Sync without merely cloning it.

## Revision

- Revision: `{rev}`
- Timestamp: `{timestamp}` (America/New_York)
- Codename: `{codename}`

## What changed in this revision

This revision continues directly from `rev0139` and does twelve specific things:

1. Pushes the **Resilio Sync** evaluation further with current official evidence about listener binding that can still hard-stop a headless seat, same-host multi-instance manual port/storage discipline, generic headless intake for materially different artifact classes, and capability ownership that can still jump to the most recently activated seat.
2. Sharpens the non-clone reason again: the remaining problem is not missing capability but too much operator-meaningful truth spread across startup flags, current-directory storage defaults, generic `Enter a key or link` intake, and activation side effects that can starve another seat.
3. Adds a new **control-listener binding / interface loss / safe exposure** interface spec so control reachability, bind fragility, and daemon survivability become one reviewed object instead of startup-flag lore.
4. Adds a new **same-host multi-instance / port-storage namespace / state-world** interface spec so a second live runtime becomes a reviewed namespace claim instead of manual port memory plus later corruption warnings.
5. Adds a new **capability-owner transfer / seat-starvation boundary** interface spec so feature-entitlement ownership moves become explicit and separate from subject/data authority.
6. Adds a new **headless artifact intake / typing / action routing** interface spec so pasted or imported artifacts are typed before action instead of funneling through one generic key-or-link box.
7. Refreshes the **Resilio evaluation** so the comparison now also covers Linux WebUI bind loss, localhost default versus widened exposure, multiple-instance manual port assignment, default `.sync` storage in the current directory, same-host dual-instance corruption risk, license-owner takeover, and activation-driven seat starvation.
8. Refreshes the **product direction** so control exposure survivability, multi-instance namespace proof, capability/data-authority separation, and typed headless intake become doctrine rather than troubleshooting folklore.
9. Refreshes the **roadmap** so the next tranche now explicitly includes listener survivability, instance namespaces, capability-owner transfer receipts, and typed artifact intake.
10. Refreshes the **source notes** so the official evidence set now explicitly includes `Guide to Linux, and Sync peculiarities`, `Sync Service Troubleshooting on Windows`, `Service files missing / Cannot identify destination folder`, `How to apply license key and share license seats`, `Can I change the device which acts as the license owner?`, and `If your device is stolen`.
11. Keeps the archive tight by extending existing bringup, control-access, host-custody, service-world, offer-artifact, and compromise-response grammar instead of inventing unrelated subsystems.
12. Preserves the earlier discovery, proxy-asymmetry, memory-budget, service-world, route, restore, naming, topology, and repair decisions while giving them stronger control-surface, instance-namespace, entitlement-boundary, and intake-typing companions.

## Current conclusion

We **still should not clone Resilio Sync wholesale**.

The reason is sharper again and still evidence-based.
Current official docs still show a maintained Sync v3 line through `3.1.2.1076` in late 2025, practical linked-device and selective-materialization workflows, and a large body of operational guidance.
That is why Resilio remains worth studying rather than dismissing.

But the better non-clone reason is now this:

> Resilio still solves many real operator problems while leaving too much meaning about **whether control exposure is fragile or survivable**, **whether a second live runtime really has its own namespace**, **whether moving premium capability ownership will starve another seat**, and **what kind of artifact a headless user just pasted** distributed across startup flags, service troubleshooting, corruption warnings, and activation/help-page ritual where AnonSync wants one control-listener receipt, one instance-namespace review, one capability-owner transfer receipt, and one typed artifact-intake lane.

That stronger conclusion is what this revision tries to preserve.

## Recommended reading order

1. `docs/00-status.md`
2. `docs/10-resilio-sync-evaluation.md`
3. `docs/221-control-listener-binding-loss-and-safe-exposure-interface-spec.md`
4. `docs/222-same-host-multi-instance-port-storage-and-state-world-review-interface-spec.md`
5. `docs/223-capability-owner-transfer-and-seat-starvation-boundary-interface-spec.md`
6. `docs/224-headless-artifact-intake-typing-and-action-routing-interface-spec.md`
7. `docs/217-discovery-bootstrap-catalog-outage-and-fallback-authority-interface-spec.md`
8. `docs/218-egress-only-proxy-and-relay-inevitability-interface-spec.md`
9. `docs/219-runtime-memory-pressure-subject-budget-and-relief-interface-spec.md`
10. `docs/220-linked-seat-rights-narrowing-and-owner-domain-separation-interface-spec.md`
11. `docs/78-bringup-and-control-entry-interface-spec.md`
12. `docs/55-control-access-and-session-boundary-spec.md`
13. `docs/83-execution-seat-and-runtime-profile-reachability-spec.md`
14. `docs/203-host-ownership-claim-dual-instance-collision-and-safe-branching-interface-spec.md`
15. `docs/52-capability-offer-and-claim-artifact-spec.md`
16. `docs/39-interface-pattern-language.md`
17. `docs/30-interface-spec.md`

## Archive map

- `docs/00-status.md` — scope, honesty notes, and revision deltas
- `docs/10-resilio-sync-evaluation.md` — updated evaluation of Resilio Sync and its implications
- `docs/20-product-direction.md` — narrowed product thesis and interface doctrine
- `docs/221-control-listener-binding-loss-and-safe-exposure-interface-spec.md` — reviewed control-exposure contract for bind fragility, fallback endpoints, and safe listener loss
- `docs/222-same-host-multi-instance-port-storage-and-state-world-review-interface-spec.md` — reviewed namespace contract for second runtimes on one host
- `docs/223-capability-owner-transfer-and-seat-starvation-boundary-interface-spec.md` — reviewed capability-envelope transfer contract for ownership jumps and seat-starvation simulation
- `docs/224-headless-artifact-intake-typing-and-action-routing-interface-spec.md` — reviewed typed-intake contract for headless pasted/imported artifacts
- `docs/50-roadmap.md` — near-term phases and exit criteria
- `docs/sources.md` — current external source notes for this revision
''')

# Status rewrite
(DOCS / '00-status.md').write_text(f'''# Status

## Scope of this revision

This revision is an in-place continuation of `rev0139`, driven by the current request:

- continue researching, brainstorming, planning, and tightening the archive without letting it sprawl
- evaluate **Resilio Sync** further so the non-clone case stays evidence-based, current, and specific not only about discovery bootstrap, proxy asymmetry, memory relief, and seat narrowing, but now also about **control-listener survivability**, **same-host multi-instance namespace truth**, **capability-owner transfer and seat starvation**, and **typed headless artifact intake**
- spend more time on **interface specs**, especially where current sync products still ask the operator to infer meaning from startup flags, port collisions, generic `Enter a key or link` flows, or activation side effects
- preserve the shell/workspace, route, disclosure, repair, rights, and service-world decisions already made unless fresh evidence actually breaks them
- make a better explicit case for why AnonSync should not inherit Resilio's bind-fragile control surface, manual multi-instance discipline, activation-driven capability takeovers, or generic headless intake model

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- Revision: {rev}
- Timestamp: {timestamp} America/New_York
- Codename: {codename}

- a further-tightened **Resilio evaluation** that now treats control-listener bind loss, same-host multi-instance namespace drift, capability-owner takeover, and generic headless intake as additional non-clone reasons
- a new **control-listener binding / interface loss / safe exposure** interface spec so widened control reachability does not silently become daemon life-or-death
- a new **same-host multi-instance / port-storage namespace / state-world** interface spec so second runtimes become reviewed namespace claims instead of manual port folklore
- a new **capability-owner transfer / seat-starvation boundary** interface spec so entitlement moves stay separate from subject/data authority
- a new **headless artifact intake / typing / action routing** interface spec so pasted or imported artifacts are typed before action instead of sharing one generic intake box
- updated top-level docs so the archive now makes firmer choices about control exposure survivability, instance namespace proof, capability/data-authority separation, and typed headless intake

## The main shift

`rev0140` closes the next seam:

> it is not enough to have strong route, disclosure, repair, rights, and service-world language if the operator still has to reconstruct **whether widened control exposure is fragile or survivable**, **whether a second live runtime really owns separate ports and storage**, **whether moving premium capability ownership will starve another seat**, and **what kind of artifact a headless user just pasted** from startup flags, service troubleshooting, corruption warnings, and activation help pages.

That changes the archive in eight specific ways:

- control listener exposure is now separable from engine survivability
- listener bind loss can now compile to degrade, withdraw, block, or hard-fail by explicit policy
- second same-host runtimes now require one namespace review that proves port, storage, and subject custody separation
- instance collisions can now be blocked before two runtimes touch the same local subject path
- capability-envelope ownership can now move without pretending subject authority moved too
- seat-budget starvation is now simulated before apply rather than discovered after reactivation
- headless pasted/imported artifacts are now typed before action routing
- new receipts can now prove listener changes, instance separation, capability-owner transfer, and artifact-intake routing directly

## Files added in this revision

- `docs/221-control-listener-binding-loss-and-safe-exposure-interface-spec.md`
- `docs/222-same-host-multi-instance-port-storage-and-state-world-review-interface-spec.md`
- `docs/223-capability-owner-transfer-and-seat-starvation-boundary-interface-spec.md`
- `docs/224-headless-artifact-intake-typing-and-action-routing-interface-spec.md`
- `update_rev0140.py`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/20-product-direction.md`
- `docs/50-roadmap.md`
- `docs/sources.md`

## The current stance in one paragraph

Resilio remains worth studying because current official docs still show a maintained Sync v3 line, practical linked-device and selective-materialization workflows, and extensive operational guidance.
But those same docs still show control exposure meaning hidden across loopback defaults, specific-interface bind failure, and restart ritual; second-runtime safety hidden across manual port assignment and storage-root discipline; premium capability ownership hidden across `apply key on a new seat` side effects; and headless artifact meaning hidden behind one generic `Enter a key or link` path.
That is enough reason for AnonSync to prefer one control-listener receipt, one instance-namespace review, one capability-owner transfer receipt, and one typed artifact-intake lane instead of cloning Resilio's support-lore-driven contract.
''')

# 10-resilio prepend section
resilio_path = DOCS / '10-resilio-sync-evaluation.md'
text = resilio_path.read_text()
insertion = '''\n### Additional current pass: four more present-day seams still worth diverging from\n\nCurrent official Resilio docs still expose four more interface contracts AnonSync should not inherit as-is.\n\n#### 1) Control exposure can still be more fragile than it looks\n\nCurrent official docs still say Linux/headless defaults WebUI to `127.0.0.1`, that widening reachability can use `0.0.0.0` or a specific interface, and that if the chosen specific interface later is unavailable Sync will shut down immediately. A current Windows service troubleshooting page still says widening service WebUI beyond localhost requires a preference or config change plus restart.\n\nThat means control exposure is not yet modeled as a survivable boundary.\nAnonSync should therefore separate listener exposure from engine liveness and make bind-loss policy explicit.\n\n#### 2) Same-host multi-instance operation still depends on manual namespace discipline\n\nCurrent official docs still say Linux can run multiple instances but requires manual port assignment for second and later instances, and the same guide still says that if `--storage` is not defined a default `.sync` storage folder is created in the current directory. A current error page still warns that two instances on the same computer, or one external storage used by two instances, can corrupt internal files if the same folder is added twice.\n\nThat means `run another copy` is still a namespace-allocation problem hiding behind flags and folder choices.\nAnonSync should therefore require one reviewed instance namespace before a second runtime starts.\n\n#### 3) Capability ownership can still jump seats as an activation side effect\n\nCurrent official docs still say applying the license key on a new device transfers license ownership to that device, that the older owner becomes a user if spare seats exist, and that if all seats are already shared one of the users may lose access. A current stolen-device page still says the owner is the peer that activated the license most recently and that re-adding the license overrides the previous activation.\n\nThat means capability ownership and seat starvation are still easy to trigger as side effects of activation rather than as reviewed entitlement moves.\nAnonSync should therefore separate capability-envelope ownership from subject/data authority and simulate starvation before apply.\n\n#### 4) Headless intake still routes different artifact classes through one generic entry verb\n\nCurrent official docs still say Linux handles shared-folder links, license-seat links, and license activation through the same `Enter a key or link` path in WebUI, while the headless license guide separately says identity must be created first and then the license file applied.\n\nThat means materially different artifact classes still collapse into one generic intake control.\nAnonSync should therefore type imported artifacts before action and route them into named reviewed lanes.\n\n'''
marker = 'This revision answers that more tightly than before.\n'
if marker in text and insertion not in text:
    text = text.replace(marker, marker + insertion, 1)
resilio_path.write_text(text)

# 20-product-direction insert bullets before Product boundaries
pd_path = DOCS / '20-product-direction.md'
text = pd_path.read_text()
insert = '''\n- **control listeners** are survivable exposure objects, not process-death traps bound to one interface by accident\n- **same-host multi-instance runs** are reviewed namespaces, not extra processes that happen to remember different ports\n- **capability envelopes** move by explicit entitlement review, not as side effects that silently starve another seat\n- **headless artifact intake** is typed before action, not one generic `paste key or link` funnel\n\n## Latest doctrine additions\n\n### Doctrine 8 — control exposure is not daemon identity\n\nWidening or relocating a control listener may change who can reach the daemon.\nIt should not silently change whether the daemon is allowed to keep syncing if one network interface disappears.\n\n### Doctrine 9 — simultaneous runtimes need explicit namespaces\n\nRunning two live seats on one host is not just a convenience flag.\nPorts, storage roots, identity roots, and local subject custody must be reserved and provable up front.\n\n### Doctrine 10 — feature entitlement is not subject authority\n\nA capability owner transfer, premium-seat reassignment, or other entitlement move should never masquerade as subject trust repair, data revocation, or owner-domain mutation.\n\n### Doctrine 11 — imported artifacts must be typed before action\n\nA pasted token, a protocol URL, a seat grant, and a subject offer may all arrive as strings or files.
The product should classify them first, then route them into the correct reviewed lane.\n\n'''
needle = '## Product boundaries\n'
if needle in text and '## Latest doctrine additions' not in text:
    text = text.replace(needle, insert + needle, 1)
pd_path.write_text(text)

# 50-roadmap insert deliver bullets and exit criteria bullets
rm_path = DOCS / '50-roadmap.md'
text = rm_path.read_text()
text = text.replace('- namespace-portability, name-plane, continuity-cost, and no-byte-horizon contract so collisions, labels, rename cost, and placeholder eviction stay semantically honest\n', '- namespace-portability, name-plane, continuity-cost, and no-byte-horizon contract so collisions, labels, rename cost, and placeholder eviction stay semantically honest\n- listener-survivability, instance-namespace, capability-owner-transfer, and typed-intake contract so control exposure, same-host concurrency, entitlement moves, and headless imports stay semantically honest\n', 1)
text = text.replace('- operators can tell whether a one-time handoff is a bounded snapshot, a reissue of the same snapshot, or a new content snapshot with new lineage\n', '- operators can tell whether a one-time handoff is a bounded snapshot, a reissue of the same snapshot, or a new content snapshot with new lineage\n- operators can tell whether losing one bound control interface narrows access, triggers fallback, or intentionally stops the engine\n- operators can tell before starting a second live runtime on one host whether ports, storage, and local subject custody are actually isolated\n- operators can tell whether moving a capability envelope owner will starve another seat before apply\n- operators can tell what kind of artifact a headless seat just imported before any authority is widened or any seat budget is consumed\n', 1)
rm_path.write_text(text)

# sources prepend addendum
sources_path = DOCS / 'sources.md'
text = sources_path.read_text()
addendum = '''## Revision addendum — listener survivability, instance namespaces, capability-owner jumps, and typed headless intake\n\nThis revision intentionally leaned on another small cluster of current official Resilio docs because they expose a different class of non-clone reason than the earlier route, restore, and service-world passes.\nThe new questions were:\n\n> where do current official docs prove that **control exposure** can still be widened in ways that make the process depend on one fragile interface rather than one survivable control boundary?\n\n> where do current docs show that **same-host multi-instance operation** still depends on manual namespace discipline instead of one reviewed separation contract?\n\n> what current evidence most clearly shows that **capability ownership** can still jump seats and starve another seat as an activation side effect rather than a reviewed entitlement transfer?\n\n> where do current docs prove that **headless intake** still routes materially different artifact classes through one generic entry verb?\n\nThe most load-bearing source set for this pass was the maintained v3 line together with docs on Linux peculiarities, Windows service troubleshooting, same-host service-file corruption, headless license application, license-owner transfer, and stolen-device reactivation behavior.\n\n### Additional Resilio official sources emphasized in rev0140\n\n- Guide to Linux, and Sync peculiarities  \n  https://help.resilio.com/hc/en-us/articles/204762449-Guide-to-Linux-and-Sync-peculiarities\n\n- Sync Service Troubleshooting on Windows  \n  https://help.resilio.com/hc/en-us/articles/207724196-Sync-Service-Troubleshooting-on-Windows\n\n- Service files missing / Cannot identify destination folder  \n  https://help.resilio.com/hc/en-us/articles/205450225-Service-files-missing-Cannot-identify-destination-folder\n\n- How to apply license key and share license seats  \n  https://help.resilio.com/hc/en-us/articles/204762369-How-to-apply-license-key-and-share-license-seats\n\n- Can I change the device which acts as the license owner?  \n  https://help.resilio.com/hc/en-us/articles/204753479-Can-I-change-the-device-which-acts-as-the-license-owner\n\n- If your device is stolen  \n  https://help.resilio.com/hc/en-us/articles/204644049-If-your-device-is-stolen\n\n'''
if not text.startswith('## Revision addendum — listener survivability'):
    text = addendum + text
sources_path.write_text(text)

# update script copy of this build for provenance
(ROOT / 'update_rev0140.py').write_text(Path('/mnt/data/build_rev0140.py').read_text())

print('built', ROOT)
