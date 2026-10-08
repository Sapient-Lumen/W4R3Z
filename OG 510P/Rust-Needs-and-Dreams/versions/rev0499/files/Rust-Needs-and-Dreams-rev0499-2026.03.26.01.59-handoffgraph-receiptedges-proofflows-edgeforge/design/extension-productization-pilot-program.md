# Design: Extension Productization Pilot Program

## Why a pilot program is needed
Extension ecosystems are unusually good at hiding their real contracts inside host internals, install flows, blog posts, and gallery UX.
Rust already has serious extension ingredients — host-defined plugin surfaces, executable protocols, Wasm/plugin runtimes, WIT/component lanes, permission/capability systems, gallery installs, and foreign/mobile package sidecars — but those ingredients live at different authority layers and fail in different ways.
A credible plan therefore needs to decide:
- when host/extension identity is already enough,
- when capability and permission activation must be attached,
- when runtime-lane truth becomes unavoidable,
- when install/update/downgrade evidence is required,
- and which support/release/gallery/policy consumers justify graduation.

## Principles
1. **Start from host/product truth, not runtime ideology**
   - a pack that proves what a host actually supports is worth more than a new extension runtime pitch.
2. **Keep host surface, package truth, and capability truth separate**
   - they travel together in products, but they are not the same source of truth.
3. **Runtime kind is not implementation trivia**
   - executable-protocol, Wasm, component, native, and mobile/plugin package lanes differ materially and should stay explicit.
4. **Install and upgrade are part of the contract**
   - gallery/override/update/downgrade posture should graduate before sweeping ecosystem-support claims do.
5. **Support claims need receipts**
   - checked docs, version ranges, and migration notes should exist before “extension ecosystem ready” language does.
6. **Consumers import; they do not reinterpret**
   - release, support, gallery, atlas, and policy consumers should import artifacts instead of becoming the hidden source of truth.

## Common artifacts this program should drive
- `extension-lane-brief/v0` — declare which pilot lane is being exercised, host identity, scope, and non-goals.
- `extension-activation-brief/v0` — bounded summary of host version, runtime lane, package source, and activation settings actually used.
- `extension-capability-brief/v0` — explicit summary of what capabilities were available, granted, denied, or scope-bounded.
- `extension-install-receipt/v0` — install/override/register/update/downgrade result for the pilot lane.
- `extension-compat-handoff/v0` — what host/plugin/runtime/version compatibility conclusions the pilot supports.
- `extension-support-handoff/v0` — what release/support/gallery/policy consumers may conclude from the pilot and what remains out of scope.
- `extension-readiness-scorecard/v0` — not a fake maturity score; a lane-by-lane checklist showing which truths exist and which remain absent.
- `extension-product-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

The direct proposal-layer candidate for aggregating those artifacts is now [`proposals/epic-extension-productization-stack.md`](../proposals/epic-extension-productization-stack.md): a thin `cargo extensioncheck` / `extension-product-pack/v0` layer rather than a new host-owned framework or registry.

## Ranked pilot lanes

### 1) Single-host Wasm extension lane
**Why first:** it proves host identity, extension identity, runtime-kind posture, and shipped artifact truth without immediately requiring every exotic lane.

**Concrete scope**
- host identity and extension-point catalog,
- extension manifest and package/source identity,
- Wasm/component or host-Wasm runtime lane,
- basic lifecycle and invocation flow,
- checked install/override flow,
- checked docs/support examples that state the lane honestly.

**Graduation bar**
- the pack can explain what the host supports, what kind of extension artifact is installed, and how that extension was checked.

### 2) Capability / permission lane
**Why second:** once host and runtime truth exist, the next hidden source of pain is what extensions are actually allowed to do.

**Concrete scope**
- available versus granted capabilities,
- named permissions/scopes,
- denied-by-default operations,
- capability failures and success paths,
- drift when capability names or defaults change.

**Graduation bar**
- a reviewer can tell which operations were possible, which required activation, which were denied, and which docs/examples relied on them.

### 3) Versioned protocol-executable lane
**Why third:** this is where host/plugin upgrade pressure becomes impossible to ignore.

**Concrete scope**
- protocol-version truth,
- executable discovery/register/search/update posture,
- host upgrade versus plugin upgrade behavior,
- compatibility failures and migration notes,
- support docs for update choreography.

**Graduation bar**
- the pack can explain what broke or stayed compatible across host/plugin version movement and why.

### 4) Gallery / install / update / downgrade lane
**Why fourth:** extension ecosystems often fail operationally before they fail semantically.

**Concrete scope**
- gallery/repository/package source identity,
- install and override flows,
- update checks and downgrade posture,
- shipped package families and signatures/hashes where relevant,
- support/playbook import for install/update incidents.

**Graduation bar**
- a reviewer can tell what was installed, from where, how it was updated or overridden, and what downgrade or rollback story exists.

### 5) Mixed-runtime or multi-package lane
**Why fifth:** this is where the stack proves it matters above any single runtime dogma.

**Concrete scope**
- multiple runtime kinds or package families in one host,
- host-package plus runtime-lane attachments,
- capability/profile differences by lane,
- support-policy differences by lane,
- atlas/learning comparison imports.

**Graduation bar**
- the pack can explain how multiple extension families coexist without pretending they share one fake contract.

## What to defer
- a universal extension registry;
- one mega extension framework owning host, runtime, package, gallery, and support all at once;
- policy-first hard gates before evidence lanes exist;
- benchmark theater about one runtime being faster without host/install/support truth;
- vague “extensible platform” claims that skip capability, install, and compatibility posture.

## Immediate archive consequences
- Treat **Plugin Surface Kit** as the anchor of a broader extension-productization seam rather than an isolated plugin/report idea.
- Treat **Runtime Capability + Wasm Component + Host Package + Distribution Contract** as the product-boundary half of the story instead of letting Plugin Surface silently absorb them.
- Treat **Support Envelope + DocProof** as downstream import lanes that should consume lower-layer extension evidence instead of retelling it.
- Keep the stack-level candidate thin: later revisions should prefer imported lower-layer evidence and bounded handoffs over another host-specific mega manifest or extension-platform rewrite.

## Read this together with
- `design/extension-productization-stack.md`
- `design/plugin-surface-kit.md`
- `design/runtime-capability-kit.md`
- `design/wasm-component-kit.md`
- `design/host-package-kit.md`
- `design/distribution-contract-stack.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
