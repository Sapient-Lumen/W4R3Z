
# Epic contribution contract witness packs (2026 Q1)

## Why this layer is now missing
The repo already knows:
- which Rust ecosystem contributions are strongest,
- what verdict they deserve now,
- what a bounded v0 should contain,
- what lands first inside that v0,
- and what contract0 surface the first implementation should honor.

What it still did **not** know concretely enough was:
> what should those surfaces **look like when actually exercised** so future revisions stop reconstructing schemas, receipts, and failure posture from prose alone?

That missing layer is a **contract witness pack** layer.
A witness pack is not a live operational dataset and not a universal schema standard.
It is a small illustrative corpus that binds together:
- one bounded command invocation,
- one example emitted artifact,
- one rendered or reviewer-facing view,
- and one explicit negative or partial-state posture.

It exists to keep contract notes honest and implementations comparable.

## Why this is justified by current Rust signals
Fresh official Rust signals still point toward small machine-facing seams with explicit caveats, not giant platform launches:
- Cargo's external-tools guidance still centers `cargo metadata`, `--message-format=json`, and custom subcommands, and it says `cargo metadata` is stable and versioned when callers pass `--format-version` explicitly.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- Cargo build analysis is still prototype work around recorded build metadata and unstable `cargo report` subcommands, so the repo needs concrete examples that keep stable-only and unstable-enhanced posture visibly separate.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The March 2026 build-dir-layout-v2 testing call still says many projects rely on unspecified internals and asks people to test real workflows with `-Zbuild-dir-new-layout`, which argues for migration and failure receipts in examples rather than prose optimism.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- The Cargo 1.94 development-cycle update again says Cargo can't be everything to everyone because of compatibility guarantees and explicitly highlights plugins, structured logging, `cargo report rebuild`, `cargo report sessions`, and related external-tool surfaces.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo now also includes an experimental JSON Schema file for `Cargo.toml` in the source code to help external tools validate or auto-complete manifest structure. Even though that is not a promise about every future schema, it reinforces that **example payloads plus schema discipline** are ecosystem-appropriate work.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- crates.io's January 2026 update extends Trusted Publishing and adds Trusted-Publishing-only mode, while the March 2026 Cargo advisory still preserves route-specific caveats for alternate registries. That makes receipt-shaped examples more honest than registry-global trust abstractions.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://blog.rust-lang.org/2026/03/21/cve-2026-33056/
- The safety-critical writeup still calls for target-focused readiness checklists, dependency lifecycle patterns, async-runtime qualification requirements, and FFI/interop guidance. That is exactly the kind of work that benefits from witness cards and packs instead of certification theater.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/

## What a contract witness pack should contain
Each witness pack should bind together four things:
1. **one command family** from contract0,
2. **one or more emitted artifact examples**,
3. **one reviewer-facing or rendered example**,
4. **one visible unsupported / partial / caveated state**.

The witness file itself should explain:
- what command was hypothetically run,
- which example files correspond to that invocation,
- what truth the example is allowed to support,
- what truth is still absent,
- and what tempting wider interpretation is refused.

## Why witness packs matter after contracts
A contract note can still fail in practice when:
- command names look clear but emitted fields are vague,
- artifact families are named but not exemplified,
- unsupported states exist in prose but disappear in output examples,
- stable and experimental imports get blended in one specimen,
- or later editors silently normalize away route-specific, tuple-specific, or evidence-freshness caveats.

A witness pack is the thinnest layer that catches those failures before an implementation exists.

## What belongs in the first witness corpus
Only kernels that already have:
- a live packet,
- a kernel brief,
- a slice-0 note,
- and a contract0 note.

That means the first witness corpus should cover:
1. **Build-State Pack**
2. **Debug Acceptance Matrix**
3. **Package Intake Review Kit**
4. **Safety-Critical Readiness Cards**

Still excluded:
- **Navigation / Defaults / Claims Commons**

Why navigation/defaults stays excluded:
- it is still `hold`;
- its blocker is stewardship and renewal burden;
- and witness packs would create fake implementation momentum before the editorial renewal problem is solved.

## The first witness family
### 1) Build-State Pack witness family
Needed examples:
- one `build-session-pack/v0` example,
- one `build-diff/v0` example,
- one bounded doctor note,
- one explicit experimental-import caveat.

What the witness should teach:
- stable-only capture is enough to be useful;
- experimental `cargo report *` or build-dir-layout signals must stay visibly separate;
- and path/layout drift is part of the truth, not cleanup noise.

### 2) Debug Acceptance Matrix witness family
Needed examples:
- one `debug-session-pack/v0` example,
- one `debug-tuple-card/v0` example,
- one `debug-replay-result/v0` example,
- one unsupported-state receipt inside the tuple/replay posture.

What the witness should teach:
- tuple identity is first-class;
- yellow and red states are not a formatting embarrassment;
- and replay truth matters more than a synthetic “best debugger” summary.

### 3) Package Intake Review Kit witness family
Needed examples:
- one `intake-receipt/v0` example,
- one `waiver-receipt/v0` example,
- one `incident-drill-report/v0` example,
- one route-specific uncertainty field that does not disappear in the happy path.

What the witness should teach:
- local review receipts are the real kernel;
- crates.io posture is not automatically portable to alternate registries;
- and waivers/quarantines are part of the product, not embarrassing edge cases.

### 4) Safety-Critical Readiness Cards witness family
Needed examples:
- one `readiness-card/v0` example,
- one `readiness-pack/v0` example,
- one `readiness-diff/v0` example,
- one stale or unsupported-state receipt posture.

What the witness should teach:
- owner, freshness, evidence, blockers, and “does not prove” fields are the honesty spine;
- example adopter evidence stays illustrative;
- and pack/diff ergonomics matter because institutional decisions happen over time, not once.

## What witness packs are allowed to do
Allowed:
- show one plausible first grammar,
- keep contract0 notes from becoming hand-wavy,
- let future revisions compare implementations to a real example family,
- and preserve negative-state posture in visible files.

## What witness packs are not allowed to do
Not allowed:
- pretend to be live operational truth,
- silently upgrade unstable Cargo experiments into stable commitments,
- become a giant registry of every possible variant,
- stand in for proving-ground evidence,
- or bypass packet, kernel, slice, or contract notes.

## Default interpretation for future revisions
Until the portfolio changes materially:
- the broad ladder is unchanged;
- the missing new layer is **contract witness packs / example emitted artifacts**, not another ranking rewrite;
- live packets still govern verdict posture;
- kernels still govern first repo shape;
- slices still govern what lands first;
- contracts still govern the first machine-facing surface;
- and witness packs now govern **what that surface should look like when exercised honestly**.
