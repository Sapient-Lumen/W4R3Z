# Reproducibility evidence layering — 2026-03-09

This note exists to keep future passes from flattening the reproducibility stack into a vague “run diffoscope and maybe sign something” story.

## Main judgment

For **P-0242 Reproducible Build Evidence Kit**, the missing value is not a single blob.
It is a small layered contract:

1. **build recipe** — what source/toolchain/config/environment was claimed,
2. **rebuild verdict** — what happened when another build was attempted,
3. **diff triage** — what the smallest useful explanation of drift is,
4. and optionally an **ecosystem attestation / publication layer** above those artifacts.

Those are related, but they are not the same thing.

## Why this boundary matters now

Several current signals sharpen the boundary:

- Reproducible Builds documentation already distinguishes recording the build environment from verification and sharing certifications.
- The Rust-specific reproducibility docs already describe practical Rust debugging surfaces such as `Cargo.lock`, `target/` diffs, and `SOURCE_DATE_EPOCH`.
- Cargo/rustc now expose more path-hygiene substrate (`trim-paths`, `remap-cwd-prefix`), which reduces some failure classes but does not eliminate the need for a receiver-facing report.
- OSS Rebuild makes rebuild results and attestations more common across ecosystems, including crates.io, which increases the need for a compact Rust-native result contract.

## The four layers

### 1. Build recipe
This is the closest thing to a `.buildinfo`-style receipt.
It should answer:

- what source revision or tarball was used,
- what lockfile and feature/profile/target state was intended,
- what toolchain and linker lane were used,
- and what reproducibility knobs were supposed to matter.

It is primarily a **claim about replay conditions**.

### 2. Rebuild verdict
This is the judgment layer.
It should answer:

- were the compared subjects actually comparable,
- did the artifacts match bit-for-bit,
- did they only match after allowed normalization,
- or does the result remain unresolved.

It is primarily a **claim about outcome**.

### 3. Diff triage
This is the explanation layer.
It should answer:

- whether drift looks like timestamps, paths, compression, build IDs, build-script output, or something unknown,
- what artifacts were affected,
- and what next action a maintainer should probably take.

It is primarily a **claim about likely cause**.

### 4. Ecosystem attestation / publication
This is the distribution and trust layer.
It may involve:

- signed attestations,
- registry-scale rebuild services,
- published verification bundles,
- or procurement / policy systems.

It is primarily a **claim about how a result is distributed and trusted**, not about how it was first diagnosed.

## Practical rule for future passes

When revising **P-0242**, say explicitly:

1. what the recipe artifact is,
2. what the verdict artifact is,
3. what the diff-triage artifact is,
4. and whether any attestation or publication surface is local, optional, or external.

## What not to collapse together

Do **not** silently flatten:

- official publisher recipe,
- third-party rebuilder recipe,
- bitwise reproduction,
- semantic reproduction after normalization,
- raw diffoscope output,
- human triage summary,
- and signed/public attestation publication

into one fake “reproducibility result”.

A worthy **P-0242** bundle is allowed to say:

- “the build was only semantically reproduced because archive compression drifted,”
- “the compared subjects were not actually equivalent because features differed,”
- “the recipe matched but the diff triage still points to path-prefix leakage,”
- and “a hosted rebuilder published an attestation, but local manual review is still required.”

That honesty is part of the product.

## Sources

- https://reproducible-builds.org/docs/rust/
- https://reproducible-builds.org/docs/recording/
- https://reproducible-builds.org/specs/source-date-epoch/
- https://diffoscope.org/
- https://doc.rust-lang.org/cargo/reference/unstable.html#profile-trim-paths-option
- https://doc.rust-lang.org/beta/unstable-book/compiler-flags/remap-cwd-prefix.html
- https://github.com/google/oss-rebuild
- https://security.googleblog.com/2025/07/introducing-oss-rebuild-open-source.html
