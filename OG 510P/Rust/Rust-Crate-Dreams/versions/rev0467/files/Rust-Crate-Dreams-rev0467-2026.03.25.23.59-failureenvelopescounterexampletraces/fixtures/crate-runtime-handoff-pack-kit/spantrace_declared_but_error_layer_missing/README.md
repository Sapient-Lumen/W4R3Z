# Scenario — span trace is declared but `ErrorLayer` is missing

This scenario exists to force **P-0513** to keep separate:

- the maintainer’s intended async-runtime handoff story,
- the actual span-trace witness,
- the difference between `EMPTY` and `UNSUPPORTED`,
- and the overall fidelity of the failure bundle.

## Why it matters

In async systems a span trace may be more useful than a raw backtrace, but that only helps if the runtime actually produced one.
If the crate claims span-context handoff while `tracing-error` status is effectively unsupported, a support bundle should not flatten that into “trace present”.

## Expected artifact pressure

- `capture-exactness.policy.json` should prevent unsupported span context from being presented as an exact captured value.
- `share-safety.receipt.json` should stay mostly uninteresting here; the important point is that safety is different from availability.
- `handoff-fidelity.report.json` should lower the handoff class when `spantrace_status` is missing, `EMPTY`, or `UNSUPPORTED`.
