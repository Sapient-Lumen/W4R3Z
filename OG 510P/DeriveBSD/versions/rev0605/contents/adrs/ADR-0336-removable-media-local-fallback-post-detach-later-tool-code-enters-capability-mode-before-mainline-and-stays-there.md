# ADR-0336: Removable-media local fallback post-detach later-tool code enters capability mode before mainline and stays there

- Status: accepted
- Date: 2026-03-28
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/741-removable-media-local-fallback-post-detach-delivery-stays-launcher-preopened-read-only-and-path-reopen-stays-out.md`, `docs/745-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md`, `spec/preopen.map.schema.json`

## Context

The recent removable-media first-cut stack already made post-detach execution much smaller:

- one preserved selected subject committed into authoritative quarantine store before detach,
- one fresh post-detach worker,
- one launcher-preopened read-only input object,
- one declared append-open append-only-protected derivative sink,
- no store browsing or subject reacquisition by path,
- and broker collection still naming derivative authority only after worker exit.

That still leaves one implementation-sized escape hatch.
The archive says the later worker receives only a tiny preopened capability set, but it still leaves open whether actual classify/scan/sanitize tool code starts before capability mode is entered.
If that timing stays unspecified, an implementation can quietly do late ambient opens during dynamic startup, plugin discovery, helper spawning, or wrapper glue and then claim the preopen map was the real authority story all along.
FreeBSD's Capsicum model is explicit that `cap_enter()` blocks access to global namespaces, that future descendants inherit capability mode, and that the flag cannot be cleared.
Keeping capability mode entry as a vague launcher detail therefore leaves a bigger hole than the surrounding removable-media cuts now permit.

## Decision

For the first host-local removable-media fallback lane:

1. **The launcher or its approved shim must enter capability mode before handing control to later tool mainline code.**
   - The later classify/scan/sanitize worker may only begin tool mainline execution after the launcher has opened and rights-limited the exact preserved-subject input object, the one declared derivative sink, and any other explicitly admitted helper descriptors.
   - This is the first-lane floor whether the launcher jumps into an already-linked program, uses `fexecve()`, or uses an approved equivalent.

2. **Capability mode remains part of the post-detach worker contract, not an optional optimization.**
   - Descendants inherit that mode.
   - The mode may not be cleared.
   - The first removable-media lane therefore stops treating “we preopened some files” as sufficient by itself.

3. **Ambient late path discovery stays out.**
   - After `cap_enter()`, no ambient absolute-path opens remain part of the first-lane story.
   - If some relative `openat()` behavior is still needed, it must stay under already preopened descriptors and cannot widen authority beyond the reviewed preopen map.

4. **Tools that cannot run on the preopened capability set stay out of the first lane unless an explicit wrapper/broker contract earns them back.**
   - The archive does not widen the first removable-media lane to fit tools that require ambient late opens, plugin discovery, or namespace browsing after startup. In plain terms, tools that cannot run on the preopened capability set stay out of the first lane.
   - Instead, those tools require a later explicit wrapper/broker decision or a different lane.

## Consequences

### Positive

- The first removable-media coding target now says when the Capsicum boundary becomes real instead of leaving it as launcher folklore.
- Support and forensics can explain why later worker path names remain compatibility-only even during runtime startup.
- Reviewers get a sharper admission rule for candidate sanitizers/classifiers: if the tool cannot run after capability-mode entry on the preopened set, it is not first-lane material.

### Negative / costs

- Some currently convenient path-shaped tools may now need a thin launcher shim or may fall out of the first lane entirely.
- Canonical examples and guardrails must now carry a small extra posture layer about capability-mode entry timing.

## Rejected alternatives

- **Leave capability-mode entry timing open and trust preopen-map review alone.** Rejected because the archive already relies on Capsicum to make path reopen and namespace browsing false after post-detach restart.
- **Admit late ambient path opens during startup as an implementation detail.** Rejected because that would reopen exactly the namespace authority the recent removable-media cuts have been removing.
- **Delay this question until a later launcher RFC.** Rejected because the current first coding target already needs an answer on whether tool startup itself can rely on ambient namespace access.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record post-detach capability-mode entry before later tool code and no-ambient-absolute-path-open posture.
- Add a drift check that fails if docs or examples slide back into treating capability-mode entry as optional or tool-mainline-late.

## Links

- boundary doc: `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`
- previous cut: `adrs/ADR-0335-removable-media-local-fallback-post-detach-derivative-slot-stays-append-open-and-append-only-protected-on-seekable-file-delivery.md`
