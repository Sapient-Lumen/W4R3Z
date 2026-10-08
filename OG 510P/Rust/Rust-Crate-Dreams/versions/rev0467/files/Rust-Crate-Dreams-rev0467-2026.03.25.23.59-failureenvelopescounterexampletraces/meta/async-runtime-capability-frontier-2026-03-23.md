# Frontier note — async runtime support now hinges on service topology and capability routes (2026-03-23)

The async-runtime lane is stronger today because the ecosystem is no longer blocked only on abstract language ergonomics.
The sharper missing layer is now above real runtime substrate and below full assurance-case work.

## What the fresh sources changed

The March 2026 challenges post still says async remains painful and that runtime lock-in is a real ecosystem problem.
The January 2026 safety-critical post explicitly asks for requirements for a safety-case-friendly async runtime.
Those are demand signals.

The current runtime docs add a sharper supply-side picture:

- Tokio documents that the runtime includes an I/O driver, scheduler, timer, and blocking pool, but also says hand-configured runtimes do not enable resource drivers by default.
- Tokio also documents that some types require entering a runtime context to be constructed safely at all.
- Embassy keeps executor and timer-provider routes meaningfully separate: integrated timers are one route, HAL time drivers are another.
- RTIC documents async software-task execution as dispatcher/priority scoped rather than as one flat general-purpose runtime.
- `async-compat` and `async_executors` show there is demand for bridges, but their docs also show that many bridges preserve hidden provider/context requirements instead of deleting them.
- `async-std`’s discontinuation note is a useful ecosystem-memory lesson: runtime family names and social momentum are not stable support contracts.

## The sharper missing crate

The missing epic crate here is not another runtime abstraction layer and not another benchmarking harness.
It is a **portable async-service contract** that can say:

1. which runtime family is in each lane,
2. which services are actually present,
3. which provider/activation route makes each service available,
4. which adapters are being used,
5. and which lock-in or manual-review debt remains.

## Review objects that now matter most

- `runtime-profile.receipt.json`
- `runtime-service-topology.receipt.json`
- `capability-route.receipt.json`
- `compatibility-bridge.report.json`
- `runtime-assurance-bundle.manifest.json`

## Why this is worth an epic crate

A crate like this would help backend teams, embedded teams, robotics teams, and safety-adjacent teams all answer the same practical question:

> “What async services does this crate/system really depend on, and what must be true for those services to exist?”

That is a bigger and more durable contribution than another runtime wrapper because it helps people publish and review the hidden contract that today still lives in scattered docs, builder flags, target-specific setup, and adapter folklore.
