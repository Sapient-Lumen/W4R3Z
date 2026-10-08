# Product plan — Async Runtime Assurance Profile Kit, capability-topology refinement (2026-03-23)

## Why this refinement is worth doing

The earlier async-runtime pass got the archive to the point where runtime family, shutdown behavior, evidence class, and host-vs-target bundle shape were explicit.
That was necessary but still not enough.

The sharper user-facing question now is not just:

> “Are you on Tokio, Embassy, or RTIC?”

It is:

> “Which async services are actually available in this lane, what provides them, and what must be activated or imported before dependent crates can rely on them?”

That question is now concrete enough to build around because current docs are specific about:

- Tokio resource drivers being optional in hand-built runtimes,
- runtime context being required for some Tokio types,
- Embassy time-driver provisioning and integrated-timer variants,
- RTIC dispatcher assignment and priority-scoped async execution,
- and adapter crates that bridge context/traits without erasing provider obligations.

## Main `0.1` refinement

Keep the existing runtime-profile, shutdown, qualification, diff, and bundle artifacts.
Add three more first-class artifacts:

- `runtime-service-topology.receipt.json`
- `capability-route.receipt.json`
- `compatibility-bridge.report.json`

## What `0.1` should classify now

### `runtime-service-topology.receipt.json`

This is the compact answer to:

> “Where do async services come from in this lane?”

It should classify at least:

- runtime lane id,
- runtime family,
- scope,
- service list,
- provider class for each service,
- activation route,
- and absent/manual-review services.

Useful services to classify in `0.1`:

- task spawning,
- local task spawning,
- time/sleep,
- network/I/O resource construction,
- signals/process integration,
- blocking work lane,
- and any board/dispatcher-specific scheduling surface.

### `capability-route.receipt.json`

This is the compact answer to:

> “What had to be true for this exact capability to work?”

It should classify at least:

- the capability being claimed,
- which lane it belongs to,
- provider kind,
- activation requirement,
- whether the capability is satisfied,
- evidence basis,
- and any residual caveats.

Good initial capabilities:

- `sleep`,
- `timeout`,
- `tcp_stream`,
- `udp_socket`,
- `spawn_blocking`,
- and `local_spawn`.

### `compatibility-bridge.report.json`

This is the compact answer to:

> “What does this bridge actually solve, and what does it not solve?”

It should classify at least:

- bridge/adaptor name,
- source and destination runtime/trait surfaces,
- which constraints remain preserved,
- which capabilities are only partially bridged,
- whether a hidden runtime context is still required,
- and what review debt remains.

## Recommended proving grounds

### Tokio manual runtime proving ground

Use Tokio because it exposes the clearest “runtime name is not enough” lesson.
A hand-built runtime can exist without I/O/time drivers enabled, and some types still require entering runtime context.

### Embassy proving ground

Use Embassy because it shows that executor, timer queue, and HAL time-driver provisioning may be separate truths.
This is exactly the kind of topology that users overflatten.

### RTIC proving ground

Use RTIC because it proves that “async service exists” can mean “priority-scoped dispatcher plus timer queue” rather than “general-purpose runtime services”.
That makes it a strong anti-flattening fixture.

### Bridge proving ground

Use `async-compat` and `async_executors` because they already encode real bridge demand while also documenting that a bridge often preserves context or provider requirements.

## Suggested workspace split after this refinement

Keep the earlier split and add two new internals:

- `runtime_assurance_topology`
- `runtime_assurance_capabilities`

So the eventual workspace shape can become:

- `runtime_assurance_model`
- `runtime_assurance_discovery`
- `runtime_assurance_topology`
- `runtime_assurance_capabilities`
- `runtime_assurance_check`
- `runtime_assurance_pack`
- `cargo-runtime-assurance`

## `0.1` adoption story after refinement

1. maintainer declares runtime lanes,
2. tool imports obvious runtime-profile facts,
3. tool captures per-lane service providers,
4. maintainer records capability routes for support-sensitive APIs,
5. any adapters are captured as explicit bridge reports,
6. `doctor` warns when runtime family is known but service route is not,
7. `pack` exports one portable bundle with runtime family, service topology, capability routes, bridge debt, and evidence basis together.

That is still small enough for a real crate, but much closer to the actual hidden contract people need help publishing.
