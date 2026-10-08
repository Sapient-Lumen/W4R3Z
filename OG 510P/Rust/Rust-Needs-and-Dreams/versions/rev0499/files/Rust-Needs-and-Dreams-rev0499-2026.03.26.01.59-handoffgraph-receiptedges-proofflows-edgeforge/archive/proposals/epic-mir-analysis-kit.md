# Epic proposal: MIR Analysis Kit (`cargo mir` + `mir-pack/v0`)

## One-liner
Ship a standard, semantics-aware MIR capture and query boundary for Rust: `cargo mir`, versioned subject/capture/capability artifacts, reviewable query reports, and diffable packs over `rustc_public`-based analysis lanes.

## Why this is worthy
Rust is finally approaching the point where sophisticated external tooling can be built on a SemVer-oriented compiler interface instead of reverse-engineering internals every release. That is exactly the moment when the ecosystem most needs a **shared handoff layer**.

The missing piece is not “one more analyzer”. It is the reusable boundary that says:
- what subject was captured,
- through which lane,
- with what completeness and semantic epoch,
- what derived graphs or query results were produced,
- and whether two results are honestly comparable.

That is the kind of contribution that can unlock many others:
- semver/public-API tools,
- safety and contracts tooling,
- formal-methods frontends,
- MIR-aware CI and review workflows,
- research tooling that otherwise keeps growing private compiler-driver forks.

## Users
- compiler-adjacent tool authors
- semver/public-API tool builders
- safety / verification / formal-methods teams
- CI/review systems consuming structured compiler-aware evidence
- research projects and organizations currently maintaining private rustc-driver glue

## MVP (6–10 weeks)
- `mir-subject/v0`, `mir-capture-profile/v0`, `mir-capability-profile/v0`, `mir-observation-report/v0`, `mir-pack/v0`
- `cargo mir capture`, `doctor`, `pack`
- one producer bridge for an existing exporter (`stable-mir-json`-style lane)
- one query family (for example unsafe reachability or mono-growth)
- one `mir-diff-report/v0` for PR/base comparison
- fixtures from a few real workspaces on more than one toolchain version

## Good v1 extensions
- more `mir-query-report/v0` families (contracts-linked slices, alloc/use summaries, recursion SCCs)
- `mir-derived-graph/v0` attachments with digest-addressable side tables
- attachable evidence for Safety Evidence Kit and Public API Kit
- richer semantic-epoch / comparability policies
- first-class consumer libraries for CI systems and issue trackers

## Non-goals (initially)
- freeze all MIR semantics forever
- replace `rustc_public` or the Rustc Librarification Project
- upstream every analysis into one tool
- guarantee perfect comparability across arbitrary toolchain changes
- invent a fake universal IR unrelated to Rust’s actual MIR and compiler evolution

## Risks and mitigations
- **Upstream churn**
  - keep the contract artifact-first and explicit about lane + capability + semantic epoch.
- **False sense of stability**
  - require completeness and comparability declarations in packs and diffs.
- **Scope bloat**
  - start with capture/query/pack instead of every imaginable analysis.
- **Project overlap**
  - ship adapters first and position the kit as shared glue, not replacement empire.

## Why now
This is no longer premature.

The accepted StableMIR goal and the active `rustc_public` publication MCP say Rust wants external tool authors to have a sustainable compiler interface. At the same time, nightly docs still warn that parts of the surface are unstable, bridge escape hatches remain necessary, and MIR semantics themselves are still evolving. That combination is precisely why a **shared evidence-and-comparability layer** is valuable *now*: before serious downstream tools each harden around a different incompatible export format and a different unspoken notion of “same MIR”.
