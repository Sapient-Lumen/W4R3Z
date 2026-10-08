# START HERE

rev0060 closes the profile-reference granularity frontier left open by rev0059.

The current answer is:
- local assessed state may carry `profile_conformance = satisfied | fallback | unsatisfied`
- exported `profile_conformance` must be scoped by a resolvable `assessed_profile`
- `assessed_profile` names the profile whose rules were used for the assessment
- explicit `assessed_profile` references are boundary-tiered rather than globally uniform
- use `id + version/revision` when that is unambiguous
- add `authority` when names can collide or the consuming boundary is outside the sealed issuer context
- add a digest when exact retained rules matter for detached audit, safety, compliance, or mutable stores
- add a signed profile-binding record only when the issuer/binding must be independently verified
- `assessed_profile` remains local/export metadata, not a mandatory minimal wire-claim field
- profile identity and binding do not become a manifest, negotiation object, alias, or request bundle

Open next:
- `PROFILE-REFERENCE-GRANULARITY-TEST.md`
- `PROFILE-IDENTITY-EXPOSURE-TEST.md`
- `PROFILE-CONFORMANCE-MARKER-TEST.md`
- `GREENFIELD-RESPONSE-SKETCH.md`
- `frontier-ticket.json`
