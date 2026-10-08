# Epic-contribution kernel artifact schemas (2026 Q1)

## Why this note exists
The archive now has:
- live decision packets,
- bounded v0 kernel briefs,
- slice-0 milestone plans,
- contract0 surface notes,
- witness/example outputs,
- and replayable fixture packs.

What it still lacked was the next practical answer after fixtures:
**what machine-readable artifact schemas should those first outputs validate against so two implementations can emit compatible payloads without reverse-engineering prose or examples?**

Without that layer, the repo still had four avoidable failure modes:
- examples looked concrete but remained illustrative prose unless readers manually copied their shape;
- fixtures named expected artifacts but did not say what minimum fields or enums those artifacts must carry;
- future assistants could quietly widen or narrow example payloads without tripping any repo-level check; and
- machine-facing kernels stayed one step short of actually interoperable because they lacked a versioned schema pack.

A **kernel artifact schema pack** is the missing bridge.
It is narrower than a contract note, stricter than a witness, and more durable than a fixture recipe.

## What a kernel artifact schema pack is
A kernel artifact schema pack should answer:
- which emitted JSON artifact families belong to a first implementation;
- which minimum required fields each family must carry;
- which fields remain additive/open so the contract does not freeze too early;
- which example payloads currently witness the family;
- and which receipts are shared across kernels rather than duplicated under many names.

A schema pack is **not**:
- proof that Rust or Cargo should stabilize the archive's artifact families;
- a full semantic ontology for every later stage of each program;
- or an excuse to turn markdown/operator views into fake JSON APIs.

Think of it as the archive's **machine-conformance spine** for already-earned kernels.

## Why this is the right next layer now
Fresh official Rust signals still reward explicit machine-readable formats, version markers, and careful compatibility posture:
- Cargo's external-tools guidance still points tool authors to `cargo metadata`, JSON messages, and custom subcommands, which reinforces schema-first companion tooling rather than scraping or hosted-state dependence.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- `cargo metadata` explicitly recommends `--format-version` and documents additive compatibility within a format version. That is almost a direct argument for versioned archive artifact schemas instead of loose examples.
  https://doc.rust-lang.org/cargo/commands/cargo-metadata.html
- docs.rs now hosts rustdoc JSON and warns consumers to inspect `format_version`; it also notes that availability depends on builds/rebuilds and that old releases may lag. That is exactly the sort of currentness/compatibility lesson the archive should inherit for its own machine outputs.
  https://docs.rs/about/rustdoc-json
- Cargo now includes an experimental JSON Schema for `Cargo.toml` in source to help external tools validate or auto-complete manifests. That does not make every future schema stable, but it does strengthen the case that concrete schema packs are ecosystem-appropriate support artifacts.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- Cargo build analysis is still prototype work around recorded metadata and unstable `cargo report` subcommands, so top-band build-state tooling especially needs a clear split between stable imports, experimental imports, and versioned local artifact schemas.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The build-dir-layout effort is still actively testing real workflows because downstream tools rely on unspecified details. That argues for schema fields that preserve caveats and unsupported states, not for silently normalized green outputs.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-dir-layout.html
- The libtest JSON goal exists because the ecosystem relies on programmatic output. That reinforces the broader point that replayable fixtures plus witness examples still need schemas if the archive wants machine-facing continuity rather than prose-only discipline.
  https://rust-lang.github.io/rust-project-goals/2025h2/libtest-json.html
- The 2026 goals and flagships keep secure supply chain, safety-critical evidence, and building blocks in the strategic core. Those are all better served by schema-checked local artifacts than by premature platforms or dashboards.
  https://rust-lang.github.io/rust-project-goals/2026/
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

Taken together, those signals say the next worthy repo layer is **artifact schemas for already-earned kernels**, not another ranking or charter rewrite.

## What belongs in the first schema corpus
The first corpus should cover only kernels that already have:
- a live packet,
- a kernel brief,
- a slice-0 note,
- a contract0 surface,
- a witness bundle,
- and a replay fixture.

That means the first schema corpus should cover:
1. **Build-State Evidence**
2. **Feedback / Debug Acceptance Commons**
3. **Package Intake + Release Boundary Review**
4. **Safety-Critical + Institutional Readiness Commons**

And it should still **not** schema-first:
5. **Navigation / Defaults / Claims Commons**

Why navigation/defaults is still absent:
- it is still `hold`;
- its main blocker is renewal/stewardship burden, not missing payload shape;
- and schema-writing it now would create fake implementation certainty before the editorial burden is honestly solved.

## Required sections for a kernel artifact schema note
Every schema-deepening note should keep these sections visible:
1. **identity and scope** — which kernels and artifact families are covered now;
2. **family list** — emitted JSON families included in schema0;
3. **example bindings** — which specimen payloads witness each family today;
4. **compatibility posture** — additive/open fields, required core fields, and non-goals;
5. **shared receipt posture** — what is shared across kernels (`unsupported-state`, `stale-card`) instead of copied ad hoc;
6. **validation posture** — what checker or linter must pass;
7. **refused expansions** — what is still not being standardized;
8. **exit criteria** — what would justify widening schema coverage or tightening constraints.

## The first schema family bundle
### 1) Build-State Pack schemas
Cover:
- `build-session-pack/v0`
- `build-diff/v0`
- `unsupported-state-receipt/v0`

The first schema set should preserve:
- capture identity,
- stable versus experimental import separation,
- path/layout caveat space,
- and explicit unsupported-state receipts for mixed streams or truncated capture.

### 2) Debug Acceptance Matrix schemas
Cover:
- `debug-session-pack/v0`
- `debug-tuple-card/v0`
- `debug-replay-result/v0`
- `unsupported-state-receipt/v0`

The first schema set should preserve:
- tuple identity,
- async/runtime/debugger posture,
- yellow/red capability states,
- and manual-observation/partial-export caveats.

### 3) Package Intake Review Kit schemas
Cover:
- `route-profile/v0`
- `intake-receipt/v0`
- `waiver-receipt/v0`
- `quarantine-receipt/v0`
- `incident-drill-report/v0`
- `unsupported-state-receipt/v0`

The first schema set should preserve:
- route identity,
- local review decision lineage,
- waiver/quarantine expiry and owner,
- and alternate-registry uncertainty that must not collapse to green by accident.

### 4) Safety-Critical Readiness schemas
Cover:
- `readiness-card/v0`
- `readiness-pack/v0`
- `readiness-lint-report/v0`
- `readiness-diff/v0`
- `stale-card-receipt/v0`
- `unsupported-state-receipt/v0`

The first schema set should preserve:
- owner/freshness/evidence-bearing cards,
- lint failures for missing proof ingredients,
- pack/diff posture that stays machine-diffable,
- and explicit non-proof/stale-evidence receipts.

## What the schema layer should teach
- a worthy top-band contribution should usually expose a **versioned schema family** before it chases broad adoption or hosted UX;
- example JSON without a schema is still too soft for long-lived machine-facing repo discipline;
- negative states belong in the schema family, not just in markdown caveats;
- additive compatibility matters more than over-tight early freezing; and
- refusing to schema-write a `hold` candidate is part of the archive's quality bar.

## Anti-goals
This layer should refuse:
- treating archive schemas as if they were Rust-project standards;
- pretending markdown/operator views must also become machine contracts right now;
- over-constraining example payloads so additive evolution becomes impossible;
- flattening shared receipts and kernel-specific artifacts into one giant omnibus schema;
- or using schema-writing to bypass the renewal/stewardship blocker on held candidates.

## Default interpretation for future revisions
Until the portfolio changes materially:
- this is an **artifact-schema deepening** move, not a frontier promotion;
- the broad ladder is unchanged;
- live packets still govern verdict posture;
- kernel briefs still govern repo shape;
- slices still govern first milestones;
- contracts still govern command/file/schema surfaces in prose;
- witnesses still govern example exercised outputs;
- fixtures still govern replayable scenario inputs and expected checks;
- and artifact schemas now govern the **machine-validatable JSON families** for kernels that already earned all of the above.
