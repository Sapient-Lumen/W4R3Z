# Frontier salience scan — 2026-03-08 (third pass)

This pass exists to do two things at once:

1. promote one more real seam, and
2. make it harder for future passes to keep adding “one more foreign package ecosystem” without a strong reason.

## External signals still worth honoring

- The 2025 State of Rust survey still leaves **resource usage / compile times** and **debugging** as real recurring pain, so the top frontier should still overweight explainability and support artifacts.
- Cargo and crates.io continue to accumulate more machine-readable policy and workflow surfaces, which keeps Cargo-facing explanation and release-review crates near the top.
- The foreign-package frontier is now broad enough that its best proposals are no longer “interop SDKs” but **producer-side release contracts**.
- The BEAM/Hex ecosystem now clearly qualifies for that framing because `rustler`, `rustler_precompiled`, Hex package tarballs/checksums, and explicit NIF loading already exist as substrate.

## What currently looks most worthy

1. **P-0468 Cargo Resolver Explanation Kit**
2. **P-0469 Cargo Rebuild Explanation Kit**
3. **P-0496 Cargo Vendor & Source Parity Kit**
4. **P-0492 Cargo Registry Auth Doctor Kit**
5. **P-0494 Cargo Compile-Time-Deps Workflow Kit**
6. **P-0500 JAR/JNI Native ShipKit**
7. **P-0498 Node-API Package & Prebuild Contract Kit**
8. **P-0499 NuGet Native Interop ShipKit**
9. **P-0497 CPU Baseline & Runtime Dispatch Contract Kit**
10. **P-0501 RubyGems Native Extension ShipKit**
11. **P-0502 Hex Native NIF ShipKit**

## Why P-0502 is real, but not top-tier frontier

What makes it worth keeping:

- the substrate is undeniably real,
- the package/release contract is still too implicit,
- and the package-manager facts are different enough to justify a distinct proposal: Hex tarball receipts, package-size posture, checked-in checksum state for remote precompiled NIFs, OTP/Elixir support windows, and `erlang:load_nif` / RustlerPrecompiled loader expectations.

What keeps it below the biggest Cargo pains:

- the user base is smaller,
- many teams can still survive with bespoke release scripts for a while,
- and Rust’s broadest ecosystem pain is still more concentrated around **build explainability, debugging, and honest release/support artifacts** closer to Cargo itself.

## New saturation rule for foreign package seams

Future passes should assume the foreign-package contract family is **mostly mapped** unless a candidate ecosystem has all three of these properties:

1. **real authoring substrate already exists**, so the sharp gap is not “write bindings at all”,
2. **real package-manager / runtime-loader facts differ materially** from the ecosystems already covered,
3. and the missing crate can emit a **review artifact other people can rely on**, not just another build helper.

If those three conditions are not met, prefer:

- strengthening one of the existing package-contract proposals,
- generalizing vocabulary/schema carefully,
- or going back to the Cargo/debug/support frontier instead.

## Working rule for future revisions

Before adding another proposal in this family, ask:

- what concrete package-manager truth does this ecosystem have that Python, Apple, Node, NuGet, JVM, Ruby, and Hex do not already teach us,
- what will the crate provide other people besides another wrapper around CI scripts,
- and does this addition outrank a better explanation/support artifact closer to Cargo?

If the answer is weak, compress or demote.
