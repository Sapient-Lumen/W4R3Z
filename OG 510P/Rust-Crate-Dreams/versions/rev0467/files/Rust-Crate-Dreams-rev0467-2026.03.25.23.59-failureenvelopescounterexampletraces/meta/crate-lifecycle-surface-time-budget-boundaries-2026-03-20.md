# Crate lifecycle-surface time-budget boundaries — 2026-03-20

This note keeps **P-0520 Crate Lifecycle Surface Pack Kit** from collapsing shutdown-barrier truth into fake “timeout support”.

A lifecycle-support crate must keep at least these nine truths separate:

1. **a stop signal was sent**,
2. **new intake stopped**,
3. **a named shutdown barrier completed**,
4. **some work escaped that barrier**,
5. **some dependency blocked that barrier**,
6. **a timeout stopped waiting**,
7. **some work still survived after that timeout returned**,
8. **the program reached quiescence**, and
9. **manual abort / cleanup / escalation is still owed**.

## What belongs in the time-budget seam

The time-budget seam is about questions like:

- Which named shutdown phases exist for this crate?
- Which of those phases are guaranteed under graceful shutdown versus merely attempted?
- What does a timeout mean: stop signal sent, barrier abandoned, or post-timeout survival still expected?
- Which workers, threads, tasks, or protocol components can survive after timeout returns?
- Does the runtime, framework, or crate invalidate handles while surviving work still runs?
- Is quiescence ever guaranteed, or is the best honest claim `wait_stopped_only`?

## What does **not** belong here

Do **not** collapse this seam into:

- generic cancellation-token support,
- generic retry or backoff policy,
- mere presence of a `shutdown_timeout` parameter,
- raw task-supervisor design,
- or general incident/diagnostics tooling.

Those may contribute evidence, but the time-budget seam is specifically the receiver-facing contract for what timeout and budget exhaustion *mean*.

## Preferred artifacts

If this lane keeps sharpening, prefer tiny artifacts such as:

- `shutdown-phase.report.json`
- `timeout-aftermath.receipt.json`
- `budget-ladder.policy.toml`

The point is not to produce another framework.
The point is to make it reviewable whether a stop path ended in:

- `signal_sent`,
- `accepting_stopped`,
- `tracked_tasks_drained`,
- `protocol_drains_finished`,
- `runtime_wait_abandoned`,
- `wait_stopped_only`,
- `blocking_thread_survives`,
- or `manual_abort_still_required`.

## LLM/archive reminder

Do **not** let future passes rephrase this seam as:

- “better graceful shutdown docs”,
- “timeouts are supported”,
- “the runtime can leak tasks”,
- or “server shutdown is complicated”.

The sharper missing value is a receiver-facing contract that says **which shutdown phase was reached before budget exhaustion and what is still alive afterward**.
