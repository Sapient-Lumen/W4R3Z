# ADR-0347: Removable-media local fallback post-detach persistent state stays absent and scratch stays ephemeral

- Status: accepted
- Date: 2026-05-18
- Deciders: archive maintainers
- Consulted: `docs/757-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md`, `docs/193-resource-budget-capabilities.md`, `spec/preopen.map.schema.json`

## Context

ADR-0337 through ADR-0346 made the post-detach removable-media later worker closed-world across descriptors, launch context, executable identity, runtime dependency closure, credentials, lifecycle, resources, peer interaction, ambient host inputs, and network egress. One remaining authority seam is persistent state: tools often expect `$HOME`, cache directories, font/config stores, history files, thumbnail databases, crash dumps, lock files, or reusable temporary directories.

Even without network authority, that state can shape derivative bytes, leak subject-derived names, or make support reconstruct hidden inputs from host-local leftovers. The first removable-media local fallback is supposed to be a one-shot computation over one preserved subject and one declared derivative sink, not a tool session that accumulates cache/config/history state across subjects.

## Decision

For the first host-local removable-media fallback lane, post-detach later workers now use `persistent-state-absent-no-home-cache-or-host-state-writes`, `receipt-records-persistent-state-absence-and-scratch-cleanup`, `launcher-created-empty-scratch-nonauthoritative`, `scratch-destroyed-before-derivative-receipt`, and `no-user-home-cache-config-or-history-state`.

These strings do not require one specific filesystem primitive. They require that ordinary post-detach later work has no user-home, host-cache, host-config, history, crash-dump, tool-state, or reusable temporary-state authority; that any scratch visible to the worker is launcher-created, empty, scoped to this run, nonauthoritative, bounded by the resource envelope, and destroyed before derivative receipt authority; and that the absence/cleanup posture is receipt-visible.

## Consequences

- The later worker cannot convert `$HOME`, XDG cache/config/state, fontconfig caches, thumbnail databases, shell/tool history, crash dumps, lock files, license databases, plugin caches, or reusable temp directories into hidden derivative input authority.
- Scratch bytes remain execution plumbing only. They do not become authoritative output, durable evidence, or a second result surface.
- Receipts become clearer: a successful derivative now records that the worker did not read or write durable host/tool state and that scratch cleanup completed before the derivative locator became authoritative.

## Alternatives considered

- **Rely on disposable worker lifetime.** Rejected because a disposable process can still write durable state if a host home/cache/config path or reusable temp directory is visible.
- **Treat scratch cleanup as an implementation detail.** Rejected because stale scratch can leak subject-derived data and confuse later support analysis even when the derivative slot is correct.
- **Allow tool caches for performance.** Rejected for the first lane. Any performance/cache compatibility lane must explicitly name cache scope, invalidation, receipt posture, and subject-separation rules.

## Follow-up

- Update canonical removable-media local-ingest examples so they record persistent-state absence, scratch authority, scratch cleanup, and cache/config/history posture.
- Add a drift check that fails if the first lane slides back to user-home/cache/config/history writes, reusable scratch, or receipt-invisible cleanup assumptions.

## Links

- boundary doc: `docs/758-removable-media-local-fallback-post-detach-persistent-state-stays-absent-and-scratch-stays-ephemeral.md`
- previous cut: `adrs/ADR-0346-removable-media-local-fallback-post-detach-network-egress-stays-absent-and-receipt-visible.md`
