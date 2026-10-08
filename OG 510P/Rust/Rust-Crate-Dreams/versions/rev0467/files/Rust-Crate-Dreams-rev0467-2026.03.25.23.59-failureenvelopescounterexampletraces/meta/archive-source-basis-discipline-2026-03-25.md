# Archive source-basis discipline — 2026-03-25

This note is a repo-hygiene and anti-amnesia rule.

The archive now depends on many different kinds of sources:
- official Rust blog posts,
- official project-goal pages,
- official docs.rs / crates.io explanatory pages,
- and community ecosystem hubs.

Those sources are all useful, but they support different strengths of claim.
Future passes should record that explicitly.

## 1. Every substantial pass should leave a source-basis note

For a pass that materially reranks, deepens, eliminates, or changes workflow, add a source-basis note such as:

- `meta/source-basis-YYYY-MM-DD-ENTRY.md`

The note should list:
- consulted sources,
- what each source supported,
- what changed since the prior pass,
- which conclusions were facts,
- which conclusions were inferences,
- and what remained open.

## 2. Group sources by authority class

At minimum separate:

### A. Official substrate / official project signals
Examples:
- Rust blog posts
- Rust project-goal pages
- docs.rs explanatory pages
- crates.io official updates

Use these for:
- current platform/tooling/status claims,
- official pain-point statements,
- official feature/goal trajectories,
- hosted-doc/build behavior,
- trust/security surface changes.

### B. Community ecosystem state hubs
Examples:
- Are We Web Yet
- Are We GUI Yet
- Are We Game Yet
- GeoRust
- Automerge project pages

Use these for:
- maturity and variety signals,
- evidence that a sector is active,
- evidence that the missing contribution might be a seam rather than an umbrella.

Do **not** use these as sole support for precise official-status claims.

### C. Research or third-party commentary
If used, say why it was needed and what claim it supports.
Prefer official or primary sources whenever possible.

## 3. Mark fact vs inference vs open question

A pass should say which of these it is making:

### Fact
Directly supported by the cited source.

### Inference
A synthesis across sources, for example:
- “docs/build/target truth is unusually buildable now”
- “domain breadth still points to seam kits, not umbrella replacements”

### Open question
Something the pass suspects but cannot yet support strongly enough to use for promotion.

If a summary changes the frontier on the basis of an inference, say so explicitly.

## 4. Record what changed since the previous pass

The archive gets weaker when each pass looks like a full reset.
A source-basis note should say what is actually new, for example:
- new crates.io trust/security surface,
- new docs.rs behavior,
- new Cargo/report substrate,
- new survey or challenge statements,
- or updated domain maturity signals.

If little changed, say that explicitly and prefer deepen-over-rerank.

## 5. Keep claim ceilings visible

Future passes should not silently turn:
- community hub maturity into official endorsement,
- docs.rs hosted behavior into full package truth,
- advisory visibility into full task fit,
- or project-goal aspiration into stable user-facing availability.

Source-basis notes should preserve those ceilings.

## 6. Update the memory spine when the basis changes

If a source-basis note materially changes how the archive reasons, also touch:
- `meta/research-ledger.md`
- `meta/decision-log.md`
- `meta/llm-hygiene.md`
- `meta/archive-memory-anchor-2026-03-22.md`

## 7. Preferred file shape

Use or adapt `templates/source-basis-note.template.md`.

## Sources

- https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- https://blog.rust-lang.org/2026/03/20/rust-challenges/
- https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
- https://blog.rust-lang.org/2026/02/13/crates.io-malicious-crate-update/
- https://docs.rs/about/builds
- https://docs.rs/about/rustdoc-json
- https://docs.rs/about/download
- https://rust-lang.github.io/rust-project-goals/2026/
- https://www.arewewebyet.org/
- https://areweguiyet.com/
- https://arewegameyet.rs/
- https://georust.org/
- https://github.com/automerge/automerge
