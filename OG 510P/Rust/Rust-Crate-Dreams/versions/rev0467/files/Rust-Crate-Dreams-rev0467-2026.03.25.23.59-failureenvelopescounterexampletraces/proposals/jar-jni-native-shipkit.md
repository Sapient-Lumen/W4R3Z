---
id: P-0500
title: JAR/JNI Native ShipKit — Maven classifiers, native-access contracts, and JVM loader receipts
status: idea
domains: [java, jvm, jni, maven, packaging, distribution, ci]
last_reviewed: 2026-03-18
evidence:
  - https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/System.html
  - https://docs.oracle.com/en/java/javase/25/docs/specs/jni/intro.html
  - https://docs.oracle.com/en/java/javase/26/migrate/migrating-from-jdk-8-later-jdk-releases.html
  - https://maven.apache.org/plugins/maven-deploy-plugin/examples/deploying-with-classifiers.html
  - https://central.sonatype.org/publish/publish-portal-maven/
  - https://github.com/trustin/os-maven-plugin
  - https://docs.rs/jni
---

# Problem

Rust already has real substrate for talking to the JVM through JNI.

Oracle documents the native-loading model around `System.load`, `System.loadLibrary`, platform-specific library-name mapping, and the broader JNI loading/linking design. Modern Java has also made native loading more explicit: native-library loading and native method binding are now a **restricted / native-access** surface that deserves deliberate review rather than folklore.

On the Rust side, `jni` / `jni-rs` already provide serious authoring substrate for implementing native methods, calling Java from Rust, and embedding a JVM.

That means the ecosystem is no longer mainly missing “some way to call Java from Rust” or “some way to call Rust from Java”.

But ordinary maintainers still cannot hand one another one boring artifact that answers the practical release questions:

- which **Maven coordinates and classifiers** actually carry native binaries,
- whether those classifiers follow a de-facto downstream-friendly dialect or only a project-local naming scheme,
- whether the Java side expects `System.loadLibrary`, `System.load`, temp-file extraction, or manual installation,
- whether the package assumes **class path + `ALL-UNNAMED`**, named-module native access, or silent manual flags,
- whether the native library base name and exported JNI surface actually match the Java declarations,
- and whether the artifacts in Maven Central honestly match the loader/runtime story the package claims.

The missing crate is **not** another JNI binding generator.

The missing crate is a **JAR/JNI native shipkit**: a crate and cargo-adjacent tool that turns “we publish a Rust native library for JVM consumers” into a portable **classifier matrix, classifier-dialect report, loader-residency receipt, native-access posture report, and support-risk bundle**.

# What it provides

- `jni-shipkit.toml` — declares Maven coordinates, native library base name, target tuples/classifiers, loader strategy (`load_library`, `absolute_load`, `extract_then_load`, `manual_install`), expected JDK floor, and module/native-access posture.
- `native-matrix.manifest.json` — normalized list of produced native binaries, hashes, library names, classifiers, and where each artifact is expected to live (inside an attached JAR, beside one JAR, or externally installed).
- `classifier-dialect.report.json` — records whether classifiers align with `os-maven-plugin`/`osdetector`-style intake, use custom classifier strings, omit classifier meaning, or require manual mapping.
- `jar-loader.receipt.json` — records Java/Kotlin-side loader entry points, whether `System.load` or `System.loadLibrary` is used, extraction behavior, classloader/module hints, and temp-path policy.
- `loader-residency.report.json` — classifies whether the native library is expected via `java.library.path`, absolute extracted path, attached resource-extraction flow, or manual installation.
- `native-access.report.json` — classifies the package as `named_module_native_access_declared`, `all_unnamed_required`, `native_access_missing`, or `manual_review_required`.
- `symbol-contract.report.json` — checks declared library names, observed filenames, and JNI symbol/export assumptions, with verdicts such as `library_name_mismatch`, `jni_symbol_gap`, and `jni_onload_policy_unknown`.
- `maven-publish.receipt.json` — records attached classifier artifacts, coordinates, and whether the published package layout matches the declared contract.
- `support-risk.report.json` — rolls classifier coverage, classifier dialect, loader strategy, and native-access posture into one downstream support verdict.
- `cargo jni-shipkit snapshot` — capture one publishable contract plus one produced native set.
- `cargo jni-shipkit doctor` — explain whether artifacts, classifiers, loader code, and runtime assumptions agree.
- `cargo jni-shipkit diff <old> <new>` — compare support promises across releases.
- `*.jnibundle.zip` — portable release-review and support artifact.

# What the crate should provide other people

1. **A boring answer to “what JVM-native package do we actually ship?”** instead of CI archaeology and README prose.
2. **A classifier matrix** that says exactly which native binaries exist and which environments are still uncovered.
3. **A classifier-dialect report** that explains whether downstream Maven/Gradle consumers can use standard OS detector intake or need custom mapping.
4. **A loader receipt** that proves the Java side’s `load` / `loadLibrary` / extraction behavior matches the packaged artifacts.
5. **A native-access review artifact** for modern JDK deployments where native loading is not just an invisible side effect.
6. **A compact support bundle** for “works on macOS but not Linux”, “works with one JDK but not another”, or “classifier exists but the loader cannot actually find the library”.

# Persona / who it’s for

- maintainers publishing Rust-backed JVM libraries to Maven repositories
- teams using `jni` / `jni-rs` and wanting a reviewable package contract
- release engineers producing multi-platform classifier matrices
- support engineers diagnosing JVM native-loading failures
- downstream Java/Kotlin teams who need an honest support statement before adoption

# Users & user stories

- **Library maintainer**: “Show me whether our published coordinates and classifiers honestly cover every OS/arch tuple we claim.”
- **Release engineer**: “Give me one bundle that joins Rust artifacts, Maven classifiers, loader strategy, native-access posture, and publication receipts.”
- **Support engineer**: “Tell me whether this failure is a missing classifier, wrong library base name, absent native-access posture, or an extraction/load mismatch.”
- **JVM consumer**: “Show whether this package expects system-installed natives, extracted resources, `java.library.path`, or a modular native-access flag we must pass at runtime.”

# Prior art (and why it’s insufficient)

- Oracle already documents JNI loading/linking semantics and the `System.load*` APIs.
- Current JDK docs explicitly surface native-library loading and native method binding as restricted/native-access behavior.
- The current JDK migration guide makes `--enable-native-access` posture and module-path versus class-path intake explicit.
- Maven already supports attached artifacts and classifiers, which are the normal substrate for shipping alternate package shapes.
- Sonatype Central already supports Maven-driven publication through the Central Publisher Portal.
- `os-maven-plugin` and `osdetector` already provide a de-facto classifier dialect for native artifact selection.
- `jni` / `jni-rs` already provide strong Rust-side JNI authoring substrate.
- The archive already has **P-0168 Rust Android Mobile Kit**, **P-0487 Foreign SDK Consumer Doctor Kit**, **P-0498 Node-API Package & Prebuild Contract Kit**, **P-0499 NuGet Native Interop ShipKit**, **P-0501 RubyGems Native Extension ShipKit**, and **P-0502 Hex Native NIF ShipKit**.

What remains missing is the **producer-side JVM package contract** that answers: “which classifiers, which classifier naming dialect, what loader residency, what native-access posture, and how honest is the support story?”

# Design goals

1. **Release-contract first** — the core value is the shipping promise, not another JNI wrapper layer.
2. **Classifier-aware** — Maven coordinates and attached-artifact layout are first-class facts.
3. **Classifier-dialect-honest** — de-facto `os.detected.classifier` compatibility should stay visibly distinct from custom project-local naming.
4. **Loader-legible** — `System.load`, `System.loadLibrary`, extraction, and manual-install stories must remain visibly distinct.
5. **Modern-JDK-aware** — native-access / restricted-method posture must be reviewable, not implicit.
6. **Consumer-build-tool neutral** — useful whether the downstream consumer uses Maven, Gradle, or another JVM build tool that consumes Maven coordinates.

# Three first-class review objects

## 1. Classifier dialect

This must stay separate from “a classifier exists somewhere”.
A package can publish attached artifacts and still make downstream intake painful if classifier names do not align with what tools already normalize.

Named classes for `0.1`:
- `os_detector_aligned`
- `custom_classifier_scheme`
- `classifier_mapping_required`
- `manual_review_required`

## 2. Native-access posture

This must answer:
- does the release expect `--enable-native-access=ALL-UNNAMED`,
- does it document named-module enablement,
- does it rely on class-path loading with warnings only,
- and does the package claim less risk than the JDK actually treats it as having?

## 3. Loader residency

This must stop the shipkit from flattening all loader stories into “the JVM will find it”.
It should keep separate:
- `java_library_path` lookup,
- absolute-path loading,
- resource extraction followed by load,
- and manual/system installation.

# MVP surface

- Minimal types: `JniShipkitContract`, `NativeMatrixManifest`, `ClassifierDialectReport`, `JarLoaderReceipt`, `LoaderResidencyReport`, `NativeAccessReport`, `SymbolContractReport`, `MavenPublishReceipt`, `SupportRiskReport`, `JniBundle`
- Minimal functions:
  - `capture_jni_shipkit_contract()`
  - `collect_native_matrix_manifest()`
  - `classify_classifier_dialect()`
  - `capture_jar_loader_receipt()`
  - `classify_loader_residency()`
  - `classify_native_access_posture()`
  - `check_symbol_contract()`
  - `diff_jni_shipkit_contracts()`
- Feature flags:
  - `jni`
  - `maven`
  - `jar-scan`
  - `serde`
  - `markdown`

# Compatibility story

- Must remain useful whether the Java side uses `System.loadLibrary`, `System.load(Path)`, or a resource-extraction helper.
- Must distinguish `library base name`, `artifact filename`, and `Maven classifier` because they drift independently.
- Must distinguish classifier existence from classifier **dialect**.
- Must stay separate from Android/AAR shipping, which already belongs under the Android proposal.
- Should tolerate packages that publish natives in separate attached artifacts or bundle them inside one resource JAR.
- Must not treat “JNI bindings compile” as evidence that downstream loading is boring.

# Conformance & fixtures

- one clean Linux/macOS/Windows classifier matrix using `os.detected.classifier`-aligned naming
- one fixture with ad-hoc classifier strings that require custom mapping downstream
- one fixture where Java expects `loadLibrary("foo")` but shipped filenames or base names drift
- one fixture where extraction is required but temp-path or resource policy is ambiguous
- one fixture where native loading is clearly present but native-access posture is undocumented or missing
- goldens for `classifier_mapping_required`, `library_name_mismatch`, `all_unnamed_required`, `extractor_policy_ambiguous`, and `manual_review_required`

# Path to boring stability

- Freeze the contract and verdict vocabulary before adding every JVM packaging edge case.
- Start with read-only inspection of artifacts, loaders, coordinates, and publication receipts.
- Keep native-access posture explicit and conservative.
- Prefer package-review artifacts over becoming a Maven publisher or Gradle plugin collection.

# Scorecard

- Impact: 4/5
- Neglectedness: 5/5
- Feasibility: 4/5
- Adoptability: 4/5
- Sustainability: 5/5
- Differentiation: 5/5
- **Total: 27/30**

# Minimum lovable MVP

A library and cargo subcommand that read one Rust→JVM native package, record its Maven coordinates and classifier matrix, classify classifier dialect and loader residency, inspect its native-access posture, and emit one support bundle that names any runtime or packaging gaps.

# De-risk plan

1. Start with one conventional `jni`-based library and one intentionally broken classifier/load scenario.
2. Keep the verdict taxonomy small and release-review oriented.
3. Validate on desktop/server JVM packaging first, not Android.
4. Avoid becoming another binding generator, Maven Central publisher, or generic Java packaging framework.

# Non-goals

- Not another Rust↔Java binding generator.
- Not a replacement for Maven, Gradle, Sonatype Central, or `os-maven-plugin`.
- Not an Android packaging tool.
- Not a generic Java security scanner.
- Not a promise that classifier coverage implies support for every JDK/runtime/container shape.

# Architecture & API sketch

```rust
pub enum ClassifierDialectClass {
    OsDetectorAligned,
    CustomClassifierScheme,
    ClassifierMappingRequired,
    ManualReviewRequired,
}

pub fn capture_jni_shipkit_contract(root: &Path) -> Result<JniShipkitContract>;
pub fn collect_native_matrix_manifest(root: &Path, contract: &JniShipkitContract) -> Result<NativeMatrixManifest>;
pub fn classify_classifier_dialect(contract: &JniShipkitContract, matrix: &NativeMatrixManifest) -> ClassifierDialectClass;
pub fn capture_jar_loader_receipt(root: &Path) -> Result<JarLoaderReceipt>;
pub fn classify_loader_residency(contract: &JniShipkitContract, loader: &JarLoaderReceipt) -> Result<LoaderResidencyReport>;
pub fn classify_native_access_posture(contract: &JniShipkitContract, loader: &JarLoaderReceipt) -> Result<NativeAccessReport>;
```

Bundle draft: `jni-shipkit.toml`, `native-matrix.manifest.json`, `classifier-dialect.report.json`, `jar-loader.receipt.json`, `loader-residency.report.json`, `native-access.report.json`, `symbol-contract.report.json`, `maven-publish.receipt.json`, `support-risk.report.json`, `notes.md`.

# Security / safety model

- Treat POMs, JARs, native artifacts, CI receipts, and build logs as untrusted input.
- Support redaction of local paths, repository credentials, and internal CI coordinates.
- Keep native-access posture separate from claims about overall package safety.
- Never imply that “published to Central” means the runtime flags, classifiers, or loader strategy are automatically correct.

# Maintenance & governance plan

- Track JDK native-access and restricted-method changes.
- Track Maven/Central publication changes only as substrate, not as the main product.
- Track de-facto classifier dialect shifts conservatively; default to `manual_review_required` when conventions drift.
- Maintain fixtures for classifier-dialect mismatch, native-access omissions, and extraction/load-policy ambiguity.
