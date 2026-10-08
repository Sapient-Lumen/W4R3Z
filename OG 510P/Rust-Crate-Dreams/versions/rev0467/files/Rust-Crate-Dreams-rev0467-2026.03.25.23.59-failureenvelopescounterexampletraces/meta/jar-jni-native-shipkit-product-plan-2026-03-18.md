# JAR/JNI Native ShipKit — product plan (2026-03-18)

This note sharpens **P-0500 JAR/JNI Native ShipKit** into an implementation-ready `0.1` shape.

## Main judgment

A buildable `0.1` should be a **small cargo subcommand plus library** that helps maintainers publish one reviewable answer to:

- which Maven coordinates and classifier artifacts they actually shipped,
- whether those classifiers follow a de-facto downstream-friendly dialect,
- whether the Java side loads via `System.loadLibrary`, absolute `System.load`, or extraction-first behavior,
- what native-access posture a current JDK consumer must actually adopt,
- whether library names and loader expectations line up,
- and whether the published package in Central honestly matches the runtime story the package claims.

It should **not** try to become a replacement for Maven, Gradle, Sonatype Central, `os-maven-plugin`, or `jni-rs`.
Those are substrate and workflow partners, not the missing product.

## What the crate should provide other people

For maintainers, release engineers, downstream JVM consumers, and support reviewers, the crate should provide:

1. **One compact support contract** instead of release truth spread across `pom.xml`, Gradle scripts, Java loader code, CI YAML, and issue-thread folklore.
2. **A classifier-dialect report** that states whether published classifiers are friendly to existing OS-detector conventions or need custom downstream mapping.
3. **A loader-residency report** that says whether runtime expects `java.library.path`, extracted temporary files, absolute paths, or manual installation.
4. **A native-access posture report** that says whether the release expects named-module enablement, `ALL-UNNAMED`, or still leaves a manual-review boundary.
5. **A classifier matrix + publication receipt** that another person can inspect without replaying the Maven build.
6. **A diffable release bundle** that makes classifier, loader, and JDK-policy drift visible across releases.

## Three first-class review objects

### 1. Classifier dialect

This should stay separate from “attached artifacts exist”.

Named classes for `0.1`:
- `os_detector_aligned`
- `custom_classifier_scheme`
- `classifier_mapping_required`
- `manual_review_required`

This object should answer:
- whether classifiers follow a de-facto `os.detected.classifier`-style scheme,
- whether Linux distro/libc distinctions are explicit,
- whether downstream users need custom classifier mapping,
- and whether a published matrix is easy to consume from Maven/Gradle.

### 2. Native-access posture

This should answer questions like:
- does the package require `--enable-native-access=ALL-UNNAMED`,
- does it declare named-module enablement,
- is its current runtime story only “you’ll get warnings on JDK 24/25/26 until you pass flags”,
- and do package docs understate what the JDK now treats as restricted?

### 3. Loader residency

This should stop the product from treating “the JVM finds the native library somehow” as enough.
It should say explicitly:
- whether runtime relies on `java.library.path`,
- whether code extracts a library to a temp location before loading,
- whether the package requires an absolute path or installed system location,
- and whether temporary-file policy and residency are honest and reviewable.

## Recommended `0.1` command surface

### `cargo jni-ship inspect`
Read project facts from `Cargo.toml`, `pom.xml`/Gradle metadata, JAR contents, loader code, and built native artifacts.
Emit early observations without pretending the release is valid yet.

### `cargo jni-ship check`
Run policy checks for:
- classifier naming drift,
- missing classifier artifacts,
- custom-mapping requirements,
- `System.load` versus `System.loadLibrary` mismatches,
- extraction/temp-path ambiguity,
- missing or misleading native-access posture,
- and library-name / JNI-export drift.

### `cargo jni-ship diff <old> <new>`
Compare release bundles and classify:
- `classifier_dialect_changed`
- `loader_residency_changed`
- `native_access_posture_changed`
- `native_matrix_changed`
- `symbol_contract_changed`
- `manual_review_boundary_changed`

### `cargo jni-ship bundle`
Produce one compact `.jnibundle.zip` containing the normalized receipts plus a short summary.

## Recommended crate/workspace split

- `jni_ship_model`
  - shared types for policies, receipts, reports, and diffs
- `jni_ship_import`
  - Maven metadata parsing, JAR inspection, loader inspection, artifact inventory import
- `jni_ship_check`
  - policy checking and conservative classification
- `jni_ship_render`
  - markdown summaries and zip bundle export
- `cargo-jni-ship`
  - user-facing cargo subcommand

Optional later adapters:
- `jni_ship_maven_central`
- `jni_ship_os_detector`
- `jni_ship_gradle_import`

## `0.1` artifact set

Core artifacts should be:
- `jni-shipkit.toml`
- `native-matrix.manifest.json`
- `jar-loader.receipt.json`
- `maven-publish.receipt.json`
- `support-risk.report.json`
- `notes.md`

This pass says `0.1` also needs three sharper review artifacts:
- `classifier-dialect.report.json`
- `loader-residency.report.json`
- `native-access.report.json`

Those matter because the shipkit gets vague again if it only records “native JAR artifacts exist” without making clear:
- whether downstream selection uses a standard or project-local classifier scheme,
- where the library is expected to reside when loaded,
- and what native-access posture current JDKs actually require.

## Discovery order

1. **Artifact inspection**
   - coordinates
   - attached artifacts
   - native filenames
   - JAR/resource layout
2. **Classifier-dialect receipt**
   - classifier names
   - normalized OS/arch/libc hints
   - custom mapping requirements
3. **Loader-residency receipt**
   - `System.loadLibrary` vs `System.load`
   - resource extraction
   - temp-path policy
   - manual installation hints
4. **Native-access posture receipt**
   - module path vs class path
   - named-module enablement
   - `ALL-UNNAMED` expectations
   - warning/manual-review boundaries
5. **Bundle + diff**
   - reviewable summary
   - previous-release comparison

## Ranking discipline

The first implementation should not treat “Central publish succeeded” as the verdict.
A good `0.1` should keep separate:
- `artifacts_published`
- `classifier_dialect_known`
- `loader_residency_honest`
- `native_access_posture_honest`
- `symbol_contract_clear`
- `manual_review_required`

## What to import from substrate, and what not to flatten

### Import, but do not flatten
- Oracle `System.load*` and JNI docs
- current JDK migration/native-access guidance
- Maven classifier deployment rules
- Sonatype Central publication receipts
- `os-maven-plugin` / `osdetector` classifier conventions
- `jni` / `jni-rs` authoring substrate

### Do not flatten into one fake verdict
- “the artifact published”
- “a classifier exists”
- “the JVM found the library locally”
- “native access can be enabled somehow”
- “Gradle/Maven can probably wire it up”

## Preferred proving grounds

- a Rust-backed JVM package publishing Linux/macOS/Windows classifier artifacts with clean `os.detected.classifier` alignment
- a package using custom classifier names that require downstream mapping
- a package that extracts the native library from a JAR before loading it
- a package that works on a local dev machine but needs an honest native-access declaration on JDK 24+

## Non-goals

- not another Rust↔Java binding generator
- not a Maven or Gradle publishing plugin suite
- not an Android packaging kit
- not a generic JDK security scanner
- not a promise that one successful local load implies boring support for all consumers

## MVP API sketch

```rust
pub enum ClassifierDialectClass {
    OsDetectorAligned,
    CustomClassifierScheme,
    ClassifierMappingRequired,
    ManualReviewRequired,
}

pub fn inspect_release(root: &Path) -> Result<ReleaseInspection>;
pub fn evaluate_classifier_dialect(release: &ReleaseInspection) -> Result<ClassifierDialectReport>;
pub fn evaluate_loader_residency(release: &ReleaseInspection) -> Result<LoaderResidencyReport>;
pub fn evaluate_native_access_posture(release: &ReleaseInspection) -> Result<NativeAccessReport>;
pub fn write_bundle(bundle: &JniBundle, out: &Path) -> Result<()>;
```

## Maintenance posture

- Follow JDK native-access changes closely.
- Follow Maven/Central publication changes only as substrate.
- Follow de-facto classifier conventions conservatively.
- Preserve `manual review required` whenever the crate cannot safely infer classifier dialect, loader residency, or native-access truth.
