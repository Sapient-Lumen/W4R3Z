# Foreign package contract vocabulary

This file exists to keep the archive from rediscovering the same pattern under five different names.

Across Python wheels, Apple XCFrameworks, Node prebuilds, NuGet native assets, JVM/JNI classifiers, and RubyGems fat gems, the sharp crate opportunity is often **not** “yet another binding layer”.

It is usually a **producer-side support contract** that turns native-package folklore into reviewable artifacts.

## Core shared nouns

- **producer-side contract** — the release promise made by the package author before a downstream consumer even opens a support ticket
- **artifact matrix** — the normalized list of platform/engine/runtime-specific native payloads that actually ship
- **loader receipt** — a compact record of how the consumer runtime finds, selects, extracts, or loads the native artifact
- **support-risk report** — a verdict-oriented artifact that names the likely support failure class without pretending to solve every runtime bug
- **fallback posture** — whether the release is prebuilt-first, source-build fallback, manual-toolchain required, or some other explicit escape hatch
- **claim-exceeds-artifacts** — the package says it supports a runtime/platform/engine tuple that the shipped artifacts and loader story do not justify

## Ecosystem-specific facts that must not be erased

- **Python**: wheels, tags, ABI/platform markers, manylinux/musllinux policy, installer behavior
- **Apple**: XCFramework slice coverage, codesign/notarization posture, SwiftPM/Xcode integration boundaries
- **Node/npm**: Node-API floors, `.node` loader behavior, Bun/Deno overclaim risk, optional local builds
- **NuGet/.NET**: RIDs, `runtimes/<rid>/native`, probing behavior, P/Invoke and Native AOT caveats
- **JVM/JNI**: classifiers, `System.load*`, native-access/restricted-method posture, extractor policy
- **RubyGems/Bundler**: gem platform tags, fat gems, Ruby-engine/version floors, Bundler platform-lock workflows
- **Hex/BEAM**: Hex package tarballs and checksums, package-size limits, `checksum.exs`, `rustler_precompiled`, `erlang:load_nif` / `priv` loader conventions, OTP/Elixir support windows, and source-build fallback posture

## Working rule for future proposals

Before adding another foreign-package proposal, ask:

1. Is the missing value really a **release contract** rather than raw authoring substrate?
2. Can the crate emit one or more **review artifacts** that another team could rely on?
3. Are the ecosystem-specific package facts strong enough that a generic framework would blur the truth?

If the answer to (3) is yes, prefer a sharp ecosystem-specific proposal first and only generalize later.
