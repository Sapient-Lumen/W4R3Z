---
id: P-0300
title: SECS-II + HSMS + GEM Interop & Evidence Kit — semiconductor equipment transcripts, state-machine replay, and fab-safe bundles
status: idea
domains: [semiconductors, industrial, protocols, interoperability, testing]
last_reviewed: 2026-03-06
evidence:
  - https://www.semi.org/en/standards-watch-2022-Sept/intro-to-semi-communication-standards
  - https://crates.io/crates/semi_e5
  - https://crates.io/crates/semi_e37
---

# Problem

Rust now has the beginnings of a native SECS/GEM stack (`semi_e5` for SECS-II and `semi_e37` for HSMS), but fabs and equipment vendors still lack the missing high-value layer: a **GEM-aware interop workbench** that treats communication as more than bytes on a socket. The costly failures live in:

- equipment and host state-machine mismatches,
- SxFy scenario coverage gaps,
- timing/reconnect/recovery behavior,
- equipment-model/profile drift,
- incident reports that cannot be safely shared outside the fab.

SECS/GEM remains central to equipment automation, yet Rust has no default crate for **canonical transcripts, replayable scenarios, and shareable redacted bug bundles**.

# What it provides

- `secs-canon` — canonical IR for SECS-II messages, HSMS session events, and GEM state transitions.
- `gem-profile` — declarative equipment/host capability and scenario profiles.
- `secs-replay` — deterministic replay of transcripts against host/equipment adapters.
- `secs-fixtures` — SxFy corpora, timing scenarios, and GEM state-machine checks.
- `secs-diff` — semantic diffs for message payloads, timers, and state transitions.
- `cargo secs` — emit `*.secsbundle.zip` artifacts for integration, certification, and incident exchange.

# Users & user stories

- **Equipment vendors**: “Run the same host-simulator scenarios in CI before shipping firmware.”
- **Factory integration teams**: “Show where the tool and host disagree about GEM states or recovery semantics.”
- **Protocol crate authors**: “Validate our encoding/decoding against a public corpus instead of one customer lab.”
- **Field support**: “Share a redacted incident bundle without exposing proprietary recipes or wafer data.”

# Prior art (and why it’s insufficient)

- `semi_e5` and `semi_e37` are strong signs that protocol substrate work is now plausible in Rust, but they are not yet a conformance/evidence stack.
- SEMI communications standards are the normative basis, but standards documents alone do not produce reproducible test artifacts.
- Commercial toolchains exist, which proves demand, but their workflows do not automatically translate into open, reusable Rust crates.

# Design goals

1. **State-machine-aware** — GEM semantics must be first-class, not comments attached to packets.
2. **Fab-safe artifacts** — recipe names, lot IDs, and proprietary data must be redactable or tokenized.
3. **Host/equipment symmetry** — the same harness should test both sides.
4. **Scenario-first** — fixture packs should speak in terms of operational flows, not isolated PDUs only.
5. **Incremental adoption** — work with existing Rust protocol crates instead of replacing them.

# Non-goals

- Not a manufacturing execution system.
- Not a recipe-management platform.
- Not a complete digital-twin of all fab equipment.

# Architecture & API sketch

```rust
pub struct SecsBundleReport {
    pub profile_id: String,
    pub state_trace: Vec<StateTransition>,
    pub verdicts: Vec<Verdict>,
}

pub trait SecsAdapter {
    fn send(&mut self, msg: CanonicalSecsMessage) -> Result<(), Error>;
    fn poll(&mut self) -> Result<Vec<CanonicalSecsEvent>, Error>;
}

pub fn replay(bundle: &SecsBundle, adapter: &mut dyn SecsAdapter) -> Result<SecsBundleReport, Error>;
```

Bundle draft: `profile.toml`, `transcript.jsonl`, `state-trace.json`, `payloads.binpack`, `redaction-map.json`, `verdicts.json`, `notes.md`.

# Security / safety model

- Redact equipment identifiers, lot IDs, recipe references, and proprietary parameter values by default.
- Treat all binary payloads as hostile input and enforce framing/size/time limits.
- Allow payload tokenization so behavior can be shared without disclosure.

# Maintenance & governance plan

- Keep protocol codecs, scenario packs, and bundle tooling modular.
- Track SEMI version assumptions explicitly in profiles and fixtures.
- Encourage community fixture contributions for generic host/equipment flows before any vendor-specific packs.

# Milestones

## 0.1
- Canonical SECS/HSMS transcript IR
- GEM state-trace model
- Redaction/tokenization support

## 0.2
- Host/equipment adapter traits
- Public scenario packs
- `cargo secs replay`

## 1.0
- Stable `*.secsbundle.zip`
- CI-ready scenario suites
- Clear mapping from bundle verdicts to GEM/state-machine failures

# Open questions

- Which GEM states and timers belong in the stable MVP IR?
- How should large proprietary payloads be tokenized while preserving reproducibility?
- Can public scenario packs meaningfully cover enough real host/equipment pain without vendor secrets?

# Sources

- SEMI communications overview: https://www.semi.org/en/standards-watch-2022-Sept/intro-to-semi-communication-standards
- Additional GEM overview: https://www.cimetrix.com/semi-secs-gem-intro
- Rust crates: https://crates.io/crates/semi_e5 ; https://crates.io/crates/semi_e37
