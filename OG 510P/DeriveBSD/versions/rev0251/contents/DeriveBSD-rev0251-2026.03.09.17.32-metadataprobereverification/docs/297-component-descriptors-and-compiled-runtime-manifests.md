# Component descriptors + compiled runtime manifests (make “how it runs” a derivation)

DeriveBSD already wants a long list of **compiled, hashable runtime artifacts**:
- service graphs (`svcgraph.json`)
- capability routing (`caproute.json`)
- preopened descriptor maps for Capsicum launchers (`preopen.map`)
- mount views / namespace groups (`mount.view`)
- stratum stacks (“which userlands are in scope?”)
- state footprints + migration plans
- promise profiles + lint outputs
- health checks + promotion gates

If we treat each of these as an independent “mini-language”, the ecosystem will rot:
people will cargo-cult, drift, and ship invisible authority.

Greenfield advantage: **make “how a component runs” a single, typed source**, then compile it into
the canonical runtime artifacts during Plan → activation planning.

The archive now fixes the boundary in `docs/500-derive-unit-source-compile-receipt-and-runtime-boundary.md` and `adrs/ADR-0090-derive-unit-source-compile-receipt-and-runtime-boundary.md`:

- `derive.unit` is the authoritative human-authored source
- `runtime.manifest` is the backend-facing launch authority
- `derive.unit.compile.receipt` is the evidence-only source→compiled join
- a `derive.unit` must name runtime bytes via exactly one authored field: `rootfs` or `strata`

## Prior art worth stealing

- **Fuchsia**: developer-facing component sources (`.cml`) are compiled into a canonical manifest format,
and capability routing is the access-control mechanism.  
  References: https://fuchsia.dev/reference/cml , https://fuchsia.dev/fuchsia-src/concepts/components/v2/component_manifests
  Testing topology steal (Realm Builder): https://fuchsia.dev/fuchsia-src/development/testing/components/realm_builder
  See also: `docs/354-realm-builder-style-hermetic-component-tests.md`

- **Flatpak**: a manifest encodes sandbox needs (finish-args) and relies on portals for mediated host access.  
  References: https://docs.flatpak.org/en/latest/manifests.html , https://docs.flatpak.org/en/latest/sandbox-permissions.html

- **Portable service images**: ship a tree + metadata, then attach/detach with an admin-selected sandbox profile.  
  Reference: https://systemd.io/PORTABLE_SERVICES/

## DeriveBSD target: a single “component descriptor” source

A **component descriptor** is a small, human-authorable source file describing one runnable unit:
- a service
- a sidecar/agent
- a desktop app (portalized)
- an incident tool (timeboxed)

It is intentionally **not** the build recipe (that stays in Spec).
It is the *runtime contract* for one component instance.

Name it something boring and toolable: `derive.unit`.

## Compiled outputs (the canonical runtime lane)

The descriptor compiles into **deterministic** artifacts recorded in evidence:

1) `svcgraph.json`  
   Service instance graph + restart semantics.  
   See: `docs/114-service-manifests-smf-lessons.md`, `docs/173-compiled-service-database-bundles.md`.

2) `caproute.json`  
   The explicit grant graph (“what may touch what?”).  
   See: `docs/140-capability-routing-manifests.md`, `docs/189-capability-graph-lint-and-viz.md`.

3) `preopen.map`  
   Capsicum preopened directory/file/socket handles + rights masks.  
   Schema: `spec/preopen.map.schema.json` (optional drift surface: `preopen.map.diff`).
   See: `docs/294-oblivious-sandboxing-launchers.md`, `docs/453-preopen-map-diff-as-review-surface.md`, `docs/180-capability-mode-dynamic-linking.md`.

4) `mount.view`  
   Namespace group + union view composition + stratum layers.  
   See: `docs/264-mount-namespaces-and-union-views.md`, `docs/295-strata-and-multi-origin-userlands.md`, `docs/485-stratum-stack-and-runtime-composition-boundary.md`.

   The multi-origin boundary is concrete: the descriptor compiles to a `stratum.stack`, that stack compiles to `mount.view`, and `runtime.manifest` carries `derive_unit_digest` + `stratum_stack_digest` + `mount_view_digest` so launch evidence can explain composition without folklore.

5) `state.footprint` + `state.migration.plan`  
   Declared persistent datasets + migration ordering.  
   See: `docs/217-state-datasets-and-migrations-as-evidence.md`.

6) `promises.json` + lint report  
   Promise profile vocabulary (pledge/unveil ergonomics) compiled to concrete knobs/backends.  
   See: `docs/232-service-promise-profiles.md`, `docs/271-promise-profile-vocabulary-and-lint.md`.

7) `healthchecks.json`  
   Health signals required for promotion/rollback decisions.  
   See: `docs/112-health-gated-updates.md`, `docs/166-test-receipts-and-promotion-gates.md`.

8) `diagnostics.profile.json`
   Structured diagnostics policy (inspect trees, flight recorder buffers, retention/redaction), compiled from descriptor intent.
   See: `docs/302-structured-diagnostics-inspect-trees.md`, `docs/303-flight-recorder-tracing-and-budgeted-diagnostics.md`.

9) `pki.profile.json` + `trust.bundle.map.json`
   Trust bundle dependencies + identity/cert requirements compiled from descriptor intent; used to inject digest-pinned CA handles and to ensure issuance/renewal steps are satisfied during activation.
   See: `docs/228-pki-and-identity-lifecycle-as-evidence.md`, `docs/304-trust-bundles-and-ca-injection-as-artifacts.md`.

10) `authority.budget`
   The reviewed least-authority budget for the component-runtime lane, compiled from the descriptor plus the canonical runtime IR (`caproute.json`, `preopen.map`, `mount.view`, `devfs.view.*`, `pki.profile.json`, `diagnostics.profile.json`).
   Review and drift tooling then emits `authority.budget.check`; waivers remain field-scoped `authority.exception` objects rather than silent edits to the budget.
   See: `docs/298-authority-budgets-and-permission-drift-alarms.md`, `docs/494-authority-budget-policy-check-and-exception-boundary.md`.

11) `runtime.manifest`
   The backend-facing launch contract.
   It is compiled from `derive.unit` and the runtime IR; it is not a second hand-authored source.

12) `derive.unit.compile.receipt`
   The evidence-only source→compiled join that preserves which source unit digest, runtime mode, compiler identity, and compiled output digests participated in the compilation step.

## Why this matters

### 1) One place to review authority

`derive diff --blast-radius` can summarize changes in *human language* by diffing the compiled IR outputs,
but reviewers can always jump to the single source descriptor that drove them.
That same compiled IR now feeds `authority.budget`, so least-authority review stops being a free-floating checklist.

### 2) Less “ambient authority by accident”

If a component wants a new capability, it must:
- express it in the descriptor (source),
- compile to canonical IR (machine truth),
- appear in diffs + receipts (audit truth).

### 3) Frontends can be plural without fragmenting semantics

We can support multiple authoring frontends (CUE/Pkl/Nickel/TOML) as long as they compile to the same canonical runtime lane.
See: `docs/79-derive-spec-frontends.md` (same “compile-to-IR” idea).

## Design sketch (v0 fields)

A minimal descriptor likely needs:

- `id`: stable instance identity (name + scope)
- `exec`: command + argv + env (env must be explicit; no implicit PATH searches)
- exactly one runtime-byte source: `rootfs` or `strata`
- `mounts`: `ro`, `rw`, `tmp`, `cache`, `secret` (each is a capability, not “just a path”)
- `state`: named datasets + schema version
- `capabilities`: network egress, device grants, time/rng, observability, IPC endpoints
- `promises`: high-level intent vocabulary compiled to backends (jail knobs, Capsicum rights, devfs, pf anchors)
- `health`: what constitutes “healthy”
- `evidence_hooks`: what to record (and redaction class)
- `diagnostics`: inspect tree + flight recorder intent (budgets, retention, redaction)
- `pki`: trust bundle dependencies + identity refs; compiled to CA handle injection and issuance requirements

## Invariants / non-negotiables

- **Compiled outputs are deterministic** given identical inputs.
- The descriptor is **typechecked and linted**; unknown fields are errors.
- A descriptor names runtime bytes through **exactly one authored field** (`rootfs` xor `strata`).
- Any descriptor change produces a **receipt** that can be audited later.
- Policies can constrain descriptors (deny new authority; require multiparty approval).  
  See: `docs/288-multiparty-approvals-and-separation-of-duties.md`.

## Remaining questions

- How much `contractset.json` / endpoint-typing needs to be first-class in v0 versus later?
- How far do we want compiler-generated specialization helpers to go before they become new authored surfaces?
- Which future runtime backends deserve new compiled outputs instead of adapter wrappers?

Last updated: 2026-03-08r229
