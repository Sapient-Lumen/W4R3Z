# Frontier salience snapshot — 2026-03-19 (73)

This pass did **not** add another advisory scanner, registry tool, or maintenance-score crate.
It sharpened a neglected but highly leverageable supportiveness lane:

- **P-0515 Crate Off-Ramp Pack Kit** — because Rust now has meaningful deprecation/advisory/yank substrate, but still lacks one boring contract for successor intent, stopgap horizons, and checked exit recipes.

## Main judgment

The next worthy move here was **not** another security detector and **not** another crate-health score.
Those already exist as substrate or adjacent lanes.

The sharper missing layer is the **crate sunset / successor / exit contract** above today’s substrate, especially once three more facts are kept explicit:

- **successor intent truth** — what is being deprecated or retired, and what class of replacement really applies;
- **stopgap horizon truth** — whether a shim or last-safe version is only temporary and where the boundary sits;
- **recipe witness truth** — whether a receiver-facing migration path was actually checked.

That move is better grounded now because:

- the rustc lint docs still say deprecated surfaces should usually include what to use instead;
- Cargo’s SemVer guidance still treats deprecations as part of update experience;
- Cargo’s yank/update flows still surface danger without defining successor paths;
- crates.io Security tabs and RustSec advisories now make risk signals more visible;
- and docs.rs redirect crates prove maintainers already improvise off-ramp surfaces in the wild.

So the gap is no longer “Rust has no way to warn users away from a crate.”
The gap is that teams still rarely get a **reviewable exit promise** above the warning surfaces.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually use?”
2. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0520 Crate Lifecycle Surface Pack Kit** — still a strong product-level support surface.
5. **P-0484 Toolchain & Target Support Contract Kit** — still crucial for real machines and real targets.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0515 Crate Off-Ramp Pack Kit** — now promoted as a stronger Band A/B supportiveness candidate because the missing value is no longer “say deprecation better,” but a successor/stopgap/recipe contract above existing warning and advisory substrate.
8. **P-0027 text-input-kit** — still one of the clearest end-user product-engineering opportunities.
9. **P-0087 UI Accessibility Doctor Kit** — still a strong authoring-side semantic-quality lane.
10. **P-0012 Desktop ShipKit** — still a strong shipping candidate now that its contract layer is sharper.
11. **P-0197 Text Layout & Shaping Conformance Kit** — still a strong cross-stack correctness lab.
12. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
13. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library-shipping lane.
14. **P-0206 Wasm Component Contract & Conformance ShipKit** — still one of the clearest Wasm contract opportunities.
15. **P-0467 Apple XCFramework & SwiftPM ShipKit** — still one of the clearest Apple-SDK contract opportunities.
16. **P-0499 NuGet Native Interop ShipKit** — still one of the clearest .NET contract opportunities.

## Why this won over adjacent candidates right now

- It beat a broader **crate-health** pass because maintenance posture is adjacent but still not the same lane as a receiver-facing exit contract.
- It beat a narrower **advisory/outdated tooling** pass because detectors do not tell downstream users what path out was actually checked.
- It beat another **foreign-package shipping** pass because the archive needed another strong cross-ecosystem supportiveness candidate outside the shipping cluster.

## What changed in the archive

Added:
- `entries/2026-03-19-253.md`
- `meta/frontier-salience-2026-03-19-73.md`
- `meta/crate-offramp-product-plan-2026-03-19.md`
- `fixtures/crate-offramp-pack-kit/README.md`
- `fixtures/crate-offramp-pack-kit/crate_rename_shim/offramp-pack.example.toml`
- `fixtures/crate-offramp-pack-kit/crate_rename_shim/successor-map.report.example.json`
- `fixtures/crate-offramp-pack-kit/security_offramp/sunset-check.report.example.json`
- `fixtures/crate-offramp-pack-kit/security_offramp/offramp-recipe.manifest.example.json`
- `fixtures/crate-offramp-pack-kit/successor_split/successor-compat.report.example.json`
- `fixtures/crate-offramp-pack-kit/no_successor_manual/deprecation-surface.receipt.example.json`

Updated:
- `README.md`
- `INDEX.md`
- `proposals/crate-offramp-pack-kit.md`
- `meta/known-existing.md`
- `meta/prioritization.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/llm-hygiene.md`

## What this pass deliberately did not do

It did **not** collapse:

- deprecation signals,
- security/advisory signals,
- temporary shims or last-safe pins,
- checked migration recipes,
- and crate-health / governance metadata

into one fake “maintenance status” story.
