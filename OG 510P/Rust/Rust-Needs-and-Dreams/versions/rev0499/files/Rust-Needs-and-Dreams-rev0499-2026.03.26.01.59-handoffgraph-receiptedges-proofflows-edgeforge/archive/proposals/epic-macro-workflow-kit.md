# Epic Proposal: Macro Workflow Kit (`cargo macro`, `macro-pack/v0`)

## One-sentence pitch
Give Rust a standard way to inventory, expand, profile, debug, and plan migrations for macros so proc-macro-heavy codebases become easier to review, optimize, and gradually simplify.

## Deliverables
- `cargo macro` reference tool
- Schemas:
  - `macro-inventory/v0`
  - `macro-expansion-pack/v0`
  - `macro-cost-report/v0`
  - `macro-debug-report/v0`
  - `macro-migration-hints/v0`
  - `macro-pack/v0`
- Adapters / integrations for:
  - Cargo tree proc-macro inventory
  - `cargo-expand`-style expansion capture
  - rust-analyzer proc-macro metadata where available
  - compile-time cost/event feeds from existing/report-oriented tooling
- Docs:
  - macro debugging guide
  - macro cost triage guide
  - proc-macro reduction / migration planning guide

## Why now (signals)
- The accepted macro improvements goal is explicitly trying to make `macro_rules!` capable enough to replace many proc-macro use cases, and names faster builds and smaller supply chains as benefits.
  https://rust-lang.github.io/rust-project-goals/2025h1/macro-improvements.html
- The reflection-and-comptime goal explicitly says proc-macro derives have historically been hard to debug and bootstrap, which is unusually direct motivation for workflow tooling.
  https://rust-lang.github.io/rust-project-goals/2025h2/reflection-and-comptime.html
- Cargo now marks proc-macro crates in `cargo tree`, which is a real upstream visibility signal, but still not a workflow or artifact layer.
  https://doc.rust-lang.org/beta/releases.html
- `cargo-expand` remains the practical expansion tool, but it documents itself as a lossy debugging aid rather than a durable artifact boundary.
  https://docs.rs/crate/cargo-expand/latest
- rust-analyzer still treats proc-macro support and ignored macros as explicit configuration surfaces, which shows the IDE seam is real and still user-visible.
  https://rust-analyzer.github.io/book/configuration
- Procedural macros still run during compilation with compiler-level resource/security concerns and dedicated `proc-macro` crates.
  https://doc.rust-lang.org/reference/procedural-macros.html

## Non-goals
- Replacing proc macros with one magical new system
- Auto-migrating arbitrary derive/attribute macros into `macro_rules!`
- Competing with rust-analyzer as an IDE backend
- Pretending expansion-to-text is lossless source truth
- Collapsing compile-time capability policy into macro workflow artifacts

## Strategic value
This is a worthy contribution because it upgrades macros from **opaque compile-time magic** into **reviewable workflow objects**.

That unlocks:
- inventory that explains where proc macros are and why they matter,
- better compile-time optimization work for macro-heavy stacks,
- issue-attachable debugging artifacts instead of ad hoc local steps,
- cleaner migration planning as declarative macro and reflection/comptime capabilities improve,
- and a thinner integration target for CI, IDEs, performance tooling, and security/policy layers.

The archive already has Compile-Time Capabilities Kit for sandboxing and permissions.
Macro Workflow Kit fills a different missing seam above it: one portable inventory/expansion/cost/debug/migration boundary.

## Milestones
1. **v0 schemas + validators**
   - publish canonical pack structure
   - validate raw vs lossy expansion markers
2. **v0.2 inventory + expansion capture**
   - ingest Cargo tree proc-macro information
   - capture targeted expansion packs
3. **v0.3 cost + debug adapters**
   - publish macro hotspot reports
   - normalize macro panic / failure context into `macro-debug-report/v0`
4. **v1 migration hints + cross-kit hooks**
   - emit candidate proc-macro reduction hints
   - integrate with Build Cache, Perf Labs, and Compile-Time Capabilities evidence flows

## Success metrics
- Teams can produce one `macro-pack/v0` artifact for a workspace without custom scripting.
- CI and issue trackers can attach macro failures and expansion context without raw log scraping.
- Macro-heavy dependency stacks become easier to inventory and prioritize for cleanup.
- Migration candidates can be tracked explicitly instead of living in tribal knowledge.

## Relationship to the Compile-Time Surface stack
This proposal is the **workflow and transition pillar** of the broader compile-time stack described in [`design/compile-time-surface-pilot-program.md`](../design/compile-time-surface-pilot-program.md).
It becomes more strategic when paired with capability evidence below and declarative/reflection transitions ahead, because that is how macro pain turns into tractable ecosystem work rather than permanent folklore.
