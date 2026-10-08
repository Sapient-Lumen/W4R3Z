# cargo-config-layer-receipt-kit lane boundaries — 2026-03-20

This note keeps **P-0474 Cargo Config Layer Receipt Kit** from collapsing into adjacent lanes.

## What this lane is for

This lane is for a **reviewable Cargo configuration contract** over one effective config surface.
It should answer:

- what config sources participated,
- what won and what lost,
- whether the bundle came from one real invocation or a reconstruction,
- and whether the exported artifact is actually replayable after redaction.

## Keep this distinct from nearby lanes

### Distinct from `P-0516 crate-configuration-scenario-pack-kit`

`P-0516` is about crate-authored receiver-facing setup lanes and named scenarios.
`P-0474` is about Cargo’s own configuration hierarchy, override precedence, path roots, and redacted support bundles.

### Distinct from `P-0477 cargo-publish-receipt-join-kit`

`P-0477` is about post-publish truth and public-surface convergence.
`P-0474` is about the config basis that shaped a Cargo invocation before or during the workflow.

### Distinct from generic config frameworks

This lane is not:

- another TOML/Serde settings library,
- another env-layering app framework,
- or another editor for dotfiles.

It should import Cargo’s config rules and publish one conservative support contract above them.

## Four truths this lane must keep separate

1. **effective config** — what Cargo would use after precedence and merging;
2. **invocation basis** — whether the bundle came from a live wrapped command, imported invocation context, or later reconstruction;
3. **redaction safety** — whether secrets and private paths were hidden;
4. **replayability** — whether the remaining bundle is sufficient for another machine to reproduce the same config surface.

## Ordinary mistakes future passes must resist

Do not let the archive treat any of the following as interchangeable:

- project defaults and invocation-scoped `--config` injection,
- env-based path roots and config-file-relative path roots,
- a safe-to-share bundle and a fully replayable bundle,
- credentials-file participation and safe disclosure of provider arguments,
- nightly inspection output and a durable review artifact.

## Preferred artifact vocabulary

- `config-files.graph`
- `config-origins`
- `config-paths.report`
- `config-redaction.report`
- `invocation-basis.receipt`
- `replayability.report`

If a future pass adds more detail, it should extend one of those objects before inventing a vague new umbrella.
