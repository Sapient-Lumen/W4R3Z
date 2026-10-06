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

Name it something boring and toolable (placeholder): `derive.unit` (TOML/JSON5/YAML frontend; canonical IR below).

## Compiled outputs (the canonical IR)

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
   See: `docs/264-mount-namespaces-and-union-views.md`, `docs/295-strata-and-multi-origin-userlands.md`.

   Optional: if a referenced tree is satisfied via on-demand mounting, the plan can also emit a `tree.mount.plan`/receipt describing the transport backend and integrity parameters.
   See: `docs/299-verified-lazy-rootfs-and-on-demand-mounts.md`.

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


## Why this matters

### 1) One place to review authority

`derive diff --blast-radius` can summarize changes in *human language* by diffing the compiled IR outputs,
but reviewers can always jump to the single source descriptor that drove them.

### 2) Less “ambient authority by accident”

If a component wants a new capability, it must:
- express it in the descriptor (source),
- compile to canonical IR (machine truth),
- appear in diffs + receipts (audit truth).

### 3) Frontends can be plural without fragmenting semantics

We can support multiple authoring frontends (CUE/Pkl/Nickel/TOML) as long as they compile to the same canonical IR.
See: `docs/79-derive-spec-frontends.md` (same “compile-to-IR” idea).

## Design sketch (v0 fields)

A minimal descriptor likely needs:

- `id`: stable instance identity (name + scope)
- `exec`: command + argv + env (env must be explicit; no implicit PATH searches)
- `rootfs`: a digest-bound tree reference (or stratum stack) for the runnable bytes; transport selection remains policy-bound
- `strata`: which userland trees are in scope (and precedence)
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
- Any descriptor change produces a **receipt** that can be audited later.
- Policies can constrain descriptors (deny new authority; require multiparty approval).  
  See: `docs/288-multiparty-approvals-and-separation-of-duties.md`.

## Open questions

- Where does the canonical IR live? (`spec/derive.unit.schema.json`?)  
- How do we version descriptors without fracturing old hosts? (schema epochs + adapters)
- How do we prevent “descriptor inflation” (people dumping arbitrary config into it)?

Last updated: 2026-02-28r175
