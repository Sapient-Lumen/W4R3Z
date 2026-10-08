# 403 — Narrow-waist public standards and interface governance

## One-line thesis

Where the state must shape a digital ecosystem, it should keep the **mandatory public layer narrow, open, testable, and durable**, while allowing plural implementation above and below it.

## Why this matters

A frequent governance failure is to over-regulate applications while under-governing the interfaces that actually determine lock-in, portability, competition, and state capacity. A better approach is to govern the **waist**: the thin layer of public standards, registries, conformance tests, and switching rules that many providers must pass through.

## Design rule

Public authority should prefer:

- **thin compulsory interfaces**,
- **thick competitive implementation space**,
- **public conformance testing**,
- **strong exit and portability rights**,
- **periodic pruning of overgrown standards**.

## Pattern pack

### 1. Public narrow waist

Define a minimal mandatory layer:

- canonical identifiers,
- message formats,
- consent / permissions signals,
- event logs and status codes,
- security and audit hooks,
- portability and handoff methods.

Do **not** hard-code entire application behavior when interface discipline is sufficient.

### 2. Protocol council, not application ministry

Establish a small multi-stakeholder standards body that can:

- version core schemas,
- publish change proposals,
- maintain compatibility windows,
- run public consultations,
- document deprecation paths.

Its job is not to pick every product winner. Its job is to maintain a fair grammar for the ecosystem.

### 3. Public reference implementation

Ship at least one open reference stack for:

- small municipalities,
- public-interest deployments,
- auditing and educational use,
- fallback continuity when vendors exit.

Reference code should clarify the standard without monopolizing production supply.

### 4. Conformance before procurement

Public procurement should privilege:

- compliance with open standards,
- exportability of records,
- substitution of modules without full rebuild,
- demonstrable migration paths.

Buyers should be able to replace a payment rail, consent manager, case-routing engine, or participation interface without rewriting the whole system.

### 5. Mandatory off-ramp

Every certified implementation should support:

- bulk export,
- human-readable and machine-readable records,
- key rotation and credential recovery,
- graceful provider exit,
- continuity transfer to a successor operator.

### 6. Sunset-and-shrink review

Every few years, review the public waist and ask:

- what rule is no longer necessary,
- what field duplicates another field,
- what interface is only preserving legacy rent extraction,
- what private workaround reveals a missing public standard.

## Guardrails

- The waist must stay small enough to preserve experimentation.
- The state should not confuse **open standards** with **single-vendor national champions**.
- Proprietary extensions must never become de facto mandatory without public review.
- Accessibility, privacy, and auditability must be first-class conformance requirements rather than optional add-ons.

## Failure modes

- **Bloated waist**: every policy anxiety gets pushed into the core protocol.
- **Fake openness**: nominal standards with no real export or interoperability.
- **Reference capture**: the reference stack becomes the only politically viable stack.
- **Procurement relapse**: agencies buy convenience bundles that silently nullify the public interface layer.

## Practical tests

A system passes the narrow-waist test when a public buyer can answer yes to all of the following:

1. Can we switch providers without losing historical records?
2. Can a smaller or local provider interoperate without bespoke permission?
3. Are audit logs exportable and intelligible to outsiders?
4. Is the mandatory layer substantially smaller than the application layer?
5. Do accessibility and privacy travel with the standard rather than depend on vendor goodwill?

## Compression rule for the archive

Whenever a draft governance proposal grows too large, ask: **what is the narrow waist here?** That question usually exposes the actual leverage point.
