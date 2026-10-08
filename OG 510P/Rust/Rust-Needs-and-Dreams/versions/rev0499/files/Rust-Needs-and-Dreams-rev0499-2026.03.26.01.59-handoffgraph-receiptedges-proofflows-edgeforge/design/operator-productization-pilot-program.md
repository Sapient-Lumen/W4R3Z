# Design: Operator Productization Pilot Program (CRD/Capability Truth → Status/Runtime Evidence → Webhook/Health Surface → Install/Upgrade Support → Release/Policy Consumers)

## Goal
Turn the **Operator Productization Stack** into a ranked execution program so the archive can answer a practical question: what is the first boring, portable, ecosystem-shaping contribution that would materially improve how Rust operators are built, tested, shipped, reviewed, and supported?

The pilot program should not chase a universal controller framework or hosted cluster platform.
It should sequence the contribution so each lane proves something concrete before the next lane widens scope.

## Why a pilot program is necessary
Operators are unusually vulnerable to fake maturity.
A successful local reconcile loop, a CRD YAML snippet, a dashboard screenshot, or one cluster smoke test can hide the actual product questions:
- what CRD schema and status contract the operator really owns,
- what permissions and external powers it actually needs,
- whether conditions, events, metrics, or webhooks are stable support surfaces,
- what install/upgrade/uninstall story is truly supported,
- which Kubernetes versions and distributions are part of the promise,
- and what release/support/incident consumers may later conclude.

A credible plan therefore needs to decide:
- when schema + capability truth is already enough,
- when status/condition/runtime evidence must be attached,
- when webhook/health/admin surfaces become part of the contract,
- when install/upgrade/Kubernetes-version truth is required,
- and which release/policy/support consumers justify graduation.

## Principles
1. **Start from CRD + capability truth, not runtime ideology**
   - a pack that proves resource and permission posture is worth more than another runtime comparison.
2. **Keep schema truth, capability truth, and runtime evidence separate**
   - they travel together in real operators, but they are not the same source of truth.
3. **Status is evidence, not the whole contract**
   - conditions, events, and metrics should attach to the declared product surface instead of silently replacing it.
4. **Install/upgrade/support truth comes after lower-layer facts exist**
   - one green cluster test is not yet a product-support story.
5. **Consumers import; they do not reinterpret**
   - release, policy, incident, atlas, and docs/support consumers should import artifacts instead of becoming the hidden truth engine.

## Common artifacts this program should drive
- `operator-product-brief/v0` — declares which pilot lane is being exercised, scope, targets, and non-goals.
- `operator-schema-brief/v0` — bounded summary of CRDs, versions, spec/status/condition semantics, and validation posture.
- `operator-capability-brief/v0` — RBAC/resources/verbs/scopes plus external-system or secret/certificate dependencies.
- `operator-runtime-brief/v0` — status/event/metric/trace mappings, degraded modes, and reconcile/runtime attachments.
- `operator-install-brief/v0` — manifests/charts/images, upgrade and uninstall posture, Kubernetes-version/distro assumptions, and checked install evidence.
- `operator-consumer-handoff/v0` — what release/policy/support/incident/atlas consumers may conclude and what remains out of scope.
- `operator-readiness-scorecard/v0` — not a fake maturity score; a lane-by-lane checklist showing which truths exist and which remain absent.
- `operator-product-pack/v0` — attachable summary pack importing the lane artifacts used in a specific pilot.

## Ranked pilot lanes

### 1) Single-CRD + capability lane
**Why first:** it proves the most universal operator-product claim with the least runtime sprawl.

**Concrete scope**
- one real operator subject,
- declared CRD/version identity,
- spec/status/condition contract summary,
- RBAC/resource/secret/certificate posture,
- checked fixtures or examples,
- docs/support notes that state schema and capability truth honestly.

**Graduation bar**
- a reviewer can tell what the operator owns and what powers it needs without reading raw YAML, Rust types, or cluster role folders.

### 2) Status / conditions / runtime-evidence lane
**Why second:** once product and capability truth are explicit, the next hidden source of failure is what runtime evidence really means.

**Concrete scope**
- condition and event identity,
- metrics/logs/traces posture,
- reconcile reason codes,
- degraded or retry posture,
- status-update versus observed-world evidence notes.

**Graduation bar**
- a reviewer can tell which runtime signals are official product evidence and how they line up.

### 3) Webhook / health / admin-surface lane
**Why third:** this is where operator products often start overclaiming from one deployment.

**Concrete scope**
- admission/webhook posture,
- CEL-versus-webhook validation notes,
- liveness/readiness/health/admin endpoints,
- service identities and request/response behavior,
- explicit note when a lane is optional, experimental, or illustrative.

**Graduation bar**
- a reviewer can tell which network-facing control-plane behaviors are first-class and which are merely implementation details.

### 4) Install / upgrade / Kubernetes-version lane
**Why fourth:** this is where support stories are usually the least portable.

**Concrete scope**
- manifest/chart/bundle/image identity,
- installation and removal assumptions,
- upgrade/downgrade posture,
- supported Kubernetes versions/distros/runtime floors,
- checked install/e2e evidence.

**Graduation bar**
- a reviewer can tell what environment/install story is actually supported and how it was checked.

### 5) Release / policy / support / incident consumer lane
**Why fifth:** this is where the stack proves it matters beyond demos and one cluster.

**Concrete scope**
- release attachments importing operator truth,
- policy/admission or security-review imports,
- support playbook handoff,
- incident/replay/debug import notes,
- atlas/comparison notes for serious Rust operator lanes.

**Graduation bar**
- a downstream consumer can answer what operator story is actually supported and what evidence shipped with it.

## What to defer
- a universal Rust Kubebuilder equivalent;
- one magical controller-runtime abstraction over every cluster pattern;
- hosted orchestration or fleet-management control planes;
- benchmark theater without product-boundary artifacts;
- policy-first hard gates before the evidence lanes exist.

## Immediate archive consequences
- Treat **Schema Contract** as the anchor of a broader operator-productization seam rather than an isolated CRD/schema idea.
- Treat **Runtime Capability** as the RBAC/power half of the story instead of letting chart files or cluster role folders silently absorb it.
- Treat **Service Surface** as the webhook/health/admin import lane instead of burying those surfaces in framework code.
- Treat **Observability** as status/runtime evidence that support and incidents should import rather than reconstructing from dashboards and issue comments.
- Treat **Distribution Contract + Support Envelope** as install/support lanes that consume lower-layer operator truth instead of retelling it.
- Add a specific amnesia resistor so later revisions cannot collapse CRD truth, capability posture, runtime evidence, webhook surface, install/support truth, and downstream conclusions into one fake readiness story.

## Read this together with
- `design/operator-productization-stack.md`
- `design/schema-contract-kit.md`
- `design/runtime-capability-kit.md`
- `design/service-surface-kit.md`
- `design/observability-kit.md`
- `design/distribution-contract-stack.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
- `design/conformance-traceability-stack.md`

## Proposal-layer companion
The explicit proposal-layer candidate is now [`proposals/epic-operator-productization-stack.md`](../proposals/epic-operator-productization-stack.md): a thin `cargo operator-product` / `operator-product-pack/v0` layer above Schema Contract + Runtime Capability + Service Surface + Observability + Distribution Contract + Support Envelope. The pilot stays intentionally narrower than “Rust Kubernetes solved”: prove CRD/capability truth first, then status/runtime evidence, then webhook/health surfaces, then install/upgrade support, then downstream consumers.
