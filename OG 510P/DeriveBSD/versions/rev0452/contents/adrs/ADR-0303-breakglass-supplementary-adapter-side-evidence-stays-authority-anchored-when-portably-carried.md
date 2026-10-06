# ADR-0303: Breakglass supplementary adapter side evidence stays authority anchored when portably carried

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0301` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`ADR-0302` then fixed that if richer supplementary breakglass adapter/runtime material travels before a dedicated typed family exists, the portable archive story stays receipt-first on typed redaction/export/transport proof instead of raw case attachment folklore.

That still leaves one expensive ambiguity:

**can those supplementary receipt chains stand on their own in a portable bundle or support handoff, or must they remain explicitly anchored to typed breakglass authority proof?**

If the archive leaves this fuzzy, implementations will drift toward a new failure mode:

1. a case exports redaction/export/transport receipts for screenshots, SOL traces, virtual-media diagnostics, or console captures,
2. but omits the exact `breakglass.receipt` digest that says emergency authority actually participated,
3. and later reviewers must guess whether those exported artifacts were really breakglass evidence, ordinary troubleshooting detritus, or even the wrong host/session entirely.

The adapter/runtime receipts are useful, but they do not self-authenticate emergency authority. They are second-order handling proof around stronger, implementation-shaped artifacts.

## Decision

1. Supplementary breakglass adapter/runtime side evidence may travel portably only when it stays **authority-anchored** to exact `breakglass_receipt_digests` in the same portable story.

2. `incident.bundle.includes.extra[]`, external case attachments, and the associated redaction/export/transport receipt chain do **not** replace or imply emergency-access authority on their own.

3. If richer supplementary breakglass adapter/runtime material is exported or referenced portably, the same bundle or handoff should include at least one matching `breakglass.receipt` digest describing the governing emergency session.

4. This decision does **not** mint first-class bundle fields for the richer adapter/runtime material itself.
   It only closes the remaining ambiguity around portable interpretation: the supplementary receipt chain stays second-class and must remain anchored to typed breakglass authority proof.

5. This decision also does **not** define automatic same-host or same-session matching rules for future richer adapter-side-evidence families.
   For now, it establishes the smaller invariant worth locking immediately: portable support/export stories must carry the authority record that makes supplementary adapter/runtime receipts intelligible.

## Consequences

Good:

- detached review no longer has to infer emergency authority from transport history or ticket context
- the official support story remains stable even when attachment ids, portal handles, or case systems churn
- and richer adapter/runtime material can remain supplementary without becoming semantically orphaned

Costs:

- support/export tooling must keep at least one exact `breakglass.receipt` digest alongside the supplementary receipt chain whenever this richer material travels
- some older case practices that relied on screenshots or upload receipts alone will now be recognized as incomplete portable evidence
- and a future richer typed family still needs separate RFC/ADR work if DeriveBSD ever wants stronger per-artifact/session joins

## Why this is the right narrow cut

The primary management sources keep console/media facilities separate from authorization/session management surfaces. Redfish documents `VirtualMedia`, `SerialConsole`, `GraphicalConsole`, `AccountService`, and `SessionService` as distinct resources/properties rather than one self-authenticating emergency-access artifact family. Separately, NIST SP 800-86 stresses preserving integrity and chain of custody when evidence is gathered, handled, and transported. Together, those are a good fit for DeriveBSD's bundle contract: receipt chains describing how supplementary artifacts were sanitized or exported are useful, but they still need the typed authority record that says why they belong to a breakglass story at all.

## Follow-on

Still open as later work:

- whether a dedicated breakglass adapter-side-evidence artifact family is worth standardizing
- whether that future family should carry stronger same-session or same-console joins
- and whether official support handoff ever needs typed acceptance/reverification joins specialized for emergency-session side evidence
