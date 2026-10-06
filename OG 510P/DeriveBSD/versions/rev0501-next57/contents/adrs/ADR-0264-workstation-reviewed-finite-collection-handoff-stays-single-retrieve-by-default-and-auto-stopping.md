# ADR-0264: Workstation reviewed finite collection handoff stays single-retrieve by default and auto-stopping

Date: 2026-03-22  
Status: Accepted

## Context

`ADR-0263` fixed the first richer workstation transfer RFC target: a reviewed finite collection handoff, with the draft design surface living in `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`.

That RFC deliberately left one replay-width question open:
**should the receiving side retrieve once by default, or should the first richer lane already carry a repeated-retrieve posture?**

This is a high-leverage seam. If the first richer lane starts replay-friendly, the archive quietly reintroduces the same authority-width and support/export ambiguity that the ordinary `ui.datatransfer.*` lane spent many cuts removing. If the first richer lane instead starts single-retrieve by default and auto-stopping, the archive learns the richer collection semantics before it learns replay semantics.

## Decision

For the first reviewed finite collection handoff lane described by `RFC-0194`:

1. the first cut stays **single-retrieve by default**.
2. the handoff session **auto-stops after the first successful retrieve**.
3. any repeated-retrieve posture is **not part of the first cut** and must come back later as an explicit follow-on RFC decision inside a distinct richer-lane family, not as a default convenience.

## Consequences

- The first richer lane stays much closer to the ordinary transfer lane's anti-replay posture while still solving selected-set handoff pressure.
- Trusted UI, receipt/export, and support surfaces only need to explain one boring answer first: the reviewed collection was retrieved once, then the session ended.
- Later replay-friendly or repeated-retrieve semantics remain possible, but only as an explicit follow-on decision with their own evidence and review burden.

## Alternatives considered

- **Carry repeated-retrieve posture inside the first cut:** rejected because it widens authority and replay semantics before the archive has even finished the narrow collection-handoff story.
- **Leave retrieve semantics open for later:** rejected because implementation pressure would turn that ambiguity into product-local folklore.
- **Require explicit manual stop but not auto-stop after first retrieve:** rejected because it keeps extra live authority around after the ordinary successful path for little first-cut benefit.

## Related

- `adrs/ADR-0263-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/673-workstation-first-richer-datatransfer-rfc-target-is-reviewed-finite-collection-handoff.md`
- `docs/674-workstation-reviewed-finite-collection-handoff-stays-single-retrieve-by-default-and-auto-stopping.md`
- `rfcs/RFC-0194-reviewed-finite-collection-handoff-session.md`
