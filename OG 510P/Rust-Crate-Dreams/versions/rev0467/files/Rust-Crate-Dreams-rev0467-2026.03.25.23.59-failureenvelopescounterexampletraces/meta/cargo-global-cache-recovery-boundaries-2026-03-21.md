# Cargo global-cache recovery boundaries — 2026-03-21

This note keeps **P-0480 Cargo Global Cache Policy & GC Receipt Kit** from collapsing cleanup plans into vague “space reclaimed” stories.

## The distinct truth

A cleanup artifact must say **what surface is being cleaned** and **how entries come back after eviction**.
That is not identical to:

- how many bytes will be recovered,
- whether automatic GC is enabled,
- whether a team shares `CARGO_TARGET_DIR`,
- or what a future user-wide build cache might support.

A worthy cache-policy crate should therefore keep **cache-surface truth** and **recovery-obligation truth** explicit.

## Surfaces that must not be flattened together

1. **Cargo-home global cache**
   - registry indexes
   - `.crate` downloads
   - unpacked `registry/src`
   - git db/checkouts

2. **Target-dir final artifacts**
   - binaries, docs, packaged tarballs, timing reports
   - useful to end users of Cargo

3. **Build-dir intermediate artifacts**
   - internal compiler/Cargo state
   - layout is internal and subject to change

4. **Future user-wide build cache / plugin-backed cache**
   - cross-workspace artifact reuse
   - different lookup and eviction story again

## Recovery classes that must not be flattened together

1. **locally_recreatable**
   - eviction costs rebuild/regen time more than network fetch

2. **redownload_required**
   - eviction costs later network/download time or mirror access

3. **plugin_or_remote_fetch**
   - entry is expected to return from an external cache route rather than Cargo home alone

4. **unknown_or_manual_review**
   - mixed toolchains, air-gap assumptions, or evolving Cargo substrate make exact recovery cost unclear

## Why this matters

If the archive forgets these splits, it will quietly produce fake certainty such as:

- “safe to clean” when the user is often offline and the recovered space is mostly redownload-only,
- “Cargo GC covers our shared target dir” when the policy only covers Cargo home,
- or “future cross-workspace cache entries are just more registry cache” when the recovery and trust story is materially different.

## Receiver-facing artifacts to prefer

- `cache-surface.receipt.json` — exactly which cache surface a plan or receipt governs
- `recovery-obligation.report.json` — how cleaned entries return and who bears the cost
- `gc.receipt.json` — what policy actually ran, with offline / compatibility caveats

## Anti-patterns

Do **not** let future revisions treat these as interchangeable:

- Cargo-home GC,
- `cargo clean` on target/build artifacts,
- shared `CARGO_TARGET_DIR` housekeeping,
- and future user-wide build-cache/plugin cleanup.

They are adjacent truths, not one “Cargo cache policy”.
