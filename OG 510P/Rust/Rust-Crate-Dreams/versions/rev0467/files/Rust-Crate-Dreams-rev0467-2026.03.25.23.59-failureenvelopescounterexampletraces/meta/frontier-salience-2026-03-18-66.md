# Frontier salience snapshot — 2026-03-18 (66)

This pass did **not** promote a brand-new ecosystem-wide lane.
It sharpened an existing **shipping and adoption accelerator**:

- **P-0500 JAR/JNI Native ShipKit** — because the archive still lacked a believable answer to “what exact JVM-native support promise is this Rust release making, and how can another person review it without replaying POM files, classifier artifacts, loader code, and JDK native-access folklore by hand?”

## Main judgment

The next worthy move here was **not** another JNI framework, another Gradle plugin collection, another Central publisher wrapper, or another generic Java/Rust bridge.
Those either already exist in real form or are too broad for a believable artifact-bearing `0.1`.

The sharper missing layer is the **JAR/JNI shipping contract** above today’s substrate, especially once three more facts are kept explicit:

- **classifier dialect** — whether published classifiers align with `os.detected.classifier`-style downstream intake or require custom mapping.
- **native-access posture** — whether the release expects named-module enablement, `ALL-UNNAMED`, or still hides a runtime warning/failure boundary.
- **loader residency** — whether runtime expects `java.library.path`, absolute-path loads, extraction-first behavior, or manual installation.

That move is better grounded now because:

- Oracle’s current JDK docs explicitly treat `System.loadLibrary`, `System.load`, and native method binding as restricted/native-access surfaces;
- current migration guidance now states how to enable native access for named modules versus all class-path code;
- Maven already makes attached classifiers an ordinary publication shape, and Sonatype Central now documents Maven-plugin-driven publication through the Publisher Portal;
- `os-maven-plugin` / `osdetector` give the ecosystem a de-facto classifier dialect for native JVM artifacts;
- `jni` / `jni-rs` already solve raw authoring, which makes the missing layer more clearly the boring support contract above them.

So the gap is no longer “Rust cannot ship JVM-native packages.”
The gap is that teams still rarely get a **reviewable cargo-native JVM bundle** above classifier dialect, native-access posture, and loader-residency truth.

## Broad portfolio ranking after this pass

1. **P-0509 Crate Ecosystem Pathfinder & Decision-Pack Kit** — still the clearest cross-domain answer to “what should we actually reach for?”
2. **P-0520 Crate Lifecycle Surface Pack Kit** — still one of the strongest support-truth lanes once a crate is chosen.
3. **P-0524 Crate Example Surface Pack Kit** — still one of the highest-leverage first-success lanes.
4. **P-0525 Crate Diagnosis Surface Pack Kit** — still one of the strongest troubleshooting lanes.
5. **P-0484 Toolchain & Target Support Contract Kit** — still one of the strongest “real machines, real targets” support lanes.
6. **P-0472 Docs.rs Build Parity & Evidence Kit** — still a sharp hosted-build support lane.
7. **P-0466 Python Wheel ABI & Free-Threading ShipKit** — still one of the clearest foreign-package shipping-contract opportunities.
8. **P-0168 Rust Android Mobile Kit** — still a strong mobile/library shipping-kit lane with explicit policy pressure.
9. **P-0206 Wasm Component Contract & Conformance ShipKit** — still one of the clearest Wasm shipping-contract opportunities.
10. **P-0467 Apple XCFramework & SwiftPM ShipKit** — still one of the clearest Apple-SDK shipping-contract opportunities.
11. **P-0499 NuGet Native Interop ShipKit** — still one of the clearest .NET shipping-contract opportunities.
12. **P-0498 Node-API Package & Prebuild Contract Kit** — still one of the clearest npm-facing ship-contract opportunities.
13. **P-0502 Hex Native NIF ShipKit** — still one of the clearest BEAM-facing ship-contract opportunities.
14. **P-0500 JAR/JNI Native ShipKit** — now one of the clearest JVM-facing ship-contract opportunities because the substrate exists but the boring contract above classifier dialect, native-access posture, and loader residency still does not.

## Why this won over adjacent candidates right now

- It beat **P-0501 RubyGems Native Extension ShipKit** because the JVM lane now has especially sharp first-party policy pressure from current JDK native-access guidance.
- It beat **another JNI helper** because `jni` / `jni-rs` already exist and the sharper pain is release-contract truth above them.
- It beat **another Maven/Central publishing helper** because classifier dialect and native-access posture are the more immediate support bottlenecks.
- It beat **generic provenance/signing follow-ons** because loader-residency and runtime-flag honesty still remain the more immediate adoption blockers.

## What changed in the archive

Added:
- `entries/2026-03-18-246.md`
- `meta/frontier-salience-2026-03-18-66.md`
- `meta/jar-jni-native-shipkit-product-plan-2026-03-18.md`
- `fixtures/jar-jni-shipkit/classifier-dialect.report.schema.json`
- `fixtures/jar-jni-shipkit/native-access.posture.report.schema.json`
- `fixtures/jar-jni-shipkit/loader-residency.report.schema.json`
- `fixtures/jar-jni-shipkit/scenarios/ad_hoc_classifier_names_require_manual_mapping/`
- `fixtures/jar-jni-shipkit/scenarios/classpath_loader_needs_all_unnamed_but_docs_omit_it/`
- `fixtures/jar-jni-shipkit/scenarios/extract_then_load_temp_policy_ambiguous/`

Updated:
- `proposals/jar-jni-native-shipkit.md`
- `fixtures/jar-jni-shipkit/README.md`
- `README.md`
- `INDEX.md`
- `meta/known-existing.md`
- `meta/roadmap.md`
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/epic-crate-portfolio-2026-03-18.md`
- `meta/prioritization.md`

## What this pass deliberately did not do

It did **not** collapse:

- attached classifier artifacts,
- de-facto classifier naming conventions,
- loader call shape,
- native-access runtime posture,
- and successful local development loading

into one fake “JVM support” story.
