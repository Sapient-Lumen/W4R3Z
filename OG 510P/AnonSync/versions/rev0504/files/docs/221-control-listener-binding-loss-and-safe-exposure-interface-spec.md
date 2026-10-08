# Control-listener binding loss and safe-exposure interface spec

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
