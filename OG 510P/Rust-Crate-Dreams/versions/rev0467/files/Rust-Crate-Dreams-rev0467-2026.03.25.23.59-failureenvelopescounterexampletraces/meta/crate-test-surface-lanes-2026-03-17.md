# Crate test-surface lanes — 2026-03-17

This note keeps **P-0523 Crate Test Surface Pack Kit** from collapsing into generic “better testing”, “better examples”, or “better mocking”.

## The lane

**P-0523** is the crate-authored, receiver-facing artifact layer for:

- officially supported fixture families,
- fake backends and deterministic seams,
- named scenario corpora,
- integration topology expectations,
- property/snapshot support posture,
- and release-to-release test-surface diffs.

It answers:

- “How am I supposed to test code that uses this crate?”
- “Which fakes/fixtures are official support surfaces versus incidental examples?”
- “Can I test this crate with paused time, temp files, mock HTTP, or only with a real service?”
- “Which scenario families are representative enough to rely on?”
- “How did the crate’s testing support change across releases?”

## What it is not

### 1. Not generic test frameworks

Rust’s built-in test harness, `rstest`, `proptest`, `assert_cmd`, and similar crates provide execution or authoring substrate.
**P-0523** sits above them as the support contract that a particular crate publishes for downstream users.

### 2. Not configuration scenarios

**P-0516** is about choosing the right feature/env/profile recipe for runtime use.
**P-0523** is about how to test code that *uses* that configuration, including fixtures and topology expectations.

### 3. Not authority surfaces

**P-0519** is about ambient powers and determinism posture in production use.
**P-0523** may import those seams, but it is specifically about which test doubles, temp-state paths, or isolated modes are supported.

### 4. Not lifecycle surfaces

**P-0520** is about background work, cancel safety, and shutdown obligations.
**P-0523** may test those things, but it is about the testing artifact surface rather than the runtime contract itself.

### 5. Not resource or persistence surfaces

**P-0521** and **P-0522** describe what a crate can accumulate and what durable bytes it leaves behind.
**P-0523** can import scenarios from them, but it exists to publish official test support for those concerns.

### 6. Not full conformance workbenches

Many archive proposals are domain-specific conformance/replay/interop kits.
**P-0523** is narrower and more generic: it is the per-crate support layer for downstream tests, not a whole standards-lab framework.

## Working rule for future passes

When a pass proposes another crate in this area, it must state explicitly whether the missing value is about:

1. **generic testing substrate**,
2. **runtime/setup support surfaces**,
3. **domain-specific conformance/evidence workbenches**,
4. or **receiver-facing test-surface contracts**.

Do **not** let the archive quietly rephrase test-surface contracts as “another mock crate”, “better examples”, or “a nicer test harness”.
