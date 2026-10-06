# ADR-0334: Removable-media local fallback post-detach derivative slot stays empty write-only and no readback or truncate

- Status: accepted
- Date: 2026-03-28
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/294-oblivious-sandboxing-launchers.md`, `spec/preopen.map.schema.json`, `adrs/ADR-0332-removable-media-local-fallback-post-detach-derivative-egress-stays-broker-collected-and-worker-outbox-paths-stay-nonauthoritative.md`, `adrs/ADR-0333-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md`

## Context

The recent removable-media first-cut stack already made post-detach derivative egress much smaller:

- one preserved selected subject committed into authoritative quarantine store before detach,
- one fresh post-detach worker,
- one launcher-preopened read-only input object,
- one broker-collected derivative egress step,
- and one declared writable derivative sink slot with no extra worker result surface.

That still leaves one practical output-slot ambiguity.
The current canonical example names one writable sink file, but it does not yet say whether that slot is allowed to behave like an ordinary mutable scratch file from the worker's point of view.
Without a tighter contract, implementations can still drift between incompatible stories:

1. let the worker read back the derivative it is still constructing and start treating that scratch file as self-verifying state,
2. let the worker seek or truncate inside the slot and silently turn one reviewed sink into arbitrary mutable rewrite surface,
3. or keep the first lane on a launcher-precreated empty regular file whose worker-side authority is write-only and forward-only, with no readback or truncate.

Only the third answer keeps the output side aligned with the already-tight input side.

## Decision

For the first host-local removable-media fallback lane:

1. **The declared derivative slot starts empty.**
   - The canonical post-detach writable derivative sink slot is a launcher-precreated empty regular file.
   - In the canonical example, `sanitized_derivative_slot` still maps to `/work/output/invoice.sanitized.pdf`, but it must begin zero-length before later-worker execution starts.

2. **Worker authority on that slot stays write-only and forward-only.**
   - The later worker may write bytes into the declared slot, but it may not read back, seek within, or truncate that slot.
   - In Capsicum terms, the canonical sink omits `CAP_READ`, `CAP_SEEK`, and `CAP_FTRUNCATE`; the launcher may hand over only the smaller rights needed to write and inspect metadata.

3. **The first lane does not treat the derivative slot as mutable scratch state.**
   - The worker does not get to use the declared slot as a general temporary file with reread/overwrite cycles.
   - If a later transform genuinely needs richer mutable output staging, that must return as a later explicit lane or RFC instead of widening this first removable-media baseline.

4. **Broker collection still names authority.**
   - The launcher/broker still collects and remeasures bytes from the declared slot after worker exit before `content.import.receipt` names an authoritative derivative locator.
   - This decision narrows only what the worker can do with the slot before that brokered collection step.

## Consequences

### Positive

- The first implementation floor becomes easier to reason about: one preserved input object, one empty declared output slot, one monotonic worker write path, one broker collection step.
- Support and forensics no longer need to guess whether the later worker treated the slot as mutable scratch state before the authoritative derivative was measured.
- This keeps the removable-media first lane aligned with DeriveBSD's least-authority posture on both the input and output side.

### Negative / costs

- Some transforms that want to inspect or rewrite their own output in place need a later explicit lane.
- Canonical examples and receipts now need a small amount of extra posture detail for the derivative slot.

## Rejected alternatives

- **Allow readback from the declared slot as a harmless convenience.** Rejected because that quietly turns one reviewed sink into self-inspected mutable worker state.
- **Allow seek/truncate inside the declared slot and rely on broker remeasurement later.** Rejected because that makes the first lane's egress surface much more scratch-file-shaped than its current authority story admits.
- **Jump straight to a richer multi-phase output manifest.** Rejected because that is a broader RFC-sized lane, not the next small implementation floor.

## Follow-up

- Update the canonical removable-media local-ingest examples so the post-detach writable sink starts empty, omits readback/seek/truncate authority, and records that posture in the receipt.
- Add a drift check that fails if the examples or docs slide back toward mutable scratch-file semantics on the declared derivative slot.

## Links

- boundary doc: `docs/744-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md`
- previous cut: `adrs/ADR-0333-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md`
