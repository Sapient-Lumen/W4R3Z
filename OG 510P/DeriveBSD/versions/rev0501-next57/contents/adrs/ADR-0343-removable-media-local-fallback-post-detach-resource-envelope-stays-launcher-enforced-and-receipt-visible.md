# ADR-0343: Removable-media local fallback post-detach resource envelope stays launcher-enforced and receipt-visible

- Status: accepted
- Date: 2026-05-18
- Deciders: archive maintainers
- Consulted: `docs/65-resource-governance.md`, `docs/143-resource-controls-rctl-racct-cpuset.md`, `docs/247-resource-budgets-and-limits-as-evidence.md`, `docs/285-hierarchical-resource-limits-compilation.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/753-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md`, `spec/preopen.map.schema.json`

## Context

ADR-0337 through ADR-0342 made the post-detach removable-media later worker closed-world across descriptors, launch context, executable identity, runtime dependency closure, credentials, and process lifecycle. That still leaves a resource-authority seam: a daemon-free non-root worker can consume unbounded CPU time, wall clock, memory, process slots, open files, scratch bytes, or derivative-output bytes while still technically respecting its descriptor and lifecycle contract.

For the first removable-media local fallback, post-detach later work is a bounded one-shot operation over one preserved subject and one declared derivative sink. Resource limits are therefore not tuning hints. They are part of the reviewed authority envelope and need to be launcher-enforced and receipt-visible.

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use `launcher-enforced-resource-envelope-no-unbounded-worker-consumption`, `receipt-records-resource-envelope-and-observed-usage`, `resource-limit-hit-fails-closed-no-derivative-authority`, and `declared-derivative-output-size-bound-before-receipt`.

1. **The launcher owns the resource envelope.**
   - The launcher fixes CPU time, wall clock, memory, open-file count, process count, scratch bytes, and declared derivative-output bytes before tool mainline starts.
   - Backend details may use `rctl`/`racct`, `rlimit`, jail limits, cpuset, wrapper timers, or equivalent mechanisms, but the portable contract is the reviewed envelope.
   - The resource envelope belongs to the post-detach worker tree, not to media-derived input or tool-local defaults.

2. **The derivative sink has a reviewed size bound.**
   - The single declared derivative slot may not grow into an unbounded result surface.
   - The broker/launcher must enforce the declared derivative-output byte limit before any receipt names an authoritative derivative locator.
   - If a tool needs a larger output class, that is a new reviewed envelope or a later lane, not an implicit exception.

3. **Limit hits fail closed.**
   - A resource-limit hit records `resource-limit-hit-fails-closed-no-derivative-authority`.
   - Partial output from a killed, denied, throttled-to-failure, or timed-out worker does not become authoritative derivative evidence.
   - The failure may be diagnosable and supportable, but it is not a successful import derivative.

4. **Receipts expose limits and observed usage.**
   - Plans, receipts, detach mapping, and preopen maps carry `post_detach_resource_limits` / `resource_limits` plus posture strings.
   - Successful receipts also carry `post_detach_observed_resource_usage` so support can reason about right-sizing without reading host-local logs.
   - The attach grant carries `post_detach_resource_envelope_required = true` and the receipt posture expected for the lane.

## Consequences

- A malicious or malformed preserved subject cannot turn the first local fallback into an unbounded CPU/memory/process/output exhaustion lane.
- The single declared derivative sink stays bounded as egress authority instead of becoming infinite scratch or storage pressure.
- Support can distinguish successful bounded execution from resource-exhaustion denial with typed evidence.
- Larger or helper-heavy compatibility targets remain possible, but they need an explicit envelope and receipts rather than inheriting hidden host defaults.

## Alternatives considered

- **Rely on service defaults or jail teardown.** Rejected because default host limits are not reviewable artifact state and vary by installation.
- **Let tools self-limit.** Rejected because tool-local limits can be bypassed by parser bugs, helper launches, library behavior, or wrapper drift.
- **Record only observed usage.** Rejected because observed usage without an enforced envelope is after-the-fact telemetry, not authority control.
- **Treat resource exhaustion as a generic failure.** Rejected because this lane needs an explicit fail-closed posture that keeps partial derivatives non-authoritative.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record post-detach resource-envelope, receipt, output-bound, and fail-closed posture.
- Add a drift check that fails if the first lane slides back to unbounded worker consumption, unbounded derivative output, or derivative authority after a resource-limit hit.

## Links

- boundary doc: `docs/754-removable-media-local-fallback-post-detach-resource-envelope-stays-launcher-enforced-and-receipt-visible.md`
- previous cut: `adrs/ADR-0342-removable-media-local-fallback-post-detach-worker-lifecycle-stays-launcher-supervised-and-daemon-free.md`
