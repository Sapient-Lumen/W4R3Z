# Frontier note — async runtime support now also hinges on deployment topology and guarded capability claims (2026-03-23)

The async-runtime lane is now strong enough that the next missing layer is not another runtime abstraction and not another comparison chart.
The sharper missing layer is a **portable deployment-and-capability contract**.

## What the fresh sources changed

The official Rust sources still say async complexity and runtime lock-in are real pains.
That keeps demand high.

The runtime docs now sharpen a different supply-side lesson:

- Tokio’s signal surfaces are split into Unix and Windows modules instead of one universal signal capability.
- Tokio’s `AsyncFd` is explicitly Unix reactor-facing rather than a cross-platform promise.
- Tokio’s timer and stdio docs still require runtime context and enabled drivers for some capabilities.
- Embassy’s book says the ecosystem can run `std` examples on a PC, while Embassy executor docs still center static-task, no-`alloc` embedded execution.
- RTIC’s model keeps dispatchers, priorities, and timer queues tied to target structure rather than one flat async service layer.

Those sources say runtime family and service topology are necessary but still insufficient.
A crate can be “Tokio-based” or “Embassy-based” and still have materially different capability truth across:

- Linux servers,
- Windows consoles,
- host-side examples/tests,
- and MCU deployment targets.

## The sharper missing crate

The missing epic crate here is not another portability shim.
It is a crate that can publish:

1. **deployment topology** — which lanes exist and what runtime family each lane actually uses,
2. **capability availability** — which async capabilities exist in each lane,
3. **surface guards** — what cfg, feature, runtime-context, or provider route fences each claim,
4. **portable runtime bundles** — one reviewable handoff another engineer can reopen later.

## Review objects that now matter most

- `runtime-profile.receipt.json`
- `runtime-service-topology.receipt.json`
- `runtime-deployment-topology.receipt.json`
- `capability-availability.matrix.json`
- `surface-guard.report.json`
- `runtime-assurance-bundle.manifest.json`

## Why this is worth an epic crate

A crate like this would help library authors and product teams say something much more useful than “supports Tokio” or “supports Embassy”.
It would let them say:

> “Here are the deployment lanes we actually support, here are the capabilities available in each lane, and here are the guards that fence those claims.”

That is a durable, reviewable contribution to the Rust ecosystem because it helps people publish the hidden support contract that today still lives in examples, target-specific docs, cfgs, builder flags, and issue-thread folklore.
