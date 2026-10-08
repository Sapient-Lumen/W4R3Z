# Hot substrate watchcard: Build-state substrate (2026-03)

## Lane
- build-state substrate watch
- drift horizon: **hot**

## Authoritative sources
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/

## Imported truths
- Cargo is moving toward recorded build facts plus `cargo report`-style explanation surfaces.
- Build-dir layout is still a live migration surface.
- Build-State Evidence remains the archive's clearest first deep product surface, but its import boundaries must stay explicit.

## Non-claims
- no stable final `cargo report` surface is proven yet;
- target-dir/build-dir scraping is not thereby made safe as a universal contract;
- the broad worthiness ladder did not change.

## Current implication
Future assistants should keep Build-State Evidence first overall, prefer import-first design, and refresh build-related packets only when a watchcard delta clearly merits it.

## Downstream assets most likely to care
- `design/build-state-evidence-execution-blueprint-2026Q1.md`
- `packets/top-band-v0/build-state-evidence.advance.current.md`
- `kernels/top-band-v0/build-state-pack.v0.md`

## Reissue triggers
- material build-analysis update, stabilization path, or scope reduction;
- settled build-dir-layout migration guidance;
- added or removed critical build-evidence fields.

## What did not change
- Build-State Evidence remains the strongest one-project answer overall;
- daemon-first or scrape-first fantasies remain refused.
