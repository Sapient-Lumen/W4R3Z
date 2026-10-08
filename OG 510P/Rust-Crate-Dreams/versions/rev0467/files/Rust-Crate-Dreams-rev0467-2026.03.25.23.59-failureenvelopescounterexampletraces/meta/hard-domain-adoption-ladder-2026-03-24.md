# Hard-domain adoption ladder — 2026-03-24

This note answers a planning question the archive now needs more often:

> How should a worthy crate scale its claims from casual exploration up to hard domains like air-gapped, mixed-language, embedded, and safety-critical work?

Current Rust sources still say the ecosystem is uneven across domains.
That means a crate’s support story should usually be described as an **adoption ladder**, not a binary “supports this domain” badge.

## Main judgment

The archive should default to five adoption tiers.
A crate can be strong at one tier and still not deserve a higher-tier support claim.

## Tier 1 — `explore`

Audience:
- solo developers, prototypes, first evaluation.

What the crate should provide:
- a quick-start surface,
- a bounded decision brief,
- one honest non-goal note.

What not to claim:
- organizational repeatability.

## Tier 2 — `team_default`

Audience:
- a small or medium team trying to standardize on a default stack.

What the crate should provide:
- replayable starter-set packets,
- scoped evidence files,
- obvious manual-review triggers.

What not to claim:
- offline, long-lived, or regulated readiness.

## Tier 3 — `shipping_baseline`

Audience:
- production teams with CI, release, and support obligations.

What the crate should provide:
- doctor outputs,
- issue bundles,
- drift policies,
- role coverage and gap visibility.

What not to claim:
- that local or CI success alone proves all environments are covered.

## Tier 4 — `restricted_or_offline`

Audience:
- air-gapped enterprise, mixed-language integration, embedded fleets, native-heavy deployments.

What the crate should provide:
- external prerequisite reports,
- native or target provenance,
- exportable manifests,
- fallback and off-ramp instructions.

What not to claim:
- that standard hosted surfaces settle support questions.

## Tier 5 — `regulated_or_evidence_heavy`

Audience:
- safety-critical and certification-heavy teams, or any team with strong evidentiary review.

What the crate should provide:
- explicit claim ceilings,
- narrow scope boundaries,
- durable witnesses and review packets,
- decomposition guidance about what is and is not covered.

What not to claim:
- broad compliance or certification outcomes it does not own.

## Mapping the current frontier to the ladder

### P-0509 Pathfinder
- Tier 1–2: starter-set packets
- Tier 3: replay / watch / reconsideration
- Tier 4: prerequisite-aware packets for offline/native/mixed-language lanes
- Tier 5: boundary-oriented choice packets for safety-critical or evidence-heavy teams

### P-0536 Crate Knowledge Pack
- Tier 1–2: pinned citations and answer packs
- Tier 3: query-support matrices and claim tracing
- Tier 4: environment-conditioned availability and importable bundle surfaces
- Tier 5: strict answerability / refusal boundaries and evidence-class labeling

### P-0486 Debuggability Support
- Tier 1–2: local session capability witnesses
- Tier 3: packaged artifact / backend / session-family packets
- Tier 4: remote/container/embedded/post-mortem variants
- Tier 5: claim ceilings that separate symbol presence, inspection, async visibility, and expression evaluation

### P-0472 Docs.rs Build Parity
- Tier 1–2: local preflight + parity gaps
- Tier 3: reproducible issue bundles
- Tier 4: hosted/local/native prerequisite mismatch explanations
- Tier 5: strict refusal to treat docs.rs success as whole-environment support proof

### P-0484 Toolchain & Target Support
- Tier 1–2: basic target-route reporting
- Tier 3: exercised-environment receipts
- Tier 4: external prerequisite and host-target split bundles
- Tier 5: scope boundaries that avoid fake “supports target X” claims

### P-0058 Native Deps
- Tier 1–2: local prerequisite detection
- Tier 3: build farm / CI diagnosis
- Tier 4: offline, vendored, and mixed-language provenance
- Tier 5: explicit ABI/provenance claim ceilings

## Why this matters for ranking

This ladder does **not** mean every hard-domain crate should jump to the top of the frontier.
It means the current top crates should be judged partly by how well they scale up the ladder.

That is why control-plane crates still dominate.
They are the ones most likely to help multiple domains without lying about maturity.

## Guardrail

Before promoting a sector-specific proposal, ask:
1. which ladder tier does it actually serve today?
2. what artifacts let it move up one tier honestly?
3. is the sharper missing seam still pathfinder, knowledge, debug, docs parity, target support, dependency transition, or native provenance instead?
