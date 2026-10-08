# Gap: operator products still lack one portable boundary above CRD truth, admission/status behavior, RBAC/capability posture, install/update reality, and shipped support claims

## What is missing
Rust now has credible ingredients for serious Kubernetes operators and control-plane software, but it still lacks a **boring, end-to-end contract workflow** for operator products.

Today teams can separately:
- define CRDs and versions,
- write reconcilers and controller runtimes,
- add CEL validation or admission webhooks,
- expose metrics / logs / traces / health endpoints,
- ship YAML / Helm / image bundles,
- and document supported Kubernetes versions or product versions.

What is still missing is the shared layer that answers:
- what CRDs, versions, spec/status fields, and conditions are actually part of the product,
- what RBAC, secrets, certificates, finalizers, and external capabilities the operator really needs,
- what webhook / health / metrics / admin surfaces are officially exposed,
- what install / upgrade / downgrade / uninstall story is actually supported,
- what Kubernetes-version / distro / platform combinations are part of the promise,
- and what support / release / incident consumers may later import without reverse-engineering manifests, cluster roles, CI jobs, and issue threads.

## Why it matters
This is not the same problem as ordinary service APIs.

For operators, the dangerous questions are often not only “does reconcile eventually succeed?” but:
- what exact CRD schema and status contract the operator owns,
- whether CEL or webhook validation is required versus optional,
- whether a condition, event, or metric is a stable supported signal or just an implementation detail,
- whether the controller needed cluster-admin-like powers or only narrowly scoped permissions,
- whether the current bundle is safe to upgrade on the Kubernetes versions and distributions a team actually runs,
- and whether support can explain what changed between two operator releases without replaying a whole cluster incident.

Today those answers are usually split across CRD YAML, Rust types, Helm charts, RBAC files, deployment flags, dashboards, CI setup, and maintainer memory.

## Existing building blocks worth composing
- Kubernetes itself frames operators as software extensions that use custom resources to manage applications and their components.
  https://kubernetes.io/docs/concepts/extend-kubernetes/operator/
- `kube` already gives Rust a real client + controller-runtime + CRD-derive substrate, and positions itself as a Rust Kubernetes client and controller runtime.
  https://docs.rs/kube/latest/kube/
  https://github.com/kube-rs/kube
- `kube-rs` now documents operators across concepts, admission, testing, observability, security, scaling, and availability. That is a strong signal that Rust has a real operator lane rather than a one-off API client story.
  https://kube.rs/controllers/intro/
  https://kube.rs/controllers/admission/
  https://kube.rs/controllers/testing/
  https://kube.rs/controllers/observability/
  https://kube.rs/controllers/security/
  https://kube.rs/controllers/availability/
- `kube-derive` and `KubeSchema` make typed CRDs and CEL-validation-aware schema generation part of the Rust lane rather than pure YAML authoring.
  https://docs.rs/kube-derive/latest/kube_derive/derive.CustomResource.html
  https://docs.rs/kube/latest/kube/derive.KubeSchema.html
- `k8s-openapi`, `schemars`, and `kopium` provide real type/schema/import lanes for cluster APIs and existing CRDs.
  https://docs.rs/k8s-openapi/
  https://docs.rs/schemars/
  https://docs.rs/kopium/
- `controller-rs` already treats status writes, events, finalizers, observability instrumentation, and packaging/e2e testing as part of the reference-controller story.
  https://github.com/kube-rs/controller-rs
- Stackable’s current operator docs show a real product family answer: supported product versions, monitoring guidance, shared CRDs, secret/certificate operators, listener operators, and product release notes all live in one place.
  https://docs.stackable.tech/home/stable/operators/
  https://github.com/stackabletech/operator-rs

## Why existing tools are not yet the whole answer
The ecosystem has **real operator point tools**, but not the **shared product contract / diff / evidence layer**:
- `kube` owns one Rust-native controller/runtime lane.
- `kube-derive` / `KubeSchema` own one typed-CRD / schema / CEL lane.
- `k8s-openapi` / `kopium` own import and generated-type lanes.
- Stackable/operator-rs and similar projects own one opinionated production lane.

Teams still have to invent their own answers for:
- stable operator subject identity,
- portable CRD/status/condition contracts,
- capability/RBAC summaries that survive beyond YAML folders,
- explicit webhook / validation / health / metrics support posture,
- diffable install/upgrade/support packs,
- and downstream handoffs for release review, policy, incident response, or atlas guidance.

The comparison with Go also sharpens the gap instead of erasing it: `controller-runtime` already treats managers, controllers, reconcilers, clients/caches, schemes, webhooks, logging/metrics, and testing (`envtest`) as one coherent mainstream stack. Rust has serious ingredients, but not yet the shared product boundary above them.
  https://pkg.go.dev/sigs.k8s.io/controller-runtime

## Target outcome
A project should be able to say:
- “this is the operator product surface this crate/image/chart/release expects,”
- “these are the CRDs, status/condition semantics, permissions, webhooks, and runtime attachments that justify the claim,”
- “these are the Kubernetes-version / distro / install / upgrade assumptions that materially shaped support,”
- and “this is the portable bundle release/support/policy/incident tooling can consume later.”

That would be a worthy contribution because it would make Rust operator products feel less like bespoke glue and more like reviewable systems.
