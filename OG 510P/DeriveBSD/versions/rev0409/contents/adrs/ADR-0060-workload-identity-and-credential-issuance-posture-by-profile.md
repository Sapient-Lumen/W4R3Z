# ADR-0060: Workload identity and credential-issuance posture by profile

- **Status:** Accepted
- **Date:** 2026-03-06

## Context

DeriveBSD already has the raw pieces for a serious workload-identity lane:
`docs/181-workload-identity-and-secretless-deploys.md` sketches a local issuance agent,
`docs/228-pki-and-identity-lifecycle-as-evidence.md` makes trust bundles and issuance receipted,
`docs/240-dynamic-service-identities.md` keeps host service identities explicit,
and `spec/workload.identity.lease.schema.json` / `spec/workload.identity.issue.receipt.schema.json` already give the archive typed contracts.

What the archive still lacked was the **product-shape default**.
Without it, incompatible stories quietly coexist:

- **A** may keep saying “brokered everything” while still normalizing shared API tokens or long-lived certs in service state.
- **B** may confuse human login/account authority with workload/service identity and let cloud tokens sprawl through AppVMs.
- **C** cannot tell whether workload identity is the preferred lane or an optional science project.
- **D** may talk about attestation and regulated production while still shipping static shared secrets in images, stations, or support kits.

We do **not** need to pick one mesh, one CA stack, or one key backend here.
We do need a stable, checkable answer to:

- when short-lived workload identity is the default instead of static tokens,
- how issuance binds to what is actually running,
- where human identity must stay separate from workload identity,
- and where attested production/service identity is mandatory enough that static shared secrets are out of bounds.

## Decision

We define workload identity as a **profile-shaped default** and thread it into `spec/examples/product.profiles.json` under the stable `workload_identity` knob.

Cross-profile guardrail:
- issuance must be **short-lived, receipted, and reviewable**,
- identity must bind to what is actually running (closure/runtime digest, declared instance identity, or an explicit adapter input),
- human identity and workload identity must remain distinct authority lanes,
- and static shared secrets or long-lived tokens are never the silent baseline.

### A) `fleet_host`

Default posture: `brokered-short-lived-digest-bound-headless`

- Fleet services obtain short-lived workload identity from a broker/agent lane.
- Issuance is tied to deployment/runtime identity rather than host folklore.
- Static shared service tokens are not the default operating model.

### B) `workstation`

Default posture: `brokered-short-lived-appvm-preferred-user-identity-separate`

- AppVMs, local dev services, and service-like workloads should prefer short-lived workload identity.
- Human login, browser/OIDC sessions, and personal account authority remain separate from workload identity.
- General interactive apps should not quietly accumulate long-lived cloud/API tokens as the baseline compatibility story.

### C) `general_os`

Default posture: `brokered-preferred-explicit-static-token-adapter`

- Workload identity is the preferred derived lane.
- Classic static-token or file-credential workflows may exist, but only as explicit adapters.
- General-purpose viability stays broad without silently redefining stricter A/B/D defaults.

### D) `appliance_factory`

Default posture: `brokered-attested-short-lived-no-static-production-secrets`

- Production/factory workloads use short-lived identities by default.
- Issuance may depend on attested/measured or otherwise stronger admission posture.
- Shipped images, stations, or support kits do not normalize static shared production secrets.

## Consequences

- Product profiles now carry a stable `workload_identity` default.
- `tools/check_product_profiles.py` must enforce this boundary so the archive cannot silently drift back into token sprawl, human/workload identity confusion, or shipped production shared secrets.
- Risk item 20 narrows from “should we decide the default?” to implementation detail: trust-domain naming, selector vocabulary, key-handle/backing choices, adapter policy, and issuance/evidence budgets.

## Non-goals

- Choosing one service-mesh or one identity-control-plane implementation.
- Forcing one workload API transport or one credential format everywhere.
- Eliminating all compatibility adapters for classic software on day 0.
- Defining the final trust-domain/federation topology here.
