# ADR-0337: Removable-media local fallback post-detach reviewed descriptor set stays closed-world and stdio is launcher-owned

- Status: accepted
- Date: 2026-03-28
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/453-preopen-map-diff-as-review-surface.md`, `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`, `spec/preopen.map.schema.json`

## Context

The recent removable-media first-cut stack already made post-detach execution much smaller:

- one preserved selected subject committed into authoritative quarantine store before detach,
- one fresh post-detach worker,
- one launcher-preopened read-only input object,
- one declared append-open append-only-protected derivative sink,
- and capability mode entry before later tool mainline begins.

That still leaves one implementation-sized escape hatch.
Capability mode removes ambient global namespaces, but it does not by itself prove that the later worker started with only the reviewed descriptors.
If the launcher can still leak extra inherited descriptors into later tool code — parent TTYs, control sockets, directory handles, logging channels with broader authority, stale helper pipes — then the archive still says “tiny reviewed capability set” while the real runtime story stays larger.
FreeBSD’s process setup model is explicit that spawn file actions transform the parent descriptor set into the child descriptor set, `posix_spawn_file_actions_addclosefrom_np()` can close all descriptors at or above a threshold before the new image executes, and `fexecve()` can execute by descriptor instead of path.
That makes the next honest first-lane question not “did cap_enter happen?” but “what exact descriptor set crossed that boundary?”

## Decision

For the first host-local removable-media fallback lane:

1. **The post-detach later worker inherits only the reviewed descriptor set.**
   - Any descriptor not explicitly admitted for that later worker stays out.
   - The reviewed set is closed-world rather than “reviewed plus whatever the launcher happened to leave open”.

2. **Non-reviewed inherited descriptors are closed before later tool mainline begins.**
   - The launcher or its approved shim must close or spawn-closefrom all non-reviewed descriptors before handing control to later classify/scan/sanitize tool code.
   - `closefrom()` / `posix_spawn_file_actions_addclosefrom_np()` or an equivalent reviewed mechanism are acceptable implementation strategies; the portable boundary is the outcome, not one exact API.

3. **stdio stays launcher-owned and non-parent-session-shaped.**
   - `stdin` stays inert null/empty input only in this first lane.
   - `stdout` and `stderr` may exist only as launcher-owned observation channels or reviewed append-only log sinks.
   - Parent TTYs, interactive session sockets, and similar inherited operator/session surfaces stay out.

4. **The reviewed descriptor set remains small on purpose.**
   - The preserved selected subject and the one declared derivative sink remain the core data-plane descriptors.
   - If a tool needs extra helper descriptors, they must be explicitly reviewed and carried in the preopen map; they do not arrive by inheritance folklore.

## Consequences

### Positive

- The first removable-media lane now says what crosses the post-detach startup boundary, not just when `cap_enter()` happens.
- Launcher, receipt, and support surfaces can now explain why the worker had no hidden parent-session or stale-helper descriptor authority.
- Candidate tools become easier to screen: if they require surprise inherited descriptors or interactive TTY semantics, they are not first-lane material.

### Negative / costs

- Some convenient launcher/logging/debug patterns now need an explicit reviewed channel instead of piggybacking on inherited stdio or extra pipes.
- Canonical examples and guardrails must carry one more posture layer about descriptor closure and stdio.

## Rejected alternatives

- **Treat capability mode entry alone as sufficient.** Rejected because extra inherited descriptors can still carry real authority across that boundary.
- **Allow parent-session stdio in the first lane as a convenience.** Rejected because that would quietly reopen interactive or session-shaped authority in exactly the lane that is trying to become launcher-reviewable and detached from the original medium.
- **Pin one exact launcher API.** Rejected because the archive needs the portable reviewed outcome (closed-world descriptor set) rather than a single implementation recipe.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record the closed-world reviewed descriptor set and launcher-owned stdio posture.
- Add a drift check that fails if docs or examples slide back into treating hidden inherited descriptors or parent-session stdio as acceptable first-lane behavior.

## Links

- boundary doc: `docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`
- previous cut: `adrs/ADR-0336-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`
