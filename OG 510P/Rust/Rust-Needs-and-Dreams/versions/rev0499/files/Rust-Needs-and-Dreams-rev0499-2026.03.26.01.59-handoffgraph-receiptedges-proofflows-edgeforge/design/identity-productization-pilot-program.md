# Design: Identity Productization Pilot Program (Supported Auth → Protected Surface Attachments → Runtime Activation → Support Truth → Transition & Consumers)

## Goal
Turn the **Identity Productization Stack** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable contribution that would materially improve Rust’s identity/auth/session story?

The pilot program should not chase a universal “auth platform.” It should sequence the contribution so each lane proves something concrete before the next lane expands scope.

## Why a pilot program is necessary
Identity is one of the easiest places for ecosystems to mistake glue code for product truth.
Rust already has serious ingredients, but they sit at different layers and fail in different ways. A credible plan therefore needs to decide:
- when supported-auth and principal truth are already enough,
- when protected routes/resources/commands must be attached,
- when runtime provider and secret activation become part of the contract,
- when support/docs truth is required,
- and which downstream consumers justify graduation.

## Principles
1. **Start where the support gap is painful and common**
   - declared auth methods, principal models, and session/token posture are earlier wins than a grand unified auth platform.
2. **Respect multiple auth families**
   - passwords, passkeys, sessions, bearer tokens, API keys, OAuth2/OIDC federation, and machine credentials are all real lanes.
3. **Keep identity truth and protected-surface truth distinct**
   - route/RPC/command requirements should attach to identity artifacts, not replace them.
4. **Runtime activation is part of the auth story**
   - issuer URLs, cookie keys, callback URLs, session stores, verifier settings, and secret sources change what was actually shipped.
5. **Partial truth is still useful**
   - a pack that knows supported auth methods and principal shape is still valuable even before provider migration and browser-support lanes are mature.
6. **Consumers import; they do not redefine**
   - release, support, policy, service, client, and atlas tooling should import the identity stack rather than reinterpret auth support from scratch.

## Common artifacts this program should drive
- `identity-lane-brief/v0` — declare which identity lane is being exercised, scope, provider families, and non-goals.
- `identity-escalation-policy/v0` — rules for when a subject must move from declared auth truth to protected-surface, runtime, support, or transition evidence.
- `identity-correlation-budget/v0` — bounded rules for correlating identity surface, protected routes/resources, runtime activation, and support claims without pretending universal inference.
- `identity-readiness-scorecard/v0` — not a fake maturity number; a lane-by-lane checklist showing which truths exist and which remain absent.
- `identity-pilot-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

## Ranked pilot lanes

### 1) Supported-auth + principal lane
**Why first:** it hits a common pain point with the least framework coercion.

**Concrete scope**
- supported auth methods,
- public principal and claims schema,
- session/token/cookie posture,
- logout/refresh/reauth/recovery declarations,
- checked positive and negative flow evidence.

**Graduation bar**
- the pack can explain which auth methods are official, what the public principal model is, and what was actually checked.

**What success looks like**
- one `identity-surface/v0` and one `auth-check-report/v0` that work for a real app or service without forcing a framework rewrite.

### 2) Protected-surface attachment lane
**Why second:** auth support matters most where it attaches to actual product surfaces.

**Concrete scope**
- route / RPC / resource / command requirement maps,
- admin/operator/machine-only distinctions,
- claim/scope/role attachments,
- unsupported or advisory-only markings,
- service/schema/client import references.

**Graduation bar**
- the pack can show which protected surfaces exist and which access conditions they import, without making route metadata the identity source of truth.

### 3) Runtime activation + secret posture lane
**Why third:** once deployed behavior enters the story, configuration and credentials become part of the contract.

**Concrete scope**
- issuer / audience / callback / discovery settings,
- cookie names, flags, and key sources,
- session-store/backend selection,
- passkey relying-party parameters,
- secret-source and rotation posture across environments,
- explicit unknown/inferred markers.

**Graduation bar**
- a release or support consumer can tell which provider and secret posture was actually activated without scraping deployment scripts and env-var tables.

### 4) Support/docs/platform-behavior lane
**Why fourth:** auth is full of browser/runtime/provider caveats that otherwise live in issue threads and setup docs.

**Concrete scope**
- browser/platform/runtime assumptions,
- docs.rs / guide / example coverage,
- supported provider families and support levels,
- cookie/browser/passkey caveats,
- source-build versus release-artifact differences,
- checked setup and denial transcripts where appropriate.

**Graduation bar**
- users and operators can tell what identity behavior is officially supported and what the docs actually prove.

### 5) Transition + downstream-consumer lane
**Why fifth:** this is where the stack proves it matters after greenfield implementation.

**Concrete scope**
- provider swaps,
- password → passkey transitions,
- role/scope/claim model changes,
- session-store or token-verifier changes,
- release/support/policy/incident consumer imports,
- archaeology diffs for “what changed between shipped identity states.”

**Graduation bar**
- the stack can answer boring real-world change questions without bespoke team memory.

## What to defer
- a mega-auth framework,
- a hosted identity-control plane,
- one universal policy language or token/session abstraction,
- hard policy gates before the evidence lanes exist,
- “AI auth copilots” that claim universal understanding without stable artifacts.

## Proposal-layer promotion
The direct proposal-layer companion to this rollout is now [`proposals/epic-identity-productization-stack.md`](../proposals/epic-identity-productization-stack.md). The pilot should stay the ranked execution path, while the epic should own the stack-level boundary, artifact family, and consumer handoff language.

## Immediate archive consequences
- Promote **Identity Surface Kit** from an isolated Tier 1/2 note to the anchor of a clearer frontier-adjacent stack.
- Treat **Runtime Settings Kit**, **Credentials Kit**, and **Support Envelope Kit** as the adjacent truth families that make identity support real.
- Treat **Service Surface Kit**, **Command Surface Kit**, **Schema Contract Kit**, and **Client App Surface Kit** as importing attachment lanes rather than new identity authorities.
- Add a specific amnesia resistor so later revisions cannot collapse supported auth methods, principal/claim truth, protected surfaces, runtime activation, support/docs truth, and migration evidence into one note.

## Read this together with
- `design/identity-productization-stack.md`
- `design/identity-surface-kit.md`
- `design/runtime-settings-kit.md`
- `design/credentials-kit.md`
- `design/service-surface-kit.md`
- `design/command-surface-kit.md`
- `design/schema-contract-kit.md`
- `design/client-app-surface-kit.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
- `proposals/epic-identity-productization-stack.md`
