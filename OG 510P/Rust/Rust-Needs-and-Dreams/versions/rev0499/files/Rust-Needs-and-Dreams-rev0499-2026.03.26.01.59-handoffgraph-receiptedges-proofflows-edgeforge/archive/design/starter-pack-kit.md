# Design: Starter Pack Kit (`cargo starter`, `starter-pack/v0`)

## Goal
Define a portable contract for declaring, deriving, checking, diffing, and refreshing **starter repos** for Rust projects.

This should help answer questions like:
- which domain/lane/adoption decision this repo starts from,
- which workspace/environment/productization truths it imports,
- which files are canonical versus generated versus overlay-local,
- what policy/support/release posture it begins with,
- how local overlays are expressed without hard forking the base starter,
- and how freshness and refresh are tracked over time.

This should **not** replace `cargo new`, `cargo init`, `cargo-generate`, framework-specific bootstrap tools, or ordinary git templates.
It should make them easier to combine honestly.

## References (signals)
- Rust’s 2025 vision work explicitly says users need help navigating the crates.io ecosystem and says there is no clear place to get advice on a good “starter set” of crates.
  https://blog.rust-lang.org/2025/12/19/what-do-people-love-about-rust/
- The 2025 State of Rust survey says online documentation remains the preferred canonical reference while LLM/editor workflows are rising.
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- `cargo new` intentionally creates a simple template with a manifest, sample source file, and VCS ignore file.
  https://doc.rust-lang.org/cargo/commands/cargo-new.html
- Cargo 1.71 added automatic inheritance of workspace fields when running `cargo new` / `cargo init`, which means scaffolding now participates in workspace governance.
  https://doc.rust-lang.org/cargo/CHANGELOG.html
- `cargo-generate` helps users start new Rust projects from pre-existing git repositories as templates and points users to a GitHub topic to discover templates.
  https://docs.rs/crate/cargo-generate/latest
- Tauri’s `create-tauri-app`, Dioxus’s `dx new`, Cargo Lambda’s `cargo lambda new`, and Espressif’s `esp-generate` show that Rust already has multiple real domain bootstrap paths.
  https://v2.tauri.app/start/create-project/
  https://dioxuslabs.com/learn/0.7/tutorial/new_app/
  https://www.cargo-lambda.info/commands/new.html
  https://docs.espressif.com/projects/rust/book/getting-started/tooling/esp-generate.html
- Rust’s 2026 flagships explicitly call out public/private dependencies and SBOM generation, meaning starter repos increasingly encode supply-chain posture from day one.
  https://rust-lang.github.io/rust-project-goals/2026/flagships.html

## Design principles
1. **Imports stay visible.** A starter repo should declare which atlas/adoption/productization/workenv/policy inputs shaped it.
2. **The generated working tree is not the only truth.** The starter pack must outlive any one rendered repo snapshot.
3. **Base starter and local overlay stay separate.** Teams should not need to hard-fork every upstream starter to add local CI, policy, or release details.
4. **File ownership must be explicit.** Humans need to know which files are canonical, generated, local, or advisory.
5. **Freshness is part of the contract.** A starter repo that has not been re-checked should age into explicit staleness.
6. **Recommendation and realization stay distinct.** Atlas / Adoption Decision choose lanes; Starter Pack realizes one of those lanes as a repo.
7. **Adapters are first-class, not a design failure.** Direct file rendering, `cargo new`, `cargo-generate`, and delegated domain bootstrappers should be recordable without pretending one renderer owns the whole ecosystem.
8. **Do not hide environment and policy posture.** Toolchain, native-dependency, lint, CI, and release assumptions should be imported or declared rather than buried in boilerplate.
9. **Derived docs and assistant contexts must remain traceable.** Starter guides and machine contexts should point back to the starter-pack artifacts.

## Artifact family
- `starter-subject/v0` — starter identity and target use
- `starter-sources/v0` — imported atlas/adoption/productization/workenv/policy/support sources
- `starter-layout/v0` — intended workspace/package/file structure
- `starter-render-plan/v0` — intended render path, bounded renderer parameters, delegated bootstrapper choice if any, and expected file-ownership map
- `starter-env-profile/v0` — imported or declared workenv/toolchain/native/bootstrap assumptions
- `starter-policy-profile/v0` — lint/CI/publish/supply-chain posture
- `starter-support-profile/v0` — docs/examples/tests/support expectations
- `starter-overlay/v0` — local overlays or substitutions against the base starter
- `starter-check-report/v0` — what was rendered and validated
- `starter-render-report/v0` — actual renderer/adapter/version, delegated steps, produced files, required follow-up edits, and known losses or skips
- `starter-refresh-report/v0` — what changed when imports were re-checked
- `starter-pack/v0` — bundle tying the pieces together

### 1) `starter-subject/v0`
Defines what is being bootstrapped.

Required ideas:
- project domain (`cli`, `service`, `library`, `embedded`, `desktop`, `plugin`, `sdk`, etc.)
- package/workspace posture (`single-crate`, `workspace`, `workspace-with-tools`, `polyglot-host`, etc.)
- intended audience (`tutorial`, `team-internal`, `public-starter`, `regulated`, `experimental`)
- success criteria / anti-goals
- freshness owner and review class

### 2) `starter-sources/v0`
Records what the starter imports.

Required ideas:
- referenced atlas lane / adoption decision ids where present
- referenced productization stack or domain-kit ids where present
- referenced workspace-environment / tooling-contract ids where present
- referenced policy, support, release, or trust inputs where present
- explicit local-only additions
- missing or intentionally omitted imports

Design rule: imports should remain references where possible, not flattened copies.

### 3) `starter-layout/v0`
Declares the intended repository shape.

Required ideas:
- workspace/package layout
- bins/libs/examples/tests/xtask posture
- default package-selection posture
- directory conventions
- generated versus hand-maintained paths
- optional foreign-language or asset attachments

### 4) `starter-render-plan/v0`
Describes how the starter is intended to be realized.

Required ideas:
- renderer class (`direct-files`, `cargo-new`, `cargo-generate`, delegated domain bootstrapper)
- bounded renderer parameters and prompts
- which imported starter truths are consumed before or after rendering
- expected file ownership after the render step
- allowed normalization or overlay application
- required checks before the result counts as a valid starter derivation

Design rule: renderer choice is part of the starter’s practical contract, but it must not become the new source of truth over the imported starter artifacts.

### 5) `starter-env-profile/v0`
Describes the starter’s environment realization posture.

Required ideas:
- toolchain and edition posture
- `.cargo/config.toml` / workspace-config posture
- native dependency posture
- devcontainer / Nix / shell bootstrap posture
- secret placeholder posture
- optional `workenv-pack/v0` or related imports

Design rule: do not flatten environment truth into generic template notes.

### 6) `starter-policy-profile/v0`
Describes the quality and supply-chain posture the starter intends.

Possible contents:
- lint / formatting posture
- CI/test/docs posture
- package-admission or public/private-dependency posture
- SBOM / release / signing hooks if present
- publishing restrictions
- explicit waivers or intentionally deferred controls

### 7) `starter-support-profile/v0`
Describes what guidance/support the starter intends to ship with.

Possible contents:
- README or getting-started guide posture
- checked examples or demo commands
- docs.rs / rustdoc posture when relevant
- issue/support template posture
- support-envelope imports where present

### 8) `starter-overlay/v0`
Lets organizations or products customize a base starter without forking it blindly.

Required ideas:
- base starter reference
- allowed substitutions/additions/removals
- org-local policy/runtime/release additions
- forbidden drift zones
- expiration / review owner

### 9) `starter-check-report/v0`
Records what was actually derived and validated.

Possible contents:
- rendered file set summary
- file ownership summary
- imported-source freshness summary
- CI/docs/example validation results
- environment/bootstrap validation results
- policy/release/support drift findings
- unresolved placeholders or required local follow-up

### 10) `starter-render-report/v0`
Records what renderer or adapter actually ran.

Possible contents:
- renderer/adapter identity and version
- delegated bootstrapper summary where relevant
- produced file/class summary
- required local follow-up edits
- skipped, opaque, or lossy steps
- freshness timestamp and operator

Design rule: render reports explain the realized repo; they do not replace starter subject/source/layout truth.

### 11) `starter-refresh-report/v0`
Captures what changed when upstream starter inputs were rechecked.

Possible contents:
- changed imports or upstream artifact ids
- file-level or policy-level diffs
- newly stale imports
- required manual migration notes
- overlay conflicts

### 12) `starter-pack/v0`
Bundle format containing:
- `starter-subject/v0`
- `starter-sources/v0`
- `starter-layout/v0`
- `starter-env-profile/v0`
- optional `starter-policy-profile/v0`
- optional `starter-support-profile/v0`
- optional `starter-overlay/v0`
- one or more `starter-check-report/v0`
- optional `starter-refresh-report/v0`
- optional raw attachments: template manifests, rendered file inventories, CI transcripts, docs/example transcripts, and imported upstream ids

## Reference UX: `cargo starter`
- `cargo starter init`
- `cargo starter derive`
- `cargo starter check`
- `cargo starter diff`
- `cargo starter refresh`
- `cargo starter overlay`
- `cargo starter pack`

`cargo starter` should begin as an explainer / derivation / refresh layer.
It should not pretend to be the one true template engine.

## How this works in practice
### Conservative CLI / internal-tool lane
A starter pack could import:
- an atlas/adoption lane for CLI tools,
- a workspace layout with one binary crate and one support crate,
- a runtime/settings posture,
- lint/test/docs defaults,
- and a small checked getting-started guide.

The point is not only to render files. It is to keep visible **why this starter looks the way it does** and how to refresh it later.

### HTTP/service lane
A service starter pack could import:
- a service productization lane,
- a workenv pack for local dev/bootstrap,
- runtime settings and observability defaults,
- docs/support posture,
- and package-admission/release hooks.

That makes the service starter repo a reviewable derivative of real productization inputs rather than a one-off framework quickstart.

### Embedded or no_std lane
A starter pack can still use an external template tool under the hood.
The value of the kit is not replacing those tools; it is recording provenance, environment posture, target/runtime assumptions, and refresh boundaries.

## Suggested phased execution
### Phase 1: Starter core
- lock down subject / sources / layout / ownership / check artifacts
- support one conservative CLI starter and one HTTP/service starter
- prove refresh/diff against changed upstream inputs

### Phase 2: Overlay-aware starters
- add org overlays
- keep forbidden-drift zones explicit
- import workenv/policy/support artifacts by reference

### Phase 3: Machine-facing derivations
- render bounded assistant contexts
- render human quickstart guides
- emit starter freshness reports for docs/platform teams

## Non-goals
This kit should **not**:
- replace `cargo new` or `cargo-generate`;
- standardize one universal project layout;
- choose crates by itself without imported atlas/adoption inputs;
- absorb workspace-environment, policy, or productization stacks into one mega-format;
- turn a rendered repo snapshot into the only source of truth;
- or hide local organizational judgment behind a fake official starter.

## Overlap boundaries
- **Atlas / Adoption Decision** own lane selection and recommendation truth.
- **Workspace Environment Stack** owns environment intent and realization posture; Starter Pack imports it.
- **Tooling Contract / Workspace Governance** own workspace discovery/scope truth; Starter Pack consumes those truths when rendering repo layouts.
- direct or delegated renderer choice is implementation truth owned by Starter Pack’s render-plan/report artifacts, not by Atlas, Adoption Decision, or the domain stacks themselves.
- **Productization stacks** own domain-specific runtime/support/release truths; Starter Pack realizes them into a beginning repo.
- **Policy / Package Admission / Release Truth / Support Envelope** remain separate imports; Starter Pack does not collapse them into one “best practice” badge.

Starter Pack Kit exists because Rust increasingly needs a first-class answer to: **“show me the repo we should start from, and make that answer reviewable and refreshable.”**
