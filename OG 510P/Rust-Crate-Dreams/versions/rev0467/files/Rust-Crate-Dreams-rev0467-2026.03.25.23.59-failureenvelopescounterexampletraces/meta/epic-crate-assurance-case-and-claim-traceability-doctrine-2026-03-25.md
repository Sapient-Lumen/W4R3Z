# Epic crate assurance-case and claim-traceability doctrine — 2026-03-25

## What this doctrine is trying to fix

A lot of crate planning fails at the last review mile.
The tool may emit receipts, summaries, or verdicts, but a downstream team still cannot answer:
- why should we believe this,
- which evidence actually matters,
- what exactly is being claimed,
- what remains unresolved,
- and which parts of the prior review still carry forward?

That is a product failure, not only a documentation failure.

A worthy crate should increasingly export a **traceable assurance surface** above raw receipts and below organization-local policy.
That surface is not “formal verification” in the narrow academic sense.
It is a practical, reviewable argument kit.

## What a worthy crate should provide other people

At minimum, the crate should provide:

### 1. A bounded claim catalog
Every output should name what is actually being claimed.
Examples:
- “crate builds on listed docs.rs targets”
- “public API diff is semver-compatible under this basis”
- “recommendation X applies for profile Y”
- “support claim is replayed locally for these tuples”
- “mirror parity is confirmed for this route and time window”

Bad behavior:
- treating “we observed something” as “we guarantee something”
- collapsing many support dimensions into one vague “works”
- implying domain qualification when only build or docs evidence exists

### 2. A witness bundle
A witness bundle is the decisive evidence slice beneath the claim.
It should identify:
- source,
- time,
- profile,
- scope,
- freshness,
- and whether the witness was imported, replayed, inferred, or manually reviewed.

Bad behavior:
- burying the decisive witness in a giant log stream
- mixing reviewed witness excerpts with raw receipts without saying which is which
- silently relying on witnesses that are outside the declared scope

### 3. A warrant vocabulary
The crate should make explicit the rule that turns witnesses into claims.
Examples:
- “docs.rs target build success is sufficient for a documentation-build claim but not for runtime qualification”
- “cargo-semver-checks pass under this basis supports a semver-compatible API claim, subject to listed exclusions”
- “route parity across mirror and upstream supports continuity only if both route identity and package digest match”

Bad behavior:
- hiding the warrant in code or prose
- pretending the warrant is universal when it is only profile- or lane-specific
- flattening partial sufficiency into total support

### 4. A challenge register
A worthy crate should help downstream users contest a claim.
The crate should therefore ship:
- open challenges,
- unresolved hazards,
- scope gaps,
- missing witnesses,
- conflicting witnesses,
- and reasons a stronger claim was refused.

Bad behavior:
- removing challenges from the review surface because they are inconvenient
- treating “unknown” as “probably fine”
- presenting unresolved contradictions as mere TODOs

### 5. A non-claim note
The crate should say what it does **not** provide.
Examples:
- not a qualification or certification package,
- not a runtime performance guarantee,
- not a debugger correctness proof,
- not source parity for private registries unless those registries are explicitly checked.

Bad behavior:
- allowing packet shape to imply a stronger guarantee than the witnesses justify
- using the absence of objections as if it were proof

### 6. An inheritance / supersession bridge
A worthy crate should explain whether a new case:
- fully inherits the old one,
- partially inherits it,
- downgrades it,
- or supersedes it.

Bad behavior:
- forcing reviewers to diff old and new cases manually
- discarding old cases without a bridge
- treating supersession as deletion rather than explanation

## Recommended artifact family

A strong default family is:

1. `claim-catalog.json`
2. `assurance-case.json`
3. `witness-bundle.json`
4. `challenge-register.json`
5. `assurance-summary.md`
6. `non-claims.md`
7. `inheritance-bridge.json`

These artifacts should sit **above** raw receipts, conformance kits, interchange bundles, review packets, renewal programs, and delta bundles.
They should **not** replace those lower layers.

## Where this doctrine sits relative to earlier archive layers

- **Conformance kits** say what support tier is being claimed.
- **Interchange profiles** say how reviewed bundles move across tools.
- **Policy packs** say how organizations decide from reviewed bundles.
- **Review packets** say what a reviewer receives.
- **Renewal programs** say when the case must be revisited.
- **Delta programs** say what changed and how much rerun is needed.
- **Assurance cases** say **why the claim should be believed at all**.

That is why this layer is additive rather than repetitive.

## Recommended first-release shape (`0.1`)

A good `0.1` should:
- support one narrow claim family,
- support one witness bundle family,
- support one explicit warrant vocabulary,
- expose unknown and refused states,
- and link one prior case to one new case.

A bad `0.1` would try to:
- standardize every claim in the ecosystem,
- become a policy engine,
- or mimic a full assurance tooling platform for regulated environments.

## Package-family recommendation

This doctrine often wants a small suite rather than one crate:
- `*-core` for claim graph and semantics
- `*-schemas` for stable packet types
- `cargo-*` or CLI front door for generation and review
- one or more bounded adapters for docs.rs / Cargo / registry inputs
- a corpus package or fixtures directory for example cases

## Evaluation checklist

Do not call a crate assurance-ready unless you can name:
1. the claim family,
2. the decisive witness family,
3. the warrant vocabulary,
4. the challenge / non-claim surface,
5. the inheritance / supersession rule,
6. and the first reviewer-facing summary.

## Sources

- 2025 State of Rust Survey results
- Rust debugging survey 2026
- What is maintenance, anyway?
- What does it take to ship Rust in safety-critical?
- crates.io development update
- crates.io malicious-crate policy update
- Cargo security advisory (CVE-2026-33056)
- docs.rs metadata / builds / download / rustdoc JSON
- cargo-semver-checks goal
- cargo build analysis goal
- relink-don't-rebuild goal
- StableMIR goal
- target tier policy
