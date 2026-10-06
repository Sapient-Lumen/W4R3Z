# ADR-0335: Removable-media local fallback post-detach derivative slot stays append-open and append-only-protected on seekable file delivery

- Status: accepted
- Date: 2026-03-28
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/294-oblivious-sandboxing-launchers.md`, `spec/preopen.map.schema.json`, `adrs/ADR-0333-removable-media-local-fallback-post-detach-derivative-egress-stays-single-declared-slot-and-no-extra-worker-result-surface.md`, `adrs/ADR-0334-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md`

## Context

The recent removable-media first-cut stack already made post-detach derivative egress much smaller:

- one preserved selected subject committed into authoritative quarantine store before detach,
- one fresh post-detach worker,
- one launcher-preopened read-only input object,
- one broker-collected derivative egress step,
- one declared writable derivative sink slot with no extra worker result surface,
- and that sink now starts empty and stays no-readback/no-truncate from the worker's point of view.

That still leaves one platform-shaped ambiguity.
The current canonical example models the later-worker sink as a seekable regular file but also claims that the worker can write it with `CAP_WRITE` while omitting `CAP_SEEK`.
FreeBSD's Capsicum documentation is more precise than that: for files and other seekable objects, `CAP_SEEK` may also be required for `write(2)`/`pwrite(2)`-class operations, and the `cap_rights_init(3)` examples pair write capability with seek when the target is a seekable file.
Without a tighter cut, implementations can drift between incompatible stories:

1. keep the regular-file sink and quietly re-add `CAP_SEEK`, thereby making the first lane look broader than the archive admits,
2. jump immediately to a pipe/stream-only sink contract and force path-shaped sanitizers back through a larger launcher/RFC redesign,
3. or keep the regular-file sink for the first lane but require it to be launcher-preopened `O_APPEND`, append-only-protected while the worker runs, and explicit that any `CAP_SEEK` present there is implementation ballast for seekable-file delivery rather than rewrite authority.

Only the third answer keeps the first lane buildable on FreeBSD without silently lying about what the platform needs.

## Decision

For the first host-local removable-media fallback lane:

1. **The declared derivative slot stays regular-file-shaped, but the launcher must hand it over append-open.**
   - The canonical later-worker sink remains the launcher-precreated empty regular file at `/work/output/invoice.sanitized.pdf`.
   - The launcher must preopen that sink `O_APPEND` (or an implementation-equivalent append-open posture) before later-worker execution begins.

2. **Seekable-file delivery must stay append-only-protected while the worker runs.**
   - The launcher must keep the sink append-only-protected for the worker's lifetime (`UF_APPEND`/equivalent host-enforced append-only posture).
   - The worker still does not get readback or truncate authority on that sink.
   - The worker also does not get `CAP_FCNTL`, so it cannot clear the append-open posture itself.

3. **If `CAP_SEEK` appears on the later-worker sink, it is ballast, not rewrite authority.**
   - On FreeBSD seekable regular files, `CAP_SEEK` may be needed alongside `CAP_WRITE` for write-class operations.
   - The archive therefore stops pretending `CAP_SEEK` always stays out on this particular sink.
   - But the design meaning stays narrow: append-open + append-only protection + no readback + no truncate + no `CAP_FCNTL` is still the first-lane authority floor.

4. **Broker collection still names authority.**
   - The launcher/broker still collects and remeasures bytes from the declared sink after worker exit before `content.import.receipt` names an authoritative derivative locator.
   - This decision only makes the worker-side sink posture more platform-honest on FreeBSD.

## Consequences

### Positive

- The first implementation floor stops relying on an imprecise Capsicum rights story for seekable regular files.
- Path-shaped sanitizers can stay in the first lane without widening execution into a browseable output namespace.
- Support and forensics now have a tighter statement of *why* `CAP_SEEK` can appear without turning the sink back into general mutable scratch state.

### Negative / costs

- Canonical examples and checks need one more layer of posture detail: append-open, append-only-protected, no `CAP_FCNTL`, and seek-is-ballast.
- Some readers may find the sink contract less aesthetically simple than “just omit `CAP_SEEK`”, even though it is more implementable on FreeBSD.

## Rejected alternatives

- **Keep claiming the regular-file sink omits `CAP_SEEK` and rely on implementation folklore.** Rejected because the FreeBSD Capsicum docs do not justify that simplification for seekable files.
- **Switch the first lane immediately to a pure pipe/stream sink.** Rejected for now because that is a larger launcher/tooling cut and would widen this iteration beyond the next small implementation floor.
- **Allow `CAP_FCNTL` and trust later workers not to clear append-open posture.** Rejected because it weakens exactly the boundary this cut is trying to make mechanically honest.

## Follow-up

- Update the canonical removable-media local-ingest examples so the post-detach writable sink is recorded as append-open and append-only-protected, keeps `CAP_READ`/`CAP_FTRUNCATE`/`CAP_FCNTL` out, and treats any `CAP_SEEK` as seekable-file ballast rather than rewrite authority.
- Add a drift check that fails if the examples or summary docs slide back toward “regular file + CAP_WRITE only” or forget the append-open / append-only-protected posture.

## Links

- boundary doc: `docs/745-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md`
- previous cut: `adrs/ADR-0334-removable-media-local-fallback-post-detach-derivative-slot-stays-empty-writeonly-and-no-readback-or-truncate.md`
