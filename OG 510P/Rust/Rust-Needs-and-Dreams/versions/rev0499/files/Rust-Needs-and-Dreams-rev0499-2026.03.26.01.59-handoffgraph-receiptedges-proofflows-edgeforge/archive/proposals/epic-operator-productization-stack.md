# Epic Proposal: Operator Productization Stack (`cargo operator-product` + `operator-product-pack/v0`)

## Why this is worthy
Rust already has credible operator ingredients, but it still lacks a **portable product layer for boring Kubernetes operators and controller products**.

The ecosystem signal is unusually aligned:
- Kubernetes still defines operators as software extensions built around custom resources and control loops.
  https://kubernetes.io/docs/concepts/extend-kubernetes/operator/
- `kube` already offers a Rust Kubernetes client, controller runtime, CRD derive, and related tooling, and the repository explicitly frames itself as a Rust client and controller runtime hosted by CNCF as a Sandbox Project.
  https://docs.rs/kube/latest/kube/
  https://github.com/kube-rs/kube
- `kube-rs` now documents controllers across admission, testing, observability, security, scaling, and availability. That means Rust operators now have enough substrate that the missing contribution looks less like “can we do this at all?” and more like “where is the shared product boundary above the pieces?”
  https://kube.rs/controllers/admission/
  https://kube.rs/controllers/testing/
  https://kube.rs/controllers/observability/
  https://kube.rs/controllers/security/
  https://kube.rs/controllers/availability/
- The testing docs are especially clarifying: Rust currently has no `envtest` equivalent, so the portable install/test/support contract matters more, not less.
  https://kube.rs/controllers/testing/
- `kube-derive` and `KubeSchema` make typed CRDs and CEL-validation-aware schema generation part of the Rust lane instead of pure YAML drift.
  https://docs.rs/kube-derive/latest/kube_derive/derive.CustomResource.html
  https://docs.rs/kube/latest/kube/derive.KubeSchema.html
- Stackable’s operator docs show that real operator products already have to publish supported product versions, monitoring posture, shared CRDs, secret/certificate handling, and internal-vs-product operator roles.
  https://docs.stackable.tech/home/stable/operators/
  https://github.com/stackabletech/operator-rs
- Go’s mainstream `controller-runtime` stack already treats managers, controllers, reconcilers, clients/caches, schemes, webhooks, logging/metrics, and testing as one coherent lane. Rust has serious ingredients, but not yet the reviewable product layer above them.
  https://pkg.go.dev/sigs.k8s.io/controller-runtime

But the ecosystem still has no single honest handoff for **operator-as-product truth**.

That means maintainers, platform teams, release reviewers, and support tools still have to reconstruct the answer from:
- Rust types and CRD YAML;
- RBAC manifests and Helm values;
- webhook/router code;
- metrics/status/event conventions;
- chart/image/install docs;
- support matrices and CI history;
- and ad hoc incident notes.

The missing contribution is a thin portable layer above those pieces, not a replacement for them.

## Proposal
Define an **Operator Productization Stack** with:
- a reference aggregation CLI, `cargo operator-product`;
- a thin linked bundle, `operator-product-pack/v0`;
- imported evidence from:
  - schema-contract reports and version diffs
  - runtime-capability profiles and waivers
  - service-surface reports for webhooks/health/admin endpoints
  - observability profiles and runtime/status evidence
  - distribution-contract/install receipts and support-envelope packs
  - optional conformance/policy/release/incident imports
- stable stack-level artifacts:
  - `operator-schema-brief/v0`
  - `operator-runtime-brief/v0`
  - `operator-surface-brief/v0`
  - `operator-support-brief/v0`
  - `operator-product-diff/v0`

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
- `cargo operator product verify-pack <path>`
  - verify schema versions, checksums, and imported-attachment integrity

This should stay a **thin composition layer**.
It should not replace `kube`, generated YAML, Helm/Kustomize, controller runtimes, incident tooling, or cluster-management platforms.

## What `operator-product-pack/v0` should contain
- `manifest.json`
- `operator-schema-brief.json`
- `operator-runtime-brief.json`
- `operator-surface-brief.json`
- `operator-support-brief.json`
- optional `operator-product-diff.json`
- imported schema-contract, capability, observability, distribution-contract, and support/docs attachments
- checksums, provenance, and generator identity
- optional release / policy / incident consumer pointers

## Design principles
- **CRD truth is not enough.** A type-safe CRD does not tell platform teams what the operator actually promises.
- **Capability truth is part of the product.** Required verbs/resources/scopes and external powers cannot stay buried in YAML.
- **Runtime evidence is evidence, not a substitute contract.** Conditions/events/metrics must connect back to declared operator and install identities.
- **Webhook/health surfaces are first-class.** Admission, health, and admin behavior should not stay implicit in framework code.
- **Install/support posture is imported, not guessed.** Charts/manifests, Kubernetes-version support, docs, and upgrade notes must travel as explicit claims.
- **Consumers import bounded conclusions.** Release, policy, incident, support, and atlas consumers should each get explicit handoff boundaries.
- **No runtime coronation.** A good operator-product layer should help `kube`, Stackable/operator-rs style production stacks, and future runtimes without anointing one as the only serious choice.

## Early implementation order
1. CRD + capability lane
2. status/condition/runtime-evidence lane
3. webhook/health/admin lane
4. install/upgrade/support lane
5. release / policy / incident consumer lane

That order follows the real pressure gradient: first prove maintainers can publish boring operator truth, then prove runtime evidence, then prove exposed control-plane behavior, then make install/support claims honest, and only then let downstream governance consumers rely on it.

## Non-goals
- a Rust Kubebuilder clone;
- a universal controller runtime or hosted control plane;
- another runtime bake-off;
- one mega-schema that flattens CRDs, RBAC, status, webhooks, install, and support into a fake maturity score;
- a promise that operator-product packs alone prove production excellence.

## Success bar
This becomes worthy when a maintainer, platform team, release reviewer, or ecosystem guide can answer:
- what operator boundary is official,
- which CRDs, versions, and conditions actually matter,
- what powers and webhooks are required,
- what runtime evidence should exist,
- what install/upgrade/Kubernetes-version/support claims are attached,
- and what changed between versions or deployment profiles,

without scraping YAML folders, router code, dashboards, and incident threads.

## Read this with
- `design/operator-productization-stack.md`
- `design/operator-productization-pilot-program.md`
- `design/schema-contract-kit.md`
- `design/runtime-capability-kit.md`
- `design/service-surface-kit.md`
- `design/observability-kit.md`
- `design/distribution-contract-stack.md`
- `design/support-envelope-kit.md`
- `design/docproof-kit.md`
