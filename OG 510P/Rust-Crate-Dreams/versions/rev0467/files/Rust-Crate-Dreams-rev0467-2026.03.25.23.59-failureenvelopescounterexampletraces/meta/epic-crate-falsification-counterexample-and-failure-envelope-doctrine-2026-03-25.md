# Epic crate falsification, counterexample, and failure-envelope doctrine — 2026-03-25

## What this doctrine is trying to fix

A lot of crate planning fails at the negative mile.
The tool may emit receipts, summaries, verdicts, or even assurance cases, but a downstream team still cannot answer:
- what exact scenario disproves this claim,
- which witness is decisive,
- what smaller claim still survives,
- what guarantee must be withdrawn,
- and what cheapest replay or rerun might clear the failure.

That is a product failure, not only a documentation failure.

A worthy crate should increasingly export a **failure envelope** above raw receipts and beside assurance cases.
That surface is not a generic chaos platform.
It is a practical, reviewable falsification kit.

## What a worthy crate should provide other people

At minimum, the crate should provide:

### 1. A failing-scenario catalog
Every negative result should name the scenario that broke the claim.
Examples:
- “crate builds locally but fails on docs.rs with hosted recipe differences”
- “support claim fails on tuple `{lldb, macOS, version X}`”
- “mirror route no longer supports inherited assurance for this package set”
- “semver-compatible claim is refuted by API diff under this basis”
- “target-support claim fails after default-target drift or tier downgrade”

Bad behavior:
- collapsing multiple failing conditions into one vague red status,
- implying all profiles fail when one tuple fails,
- or erasing scenario identity once the failure reaches a summary packet.

### 2. A decisive counterexample trace
A counterexample trace is the compact disproof slice beneath the failure.
It should identify:
- source,
- time,
- profile or tuple,
- decisive witness,
- imported versus replayed status,
- and whether the failure is direct, inherited, or inferred.

Bad behavior:
- burying the decisive failing witness in a giant log stream,
- mixing disproving witnesses with merely noisy witnesses,
- or losing the route from the old claim to the new failure.

### 3. A degraded-claim surface
The crate should make explicit what still survives.
Examples:
- “docs build claim survives for listed custom targets but not hosted defaults”
- “debugger support remains for tuple family A but not B”
- “mirror continuity survives for upstream route only”
- “API compatibility remains within profile X but not for public item Y”

Bad behavior:
- turning every failure into total rejection,
- or turning every failure into “still mostly fine.”

### 4. A withdrawn-guarantee note
The crate should say what is no longer justified.
Examples:
- no broader “works on docs.rs” claim,
- no inherited support across this mirror route,
- no debugger-support claim for this async tuple,
- no semver-safe conclusion without override review.

Bad behavior:
- keeping the old guarantee language alive after a counterexample,
- or quietly downgrading without telling reviewers what was lost.

### 5. A repair-hint / replay-slice note
A worthy crate should not only disprove.
It should help another team see the cheapest honest next action.
Examples:
- replay docs build locally with hosted recipe,
- rerun tuple matrix for one debugger version,
- re-import target facts after tier/default drift,
- review one override path instead of redoing the whole decision.

Bad behavior:
- prescribing a full rerun when a smaller slice is honest,
- or prescribing a tiny replay when the claim actually needs a reset.

### 6. A refutation / supersession bridge
A worthy crate should explain whether a failure:
- fully refutes the old claim,
- partially downgrades it,
- merely challenges it pending more witnesses,
- or is cleared by a later replay.

Bad behavior:
- forcing reviewers to diff old and new packets manually,
- deleting failed cases without a bridge,
- or treating cleared failures as if they never existed.

## Recommended artifact family

A strong default family is:

1. `failure-envelope.json`
2. `counterexample-trace.json`
3. `disproof-summary.md`
4. `degraded-claim.json`
5. `withdrawn-guarantee.md`
6. `repair-hint.json`
7. `refutation-bridge.json`

These artifacts should sit **beside** assurance cases, review packets, renewal programs, and delta bundles.
They should **not** replace those lower layers.

## Where this doctrine sits relative to earlier archive layers

- **Conformance kits** say what support tier is being claimed.
- **Interchange profiles** say how reviewed bundles move across tools.
- **Policy packs** say how organizations decide from reviewed bundles.
- **Review packets** say what a reviewer receives.
- **Renewal programs** say when the case must be revisited.
- **Delta programs** say what changed and how much rerun is needed.
- **Assurance cases** say why a claim should be believed.
- **Failure envelopes** say **how a claim is disproved, narrowed, or withdrawn**.

That is why this layer is additive rather than repetitive.

## Recommended first-release shape (`0.1`)

A good `0.1` should:
- support one narrow failure family,
- support one decisive counterexample trace family,
- support one degraded-claim vocabulary,
- expose withdrawn guarantees explicitly,
- and link one prior claim to one refutation or downgrade.

A bad `0.1` would try to:
- become a full observability platform,
- standardize every possible failure grammar in the ecosystem,
- or blend positive assurance and falsification into one opaque mega-schema.

## Package-family recommendation

This doctrine often wants a small suite rather than one crate:
- `*-core` for failure semantics and downgrade rules
- `*-schemas` for stable packet types
- `cargo-*` or CLI front door for generation and review
- one or more bounded adapters for docs.rs / Cargo / debugger / registry inputs
- a corpus package or fixtures directory for counterexample scenarios

## Evaluation checklist

Do not call a crate falsification-ready unless you can name:
1. the failing-scenario family,
2. the decisive counterexample family,
3. the degraded-claim vocabulary,
4. the withdrawn-guarantee surface,
5. the repair-hint / replay-slice rule,
6. and the refutation / supersession bridge.

## Sources

- 2025 State of Rust Survey results
- Rust debugging survey 2026
- What is maintenance, anyway?
- What does it take to ship Rust in safety-critical?
- crates.io development update
- crates.io malicious-crate policy update
- Cargo security advisory (CVE-2026-33056)
- docs.rs changed default targets
- docs.rs metadata / builds / download / rustdoc JSON
- sandboxed build scripts goal
- cargo-semver-checks goal
- cargo build analysis goal
- build-dir layout goal
- StableMIR goal
- target tier policy
