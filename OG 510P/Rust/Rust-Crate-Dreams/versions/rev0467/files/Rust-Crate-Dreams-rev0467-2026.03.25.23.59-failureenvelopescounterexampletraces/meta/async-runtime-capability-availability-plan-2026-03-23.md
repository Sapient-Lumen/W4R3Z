# Product plan — Async Runtime Assurance Profile Kit, deployment-topology and capability-matrix refinement (2026-03-23)

## Why this refinement is worth doing

The previous runtime-assurance pass got the archive to the point where runtime family, service topology, capability routes, and bridge debt were explicit.
That was strong progress, but it still left a recurring support failure:

> a crate would name one runtime family and then let readers over-assume that every public async surface existed everywhere that runtime name appeared.

Current Tokio, Embassy, and RTIC docs make it clear this is not safe.
Some capabilities are:

- platform-scoped,
- feature-scoped,
- runtime-context-scoped,
- or host-vs-target scoped.

## Main `0.1` refinement

Keep the existing runtime-profile, shutdown, qualification, topology, capability-route, bridge, diff, and bundle artifacts.
Add three more first-class artifacts:

- `runtime-deployment-topology.receipt.json`
- `capability-availability.matrix.json`
- `surface-guard.report.json`

## What `0.1` should classify now

### `runtime-deployment-topology.receipt.json`

This is the compact answer to:

> “Which deployment lanes exist, and what runtime family/support posture belongs to each lane?”

It should classify at least:

- subject,
- lane id,
- lane role,
- host or target class,
- target triple or board class when known,
- runtime family,
- environment class,
- and support level.

Good initial lane roles:

- local development host,
- CI host,
- integration-test host,
- simulator host,
- production host,
- target board/MCU.

### `capability-availability.matrix.json`

This is the compact answer to:

> “Which async capabilities are actually available in which lane?”

It should classify at least:

- capability name,
- lane id,
- status,
- basis,
- and short caveats.

Good initial capabilities:

- `sleep`,
- `timeout`,
- `tcp_stream`,
- `udp_socket`,
- `async_fd`,
- `unix_signal`,
- `windows_ctrl_c`,
- `spawn_blocking`,
- `local_spawn`.

### `surface-guard.report.json`

This is the compact answer to:

> “What exact guards fence a support claim?”

It should classify at least:

- surface name,
- relevant lane or lane set,
- guard kind,
- guard expression,
- consequence,
- and evidence basis.

Good initial guard kinds:

- `cfg_target`,
- `feature_flag`,
- `runtime_context`,
- `resource_driver`,
- `provider_route`,
- `manual_review`.

## Recommended proving grounds

### Tokio lane-scope proving ground

Use Tokio to prove that one runtime family can still have lane-scoped capability truth:

- Unix signals are not Windows console signals.
- `AsyncFd` is Unix reactor-facing.
- Timer/I/O surfaces still depend on runtime context and enabled drivers.

### Embassy host-vs-target proving ground

Use Embassy because the book explicitly includes PC `std` examples while the executor docs keep embedded static-task posture explicit.
That makes it a strong proving ground for one family spanning multiple deployment lanes without one uniform support claim.

### RTIC target-structure proving ground

Use RTIC because it shows that a capability surface may be tied to dispatchers, priorities, and timer queues rather than a flat runtime/service brand.

### Mixed-repo proving ground

Use one project with host-side tooling/tests and target-side firmware to prove that “the repository uses async Rust” is not a sufficient support artifact.

## Suggested workspace split after this refinement

Keep the earlier split and add two focused internals:

- `runtime_assurance_topology`
- `runtime_assurance_matrix`

So the eventual workspace shape can become:

- `runtime_assurance_model`
- `runtime_assurance_discovery`
- `runtime_assurance_topology`
- `runtime_assurance_capabilities`
- `runtime_assurance_matrix`
- `runtime_assurance_check`
- `runtime_assurance_pack`
- `cargo-runtime-assurance`

## `0.1` adoption story after refinement

1. maintainer declares runtime lanes,
2. tool captures runtime family and service topology per lane,
3. tool emits deployment topology for host/CI/target surfaces,
4. maintainer records capability availability per lane,
5. tool emits guard reports for platform/context/provider-sensitive surfaces,
6. `doctor` warns when a public support claim lacks a lane or guard basis,
7. `pack` exports one portable bundle with runtime family, service topology, deployment topology, capability matrix, and guard reports together.

That is still compact enough for a real crate, but much closer to the hidden contract other people actually need.
