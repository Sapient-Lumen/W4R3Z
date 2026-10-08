# Design: Compiler Extensibility Pilot Program (compiler-attached tools as reviewable ecosystem products)

## Goal
Turn the **Compiler Extensibility Stack** into a ranked execution program instead of leaving it as a vague endorsement of “more tooling”.

A worthy contribution here should prove that Rust can ship at least a few **compiler-attached tool lanes** with:
- explicit attachment truth,
- reviewable scope/configuration,
- honest stability posture,
- reusable result artifacts,
- and downstream consumer handoffs.

## Why a pilot layer is necessary
The underlying ideas are attractive enough that the archive could easily get sloppy here.
Without a pilot layer, this seam risks several bad habits:
1. **nightly glamour** — a tool looks ecosystem-ready because the demo is impressive;
2. **attachment confusion** — rustdoc JSON, `rustc_public`, Clippy, witness compilation, and custom drivers get treated as if they mean the same thing;
3. **consumer overreach** — CI/release/safety consumers start making stronger claims than the tool actually supports;
4. **Cargo-merger fantasy** — every useful tool gets narrated as future core Cargo rather than as a legitimate companion product.

A pilot program forces the archive to ask:
- which lane is being proven,
- what evidence counts,
- who the first real consumers are,
- and what graduation would actually mean.

## Pilot artifact family
### 1. `tool-pilot-brief/v0`
Records:
- pilot id and summary
- chosen lane
- why this lane matters now
- intended consumers
- explicit non-goals

### 2. `compiler-attachment-profile/v0`
Records:
- attachment family and version requirements
- stability posture
- scope and blind spots
- required toolchain/config

### 3. `analysis-input-profile/v0`
Records:
- imported source kinds
- whether cross-crate/generated/foreign items were visible
- whether witness compilation or synthetic programs were used
- reproducibility/freshness posture

### 4. `tool-stability-profile/v0`
Records:
- supported Rust/toolchain ranges
- result stability promises
- known incompleteness
- gating-vs-advisory posture

### 5. `tool-result-report/v0`
Records:
- reason-coded findings, witnesses, diffs, or guidance
- machine-readable outputs
- human-readable rendering boundaries
- waiver / uncertainty fields

### 6. `tool-consumer-handoff/v0`
Records:
- who may consume the pilot output
- what human review remains mandatory
- what automatic conclusions are forbidden

### 7. `tool-pilot-scorecard/v0`
Asks:
- did the pilot declare its attachment lane honestly?
- did it preserve subject/configuration truth?
- did it export reusable artifacts rather than bespoke output?
- did at least one real consumer use the handoff?
- did it avoid overstating stability or completeness?
- does widening still look justified?

### 8. `tool-pilot-pack/v0`
Bundle for review and reuse:
- pilot brief
- attachment/input/stability profiles
- result reports
- consumer handoff
- scorecard

## Ranked first pilots

### 1) SemVer / compatibility lane
**Why first**
- It is already a real ecosystem problem with a real tool and a plausible Cargo-adjacent future.
- `cargo-semver-checks` exposes exactly the kind of boundary pain this stack is meant to clarify: rustdoc JSON limits, cross-crate visibility, witness-generation needs, and type-precision issues.
- The first consumers are concrete and high-value: maintainers, release review, and eventually publish-path workflows.

**Core artifacts**
- `tool-subject`
- `compiler-attachment-profile`
- `analysis-input-profile`
- `tool-result-report`
- `tool-consumer-handoff`
- `tool-pilot-scorecard`

**Primary consumers**
- maintainers before release
- release review
- package-admission / public-API consumers later

### 2) Safety-critical lint lane
**Why second**
- The 2026 flagships explicitly call out safety-critical lints in Clippy.
- This lane proves the stack can handle policy-heavy lint families without collapsing them into generic style linting.
- It also tests the boundary between lint findings, debt budgets, guidance, and safety/release consumers.

**Core artifacts**
- `compiler-attachment-profile`
- `tool-capability-profile`
- lint baseline / finding reports
- `tool-consumer-handoff`
- `tool-pilot-scorecard`

**Primary consumers**
- safety-focused maintainers
- CI with human review
- assurance-facing downstream consumers

### 3) `rustc_public` / MIR read-only analyzer lane
**Why third**
- This is the cleanest lane for proving that compiler-derived semantic export can support ecosystem tools without every project inventing a custom driver.
- It is deliberately read-only, which keeps the first proof narrow and honest.
- It tests whether subject/configuration and comparability truth are good enough for shared analysis tooling.

**Core artifacts**
- `tool-subject`
- `compiler-attachment-profile`
- `analysis-input-profile`
- MIR/query/derived-graph reports
- `tool-pilot-scorecard`

**Primary consumers**
- analyzer authors
- semver/safety/verification tooling
- research/prototyping consumers

### 4) Guidance / fix handoff lane
**Why fourth**
- Many tools become truly useful only when results can be rendered as actionable guidance or bounded fix suggestions.
- This lane proves the stack can keep findings distinct from generated guidance and fixes.
- It also tests editor and CI handoff without requiring that generated edits become authoritative.

**Core artifacts**
- `tool-result-report`
- guidance pack / fixpack attachments
- `tool-consumer-handoff`
- `tool-pilot-scorecard`

**Primary consumers**
- editors and assistants
- maintainers doing reviewable cleanup
- policy/lint migration consumers

### 5) Assurance / conformance consumer lane
**Why fifth**
- This is the highest-stakes import path and should come after the lower lanes prove honest attachment and handoff.
- It tests whether compiler-aware tooling can feed spec/safety/conformance consumers without flattening partial evidence into fake certification.
- It is the right place to join compiler-extensibility work to the archive’s assurance layers.

**Core artifacts**
- `compiler-attachment-profile`
- `analysis-input-profile`
- conformance / assurance reports
- `tool-consumer-handoff`
- `tool-pilot-scorecard`

**Primary consumers**
- conformance review
- safety-critical evidence consumers
- high-assurance release workflows

## Graduation logic
A lane should graduate only when it can answer **yes** to most of these:
- is the attachment lane declared explicitly?
- can another tool or workflow import the result without bespoke scraping?
- are subject/configuration details precise enough for review?
- are incompleteness and instability still visible?
- is at least one real consumer using the handoff?
- would widening this lane add leverage instead of only complexity?

## What should wait
The following should stay **later** until earlier pilots prove themselves:
- grand unified compiler-plugin stories;
- automatic publish-path gating for broad tool families;
- universal editor/assistant integration claims;
- assurance or certification claims that outrun the evidence;
- one schema that tries to normalize every compiler-attached tool at once.

## Immediate archive consequence
The archive should now treat the next worthy move in this area as:
- **ranked compiler-extensibility pilots**, not another isolated kit;
- **tool contracts and handoffs**, not just new analyzers;
- and **consumer-proof artifacts**, not only tool-author convenience.
See also: [`proposals/epic-compiler-extensibility-stack.md`](../proposals/epic-compiler-extensibility-stack.md).

