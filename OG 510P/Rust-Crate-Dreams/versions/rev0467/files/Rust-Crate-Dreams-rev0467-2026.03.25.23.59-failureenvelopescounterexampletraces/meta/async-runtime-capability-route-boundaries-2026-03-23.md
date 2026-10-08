# Lane boundaries — async runtime capability routes and service topology (2026-03-23)

Do not let this lane collapse into a fake “runtime support” or “async portability” story.

## Keep these review objects separate

1. **runtime family**
   - Tokio-style hosted runtime,
   - Embassy-style embedded executor,
   - RTIC-style interrupt-priority scheduler,
   - smol/futures-style executor family,
   - or mixed/custom lane.
2. **service topology**
   - where spawn, time, I/O, process, signal, and blocking services actually come from,
   - and whether those services are absent or lane-specific.
3. **capability route**
   - the exact provider and activation route required for a capability such as `sleep`, `TcpStream`, or `spawn_blocking`.
4. **compatibility bridge**
   - which trait/context mismatch is bridged,
   - and which runtime/provider constraint still remains.
5. **evidence class**
   - docs only,
   - docs plus metrics,
   - docs plus on-target measurement,
   - imported assurance artifact,
   - or manual review.

## Do not confuse

- a runtime name with a service-topology answer;
- an executor with time, I/O, signal, or blocking services;
- an adapter crate with erased runtime lock-in;
- a board/HAL time driver with an executor-intrinsic timer guarantee;
- or host-only bridge success with shipped target/runtime support.

## Keep these adjacent lanes distinct

- **P-0520 Crate Lifecycle Surface Pack Kit** owns stop verbs, teardown barriers, and lifecycle-phase evidence.
- **P-0529 Channel Surface Contract Kit** owns channel capacity, delivery, and drain semantics.
- **P-0521 Crate Resource Surface Pack Kit** owns budget topology and clone/resource multiplication.
- **P-0484 Toolchain & Target Support Contract Kit** owns target posture, docs posture, and tested-environment truth.
- **P-0073 Async Replay Debugger Kit** owns replay fidelity and schedule/time reconstruction.
- **P-0503 Assurance Case Workbench Kit** owns broader claims/evidence graphs.

This lane sits above runtime/executor substrate and below full-system portability or assurance work.
It should answer:

> “What async services really exist here, what makes them available, and what bridge debt remains?”

not:

> “Can we make every async crate runtime-neutral?”
