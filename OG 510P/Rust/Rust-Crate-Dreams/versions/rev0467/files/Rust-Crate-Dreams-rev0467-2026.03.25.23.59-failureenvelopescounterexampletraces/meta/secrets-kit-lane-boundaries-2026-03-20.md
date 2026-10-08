# secrets-kit lane boundaries (2026-03-20)

This note exists so the archive does not flatten several adjacent secret-handling lanes into one fake “Rust secrets crate” story.

## Core judgment

**P-0037 secrets-kit** should be the lane for:

- **revelation-path truth**,
- **persistence-posture truth**,
- **memory-posture truth**,
- and **export-posture truth**.

It is the lane for the question:

> “What secret-handling support contract is this Rust crate or app actually publishing to another team?”

## Keep separate from these adjacent lanes

### 1. P-0105 Secrets Envelope & Policy Kit

Secrets Envelope & Policy Kit is about:
- encrypted envelopes,
- rotation / policy / environment scoping,
- and interoperating with SOPS / age / KMS workflows.

`secrets-kit` is **not**:
- the encrypted envelope format,
- the rotation-policy engine,
- or the secrets-at-rest governance lane.

Envelope workflows may import contract artifacts.
They do not own them.

### 2. P-0166 Sensitive Data Redaction & Policy Kit

Sensitive Data Redaction & Policy Kit is about:
- logs / traces / metrics,
- classification and transforms,
- and policy-first privacy handling for telemetry.

`secrets-kit` is **not**:
- the general telemetry-redaction lane,
- the policy-as-code framework for all sensitive fields,
- or the before/after observability evidence bundle.

This lane owns the **secret-handling support contract**, not all privacy policy.

### 3. Generic provider/adaptor crates

Existing crates already provide:
- keychains / secure stores,
- zeroize wrappers,
- protected-memory wrappers,
- and remote/client-specific secret backends.

`secrets-kit` should **not** collapse into:
- another keyring adapter only,
- another `Secret<T>` wrapper only,
- or another provider chain without a receiver-facing contract.

The missing value is the **reviewable support contract above those helpers**.

### 4. Authorization / policy engines

This lane is **not**:
- a full authZ system,
- an ABAC/RBAC engine for who may reveal secrets,
- or a workflow engine for rotation approvals.

It can record reveal/export posture.
It does not own organizational policy.

## Review objects that should stay first-class

### `revelation-path.receipt`

Keeps env strings, decrypted files, OS secure stores, remote fetches, and mocks from collapsing into one fake “loaded secret” claim.

### `persistence-posture.receipt`

Keeps native-store persistence, file-envelope persistence, session-only behavior, in-memory-only behavior, and mock/non-persistent test backends from collapsing into one fake “stored securely” claim.

### `memory-posture.receipt`

Keeps ordinary heap values, zeroize-on-drop wrappers, and `mlock`/`mprotect`-class protected memory from collapsing into one fake “protected in memory” claim.

### `export-posture.report`

Keeps default debug redaction, disabled `serde`, explicit serialization opt-ins, custom reveal helpers, and clone posture from collapsing into one fake “won’t leak” claim.

## Doctor warnings worth keeping separate

The first implementation should distinguish warnings such as:

- `plaintext_intermediate_not_disclosed`
- `mock_backend_used_in_supported_profile`
- `protected_memory_claim_without_protected_backend`
- `serialization_opt_in_widens_export_surface`
- `manual_review_required`

## Non-goals for this boundary note

This note is **not** asking P-0037 to become:

- a secret manager,
- an encrypted envelope system,
- a generic privacy/redaction platform,
- or an authorization-policy engine.

It is only insisting that **revelation path**, **persistence posture**, **memory posture**, and **export posture** stay reviewable.
