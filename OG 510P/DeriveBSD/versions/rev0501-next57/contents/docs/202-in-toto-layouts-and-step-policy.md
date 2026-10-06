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

   This is a **workflow-constraint policy**, not a release-authority object.

2) `derive build` and CI can emit a `supplychain-verify-receipt` evidence object showing:
   - which layout policy was applied
   - which attestation/link/statement objects were consumed
   - pass/fail, with structured failure reasons

   The receipt is **supplemental workflow-verification evidence** only. A passing receipt should be allowed to gate publication, but it is not itself publication authority.

3) Promotion gates can require `supplychain-verify-receipt == pass` for:
   - public channels
   - high-assurance workloads
   - “release” targets

   If publication review consults workflow verification, the decision should be summarized in `release.publish.receipt.supplychain_verification` rather than inferred from loose CI folklore. The authoritative publish answer still lives in `release.publish.receipt`.

This avoids inventing a bespoke supply-chain DSL when a workable standard already exists.

## How it plugs into what we already have

- Attestations remain DSSE-wrapped in-toto statements (recommended in SLSA’s attestation model).
- Layout verification is a *policy decision step* that emits receipted evidence.
- `release.authority.policy` remains the only publication-authority policy; workflow verification stays supplemental.
- Derive’s own Plan/Lock/Spec digests are still the “source of truth”; the layout policy is an additional constraint describing **allowed workflows**.

See:
- `docs/31-provenance-and-sbom.md`
- `docs/71-attestations-dsse-in-toto-slsa.md`

Last updated: 2026-03-07r218
