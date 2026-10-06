# ADR-0352: Removable-media local fallback post-detach export bundles are redacted and negative-tested

- Status: accepted
- Date: 2026-05-21
- Deciders: archive maintainers
- Consulted: `adrs/ADR-0351-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md`, `docs/293-attribute-indexed-metadata-and-live-queries.md`, `spec/removable.media.local.post_detach.export.bundle.schema.json`

## Context

ADR-0351 made receipt queryability a typed, redacted projection. That closes the ordinary index surface, but it leaves an operational escape hatch: support, incident, and debug workflows often ask for a bundle. A raw debug bundle can undo the whole r504-r507 lane by exporting raw receipt payloads, original media paths, observed device hints, host identity, untrusted filenames, body text, environment values, fd paths, mount paths, or secret material.

## Decision

Add `spec/removable.media.local.post_detach.export.bundle.schema.json` with kind `removable.media.local.post_detach.export.bundle`, the canonical example `spec/examples/removable.media.local.post_detach.export.bundle.json`, and a red corpus under `spec/examples/invalid/removable-media/post-detach-export-bundle/`.

The ordinary B/C removable-media local fallback now records `typed-post-detach-export-bundle-positive-and-negative-fixture-guarded`, `sha256:6262626262626262626262626262626262626262626262626262626262626262`, and `known-bad-post-detach-export-bundle-shapes-must-fail-validation` in the query projection, recovery evidence, post-detach contract backend evidence, canonical content import plan/receipt, and preopen map. Export starts from the redacted query projection and authoritative receipt digests, not from raw receipt payloads or media-derived strings.

The first export bundle is explicitly human-approved, recipient-bound, purpose-scoped to support or incident review, retention-bounded, offline-verifiable, and deletion-receipt-shaped. It carries redacted projection material, digest references, schema references/digests, a validation summary, and an approval receipt digest. It does not carry raw media bytes, derivative output bytes, raw query indexes, raw authoritative receipt payloads, secret material, live locators, raw paths, observed hints, host identity, filenames, or body text.

## Consequences

- Support and debug workflows become a typed export boundary rather than an ad hoc archive of everything interesting.
- The redacted query projection remains the only first-lane starting point for exported evidence.
- Raw debug bundles fail closed in the same way raw query indexes do.
- Recipient binding, bounded retention, and approval receipts become part of the evidence contract instead of ticket-system convention.
- Negative fixtures make the most common leaks executable: export without approval, raw path inclusion, raw receipt payload inclusion, host identity leakage, filename leakage, body-text inclusion, unbound recipient, unbounded retention, live locator, and secret material all fail validation.

## Alternatives considered

- **Let support tools decide what to redact.** Rejected because the support tool is exactly where urgent incident pressure tends to bypass security invariants.
- **Bundle raw receipts and trust downstream reviewers.** Rejected because raw receipts can contain precisely the path/device/user strings that the first lane forbids from becoming ambient observation authority.
- **Forbid all export.** Rejected because incident and support workflows still need portable evidence; the correct first lane is a small redacted bundle with explicit digest rehydration.

## Follow-up

- Teach the first launcher/indexer prototype to emit `removable.media.local.post_detach.export.bundle` only from a validated query projection.
- Add a future generic evidence-export bundle only after the removable-media lane proves stable.
- Define recipient-digest UX and deletion-receipt behavior for local-file versus approved remote-object transports.

## Links

- boundary doc: `docs/763-removable-media-local-fallback-post-detach-export-bundles-are-redacted-and-negative-tested.md`
- schema: `spec/removable.media.local.post_detach.export.bundle.schema.json`
- positive example: `spec/examples/removable.media.local.post_detach.export.bundle.json`
- red corpus: `spec/examples/invalid/removable-media/post-detach-export-bundle/`
- query projection: `docs/762-removable-media-local-fallback-post-detach-query-projection-is-typed-and-negative-tested.md`
