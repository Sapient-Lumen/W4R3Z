# Build-std workbench lane boundaries — 2026-03-16

This note keeps the archive from collapsing several related sysroot / toolchain ideas into one fake “std-aware crate”.

## Main judgment

Rust now has meaningful official motion around `build-std`:

1. a staged plan for manual enablement, explicit std dependencies, target-modifier/codegen support, and automatic rebuild behavior,
2. posted RFCs for context, always-on rebuild configuration, and explicit std dependencies,
3. today’s unstable Cargo substrate for `-Z build-std` and `-Z build-std-features`.

That makes a worthy crate possible.
But the worthy crate here is still specifically the **recipe / lock / receipt / diff layer** above that substrate.

## The layers

### 1. P-0430 Build-Std Workbench Kit

This is the lane for:

- sysroot recipes,
- sysroot locks,
- direct build receipts,
- stage-posture reports,
- evidence-source receipts,
- and sysroot diffs.

This crate answers:

- what was requested,
- what was directly observed,
- which stage of build-std evolution the workflow assumes,
- and what changed between two sysroot builds.

It is the best candidate for the boring workflow crate above Cargo’s evolving std-aware substrate.

### 2. P-0454 ABI Coherence Profile Kit

This is the lane for:

- ABI-affecting flag profiles,
- exemption ledgers,
- whole-program coherence claims,
- and sysroot-coherence receipts for those flag families.

It is adjacent to build-std, but it should not own general recipe capture, stage posture, or sysroot recipe portability.

### 3. Sanitizer / hardening evidence crates

This includes sanitizer-profile and BorrowSanitizer-oriented lanes.

Those crates answer:

- which instrumentation profile was used,
- which findings were observed,
- and how runtime evidence should be reviewed.

They may depend on build-std or sysroot rebuilding, but they are not the same thing as a sysroot recipe/lock crate.

### 4. Source-path / debug-source hygiene crates

These crates answer:

- whether paths were trimmed or virtualized,
- whether `rust-src` / compiler sources are available,
- and whether debugger/source-lookup posture degraded.

They are about source lookup and observability, not about rebuilding the sysroot itself.

### 5. Tool-surface parity crates

Compile-time-deps/editor workflow crates answer:

- whether a tool-facing build surface is representative enough,
- whether target-dir/build-dir/sysroot config caused drift,
- and when a full build is required.

They should not absorb sysroot recipes, patched std provenance, or stage-aware build-std capture.

## Anti-patterns to avoid

### Anti-pattern 1: “build-std support” means one giant crate

Manual enablement, explicit std dependencies, target-modifier support, automatic rebuilds, ABI policy, sanitizer policy, and source lookup are not one crate.

### Anti-pattern 2: treating sysroot rebuilds as automatically coherent

Rebuilding `core` / `alloc` / `std` does not by itself prove ABI coherence, sanitizer parity, or debugger/source support.

### Anti-pattern 3: pretending stage posture is implicit and obvious

A future bundle reader must be able to tell whether a result came from:

- today’s manual `-Z build-std` usage,
- an explicit std-dependency transition,
- a target-modifier/codegen experiment,
- or a workflow that assumes future automatic rebuild behavior.

### Anti-pattern 4: flattening imported context into direct evidence

If a bundle imports facts from local configuration inspection, prior captures, or manual annotations, that should stay visible in an evidence-source receipt.

## What future passes should do

When touching build-std proposals, say explicitly:

1. whether the crate owns **sysroot recipes/locks/receipts**, **ABI coherence**, **sanitizer instrumentation**, **source lookup**, or **tool-surface parity**,
2. which facts are direct Cargo/build observations versus normalization or manual annotation,
3. which stage of the build-std roadmap the crate is designed for,
4. and where ambiguity forces `manual_review_required` instead of fake certainty.
