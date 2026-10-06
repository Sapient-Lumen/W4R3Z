# ADR-0339: Removable-media local fallback post-detach executable identity stays launcher-pinned and path-search-free

- Status: accepted
- Date: 2026-05-18
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/294-oblivious-sandboxing-launchers.md`, `docs/746-removable-media-local-fallback-post-detach-later-tool-code-enters-capability-mode-before-mainline-and-stays-there.md`, `docs/749-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md`, `spec/preopen.map.schema.json`

## Context

ADR-0338 made the post-detach later worker's process-launch context reviewed: environment, argv, and cwd no longer come from parent or removable-media state. That still leaves one ordinary-looking startup decision with authority: which executable image actually runs.

A fixed argv template that begins with `sanitize-pdf` is not enough if the launcher later resolves that name through `PATH`, cwd, a mutable host package view, or helper/plugin discovery. In that shape, the archive could review descriptors and launch context while the actual code identity remains a moving ambient lookup.

The first removable-media local fallback needs the executable identity to be as explicit as the descriptor set: launcher-selected, digest-pinned, and receipt-visible.

## Decision

For the first host-local removable-media fallback lane, the post-detach later worker now uses `launcher-resolved-executable-digest-no-path-search` and `receipt-records-executable-and-wrapper-digests`.

1. **The executable is launcher-resolved before handoff and digest-pinned.**
   - The launcher resolves the tool from reviewed host policy or a trusted store locator before creating the worker.
   - The worker does not perform `PATH` search, cwd-relative executable lookup, or media-derived executable selection.
   - The executable digest is recorded beside the preopen map and launch context.

2. **The wrapper contract digest is receipt-visible.**
   - The wrapper contract digest covers the reviewed executable identity, argv template, environment allowlist, cwd, descriptor/stdio posture, and any helper/plugin discovery posture admitted by the wrapper.
   - Review and support do not have to reconstruct the real wrapper from tool-name folklore.

3. **Implicit helper and plugin discovery stay out of the first lane.**
   - The first lane records `no-implicit-helper-or-plugin-discovery`.
   - A tool that needs plugin/helper/module discovery must earn a later explicit wrapper/broker contract with its own preopens and receipt fields.

4. **Receipts expose the executable identity rather than trusting the current host.**
   - The import plan, import receipt, detach receipt, and preopen map all carry the executable posture plus the executable/wrapper digests.
   - The launcher may still show a human-friendly tool name, but the authority handle is the digest-pinned executable and wrapper contract.

## Consequences

- A renamed or replaced host binary cannot silently change what code processed a removable-media subject while preserving the same receipt shape.
- `PATH`, cwd, package-manager current state, and media filenames no longer serve as hidden executable selection inputs.
- Support can answer “what code and wrapper policy produced this derivative?” from the portable receipt stack.
- Legacy tools that require ambient helper/plugin discovery stay out of the first lane until a later wrapper/broker contract names and receipts that surface.

## Alternatives considered

- **Trust the argv tool name.** Rejected because names are mutable handles and can hide `PATH` or package-view changes.
- **Trust the host's current package database during review.** Rejected because support/replay needs the receipt's historical executable identity, not the host's later state.
- **Allow plugin discovery while keeping argv fixed.** Rejected for the first lane because plugin/helper discovery is executable authority; it needs its own reviewed preopen/broker surface.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record executable and wrapper identity after detach.
- Add a drift check that fails if the first lane slides back to `PATH` search, unrecorded executable identity, or implicit helper/plugin discovery.

## Links

- boundary doc: `docs/750-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md`
- previous cut: `adrs/ADR-0338-removable-media-local-fallback-post-detach-process-launch-context-stays-reviewed-and-ambient-free.md`
