# Gap: Workspace environments, contributor onboarding, and agent-safe dev contracts

## What is missing
Rust still lacks a **portable, reviewable contract for workspace development environments** — an honest workspace environment contract rather than another pile of setup prose.

The raw ingredients exist, but they are split across too many layers:
- `rust-toolchain.toml` and rustup directory overrides pin toolchains, components, targets, and profiles;
- Cargo config is hierarchical and can be discovered from parent directories all the way up to `$CARGO_HOME`;
- rust-analyzer carries its own `cargo`/build-script override commands, extra args, extra env, and linked-workspace assumptions;
- modern developer-environment substrates like Dev Containers and Nix can realize reproducible environments, but they are intentionally language-agnostic;
- CI bootstraps, `just`/shell scripts, README snippets, and private dotfiles still carry a lot of the actual setup burden.

That means the missing problem is no longer “can someone script this repo setup somehow?”
The missing problem is:

**how does a Rust workspace declare, realize, observe, diff, and hand off its contributor environment without forcing every human, CI system, editor, or agent to rediscover it from prose and shell history?**

## Why this matters now
Current Rust signals line up around this seam more than they used to:
- the 2025 State of Rust survey says online documentation remains the preferred canonical reference while people increasingly learn with LLM tooling in the loop and editors with agentic support are on the rise;
- the same survey still surfaces resource usage and debugging among important productivity problems, which is a reminder that local setup and developer-loop reality matter, not just library APIs;
- Cargo 1.94 is actively discussing workspace and configuration discovery because stray parent manifests or `.cargo/config.toml` files can poison unrelated builds;
- Cargo 1.94 also reiterates that Cargo cannot be everything to everyone and that plugins matter;
- the Rust Foundation’s 2026–2028 strategy makes **Adoption & Innovation**, **Stable Infrastructure**, and **Sustainable Maintenance** first-class ecosystem priorities.

Taken together, that means workspace setup is no longer just a README ergonomics problem. It is an adoption, maintenance, and machine-consumption problem.

## The current seam is awkward
Today, a serious Rust workspace environment often gets reconstructed from a messy mixture of:
- `rust-toolchain.toml` or `rustup override` state,
- `.cargo/config.toml` files in multiple directories,
- editor-local rust-analyzer settings,
- Nix / devcontainer / Docker Compose / local shell setup,
- host-native dependency instructions,
- hand-run service bootstrap commands,
- copied environment variables,
- and tribal knowledge about which steps are optional, local-only, or security-sensitive.

That causes predictable failures:
1. **onboarding drift** — contributors do not know which steps are required versus convenience-only;
2. **CI parity drift** — local, CI, and remote-dev setups silently differ;
3. **editor drift** — rust-analyzer and other tools see a different workspace than the one builds actually use;
4. **native/provider drift** — linkers, SDKs, databases, and service emulators are installed differently across machines;
5. **secrets drift** — repos either overshare environment variables in docs or underspecify credential posture entirely;
6. **agent drift** — assistants and automation infer setup from stale docs and partial logs because there is no bounded machine-readable handoff.

The result is not merely annoyance. It is wasted maintainer time, hard-to-reproduce failures, and a growing amount of hidden environment state that survives only in private memory.

## What truths need to stay distinct
A worthy contribution here should keep these truths distinct but composable:

1. **subject / discovery truth**
   - which repo/workspace the environment is for;
   - what root, package-selection, and discovery assumptions apply;
   - what sub-workspaces or non-Cargo attachments are in or out of scope.

2. **declared environment intent**
   - required toolchain/targets/components;
   - required native providers, SDKs, or emulators;
   - expected services/tasks/editors;
   - optional lanes versus mandatory lanes.

3. **realization truth**
   - how the environment is realized:
     - host shell,
     - Dev Container,
     - Nix shell/flake,
     - CI image,
     - remote workspace,
     - other substrate.

4. **secret / credential posture**
   - which secret handles or credential sources are required;
   - whether values come from OIDC, keychain, `.env`, cloud profile, or local prompt;
   - which secrets are intentionally *not* serializable.

5. **override / precedence truth**
   - which parent-directory or local overrides materially changed the effective environment;
   - which editor-local command/arg/env settings changed Cargo-facing behavior;
   - which discovery rules were applied before any observation claim was made.

6. **observed environment truth**
   - what toolchain/config/editor/native/service facts were actually observed on one machine or run;
   - what mismatched or remained unavailable;
   - what is reproducible versus local-only.

7. **handoff truth**
   - what a new contributor may do next;
   - what CI may rely on;
   - what an editor may import;
   - what an assistant or agent may consume without seeing raw secrets or pretending uncertain setup is confirmed.

## What this should not become
This should **not** become:
- another universal environment manager;
- a Rust-only replacement for Dev Containers or Nix;
- a secret vault or `.env` sync product;
- another shell-task runner dressed up as infrastructure;
- a giant mega-schema that swallows toolchain, native-dependency, runtime-settings, and editor concerns whole;
- or a bot that mutates local machines while pretending it only exported facts.

The missing contribution is a **thin workspace-environment contract layer** above existing ingredients.

## What a worthy contribution would look like
The strongest shape is a **Workspace Environment Stack** that composes:
- **Toolchain Productization Stack** for toolchain / stdlib / target truth;
- **Native Dependency Kit** for external provider and link-plan truth;
- **Runtime Settings Kit** for config/env/default/source posture;
- **Credentials Kit** for secret-handle and credential-source posture;
- **Tooling Contract Stack** for workspace/discovery/scope truth;
- optional imports from **Support Envelope** when the workspace needs a contributor-facing support story.

A thin artifact family could look like:
- `workenv-brief/v0`
- `workenv-subject/v0`
- `workenv-intent/v0`
- `workenv-secret-profile/v0`
- `workenv-realization-report/v0`
- `workenv-observation-report/v0`
- `workenv-handoff/v0`
- `workenv-import-handoff/v0`
- `workenv-diff-report/v0`
- `workenv-pack/v0`

That would let teams answer questions like:
- “what does a contributor actually need to open this workspace?”
- “which parts are Rust toolchain facts versus native/service facts?”
- “how does the devcontainer or Nix realization differ from the host-shell realization?”
- “which editor assumptions are real and which are optional?”
- “what can an assistant safely consume without seeing raw credentials?”
- “what changed between last month’s working setup and this one?”

## Why this belongs in the archive now
This is the kind of contribution that can unlock many others without becoming another giant platform:
- better onboarding and archaeology,
- fewer “works on my machine” failures,
- clearer CI/local/editor parity,
- a cleaner place to attach toolchain/native/service/credential truth,
- and a bounded machine-readable handoff for the increasingly real human+agent development loop.

The archive already has many of the pieces.
What it does **not** yet have is the synthesis saying that Rust workspaces need an honest **environment contract** instead of more README setup prose, shell fragments, or private maintainer memory.

## References (signals)
- 2025 State of Rust survey:
  https://blog.rust-lang.org/2026/03/02/2025-State-Of-Rust-Survey-results/
- Cargo 1.94 dev-cycle note:
  https://blog.rust-lang.org/inside-rust/2026/02/18/this-development-cycle-in-cargo-1.94/
- Cargo config reference:
  https://doc.rust-lang.org/cargo/reference/config.html
- rustup overrides / `rust-toolchain.toml`:
  https://rust-lang.github.io/rustup/overrides.html
- rust-analyzer configuration:
  https://rust-analyzer.github.io/book/configuration.html
- Dev Container specification:
  https://containers.dev/implementors/spec/
- Nix flakes:
  https://nix.dev/concepts/flakes.html
- Rust Foundation strategic plan:
  https://rustfoundation.org/strategic-plan/
