# Supply chain step policies with in-toto layouts (optional lane)

DeriveBSD already uses **DSSE-wrapped in-toto Statements** for provenance and other attestations (`docs/71-attestations-dsse-in-toto-slsa.md`).

But there is a missing piece in most “attestations everywhere” systems:

- provenance answers *what happened for one artifact*
- we also need a way to declare *what must happen* across a workflow (build/test/sign/release), *who* is allowed to do it, and *how steps chain together*

in-toto’s older-but-still-useful concept for this is the **layout**: a signed declaration of the expected supply chain steps (“functionaries” + expected materials/products) that can be verified against recorded link/statement metadata.

References:
- in-toto spec (layout + link model): https://github.com/in-toto/docs/blob/master/in-toto-spec.md
- in-toto getting started (layout concept): https://in-toto.io/docs/getting-started/

## DeriveBSD posture

Keep this lane **optional** and **policy-driven**, but make it easy to adopt:

1) A namespace/channel can publish a `supplychain-layout-policy` object that binds:
   - a layout digest (stored in the Derive store)
   - the trust roots / key sets that are allowed to author layouts and functionary keys
   - enforcement mode (warn/deny)

2) `derive build` and CI can emit a `supplychain-verify-receipt` evidence object showing:
   - which layout policy was applied
   - which attestation/link/statement objects were consumed
   - pass/fail, with structured failure reasons

3) Promotion gates can require `supplychain-verify-receipt == pass` for:
   - public channels
   - high-assurance workloads
   - “release” targets

This avoids inventing a bespoke supply-chain DSL when a workable standard already exists.

## How it plugs into what we already have

- Attestations remain DSSE-wrapped in-toto statements (recommended in SLSA’s attestation model).
- Layout verification is a *policy decision step* that emits receipted evidence.
- Derive’s own Plan/Lock/Spec digests are still the “source of truth”; the layout policy is an additional constraint describing **allowed workflows**.

See:
- `docs/31-provenance-and-sbom.md`
- `docs/71-attestations-dsse-in-toto-slsa.md`

Last updated: 2026-02-24
