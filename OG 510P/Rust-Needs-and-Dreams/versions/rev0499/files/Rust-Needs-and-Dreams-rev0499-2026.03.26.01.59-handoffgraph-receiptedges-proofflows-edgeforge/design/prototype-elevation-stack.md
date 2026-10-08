# Design: Prototype Elevation Stack (ScriptKit + Project Bootstrap + Workspace Environment + Tooling Contract)

## Goal
Treat the promotion from **single-file repro / script / quick prototype** to **reviewable Rust project** as a first-class ecosystem seam.

Rust is finally close to making single-file packages feel normal. That is a big win. But it also creates a new missing layer: the ecosystem still lacks a clean, reviewable way to decide when a one-file subject should stay a script and when it should be **lifted** into a package, repo, workspace, or supported product lane.

The worthy contribution here is therefore **not** another template generator, repo wizard, shell wrapper, or “just run cargo new for me” helper.
It is a thin `cargo elevate` / `elevate-pack/v0` layer that keeps these truths separate:
- **script / repro subject truth** — what the original one-file package actually was;
- **promotion decision truth** — why it should remain standalone or be lifted;
- **lift plan truth** — which manifest/package/workspace/environment structures were introduced;
- **equivalence / drift truth** — what behavior stayed the same, what widened, and what became intentionally different;
- **handoff truth** — what editors, CI, docs, support, or assistants may import next.

## Why this seam matters now
Fresh official Rust/Cargo signals line up unusually well:
- The active cargo-script goal says single-file packages matter for **bug reports, educational material, prototyping, and small utilities**. That means scripts are no longer just convenience folklore; they are a real public-facing Rust lane.
  https://rust-lang.github.io/rust-project-goals/2025h2/cargo-script.html
- The January 2026 program-management update says cargo script is especially valuable for **minimal bug reproducers and quick prototypes**, and stresses that being able to share one file or paste it into a Markdown block makes a practical difference.
  https://blog.rust-lang.org/inside-rust/2026/02/11/program-management-update-2026-01/
- Cargo’s unstable docs now make single-file packages explicit: they cannot be auto-discovered like `Cargo.toml`, they disallow `[workspace]`, `[lib]`, `[[bin]]`, `[[example]]`, `[[test]]`, and `[[bench]]`, and they use a hashed `$CARGO_HOME/target/<hash>` target dir plus a lockfile in `CARGO_TARGET_DIR`. That is strong evidence that scripts are intentionally a **different subject lane** from full projects.
  https://doc.rust-lang.org/cargo/reference/unstable.html
- The 2025 State of Rust survey says docs remain the canonical reference while editor/LLM-mediated workflows are rising. That increases the value of a machine-usable handoff from lightweight prototypes to real projects.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Rust’s 2025 vision work says users need better ecosystem navigation and a better “starter set” answer. A script or repro is often the earliest concrete subject from which that handoff should happen.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The March 20, 2026 challenges post recommends background- and domain-sensitive learning paths and says compilation friction remains a universal productivity tax. That makes “start tiny, then lift deliberately” more strategically important than another fixed template empire.
  https://blog.rust-lang.org/2026/03/20/rust-challenges/

## Current archive decision
The right contribution is **not**:
- a magical “promote this script” button that hides what changed;
- a universal starter-template answer;
- a repo generator that silently invents package/workspace/environment structure;
- or a publication shortcut that mistakes “runs once” for “ready to ship”.

It is a stack with explicit boundaries:
- [`design/scriptkit.md`](./scriptkit.md) owns one-file subject, frontmatter, target-dir/lockfile, and script-run truth.
- [`design/project-bootstrap-stack.md`](./project-bootstrap-stack.md) owns first reviewable starter realization.
- [`design/workspace-environment-stack.md`](./workspace-environment-stack.md) owns environment intent / realization / observation / handoff truth.
- [`design/tooling-contract-stack.md`](./tooling-contract-stack.md) owns discovery / package-selection / graph-plan / execution-evidence truth once a real project exists.
- A new **Prototype Elevation Stack** should own the explicit lift boundary above them.

## What a worthy contribution would look like in practice
### 1) Make “stay a script” a first-class outcome
A credible promotion stack must be able to say:
- this should remain a single-file repro,
- this should remain a local utility,
- this should become an in-repo automation subject,
- this should become a real Cargo package,
- this should become a workspace member or starter repo.

Without that, every improvement turns into premature repo growth.

### 2) Preserve what the original subject actually proved
When lifting a script, the stack should preserve:
- original file digest / subject id,
- parsed frontmatter and inferred defaults,
- lock / target-dir posture,
- run evidence or build-state links,
- issue/repro context when relevant.

Otherwise the “project” silently ceases to be the thing that originally worked or reproduced the bug.

### 3) Make introduced structure visible
A promotion layer must say what new structure was added:
- package name/version/license/readme assumptions,
- target layout (`src/main.rs`, `src/lib.rs`, tests/examples/benches, etc.),
- workspace membership or explicit non-membership,
- environment realization choices,
- CI/editor/bootstrap attachments.

That difference between **lifted** and **inherited from the original script** is the whole point.

### 4) Keep equivalence claims bounded
A lifted project may preserve:
- dependency graph,
- binary behavior,
- CLI shape,
- repro behavior,
- docs/example meaning,
- or only some subset.

The stack should be able to say:
- behavior preserved,
- behavior widened,
- behavior intentionally changed,
- equivalence not checked.

### 5) Prefer handoff artifacts over another generator empire
The stack should help:
- bug-report reproducers become reviewable fixtures,
- learning examples become starter repos,
- small internal scripts become governed in-repo automation,
- promising prototypes become bootstrap candidates,
- assistants/editors avoid hallucinating what got introduced.

That means bounded handoff artifacts matter more than another pile of templates.

## Suggested artifact family
A good epic candidate should add only a thin composition family:
- `elevate-subject/v0`
- `elevate-decision-report/v0`
- `elevate-lift-plan/v0`
- `elevate-equivalence-report/v0`
- `elevate-handoff/v0`
- `elevate-pack/v0`

### `elevate-subject/v0`
Defines:
- original script/prototype/repro identity,
- source lane (`single-file`, `embedded-frontmatter`, `markdown-repro`, `repo-script`, `other`),
- imported ScriptKit / manifest-truth attachments,
- known run/build evidence.

### `elevate-decision-report/v0`
Records:
- why the subject should stay small or be lifted,
- intended destination lane,
- constraints (teaching, repro fidelity, CI, publishing, support, reuse),
- explicit non-goals,
- review posture.

### `elevate-lift-plan/v0`
Records:
- introduced manifest/package/workspace structure,
- starter/bootstrap choice,
- environment/toolchain expectations,
- CI/editor/docs attachments,
- unresolved follow-ups.

### `elevate-equivalence-report/v0`
Records:
- what was checked for preservation,
- what widened or changed,
- lock/dependency/toolchain drift,
- behavior- or repro-sensitivity warnings,
- explicit `unchecked` zones.

### `elevate-handoff/v0`
A bounded summary for:
- `human-review`
- `bootstrap`
- `editor`
- `ci`
- `support`
- `agent`

The `agent` lane should stay capability-bounded and explicit about introduced structure.

### `elevate-pack/v0`
Thin bundle linking:
- original subject,
- decision report,
- lift plan,
- equivalence report,
- handoff summaries,
- imported script/bootstrap/workenv/tooling-contract attachments,
- checksums and generator identity.

## Shared success criteria
A strong prototype-elevation contribution should let a reviewer answer six questions quickly:
1. What was the original script/prototype/repro subject?
2. Why is it staying small or being lifted?
3. What new project/workspace/environment structure was introduced?
4. What behavior or repro property was checked for preservation?
5. What changed intentionally versus accidentally?
6. What may downstream consumers safely import next?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Ranked opportunity inside this stack
1. **single-file repro → reviewable fixture lane**
2. **single-file utility → in-repo automation lane**
3. **prototype → starter/bootstrap lane**
4. **starter/bootstrap → workenv/tooling-contract lane**
5. **support/docs/assistant consumer lane**

That order matters. The archive should not jump straight to a universal “promote to app” platform.

## Boundaries / non-goals
- not a replacement for Cargo’s built-in single-file package support,
- not a replacement for ScriptKit,
- not a replacement for `cargo new`,
- not a replacement for starter templates,
- not a replacement for workspace/environment managers,
- not a justification for silently mutating a repro into a product.

## Why this is an ecosystem contribution, not just repo polish
Rust is explicitly making single-file packages more real. Once that happens, the next missing question is inevitable:
> how does a lightweight one-file Rust subject become a reviewable long-lived project without losing the truth of what it originally was?

A real **Prototype Elevation Stack** would answer that question with bounded artifacts and explicit handoffs instead of folklore, template sprawl, or assistant guesswork.
