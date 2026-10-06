# ADR-0302: Breakglass supplementary adapter side evidence stays receipt-first when exported

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0300` fixed the baseline `breakglass.receipt` to stay adapter-thin.
`ADR-0301` then fixed the official support-bundle contract to stay authority-first on exact `breakglass.receipt` digests, while richer BMC / KVM / SOL / virtual-media runtime material stays supplementary until a dedicated typed family exists.

That still leaves one expensive export seam fuzzy:

**when richer breakglass adapter/runtime material really does have to leave the host or appear in a support case before that future typed family exists, what is the portable archive truth?**

If the archive leaves this implicit, implementations will drift toward one of two bad habits:

1. treating raw ticket attachment ids, portal object handles, screenshots, or operator notes as if they were the reviewable portable truth, or
2. skipping the ordinary redaction/export/transport proof chain because the material is only “supplementary” anyway.

Both are costly. The first turns case-system folklore into quasi-authority. The second weakens the archive’s export discipline exactly where the material is most vendor-shaped and policy-sensitive.

## Decision

1. Supplementary breakglass adapter/runtime side evidence stays **receipt-first** whenever it is exported or referenced portably before a dedicated typed family exists.

2. The portable archive truth remains the accompanying typed proof objects, not the raw external handle.
   When richer adapter/runtime material is represented in `incident.bundle.includes.extra[]`, prefer evidence digests for the matching:
   - `redaction.receipt` when sanitization materially shaped the exported artifact,
   - `export.receipt` for the governed export act,
   - `transport.receipt` and `transport.acceptance.receipt` when the stronger handoff lane emitted them.

3. Raw case attachment ids, portal object handles, visible upload URLs, or ticket prose are not themselves portable truth for this material.
   They may exist operationally, but they do not replace the typed receipt chain.

4. This decision does **not** mint a new first-class `incident.bundle` field family for breakglass adapter/runtime material.
   The official bundle contract still stays authority-first on `breakglass_receipt_digests`.

5. This decision also does **not** standardize the future artifact family for the richer adapter/runtime content itself.
   It standardizes only the boring export boundary worth locking now: if supplementary material travels, keep the archive-facing proof on typed receipts rather than on case-system folklore.

## Consequences

Good:

- supplementary adapter/runtime material can travel under ordinary export/redaction discipline without pretending the archive already standardized the content family itself
- detached review can still verify how the material was sanitized and handed off
- and the portable support story stays stable even when the underlying case system, portal UI, or attachment ids change

Costs:

- support cases may still contain raw attachments or vendor-specific handles, but those are explicitly second-class relative to the typed receipt chain
- operators must keep export/redaction proof if they want supplementary adapter/runtime material to remain reviewable off-host
- and the future richer artifact family still needs separate RFC/ADR work

## Follow-on

Still open as later design cuts:

- whether a dedicated breakglass adapter-side-evidence artifact family is worth standardizing
- whether that future family should gain stronger typed acceptance/reverification joins
- and which redacted adapter/runtime facts are portable enough to review across vendors
