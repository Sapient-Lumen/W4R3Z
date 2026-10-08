# Epic-contribution kernel slices (2026 Q1)

## Why this note exists
The archive now has:
- rankings and macro-programs,
- reference architectures,
- charters,
- stage gates,
- review packets,
- dossier and live-packet posture,
- and bounded **v0 kernel briefs** for the top candidates that earned a first build.

What it still lacked was a sharper answer to the next practical question:
**inside a bounded v0, what do you build first, second, and third so the kernel proves something real before it grows new surface area?**

Without that layer, the repo still risks four failures:
- a good v0 brief turns back into an amorphous backlog;
- `advance` candidates widen too early because “v0 exists” is mistaken for “everything in the brief should ship now”;
- future assistants invent new milestone sequences from memory instead of reusing one canonical first slice; and
- “first repo shape” silently mutates into mini-platform planning before the kernel has earned it.

A **kernel slice** is the missing bridge between a v0 brief and a real first milestone.
It is smaller than the kernel brief, more build-shaped than a packet, and more execution-real than a charter.

## What a kernel slice is
A kernel slice should answer:
- what the **first bounded milestone** is;
- what concrete files, commands, schemas, fixtures, or cards land in that milestone;
- what proving grounds are enough for the first honest claim;
- what should be postponed to slice 2 or later;
- what negative states must remain visible;
- and what would justify taking the next slice.

A slice is therefore **not**:
- the full v0 roadmap,
- an excuse to launch a hosted platform,
- or a backlog dump that smears every good idea into “phase one”.

Think of it as the archive’s answer to:
**what is the first implementable thin plan that still proves the kernel is worthwhile?**

## Why this is the right next layer now
Fresh Rust signals still reward narrow, machine-usable, proving-ground-first work:
- Cargo build analysis is still prototype work around recorded build metadata and unstable `cargo report *` commands, which argues for thin local capture/diff/doctor slices rather than broad analytics products.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-build-analysis.html
- The build-dir-layout-v2 testing call still says downstream tools rely on unspecified internals and asks people to validate real workflows, which argues for migration-ready fixtures and explicit unsupported-state receipts.
  https://blog.rust-lang.org/2026/03/13/call-for-testing-build-dir-layout-v2/
- Cargo’s documented external-tool seams remain `cargo metadata`, `--message-format=json`, and custom subcommands, which supports small companion-first milestones.
  https://doc.rust-lang.org/cargo/reference/external-tools.html
- The 2025 State of Rust survey still shows debugging and resource usage as meaningful pain points, but it does not imply one grand product is missing; acceptance truth and better local evidence are still more grounded first builds.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- The 2026 debugging survey still frames the work as cross-debugger, cross-OS, visualizer, async, and Rust-expression-evaluation acceptance, which argues for fixture/replay corpus slices.
  https://blog.rust-lang.org/2026/02/23/rust-debugging-survey-2026/
- Cargo’s current development-cycle update still lists public/private dependencies, plumbing commands, and SBOM work as active or owner-hungry areas, while report commands and build-dir work are still moving. That combination argues for first slices that stay local, replayable, and honest about unstable or owner-missing seams.
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- The 2026 goals/flagships page keeps supply-chain work, safety-critical work, building-blocks work, and async parity in the flagship band, which reinforces that top contributions should graduate through proof-bearing milestones.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html
- crates.io and Rust Foundation security updates keep proving that package-boundary work is real but route-specific: Trusted Publishing is expanding, provenance/security tooling is becoming more concrete, and capability-analysis work is explicitly Cargo-subcommand-shaped.
  https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
  https://rustfoundation.org/media/strengthening-rust-security-with-alpha-omega-a-progress-update/
- The safety-critical writeup and Foundation strategy still point toward maintained evidence cards, shared ownership, and sustainable maintenance rather than giant certification products.
  https://blog.rust-lang.org/2026/01/14/what-does-it-take-to-ship-rust-in-safety-critical/
  https://rustfoundation.org/strategic-plan/

Together those signals say the next worthy repo layer is **thin-slice execution discipline for kernels**, not another broad synthesis note.

## What belongs in the first slice corpus
The first slice corpus should cover only the top-band kernels that already exist:
1. **Build-State Pack**
2. **Debug Acceptance Matrix**
3. **Package Intake Review Kit**
4. **Safety-Critical Readiness Cards**

It should still **exclude**:
- **Navigation / Defaults / Claims Commons** — because that candidate is still `hold`, and its blocker is renewal cadence, not milestone imagination.

## Required fields for a kernel slice
Every slice note should keep these sections visible:
1. **identity** — candidate, kernel, current verdict, slice name;
2. **why this slice first** — what this milestone proves better than adjacent options;
3. **deliverables** — exact files, commands, schemas, fixtures, or cards;
4. **acceptance checks** — what must work before the slice counts as done;
5. **proving grounds** — where it is tried first;
6. **imports and dependencies** — what it uses without pretending those seams are solved;
7. **postponed work** — what is explicitly not in slice 0;
8. **failure receipts** — what unsupported states or caveat notes must ship with it;
9. **next-slice trigger** — what evidence earns slice 1 / wider scope.

## The first slice family
### 1) Build-State Pack → `slice0: capture + diff + one doctor note`
The first slice should ship:
- one canonical session-pack schema,
- one capture path on stable Cargo seams,
- one diff command between two packs,
- one doctor note for a narrow class of rebuild/path surprises,
- and a minimal proving-ground corpus.

### 2) Debug Acceptance Matrix → `slice0: fixture corpus + tuple cards`
The first slice should ship:
- a tiny fixture family,
- one normalised session-pack shape,
- a tuple-card renderer,
- at least one yellow/red unsupported-state receipt,
- and one regression replay.

### 3) Package Intake Review Kit → `slice0: route profiles + review receipts + one incident drill`
The first slice should ship:
- route-profile definitions,
- a receipt schema,
- waiver/quarantine mechanics,
- one replayable incident drill,
- and optional capability-analysis import hooks without making them mandatory.

### 4) Safety-Critical Readiness Cards → `slice0: card schema + linter + small exemplars`
The first slice should ship:
- one card front-matter schema,
- one linter/validator,
- a tiny exemplar card pack,
- one freshness/owner diff surface,
- and explicit “does not prove” clauses.

## What these slice notes should teach
- a kernel brief is still too broad to code from directly;
- good first milestones are smaller than the repo tree they live in;
- the right early proof is usually **one better local decision**, not one prettier dashboard;
- and the archive should refuse widening until a slice proves itself in real proving grounds.

## Anti-goals
This layer should refuse:
- treating every kernel brief as a mandate to ship every subdirectory immediately;
- replacing thin slices with “phase one will include…” platform prose;
- hiding unstable imports or source caveats inside milestone language;
- or silently granting `hold` candidates a thin-slice plan anyway.

## Default interpretation for future revisions
Until the portfolio changes materially:
- this is a **kernel execution-sequencing** move, not a frontier promotion;
- the broad ladder is unchanged;
- live packets still govern verdict posture;
- kernel briefs still govern first honest repo shape;
- kernel slices now govern the **first bounded milestone inside that shape**; and
- future practical-build revisions should deepen the nearest slice before inventing another abstract “what should we build first?” note.
