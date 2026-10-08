# Sanitizer Profile & Evidence Kit lane boundaries (2026-03-22)

This note exists so the archive does not flatten several adjacent debugging, safety, and support lanes into one fake “sanitizer support” crate.

## Core judgment

**P-0434 Sanitizer Profile & Evidence Kit** should be the lane for:

- **instrumentation-scope truth**,
- **runtime-linkage truth**,
- **symbolization-route truth**,
- **suppression-policy truth**,
- and conservative sanitizer-bundle interpretation.

It is the lane for the question:

> “What exactly did this sanitizer run instrument, how was it linked and symbolized, and how much should another team trust the resulting evidence?”

## Keep separate from these adjacent lanes

### 1. P-0484 Toolchain & Target Support Contract Kit

Toolchain/target support is about a project’s broader support posture across hosts, targets, docs, tests, and external prerequisites.

Sanitizer evidence is **not**:
- the full project support contract,
- a target-readiness checklist,
- an artifact-route map for the whole build,
- or a proof that a target is broadly supported.

Sanitizer evidence may import host/target facts from **P-0484**, but it owns the narrower workflow truth for one sanitizer lane.

### 2. P-0486 Debuggability Support Contract Kit

Debuggability support is about debugger families, symbol asset availability, visualizers, source lookup, and advanced debugging capability ceilings.

Sanitizer evidence is **not**:
- a debugger capability matrix,
- a NatVis / LLDB / GDB support contract,
- or a guarantee that postmortem debugging is broadly excellent.

It may share symbolization concerns, but sanitizer evidence owns the **capture-time sanitizer handoff route**, not the whole debugger story.

### 3. P-0485 Verification Campaign Workbench Kit

Verification campaigns are about obligations, tool lanes, trust ledgers, policy evaluation, and campaign comparability.

Sanitizer evidence is **not**:
- a full cross-tool verification campaign,
- a proof that safety goals were met,
- or a substitute for deductive, model-checking, or theorem-proving evidence.

A sanitizer bundle may become one evidence lane inside **P-0485**, but it does not replace it.

### 4. P-0121 FFI Boundary & Bindings Conformance Kit

FFI boundary work is about ownership transfer, unwind posture, callback execution, layout authority, and binding correctness.

Sanitizer evidence is **not**:
- a proof that the ABI boundary is correct,
- a layout-conformance witness,
- or a binding-generation contract.

Sanitizer runtime-linkage receipts may mention mixed-language routes, but they must not masquerade as FFI correctness.

### 5. Borrowsanitizer / single-tool experimental lanes

A workflow/evidence crate should not collapse into the semantics or roadmap of one specific experimental sanitizer or research prototype.

It must stay:
- receipt-oriented,
- conservative,
- and multi-sanitizer enough to be portable across ASan/LSan/MSan/TSan-class workflows.

## Allowed imports

Sanitizer evidence may import:

- unstable-book sanitizer guidance,
- Cargo `-Z build-std` requirements,
- rustup/toolchain facts,
- CI invocation and environment facts,
- symbolizer discovery,
- and mixed-language linkage notes.

But it must keep visibly separate:

- `requested_policy`
- `observed_scope`
- `inferred`
- `manual_review_required`

## Preferred proving grounds

The best tests for this lane are not “an ASan hello world succeeded.”
They are cases like:

- MemorySanitizer with incomplete instrumentation,
- Cargo runs missing `--target` and accidentally trying to instrument host helpers,
- mixed Rust/C++ runs with ambiguous runtime ownership,
- and reports that are technically present but not symbolized enough for handoff.

## Failure mode to resist

Do not let future passes quietly rephrase this lane as:

- “we enabled sanitizers,”
- “the target is supported,”
- “the debugger stack is good,”
- or “verification passed.”

The archive now has a distinct lane for the **workflow-and-evidence contract** of sanitizer use.
