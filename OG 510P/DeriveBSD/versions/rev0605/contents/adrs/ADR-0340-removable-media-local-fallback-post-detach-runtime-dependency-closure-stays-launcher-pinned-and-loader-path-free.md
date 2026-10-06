# ADR-0340: Removable-media local fallback post-detach runtime dependency closure stays launcher-pinned and loader-path-free

- Status: accepted
- Date: 2026-05-18
- Deciders: archive maintainers
- Consulted: `docs/49-capsicum-casper-hardening.md`, `docs/180-capability-mode-dynamic-linking.md`, `docs/289-exec-integrity-policy-and-verified-execution.md`, `docs/486-exec-integrity-authority-and-verified-execution-boundary.md`, `docs/750-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md`, `spec/preopen.map.schema.json`

## Context

ADR-0339 made the later worker's executable identity launcher-resolved, digest-pinned, and path-search-free. That closes the obvious tool-selection hole, but not the whole runtime-code surface.

A digest-pinned executable can still execute different bytes if the dynamic loader, shared-library closure, interpreter path, NSS/engine/module lookup, or loader environment is selected from mutable host state. A first-lane sanitizer that starts from a pinned binary but then resolves libraries through `LD_LIBRARY_PATH`, cwd, `/ingest`, a host package view, or media-derived paths has only moved the ambient authority one layer down.

The first removable-media local fallback therefore needs a receipt-visible runtime dependency closure, not just a receipt-visible entrypoint digest.

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use `launcher-pinned-runtime-dependency-closure-no-ambient-loader-search` and `no-ld-library-path-cwd-or-media-derived-loader-inputs`.

1. **The runtime dependency closure is launcher-pinned before handoff.**
   - The launcher selects the executable's runtime dependency closure from reviewed policy or a trusted store locator.
   - The closure digest is recorded beside the executable digest, wrapper contract digest, and preopen map.
   - The worker does not discover libraries, interpreters, engines, modules, or runtime helper code from cwd, `/ingest`, parent environment, removable-media paths, or mutable host package state.

2. **Ambient loader path inputs stay out of the first lane.**
   - Loader-affecting environment variables such as `LD_LIBRARY_PATH` are not admitted into the reviewed environment allowlist.
   - Cwd-relative library lookup, media-derived library paths, and host-global loader hints are not authority-bearing inputs for this lane.
   - Dynamic loader/interpreter resolution is either inside the pinned closure or out of lane.

3. **Late dynamic loading stays out unless explicitly brokered later.**
   - The first lane already records `no-implicit-helper-or-plugin-discovery`; this decision extends the same shape to ordinary runtime dependency loading.
   - A legacy sanitizer that needs late `dlopen`, engines, NSS modules, font/plugin discovery, or helper process lookup must earn a later explicit wrapper/broker contract with its own preopens and receipts.

4. **Receipts expose the dependency closure rather than trusting the current host.**
   - Plans, receipts, detach mapping, and the preopen map carry `post_detach_runtime_dependency_posture`, `post_detach_runtime_dependency_closure_digest`, and `post_detach_dynamic_loader_posture` where applicable.
   - Support can answer which runtime code closure was in force without replaying the host's current linker/package state.

## Consequences

- A package upgrade or library replacement cannot silently change the code executed by the first removable-media fallback while preserving the same executable digest.
- `LD_LIBRARY_PATH`, cwd, `/ingest`, media filenames, and host-global loader hints do not become hidden authority.
- The first lane remains practical: static tools, store-managed dynamic closures, or launcher-prelinked wrappers fit; ambient dynamic discovery does not.
- Tools that need richer runtime-code discovery remain possible, but only in a later explicit wrapper/broker lane.

## Alternatives considered

- **Treat the executable digest as sufficient.** Rejected because dynamic linking and interpreter/helper resolution can execute different bytes under the same entrypoint digest.
- **Rely on the host's current package database.** Rejected because receipts need historical identity; the current host is not evidence for past runtime dependencies.
- **Allow `LD_LIBRARY_PATH` because the environment is reviewed.** Rejected for the first lane because loader path variables are code-selection authority, not ordinary configuration.
- **Require static linking for all later tools.** Rejected as too narrow for B/C compatibility; the accepted rule permits pinned dynamic closures while rejecting ambient loader search.

## Follow-up

- Update the canonical removable-media local-ingest examples so they record the post-detach runtime dependency closure and dynamic-loader posture.
- Add a drift check that fails if the first lane slides back to ambient loader search, host-global library resolution, or unrecorded dependency closure identity.

## Links

- boundary doc: `docs/751-removable-media-local-fallback-post-detach-runtime-dependency-closure-stays-launcher-pinned-and-loader-path-free.md`
- previous cut: `adrs/ADR-0339-removable-media-local-fallback-post-detach-executable-identity-stays-launcher-pinned-and-path-search-free.md`
