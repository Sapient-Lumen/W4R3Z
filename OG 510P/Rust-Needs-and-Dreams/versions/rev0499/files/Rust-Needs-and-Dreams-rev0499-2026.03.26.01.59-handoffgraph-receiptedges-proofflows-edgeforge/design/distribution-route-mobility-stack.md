# Design: Distribution-Route Mobility Stack (Publisher & Source Identity + Distribution Contract + Airgap + lifecycle/continuity imports)

## Goal
Treat **Publisher & Source Identity**, **Distribution Contract**, **Airgap**, and selected **Fork Continuity / Sunset Transition / Ecosystem Incident Response** imports as one shared **Distribution-Route Mobility Stack** for the moments when Rust artifacts **change homes, add homes, or narrow homes**.

The missing contribution is **not** another registry implementation, another mirror manager, another vendoring helper, or another “just publish here instead” migration assistant.
It is a portable, reviewable stack that keeps these truths distinct while letting them compose when a Rust subject moves between route classes:
- **route subject truth** — which package/workspace/release line the route story is about;
- **route class truth** — whether the current lane is crates.io, an alternate registry, an exact-copy replacement/mirror, a local registry, a vendored directory source, a git/path development lane, or a mixed bridge;
- **sameness/divergence truth** — whether the route claims exact-copy equivalence, local-only carry, or intentional divergence;
- **publish/consumer constraint truth** — what Cargo or crates.io rules apply to that route;
- **route-change intent truth** — why the route changed: continuity, internal policy, offline/bootstrap posture, emergency containment, or ordinary publication evolution;
- **compatibility and handoff truth** — what downstream users may conclude, migrate to, or ignore.

That separation matters because Rust now has many official route types and each of them carries different semantics. The ecosystem has the pieces, but not yet a compact, reusable control layer for **route motion itself**.

## Why this seam matters now
Current Rust signals are unusually aligned here:
- Cargo’s registries docs make alternate registries a first-class route and let `package.publish` restrict where a crate may be published; recent release notes also say `cargo publish` will use an alternate registry by default when it is the only allowed publish target.
- Cargo’s source-replacement docs explicitly say replacement sources must be **exact copies**, may not add new crates, and are not the same thing as patching or a private registry.
- Cargo’s dependency docs say crates.io packages cannot depend on code published outside crates.io (except ignored dev-dependencies), while the **multiple locations** feature lets local `git`/`path` work bridge to a registry version later.
- `cargo vendor` says vendored sources are read-only and directs actual modifications toward `[patch]` or local `path` dependencies, which means “offline/local copy” and “local divergent carry” already have different official semantics.
- crates.io’s January 2026 development update expanded Trusted Publishing and Trusted-Publishing-only mode, which makes publish-home and publish-authority transitions more explicit and reviewable.
- the Rust Foundation’s 2026–2028 strategy explicitly names **signed crates** and **official mirrors**, which means route plurality is now part of Rust’s infrastructure strategy rather than a side topic.
- Rust’s March 2026 challenges post says ecosystem navigation still depends too much on tacit knowledge and choice paralysis; route changes hidden in `.cargo/config.toml`, CI, or a release note make that worse.

Taken together, these signals say ideal Rust now needs a **stack-level route-mobility layer** between source identity and consumer install truth.

## What adjacent layers own
### Publisher & Source Identity Stack
[`design/publisher-source-identity-stack.md`](./publisher-source-identity-stack.md) owns:
- claim/project identity;
- publish-authority facts;
- current source identity;
- and the distinction between alternate registries, source replacement, vendoring, and local registries.

Its question is:
> what is this source/home/authority posture **right now**?

### Distribution Contract Stack
[`design/distribution-contract-stack.md`](./distribution-contract-stack.md) owns:
- what candidates a consumer actually saw;
- which install path was selected;
- what verification happened;
- and what ended up on disk.

Its question is:
> what acquisition/install path did the consumer actually take?

### Airgap Kit
[`design/airgap-kit.md`](./airgap-kit.md) owns:
- restricted-network topology;
- offline/bootstrap posture;
- exact-copy mirror posture;
- and local-registry / vendored preparation.

Its question is:
> under constrained network assumptions, what route types were actually available?

### Fork Continuity / Sunset Transition / Ecosystem Incident Response
These layers own:
- why a project is continuing without transfer;
- why support is narrowing or ending;
- or why an emergency containment/reissue path is in effect.

Their shared question is:
> why is the route changing, and what governance/lifecycle claim does that change support?

### Distribution-Route Mobility Stack
This stack owns:
- route-state comparison and route-change records;
- route-class transitions or multi-route overlays;
- exact-copy versus divergent-carry posture;
- Cargo/crates.io rule imports that meaningfully constrain the route change;
- and bounded handoffs into continuity, incident, install, and airgap consumers.

Its question is:
> when a Rust artifact changes homes or adds/removes homes, **what exactly changed and what did not**?

Design rule: **route movement is not endorsement.**
A new registry, mirror, vendor directory, or local patch lane may be appropriate without implying project blessing, ecosystem preference, or drop-in compatibility.

## What the stack should make possible
A reviewer should be able to answer all of these from one linked route bundle, without reverse-engineering `.cargo/config.toml`, CI secrets, mirror docs, or release notes:
1. Which route classes are in scope now, and which one used to be primary?
2. Is the new route exact-copy, local-only, or intentionally divergent?
3. Which Cargo/crates.io constraints matter to this move?
4. Does the move change publish authority, distribution topology, consumer compatibility, or all three?
5. Is the route addition temporary, parallel, successor-oriented, offline-only, or intended as the new long-term home?
6. Which downstream consumers should import the change: continuity, incident, install, airgap, trust, or sunset?

If the stack cannot answer those six questions, it is not yet ecosystem infrastructure.

## Stack boundary relative to Fork Continuity
This stack must stay clearly distinct from **Fork Continuity Stack**.

Fork continuity is about:
- whether a project continues without ownership transfer,
- how identity/authority changed,
- and what compatibility/migration story users should hear.

Route mobility is about:
- how publication/distribution homes changed,
- whether the move claims exact equivalence or divergence,
- and which official Cargo/crates.io route semantics constrain the change.

A continuation often **uses** route mobility, but route mobility must not silently infer continuity legitimacy.

## Recommended execution posture
The stack now needs a shared execution layer, conceptually captured as a thin `cargo route` / `route-pack/v0` bundle with the following proof order:
1. **publish-home lane first**
   - crates.io vs alternate-registry selection, `package.publish` restrictions, default-registry behavior;
2. **equivalence lane second**
   - exact-copy mirror/source-replacement truth versus divergent carry truth;
3. **bridge lane third**
   - local `path`/`git` plus registry-version multiple-location bridges;
4. **offline and restricted-network lane fourth**
   - vendored/local-registry/mirror imports without pretending they are the same thing;
5. **continuity/incident/sunset handoff lane fifth**
   - route changes that matter because the project is moving, containing, narrowing, or rehoming.

That ordering is intentional.
The archive should not jump straight to another registry server, publish proxy, or route dashboard.
It should first prove that ordinary Rust route changes can carry enough structured truth to make **home changes reviewable**.

## Design principles
1. **Current route truth before route-change prose.** Import the actual route class first.
2. **Equivalence before convenience.** Mirrors, vendoring, and local carries should not collapse into “local copy”.
3. **Publish constraints are first-class.** crates.io publication rules and registry restrictions materially shape route choices.
4. **Local-only routes stay visible.** A local `[patch]`, vendored tree, or path override must not masquerade as an ecosystem-visible home.
5. **Parallel homes are not one story.** crates.io + mirror + alternate-registry + local vendor may coexist without identical promises.
6. **Authority and route are related but distinct.** Trusted Publishing or owner changes do not by themselves tell you the route class.
7. **Continuity/lifecycle imports must stay bounded.** Route motion should feed succession, fork, incident, or sunset notes rather than replace them.
8. **Honest incompleteness is allowed.** Unknown or policy-private route details should remain representable.
9. **Thin consumers later.** Dashboards, release pages, assistants, and policy gates should consume the stack, not redefine it.

## What an epic contribution would look like in practice
A serious contribution here would:
- reuse Cargo-native route classes instead of inventing a new taxonomy detached from Cargo semantics;
- make `crates.io` publication, alternate registries, exact-copy mirrors, vendored sources, local registries, and local development bridges comparable without flattening them;
- preserve the difference between **same bytes elsewhere** and **different bytes carried locally**;
- and produce bounded handoffs that continuity, incident, install, and trust layers can actually consume.

## Anti-goals
Do not turn this stack into:
- one universal registry chooser,
- one private-registry product pitch,
- one forced migration engine,
- one giant route score,
- one source-replacement wrapper that hides semantics,
- or one continuity policy that silently decides which home is legitimate.

The stack is a **route-change review boundary**, not another distribution empire.
