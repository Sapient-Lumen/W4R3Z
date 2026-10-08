# 157. Manufacturing + build evidence pipeline (North Star)

**Track:** C (North Star)



> **Deployment honesty:** Track C documents describe a "North Star" hardening agenda.
> They are **not Track A deployment guidance** and must not be used to imply supply‑chain or fully electronic voting safety.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N‑4**) and the [`promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

If the North Star is “attestable devices with transparent manufacturing”, we need a concrete
pipeline describing **what gets signed**, **by whom**, and **how it is audited**.

This doc is a first-pass sketch using:
- in-toto statement framing (subject hashes + predicate types)
- SLSA-style provenance predicates for builds
- transparency logging for statements + key material

## 157.1 Roles (signers)

Define named signer roles (each with a public key and transparency-logged identity):

- **Maintainer** (source approval)
- **Build System** (reproducible build provenance)
- **Test Lab** (test/audit results)
- **Firmware Signer** (release signing)
- **Factory Station** (assembly checkpoints)
- **Hardware Root** (secure element / device identity injection)
- **Enrollment Authority** (bind device identity to attestation ecosystem)

## 157.2 Pipeline steps (minimal)

### Step 1 — Source approval
Output: signed statement that a commit/release tag is approved.

Subject:
- source tree digest / commit ID

Predicate:
- review policy satisfied; reviewers; ticket references

### Step 2 — Reproducible build
Output: SLSA provenance predicate (build recipe, builder identity, inputs/outputs).

Subject:
- firmware binary digest(s)

Predicate:
- builder identity, build parameters, materials, reproducibility attestations

### Step 3 — Test and security evaluation
Output: signed test results / security evaluation statement.

Subject:
- firmware digest(s) + hardware model

Predicate:
- test suite version, results, known limitations, lab environment hash

### Step 4 — Firmware signing
Output: statement binding firmware digest(s) to a signing event.

Subject:
- firmware digest(s)

Predicate:
- signing key ID, policy, validity window, revocation pointer

### Step 5 — Hardware assembly checkpoints
Output: per-station statements for critical assembly steps.

Subject:
- device serial / batch ID + component digests

Predicate:
- station identity, step name, measured components, QC results

### Step 6 — Device identity injection (secure element)
Output: statement that a device identity key was generated/injected under policy.

Subject:
- device identity public key (or hash)

Predicate:
- HSM policy, key ceremony references, anti-cloning measures

### Step 7 — Enrollment into attestation ecosystem
Output: statement binding device identity to reference values and endorsement set.

Subject:
- device identity

Predicate:
- allowed hardware model, initial reference value IDs, enrollment time

## 157.3 Transparency requirements

All statements MUST be:
- content-addressed (hash-stable canonical form),
- signed by the correct role key,
- published to a transparency service with receipts (CT/SCITT-style),
- and revocable (with revocation statements also logged).

## 157.4 Audit paths

A verifier/auditor should be able to traverse:

device attestation bundle → reference values + endorsements → enrollment statement →
factory checkpoints → firmware signing → build provenance → source approval

…and detect missing links.

## 157.5 What this enables

- Rapid recall / revocation with public proof.
- Independent detection of “shadow builds” or unapproved firmware.
- Public accountability for labs and manufacturing stations.
- A path to “end-to-end transparent manufacturing” that is concrete enough to argue about.

## 157.6 Next upgrades

- Define predicate schemas (JSON) for each step (source approval, build provenance, lab report, etc.).
- Choose a signing and receipt format (COSE / JWS) and a registry for signer identities.
- Decide retention and privacy rules for per-device vs per-batch statements.
