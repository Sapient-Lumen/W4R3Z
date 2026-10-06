# Policy modules as WebAssembly (optional lane)

DeriveBSD wants **strict determinism + explainability** without locking the ecosystem into a single policy language.
Many teams, however, will want richer policy than “schema + matchers” once they hit real fleets.

A common failure mode is to embed a general-purpose language in the core planner/activator.
That trades short-term flexibility for long-term fragility.

This doc captures an optional lane: **policy modules compiled to WebAssembly (Wasm)**.

## Lesson to steal

Policy engines increasingly ship a *compile-to-Wasm* path so that:
- the policy language stays an ecosystem choice
- the runtime stays small, sandboxable, and embeddable
- policy becomes a digest-pinned artifact, not "live code" in the control plane

OPA is a notable example: Rego policies can be compiled into Wasm modules evaluated locally.

## DeriveBSD mapping

DeriveBSD already requires policy decisions to be captured as **policy decision records**.
A Wasm lane lets DeriveBSD keep v1 policy schema stable while enabling richer org policy as a separate artifact.

### Core idea

- A **policy bundle** may reference zero or more **policy modules**.
- A module is an artifact with a digest and a declared **ABI**.
- The policy engine calls `evaluate(context_json, data_json)` and obtains:
  - `decision = allow|deny`
  - optional `obligations[]`
  - optional `trace` (bounded; stable schema)

### ABI and determinism

For v0, define a tiny ABI:

- input: canonical JSON bytes (context + data)
- output: canonical JSON bytes (result)
- no network
- no filesystem
- bounded CPU (fuel) and memory

This keeps the evaluation functionally pure.

### Safety posture

Treat modules as **untrusted**:
- execute in a Wasm runtime with strict hostcall allowlist
- cap runtime resources (fuel + memory)
- pin the runtime version as part of the trust policy

### Evidence objects (optional)

To preserve explainability without turning policy into an opaque blob:

- `policy.module` evidence: module digest, ABI, compiler metadata, declared hostcalls
- policy decision trace records the module digests invoked

Schema sketch: `spec/policy.module.schema.json`.

## Where this plugs in

- `derive plan` / `derive activate`: policy decisions may consult modules
- fleet rollouts: org policies like “only staged wave X for this cohort” live in a module
- portal brokers: policy modules can enforce “only allow this portal type for these workloads”

## How to keep it from turning into "policy = arbitrary code"

- require stable, bounded result schemas
- require trace output to be bounded (size + depth)
- prohibit hostcalls that reintroduce ambient authority
- treat modules as optional backends; v1 schema policies remain sufficient for a safe baseline

Pointers:
- Policy engine baseline: `docs/30-policy-engine.md`
- Policy traces: `docs/85-policy-engine-options-and-traces.md`
- Decision records: `docs/93-policy-decision-records.md`
- Deterministic redaction transforms (reuse runtime): `docs/195-deterministic-redaction-transforms.md`

Last updated: 2026-02-24
