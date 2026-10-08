# Frontier salience scan — 2026-03-16 (compile-time-deps lane upgraded around root-lane truth and optional session imports)

This pass did not add a new top-level proposal.
It upgraded **P-0494 Cargo Compile-Time-Deps Workflow Kit** into a more implementation-shaped lane by freezing the next missing layer: **root-lane truth and evidence provenance** above tool-only or check-like workflows.

## Main judgment

The strongest contribution here is not another editor wrapper, not another lock-contention tool, and not another build-dir migration note.
It is the boring crate that can hand other people:

- one conservative tool-build receipt,
- one parity verdict,
- one root-lane receipt saying how `target-dir` and `build-dir` were actually arranged,
- one evidence-source receipt saying where the facts came from,
- and one optional session link when Cargo build-analysis data exists.

## Broad ranking after this pass

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0035 cargo-build-insights**
3. **P-0469 Cargo Rebuild Explanation Kit**
4. **P-0429 rustc_public Analysis Workbench Kit**
5. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
6. **P-0478 Cargo Future-Incompat Triage Kit**
7. **P-0470 Cargo Package Review Kit**
8. **P-0125 Cargo SBOM Precursor Workbench Kit**
9. **P-0471 Cargo Artifact Handoff Kit**
10. **P-0490 Cargo Lock Contention Witness Kit**
11. **P-0055 Cargo Workspace Toolchain Manifest Kit**
12. **P-0244 SemVer API Diff Evidence Kit**

## Why P-0494 moved up

Fresh official substrate now makes three specific claims much easier to freeze:

- Cargo says `--compile-time-deps` is an intended tool-only mode and will never be stabilized for ordinary end-user workflows.
- RFC 3477 keeps `cargo build` as the stronger guarantee boundary, which means a reviewable parity/fallback artifact still matters.
- Cargo’s March 13, 2026 build-dir-layout-v2 call-for-testing says teams should test anything touching `build-dir` / `target-dir`, and notes that Cargo 1.91 already separates intermediate build artifacts from final ones.
- Cargo’s unstable docs also expose persisted build-analysis sessions and say the config knob can stay enabled even on stable with only an unknown-config warning there.

That combination means the crate can now do something sharper than “editor run succeeded.”
It can freeze:

- what tool-facing command ran,
- what it covered,
- how its root lanes were arranged,
- what facts were directly observed versus conservatively inferred,
- and whether imported Cargo sessions were available as supporting evidence.

## What changed in the archive

Added:
- `meta/cargo-tool-workflow-root-lanes-2026-03-16.md`
- `meta/frontier-salience-2026-03-16-21.md`
- `fixtures/cargo-compile-time-deps-workflow-kit/root-lane.receipt.schema.json`
- `fixtures/cargo-compile-time-deps-workflow-kit/evidence-source.receipt.schema.json`
- `fixtures/cargo-compile-time-deps-workflow-kit/tool-session.link.schema.json`
- scenario families for root-lane separation, build-dir-layout drift, and optional imported sessions
- `entries/2026-03-16-192.md`

Updated:
- `proposals/cargo-compile-time-deps-workflow-kit.md`
- `fixtures/cargo-compile-time-deps-workflow-kit/README.md`
- `README.md`
- `INDEX.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- live lock contention,
- build-dir consumer transition,
- historical build-analysis warehousing,
- or per-run rebuild explanation

into one fake “editor performance” crate.

## Sources

- Build Dir Layout v2 call for testing: https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo unstable docs (`compile-time-deps`, `build-analysis`, `build-dir-new-layout`): https://doc.rust-lang.org/cargo/reference/unstable.html
- rust-analyzer configuration: https://rust-analyzer.github.io/book/configuration
- RFC 3477 (`cargo build` vs `cargo check`): https://rust-lang.github.io/rfcs/3477-cargo-check-lang-policy.html
