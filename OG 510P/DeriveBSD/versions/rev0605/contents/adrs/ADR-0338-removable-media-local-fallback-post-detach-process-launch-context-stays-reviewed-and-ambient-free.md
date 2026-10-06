# ADR-0338: Removable-media local fallback post-detach process launch context stays reviewed and ambient-free

- Status: accepted
- Date: 2026-05-18
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/453-preopen-map-diff-as-review-surface.md`, `docs/747-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`, `spec/preopen.map.schema.json`

## Context

ADR-0337 closed the hidden descriptor tail in the first host-local removable-media fallback lane: after verified capture and detach, later tool code starts on a reviewed closed-world descriptor set, with non-reviewed descriptors closed and parent-session stdio out.
That was necessary, but descriptor closure is not the whole process-start story.
A launched tool still receives environment variables, argument strings, and a current working directory.
Those fields are ordinary-looking startup context, but they can carry authority or covert policy: plugin discovery paths, helper search paths, locale/module loaders, temporary-directory routing, debug hooks, media-derived filenames passed as options, or cwd-relative opens that reintroduce `/ingest`, the authoritative store, or the launcher's parent directory.

The first lane needs an implementation-sized floor, not a folklore rule.
If descriptors are closed-world while `envp`, `argv`, or cwd remain inherited from the parent or derived from the hostile medium, then the archive would still be saying “reviewed preopen set” while leaving unreviewed startup authority beside it.

## Decision

For the first host-local removable-media fallback lane, the post-detach later worker now has a reviewed process-launch context in addition to a reviewed descriptor set. The receipt posture strings are `reviewed-minimal-env-no-inherited-parent-env`, `launcher-reviewed-argv-no-media-derived-args`, and `launcher-owned-empty-workdir-no-ingest-store-cwd`:

1. **The environment is minimal, reviewed, and not inherited from the parent.**
   - The launcher constructs a small allowlist for values required by the wrapper contract.
   - Parent environment variables do not flow through by default.
   - Search-path, plugin-path, loader, debug, proxy, home, temp, and application-discovery variables stay out unless an explicit later wrapper/broker contract admits them.

2. **The argument vector is launcher-reviewed and not media-derived.**
   - Worker `argv` comes from a fixed reviewed template or equivalent compiled launch contract.
   - The preserved subject is passed by already-reviewed descriptors/handles, not by a media path or hostile filename argument.
   - Media names may appear in receipts as evidence, but they do not become executable options or implicit parser policy.

3. **The current working directory is launcher-owned empty scratch, never inherited authority.**
   - The worker cwd is a launcher-prepared empty work directory such as `/work`.
   - It is not `/ingest`, not the authoritative quarantine store, and not the launcher's parent cwd.
   - Cwd-relative behavior is treated as compatibility plumbing only; authority remains in reviewed preopens.

4. **Receipts and preopen maps carry the posture.**
   - The canonical plan, receipt, detach receipt, attach grant, and preopen map record the environment, argv, and cwd postures.
   - The preopen map records the reviewed environment allowlist, the reviewed argv template, and the cwd posture so reviewers can see the complete launch shape beside the descriptor set.

## Consequences

### Positive

- The first removable-media lane now covers the full startup boundary: descriptors, stdio, environment, argv, and cwd.
- Tool admission becomes easier to review because hidden plugin discovery, search-path, or cwd-relative assumptions are exposed as contract violations.
- Receipts can explain why a later sanitizer/classifier did not keep authority to the original medium or parent process by startup-context accident.

### Negative / costs

- Some existing tools will need wrappers because they assume parent environment, cwd-relative resources, or filename-based inputs.
- Launchers must maintain a small reviewed environment allowlist and argv template instead of copying `environ` and string-building commands.
- Debugging requires explicit reviewed logging/observation channels rather than inherited shell context.

## Rejected alternatives

- **Trust descriptor closure alone.** Rejected because environment variables, argv strings, and cwd can still shape loader behavior, plugin discovery, search paths, helper selection, and path-relative opens.
- **Allow media-derived filenames as normal worker arguments.** Rejected because hostile names then become parser options or policy hints; preserved subject identity is already carried by digest-bound descriptors and receipts.
- **Keep the parent cwd for convenience.** Rejected because cwd is ambient path authority and can accidentally point at `/ingest`, the store, or a broader launcher workspace.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record the reviewed environment, argv, and cwd postures.
- Add a drift check that fails if docs or examples slide back into inherited parent environment, media-derived argv, or inherited `/ingest`/store cwd behavior.

## Links

- boundary doc: `docs/749-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md`
- previous cut: `adrs/ADR-0337-removable-media-local-fallback-post-detach-reviewed-descriptor-set-stays-closed-world-and-stdio-is-launcher-owned.md`
