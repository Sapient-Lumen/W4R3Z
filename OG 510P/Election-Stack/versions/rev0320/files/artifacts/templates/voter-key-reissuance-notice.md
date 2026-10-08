# Public notice: credential reissuance / recovery update (template)

**Track:** Shared (cross-cutting)

This is a **drafting** template. The canonical publishable artifact SHOULD be a signed `PublicNotice`:
- kind: `hfv.public.notice`
- notice_type: `incident_advisory` (or `status_update` if routine)

Drafting discipline:
- Do not hedge (“likely / appears / seems / probably”) as a substitute for accountability.
- Use explicit epistemic tags (`DOC:docs/218-epistemic-status-tags-and-confidence-rubric.md`) and make missingness visible (`DOC:docs/219-uncertainty-safe-public-updates.md`).
- Prefer **digest pointers** (packet/manifest/checkpoint IDs) over screenshots.


**Date/Time:** 

**Summary (plain language):**
- [OBSERVED|HIGH] What happened (known facts only):
- [OBSERVED|HIGH] What we did immediately:
- [OBSERVED|HIGH] What voters should do now:
- [UNKNOWN|HIGH] What we do not know yet (if any):

**What is affected:**
- [TAG|CONF] Which counties/precincts (if known):
- [TAG|CONF] Which credential types:

**How voting continues safely:**
- [OBSERVED|HIGH] In-person recovery locations/hours:
- [OBSERVED|HIGH] Paper-of-record fallback:

**Evidence and transparency:**
- Latest witness-quorum checkpoint ID + digest (if applicable):
- Packet manifest digest (if publishing a packet):
- PublicNotice feed digest (if available):

**Next update time:**
