# Missing crate territory map — 2026-03-25

This map is not a ranking by market size.
It is a map of **where the Rust ecosystem still seems to lack durable crate contributions** after comparing current community maturity, official priorities, and the archive’s existing proposal bank.

For each sector, the main question is not “is there pain?”
It is “what shape of crate would still be worthy?”

## 1. Web and service backends

### Status
Rust web work is energetic and no longer “missing” in a blanket sense.
The stronger need is not a replacement umbrella but better **selection, qualification, debug, build, and lifecycle control planes** around existing choices.

### Worthy missing shapes
- framework-selection / starter-set decision packs for concrete service profiles;
- runtime/observability/debug support contracts that compare service stacks honestly;
- compile-iteration and restart-truth kits that stop fuzzy hot-reload claims.

### Do not promote yet
- a generic “one true web stack” crate.

## 2. GUI and desktop

### Status
GUI is still fragmented, but fragmentation alone does not prove that a single new umbrella crate would win.

### Worthy missing shapes
- packaging, installer, asset, plugin, accessibility, and upgrade evidence kits;
- interop/embedding kits for mixing Rust with existing desktop shells;
- compile-iteration feedback receipts for GUI loops.

### Do not promote yet
- a generic GUI salvation crate that tries to erase all toolkit differences.

## 3. Game development

### Status
Game development has active engine/framework communities already.
The missing opportunity is more likely to be around **tooling seams** than a whole new engine abstraction.

### Worthy missing shapes
- asset-pipeline evidence kits;
- hot-iteration claim-ceiling kits;
- plugin/modding compatibility packs;
- engine-interop or save-format transition packs.

## 4. Audio, media, and plugins

### Status
This area still looks rich in specific seams.
Cross-host/plugin correctness, sandboxing, and test/evidence surfaces remain attractive.

### Worthy missing shapes
- plugin-host compatibility and packaging evidence kits;
- golden-audio / deterministic DSP fixture kits;
- media pipeline capability/latency envelope packs.

## 5. ML / AI / data science

### Status
There is clear demand, but the broad “ML supercrate” dream is too fuzzy and too dependent on fast-moving external ecosystems.

### Worthy missing shapes
- model/runtime packaging and provenance kits;
- dataset/array/feature-store interop evidence packs;
- local/offline inference deployment kits with explicit boundary, artifact, and acceleration receipts.

### Do not promote yet
- a monolithic Rust-native ML umbrella pitched as a whole ecosystem replacement.

## 6. Embedded and edge

### Status
Embedded remains high-friction and strategically important.
The ecosystem already knows it needs more than one crate, so worthy contributions are likely to be **qualification and support artifacts**, not just drivers.

### Worthy missing shapes
- board/support contract kits;
- target+probe+debug evidence kits;
- update/rollback/signing/workbench kits for device fleets;
- peripheral/RTOS/async capability receipts.

## 7. Safety-critical and regulated domains

### Status
This is one of the clearest places where Rust interest is high but ecosystem support is thin and evidence-heavy.

### Worthy missing shapes
- assurance-case workbenches;
- dependency/support lifecycle evidence kits;
- artifact traceability and target/toolchain qualification packs;
- mixed-language boundary evidence kits.

### Promotion note
This sector should promote proposals that export **reviewable evidence** rather than generic “safe by design” claims.

## 8. Wasm components, plugins, and extension systems

### Status
Rust’s goals explicitly keep pushing Wasm/components.
The likely missing wins are around packaging, boundary truth, permissions, and host/plugin qualification.

### Worthy missing shapes
- component packaging receipts;
- capability/policy boundary kits;
- host/plugin compatibility evidence packs;
- offline or restricted-delivery bundle kits.

## 9. Mixed-language, C++, SDK, and FFI-heavy stacks

### Status
This remains a strong seam because real teams keep needing to fit Rust into non-Rust systems.

### Worthy missing shapes
- ABI/coherence profile kits;
- SDK handoff / xcframework / package-manager shipkits;
- native dependency, linker-lane, and public-boundary evidence kits;
- C++ interop transition workbenches.

## 10. Enterprise offline, mirrors, supply chain, and internal distribution

### Status
This remains one of the archive’s best concrete seams because the substrate is operational and painful in a repeated way.

### Worthy missing shapes
- source parity / mirror honesty / vendor-lock receipts;
- artifact sidecar contracts;
- restricted-delivery documentation and examples bundles;
- public dependency and SBOM precursor workbenches.

## 11. Local-first and collaboration systems

### Status
There is real energy here, but not yet a case for one generic umbrella crate from the archive’s point of view.

### Worthy missing shapes
- sync/merge interop evidence kits;
- conflict-surface receipts;
- offline-first packaging/persistence/debug workbenches;
- schema and migration evidence packs.

## 12. Robotics, digital twins, automotive, industrial, and field systems

### Status
This area is broad but full of sharp protocol, file-format, and qualification seams.

### Worthy missing shapes
- protocol conformance/evidence kits;
- field-bus/diagnostic workbenches;
- dataset/telemetry interchange packs;
- deployment/update and mixed-language support kits.

## 13. Geospatial

### Status
GeoRust already provides a visible community center.
That means worthy contributions should probably be interoperability, conformance, or workflow kits rather than another generic geo umbrella.

### Worthy missing shapes
- format / service / CRS conformance kits;
- reproducible geoprocessing pipeline packs;
- data-engineering handoff kits between Rust and larger data platforms.

## 14. Data engineering and lakehouse / analytics pipelines

### Status
Pain exists, but the likely epic contribution is not a generic “data platform crate”.

### Worthy missing shapes
- format/protocol interop evidence kits;
- reproducible pipeline / lineage receipts;
- mixed-language packaging and native-boundary kits;
- boundary/provenance kits for Arrow/Flight/lakehouse-adjacent work.

## 15. Kernel, drivers, and low-level systems work

### Status
This remains strategically important, but the winning crates are likely to be sharply bounded support and integration kits.

### Worthy missing shapes
- integration/readiness packs for kernel-adjacent targets;
- build, ABI, and support contracts;
- debug and test witness bundles for constrained environments.

## Cross-sector conclusion

Across these sectors, the strongest recurring missing shapes are:
1. **decision/control-plane kits**;
2. **evidence/conformance/interop kits**;
3. **transition and boundary kits**;
4. **support/debug/build truth kits**.

That is why the broad map still feeds the archive’s current frontier instead of replacing it.

## Sources

- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- https://www.arewewebyet.org/
- https://www.areweguiyet.com/
- https://arewegameyet.rs/
- https://www.arewelearningyet.com/
- https://github.com/rust-embedded/wg
- https://github.com/rust-embedded/not-yet-awesome-embedded-rust
- https://georust.org/
- https://automerge.org/
- https://blog.rust-lang.org/inside-rust/2025/11/24/safety-critical-rust-in-2025/
- https://rust-lang.github.io/rust-project-goals/2025h1/cpp-interop.html
- https://rust-lang.github.io/rust-project-goals/2025h2/linux-kernel-integration-do-not-edit-target.html
