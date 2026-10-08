# Design note: Operator Productization Stack (Schema Contract + Runtime Capability + Service Surface + Observability + Distribution Contract + Support Envelope)

## Goal
Define the **division of labor and consumer flow** between Rust operator/control-plane contracts, capability posture, webhook/endpoint surfaces, runtime evidence, install/update bundles, and support claims so the ecosystem can make **boring Kubernetes operators and controller products** reviewable without anointing one controller runtime, one YAML generator, one chart workflow, or one hosted control plane as the answer.

This is **not** a new top-level kit.
It is a stack note explaining how existing archive pieces should compose:
- [`design/schema-contract-kit.md`](./schema-contract-kit.md)
- [`design/runtime-capability-kit.md`](./runtime-capability-kit.md)
- [`design/service-surface-kit.md`](./service-surface-kit.md)
- [`design/observability-kit.md`](./observability-kit.md)
- [`design/distribution-contract-stack.md`](./distribution-contract-stack.md)
- [`design/support-envelope-kit.md`](./support-envelope-kit.md)
- [`design/docproof-kit.md`](./docproof-kit.md)
- [`design/conformance-traceability-stack.md`](./conformance-traceability-stack.md)
- [`design/policy-kit.md`](./policy-kit.md)

## Why this note is needed now
Rust’s current signals are no longer saying only “operators are possible.” They are saying Rust already has a serious operator lane, but the ecosystem still lacks a **portable productization layer**:
- Kubernetes still defines operators as software extensions built around custom resources and control loops;
- `kube` now explicitly ships the pieces for Rust applications and controllers that interact with Kubernetes, including a controller runtime, CRD derive, and broader tooling;
- `kube-rs` now documents operators across admission, testing, observability, security, scaling, and availability, which means the operator story is broad enough that the missing layer is increasingly the contract above the parts rather than the existence of the parts;
- `kube-rs` testing docs are honest that there is no `envtest` equivalent in Rust so far, which makes portable install/test/support artifacts more valuable, not less;
- `kube-derive` + `KubeSchema` make typed CRDs and CEL-validation-aware schema generation part of the Rust lane;
- Stackable and `operator-rs` show that real Rust operator product families already have to publish supported versions, monitoring posture, shared CRDs, secret/certificate handling, and internal-versus-product operator boundaries;
- and Go’s mainstream `controller-runtime`/Kubebuilder stack already treats managers, controllers, clients/caches, schemes, webhooks, logging/metrics, and testing as one coherent product-adjacent lane, which sharpens the shape of what Rust still lacks.

Together these signals justify treating operator productization as a **frontier-worthy ecosystem seam** rather than leaving Rust operators as a pile of CRD YAML, controller crates, Helm charts, RBAC files, and runbooks.

## Stack layers

### 1) Schema Contract: CRD and status authority
Schema Contract owns the **public control-plane contract**:
- CRD identities and served/stored versions
- spec/status shape and evolution posture
- condition and finalizer semantics
- CEL / schema validation posture
- diffable contract reports

Schema Contract answers questions like:
- “What resource types and versions are official?”
- “Which spec and status fields are part of the product contract?”
- “Which conditions or subresources are stable versus incidental?”

Design rule: **operator shape must not be inferred only from generated CRD YAML, Rust structs, or one cluster install**.

### 2) Runtime Capability: RBAC and external-power posture
Runtime Capability owns the **power boundary**:
- required verbs/resources/scopes
- namespace vs cluster posture
- secret/certificate/provider requirements
- finalizer/delete/update powers
- outbound network or external-system capability assumptions

Runtime Capability answers questions like:
- “What powers does this operator need to function?”
- “Which permissions are mandatory, optional, or profile-specific?”
- “What happens if a capability is absent?”

Design rule: **capability truth must not hide inside ClusterRole YAML, Helm values, or one platform team’s deployment notes**.

### 3) Service Surface: webhook, health, and admin endpoints
Service Surface owns the **network-facing boundary** attached to the operator:
- admission webhook identities and behavior
- liveness/readiness/health endpoints
- metrics and admin HTTP surfaces when relevant
- request/response/media-type posture
- diffable endpoint behavior reports

Service Surface answers questions like:
- “Does this operator expose webhooks?”
- “Which health or admin endpoints are part of the support story?”
- “Is validation declarative-only, webhook-only, or both?”

Design rule: **webhook and health behavior must not be inferred only from router code or manifest snippets**.

### 4) Observability: reconcile/status/runtime evidence
Observability owns the **runtime evidence contract**:
- reconcile identities and reason codes
- logs / traces / metrics posture
- status/condition/event evidence
- degraded-mode and retry evidence
- explainable runtime reports

Observability answers questions like:
- “What runtime evidence should exist for reconcile loops?”
- “Which conditions or events correspond to supported product states?”
- “How do metrics, logs, and status updates line up?”

Design rule: **a condition update, event emission, and metrics series are not the same truth, even when they describe the same incident**.

### 5) Distribution Contract + Support Envelope: install, upgrade, and platform truth
Distribution Contract and Support Envelope together own the **shipped and supported operator story**:
- manifest/chart/bundle identities
- image and install receipts
- upgrade/downgrade/uninstall posture
- supported Kubernetes versions/distros/runtime floors
- checked docs/examples and support notes

This layer answers questions like:
- “What exactly gets installed?”
- “Which Kubernetes versions or distributions are part of the promise?”
- “Which upgrade paths are supported?”
- “What docs/examples were actually checked?”

Design rule: **support claims must not be inferred from one successful cluster test, one chart release, or one CI matrix**.

### 6) Downstream consumers
The stack becomes worthy when real consumers can import it without flattening it:
- **Policy** can gate deployment or admission based on explicit capability and contract evidence.
- **Release / distribution** can attach operator-surface/install/support artifacts to a release.
- **Incident / replay / support** consumers can start from declared runtime and install truth instead of reconstructing a cluster story from logs.
- **Atlas / learning** consumers can describe credible operator lanes without turning one runtime or company stack into “the official answer.”

Design rule: **consumers import selected evidence; they do not redefine operator truth models**.

## What an epic contribution should look like in practice
A worthy contribution here is not “build Rust Kubebuilder.”
It is a portable, reviewable stack with clear boundaries:

1. **CRD + capability first**
   - prove `schema-contract` + `runtime-capability` + checked examples on one real operator;
2. **status + runtime evidence second**
   - add `obs-profile`, condition/event/metric mapping, and reconcile reports;
3. **webhook + health lane third**
   - attach admission, health, and metrics endpoint truth without flattening them into CRD semantics;
4. **install/upgrade/support fourth**
   - prove manifests/charts, Kubernetes-version support, and checked docs/examples;
5. **consumers fifth**
   - show one policy/release/incident/support consumer can import the stack honestly.

An eventual aggregate artifact may exist, but it should be a **thin pack of referenced artifacts**, not a new truth engine that erases the lane boundaries.

## Candidate artifact family
A worthy operator-productization contribution should stay thin and linked instead of becoming an operator mega-schema.
A plausible family is:
- `operator-schema-brief/v0`
- `operator-runtime-brief/v0`
- `operator-surface-brief/v0`
- `operator-support-brief/v0`
- `operator-product-diff/v0`
- `operator-product-pack/v0`

These artifacts should mostly reference lower-layer packs and checked attachments instead of replacing them.

## Reference CLI shape
- `cargo operator product export`
  - emit `operator-schema-brief/v0` from imported schema-contract and runtime-capability evidence
- `cargo operator product observe`
  - emit `operator-runtime-brief/v0` from observability imports and status/condition mappings
- `cargo operator product surface`
  - emit `operator-surface-brief/v0` from service-surface imports for webhooks/health/admin endpoints
- `cargo operator product support`
  - emit `operator-support-brief/v0` from distribution-contract, support-envelope, and docproof imports
- `cargo operator product diff --against <ref|version|path>`
  - emit `operator-product-diff/v0`
- `cargo operator product pack`
  - produce `operator-product-pack/v0`

This should remain a **composition layer**, not a controller runtime, chart framework, or hosted cluster control plane.

## Ranked first execution lanes
1. **Single-CRD + capability lane**
   - best first exporter because many Rust teams can already define CRDs and controllers, but reviewers still cannot see the product contract without reading YAML and code.
2. **Status / conditions / runtime-evidence lane**
   - proves the stack can describe how operator state is surfaced, not only what the CRD says.
3. **Webhook / health / admin lane**
   - makes externally reachable control-plane behavior explicit.
4. **Install / upgrade / support lane**
   - proves Kubernetes-version, distro, image/bundle, and docs truth instead of README optimism.
5. **Release / policy / incident consumer lane**
   - shows the stack matters beyond local engineering taste.

## Non-goals
- one universal Rust controller framework;
- one universal Helm/Kustomize replacement;
- a hosted operator management platform as the primary artifact;
- flattening CRD schema, RBAC/capabilities, webhook behavior, status evidence, and install/support truth into one fake “operator maturity” schema;
- pretending a running controller pod alone proves product support.

## Archive implications
- The archive should now treat **Schema Contract + Runtime Capability + Service Surface + Observability + Distribution Contract + Support Envelope** as a coupled **Operator Productization Stack** in frontier discussions.
- Future revisions should prefer **CRD/status truth, capability posture, webhook/health truth, runtime evidence, install/upgrade truth, and support/docs truth** over new runtime wrappers, chart generators, platform dashboards, or “Rust for Kubernetes” manifestos.
- The next credible move is now explicit: turn this stack plus the pilot program into the epic sketched in [`proposals/epic-operator-productization-stack.md`](../proposals/epic-operator-productization-stack.md), keeping the stack thin enough that operator teams can import it without adopting one official runtime or bundling tool.
- When Policy, Release Pipeline, Incident, DocProof, or Atlas work cites operator readiness, they should import **schema truth**, **capability truth**, **webhook/service truth**, **runtime evidence**, and **support/install truth** separately.

## References (signals)
- Kubernetes operator pattern:
  https://kubernetes.io/docs/concepts/extend-kubernetes/operator/
- `kube` crate overview:
  https://docs.rs/kube/latest/kube/
- kube-rs repository:
  https://github.com/kube-rs/kube
- kube-rs controller docs (admission/testing/observability/security/availability):
  https://kube.rs/controllers/admission/
  https://kube.rs/controllers/testing/
  https://kube.rs/controllers/observability/
  https://kube.rs/controllers/security/
  https://kube.rs/controllers/availability/
- `kube-derive` / `KubeSchema`:
  https://docs.rs/kube-derive/latest/kube_derive/derive.CustomResource.html
  https://docs.rs/kube/latest/kube/derive.KubeSchema.html
- Stackable operators docs:
  https://docs.stackable.tech/home/stable/operators/
- `operator-rs`:
  https://github.com/stackabletech/operator-rs
- Go `controller-runtime`:
  https://pkg.go.dev/sigs.k8s.io/controller-runtime
