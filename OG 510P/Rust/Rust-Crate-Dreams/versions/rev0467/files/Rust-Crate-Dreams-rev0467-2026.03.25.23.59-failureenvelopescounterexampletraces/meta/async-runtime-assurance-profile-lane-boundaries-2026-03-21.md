# Lane boundaries — Async Runtime Assurance Profile Kit (2026-03-21)

Do not let this lane collapse into a fake “async runtime support” story.

## Keep these review objects separate

1. **runtime family / scheduler model**
   - Tokio-style I/O runtime,
   - Embassy-style cooperative embedded executor,
   - RTIC-style interrupt-priority scheduler,
   - or custom/manual-review.
2. **allocation posture**
   - requires heap,
   - can run without heap,
   - static task allocation,
   - shared stack without hard dynamic allocator dependence,
   - or mixed/manual-review.
3. **shutdown behavior**
   - when async tasks actually stop,
   - what happens to blocking work,
   - what timeout means,
   - what becomes unusable after shutdown.
4. **preemption/timing authority**
   - cooperative only,
   - priority preemptive,
   - integrated timer queue,
   - hardware timer queue,
   - or external/manual-review.
5. **qualification basis**
   - documentation only,
   - metrics/instrumentation,
   - on-target measurement,
   - imported assurance artifact,
   - or manual review.

## Do not confuse

- a language-level async improvement with a runtime support contract;
- a runtime name in `Cargo.toml` with a published runtime profile;
- a clean shutdown helper with a proof that all work stopped;
- no-`alloc` marketing with a full allocation-posture answer;
- metrics availability with qualification evidence;
- or interrupt-priority scheduling with a general-purpose async runtime.

## Keep these adjacent lanes distinct

- **P-0520 Crate Lifecycle Surface Pack Kit** owns stop verbs, shutdown barriers, timeout aftermath, and teardown evidence at the crate/application support surface.
- **P-0529 Channel Surface Contract Kit** owns channel capacity, overflow, delivery, and drain semantics.
- **P-0521 Crate Resource Surface Pack Kit** owns budget topology, clone sharing, and aggregate bounds.
- **P-0484 Toolchain & Target Support Contract Kit** owns target posture, components, docs posture, and contributor bootstrap truth.
- **P-0503 Assurance Case Workbench Kit** owns claim/evidence graphs and broader assurance-argument structure.

This lane sits above imported runtime substrate and below full system assurance.
It should answer:

> “What runtime model did we actually choose, what support-sensitive behavior comes with it, and what evidence backs that claim?”

not:

> “Is the whole system safe?”


## Also keep these newly-explicit review objects separate

6. **qualification basis**
   - docs only,
   - docs plus metrics,
   - docs plus on-target measurement,
   - imported assurance artifact,
   - or manual review.
7. **runtime drift meaning**
   - runtime model changed,
   - evidence class changed,
   - support meaning changed,
   - or manual review required.
8. **bundle shape**
   - single hosted runtime lane,
   - single target runtime lane,
   - mixed host-and-target lanes,
   - or manual-review-only export.

Do not confuse:

- runtime metrics with target qualification,
- a host-side async harness with shipped target behavior,
- or a multi-lane runtime bundle with one uniform runtime claim.
