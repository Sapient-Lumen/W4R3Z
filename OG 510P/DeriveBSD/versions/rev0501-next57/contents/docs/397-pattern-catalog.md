# DeriveBSD pattern catalog (how we prevent design sprawl)

**Tier:** A (Core meta-doc)  
**Profiles:** A, B, C, D  
**Pillars:** reproducibility, isolation, supply-chain, operability
**Patterns:** Plan→Apply→Receipt, Broker→Lease→Receipt, Registry→Diff→Gate, Quarantine→Promote, Observation→Suggestion→Review→Enforce, Capsule, Bundles, Adapter→Shadow→Replace  

DeriveBSD is ambitious, so the only way it stays **coherent** is if new subsystems land as instances of a small set of reusable patterns.

This is a **meta-engineering** doc: it names the patterns, when to use them, and which artifacts they imply.

## The rule

If a new feature can’t be described as one of these patterns (or a trivial composition of them), it probably belongs in an RFC and should be treated as suspicious.

For docs in the meta-engineering range (>=397), make the mapping explicit by adding a `**Patterns:**` metadata line near the top (stable review surface; prevents design sprawl).

The goal is not dogma. The goal is to keep the system:

- reviewable (stable diff surfaces)
- operable (repeatable workflows)
- least-authority by default (no ambient backdoors)
- evidence-producing (receipts everywhere)

## Pattern 1: Plan → Apply → Receipt

**Use when:** the system will mutate something (disk, ZFS datasets, PF ruleset, sysctls, service graph).

**Shape:**

- `*.plan` (what will be done, with stable ordering + digests)
- an apply engine that is deterministic and idempotent
- `*.receipt` (what actually happened, including the exact objects touched)

Examples:
- change sets: `docs/219-change-sets-and-apply-engine.md`
- sysctls: `docs/318-kernel-tunables-and-sysctls-as-evidence.md`
- network topology: `docs/322-network-topology-and-firewall-as-derived-operations.md`
- disk layout: `spec/disk.layout.plan.schema.json`, `spec/disk.layout.receipt.schema.json`

## Pattern 2: Broker → Lease → Receipt (authority is temporary)

**Use when:** a component needs access it should not hold forever (network egress, inbound listen, crypto ops, exports, debugging).

**Shape:**

- a broker endpoint (usually a local RPC surface or portal)
- a `*.grant` / `*.lease` object with explicit scope + expiry
- receipts for issuance + use (canonical cross-lane: `lease.issue.receipt`, `lease.use.receipt`)

Examples:
- network egress broker: `docs/281-network-egress-broker-and-consent.md`
- inbound listen broker: `docs/286-inbound-listen-broker-and-firewall-leases.md`
- crypto ops portal: `docs/306-crypto-operations-portal-and-split-keys.md`
- exports + consent: `docs/251-export-policies-and-support-bundle-portal.md`, `docs/256-consent-ux-contract.md`

## Pattern 3: Registry → Diff → Gate (drift is reviewable)

**Use when:** the system grows a surface that people/clients will depend on (APIs, UAPI, parsers, crypto suites, trust boundaries).

**Shape:**

- `*.registry` (compiled, canonical ordering, stable ids)
- `*.diff` (classified deltas)
- policy gates that can block or require approvals

Examples:
- contracts: `docs/370-contract-registries-and-api-diff-gates.md`
- UAPI: `docs/362-uapi-surface-registry-and-compat-gates.md`
- parsers: `docs/376-parser-surface-registry-and-fuzz-gates.md`
- crypto: `docs/391-crypto-surface-registry-and-agility-gates.md`
- trust boundaries: `docs/380-trust-boundary-graphs-and-threat-diff.md`

## Pattern 4: Quarantine → Promote (imports are untrusted until proven)

**Use when:** bytes arrive from the outside (updates, image imports, mirror kits, USB media, user file imports).

**Shape:**

- put bytes in a quarantined namespace
- attach origin labels + verification results
- promote only after policy acceptance

Examples:
- origin labels + quarantine: `docs/280-origin-labels-and-quarantine-attributes.md`
- update quarantine flow: `docs/61-channel-metadata-tuf-inspired.md`, `docs/138-offline-signed-update-bundles.md`
- sanitization portal: `docs/267-sanitization-portal-and-disposable-sandboxes.md`

## Pattern 5: Observation → Suggestion → Review → Enforce

**Use when:** the secure setting is hard to author up-front (promise profiles, network policy, resource budgets).

**Shape:**

- an observation mode that emits structured denials/flows
- a `policy.suggestion` artifact (never auto-applied)
- a human review surface (diff + context)
- enforcement gates once adopted

Examples:
- learned promise profiles: `docs/326-learned-promise-profiles-and-observation-mode.md`
- denial-driven suggestions: `docs/378-denial-driven-policy-suggestions.md`
- learned network policies: `docs/328-learned-network-policies-from-flow-receipts.md`
- learned resource budgets: `docs/329-learned-resource-budgets-and-observation-mode.md`

## Pattern 6: Capsule (reproducible context packages)

**Use when:** a failure needs to be shareable and replayable (build failure, boot failure, incident response).

**Shape:**

- minimal set of inputs + evidence + transforms (redaction)
- deterministic export plan
- a receipt that proves what was included / excluded

Examples:
- incident snapshots: `docs/216-incident-snapshots-and-support-bundles.md`
- export plans: `docs/253-bundle-plans-and-deterministic-exports.md`
- replay/debug capsules: `docs/194-debugging-by-lease-and-replay-capsules.md`

## Pattern 7: Bundles compose drift surfaces

**Use when:** humans must review *many* diffs, and policy must gate a single object.

**Shape:**

- a single `drift.bundle` that links multiple diffs + evidence

Example:
- `docs/395-drift-bundles-and-review-summaries.md`

## Pattern 8: Adapter → Shadow → Replace (interop without forever-legacy)

**Use when:** DeriveBSD must interoperate with an external ecosystem (ports/pkg, OCI transports, full TUF metadata, foreign binary views) but we want a clear deletion path.

**Shape:**

- an explicit adapter that translates external formats into DeriveBSD objects (planned + receipted)
- an optional **shadow mode** that runs adapter + native paths side-by-side and emits a diff
- a bounded **replacement** plan (deprecation notice + removal receipts)

This pattern is the antidote to “compat forever”: adapters are allowed, but they must be **killable**.

See:
- adapter lane discipline: `docs/402-adapter-lanes-and-strangler-discipline.md`
- deprecation + removal receipts: `docs/385-deprecation-policies-and-removal-receipts.md`
- existing adapters: `docs/108-ports-pkg-adapter-lane.md`, `docs/203-full-tuf-metadata-adapter.md`, `adrs/ADR-0021-oci-as-optional-transport.md`


## How to use this doc (practical)

When proposing a new subsystem:

1) Pick the primary pattern(s).
2) Name the contract objects (schemas) up front.
3) Identify the review surface (diffs/registries/bundles).
4) Show how authority is attenuated and revocable.
5) Define failure/rollback semantics.

Then run the rubric:
- `docs/348-design-review-rubric-and-feature-intake.md`


Last updated: 2026-02-28r170
