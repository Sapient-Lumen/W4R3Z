## Refresh note (rev0398)
This gap is now explicitly tied to Cargo's **plumbing-command** direction.
The key missing move is no longer just “better final-artifact enumeration”; it is the boundary between Cargo's explicit build phases and the downstream consumers that need one reusable final-artifact subject/handoff contract.

Recent official signals that sharpen the gap:
- the accepted Cargo plumbing goal enumerates build stages and names **stage final artifacts** as the final phase;
- the GSoC plumbing prototype implemented seven subcommands through `plan-build` but stopped short of final-artifact staging;
- Cargo's build-dir-layout-v2 call says projects still rely on unspecified details due to missing features;
- and Cargo's current docs distinguish internal build-dir state from public artifact-dir / final-artifact surfaces.

That combination is why the archive now treats Artifact Surface as a promoted frontier instead of a useful but secondary leaf.

# Gap: Cargo final-artifact truth is still thinner than the downstream consumers now need

## Summary
Cargo is getting better at exposing **where final outputs live**, but the ecosystem still lacks a portable, reviewable contract for **what final artifacts were actually produced for this build subject**.

Today serious consumers still have to reconstruct that story from some combination of:
- `cargo metadata`,
- `--message-format=json` streams,
- target-dir or artifact-dir path assumptions,
- build-script output,
- release-tool manifests,
- and ad hoc CI glue.

That is enough to build wrappers, but it is not yet a clean answer to the questions downstream tools actually ask:
- which selected package/target/profile/toolchain combination produced this output;
- whether an output is Cargo-native, rustdoc/package output, or build-script-uplifted;
- where the output originally lived versus where Cargo copied it;
- which sidecars belong to it (for example SBOM precursors);
- and what Release/Inventory/Repro/Support/Polyglot consumers may safely import next.

## Ecosystem signals
- The March 2026 build-dir-layout-v2 call for testing says the build-dir layout is internal-only, but many projects still rely on unspecified details because Cargo is missing the right features. That is exactly the pattern where a thin public final-artifact boundary becomes more valuable than more layout folklore.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo’s build-cache docs now explicitly distinguish **final artifacts** in `target-dir` from **intermediate artifacts** in `build-dir`.
  https://doc.rust-lang.org/cargo/reference/build-cache.html
- Cargo’s compiler-layout docs now say `artifact-dir` is public API while `build-dir` remains an internal implementation detail. That creates a clearer “public final output surface vs internal intermediate layout” split than the ecosystem had before.
  https://doc.rust-lang.org/beta/nightly-rustc/cargo/core/compiler/layout/index.html
- Cargo’s unstable `--artifact-dir` docs explicitly say the flag exists because determining exact final filenames is otherwise awkward and requires parsing JSON output.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- Cargo 1.93’s custom-final-artifacts discussion says build scripts should not get direct `artifact-dir` access, and instead sketches explicit, collision-checked Cargo-mediated uplift for selected packages. That means the final-artifact surface is becoming more structured rather than less important.
  https://blog.rust-lang.org/inside-rust/2026/01/07/this-development-cycle-in-cargo-1.93/
- Cargo’s external-tools docs still mainly expose stable package metadata plus per-build JSON messages. Those messages are useful, but downstream tools still have to assemble their own final-artifact subject and handoff model.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo’s unstable SBOM precursor work now emits precursor files next to executable/linkable outputs and keeps them aligned with uplift into target/artifact directories. That makes artifact-linked sidecars real, not hypothetical.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- `cargo-dist` already has a machine-readable `dist-manifest.json` schema for release/distribution work. That is strong evidence of downstream demand, but it is a release-oriented layer, not a Cargo-native final-artifact contract.
  https://docs.rs/cargo-dist-schema/latest/cargo_dist_schema/
  https://docs.rs/crate/cargo-dist/latest

## What is missing
The missing contribution is a thin **Artifact Surface Kit** above Cargo-native build outputs and bounded uplift/import lanes.

It should make six truths portable without flattening them together:
1. selected build subject truth;
2. final artifact identity truth;
3. origin truth (`Cargo`, rustdoc/package, or Cargo-mediated uplift);
4. location/copy truth;
5. attached sidecar truth;
6. bounded downstream handoff truth.

## What “good” looks like
- A machine-readable artifact manifest that can identify final outputs without target-dir spelunking.
- Explicit separation between **artifact identity** and **release/install identity**.
- Explicit separation between **Cargo-native outputs** and **build-script-uplifted** outputs.
- Stable handling of executable, linkable, docs, and package outputs without pretending they are all the same consumer story.
- Honest lossiness notes when a consumer is inferring from JSON streams, nightly-only features, or partial sidecar availability.
- Diffable reports that say whether change happened in selection, output class, paths, sidecars, or downstream handoff.

## Candidate contribution
Promote an **Artifact Surface Kit** with:
1. `artifact-subject/v0` for selected package/target/profile/toolchain/build invocation truth,
2. `artifact-entry/v0` for each final output and its origin/location facts,
3. `artifact-manifest/v0` for the collected final-artifact set,
4. `artifact-report/v0` for collisions, missing outputs, lossiness, and sidecar drift,
5. `artifact-pack/v0` for bounded downstream handoff.

## Distinction from nearby archive entries
- **Not Build Cache Kit:** that kit owns intermediate state, lock/reuse, and retention. Artifact Surface Kit owns final outputs.
- **Not Build Extension Kit:** that kit owns how build scripts declare generated outputs. Artifact Surface Kit owns the final public output surface after Cargo selection/uplift decisions.
- **Not Release Truth Stack:** that stack owns producer-side release bundles, signatures, rebuild evidence, and hosted release continuity. Artifact Surface Kit stops earlier.
- **Not Distribution Contract Stack:** that stack owns channel selection, verification/fallback, and install receipts.
- **Not Inventory Evidence Stack:** that stack owns dependency/component inventory meaning. Artifact Surface Kit only links artifact-side sidecars and handoff points.
