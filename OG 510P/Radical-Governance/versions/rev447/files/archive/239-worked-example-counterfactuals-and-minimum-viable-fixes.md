> NOTE: This memo is now part of the consolidated Worked Example System (see 276-worked-example-system-consolidated.md).

# Worked Example Counterfactuals & Minimum Viable Fixes


**Purpose:** turn each case cluster into compact repair sequences so readers can see what to fix first instead of only diagnosing failure.

**Person served:** implementers, auditors, memo writers, and operators who need a plausible first move rather than a perfect redesign.

**From-below:** this memo exists so the archive can say what would have made the case materially better this week, not only what a fully rebuilt institution might someday do.

---

## Counterfactual repair table

| Cluster | First 48 hours | 30-day move | 90-day move |
|---|---|---|---|
| `WX-28..31` shelter / debt / care / lockout seams | restore continuity, halt derivative penalties, and issue person-usable receipts | add carry-forward defaults and assisted/offline recovery | publish seam-failure patterns by office/vendor |
| `WX-32..35` safety transfer / billing seam / supervision feasibility / care cuts | preserve current protective state and expose the real blocker | add one visible owner across seams and a live review clock | audit failures by contractor, geography, and rubric/version |
| `WX-36..39` halt / extraction / restoration / stale-state failures | stop the next harmful edge and give the person portable proof | propagate reversal/override across all downstream systems | sample restoration lag and make-good failures independently |
| `WX-40..43` medication seam / transport exclusion / counsel continuity / missing records | bridge the live necessity and shift proof burdens back to the institution | require exportable vendor logs, continuity receipts, and notice-and-basis packets | review repeated seam and proof-failure patterns portfolio-wide |
| `WX-44..47` pending-state drift / impossible timing / bridge expiry / renewal seams | reopen the clock or restore the last safe state | add non-hardening defaults and receiving-readiness checks | publish overdue-pending, bridge-gap, and protection-drop metrics |
| `WX-48..51` invalid signatory / hidden delegated closure / dropped support-state / shadow finality | pause enforcement and issue the missing authority, closure, carry-forward, or stage packet | add countersign rules, handoff invariants, and ratification boundaries | audit expired acting orders, delegated closures, dropped support-state, and disagreement rates across review tiers |
| `WX-52..55` identity rendering / duplicate resolution / household graph / severe false-positive seams | preserve continuity, freeze punitive side effects, and emit the identity or relationship packet that is missing | add alias maps, household-edge receipts, and same-day severe-match override paths | audit false matches, bad merges, spillover harms, and cross-jurisdiction mismatch patterns |
| `WX-56..59` address-role / boundary / place-resolution / no-fixed-address seams | stop wrong-place action, preserve the last safe contact or service path, and emit the location packet that is missing | add address-role receipts, map/version traces, confidence classes, and location substitutes | audit wrong-door incidents, wrong-place actions, and unstable-address continuity failures |

## Fix packs

### Pack A — Receipt first
Use when the regime is opaque but not yet emitting person-usable artifacts. Start with `31`, `36`, `82`, and the relevant `WX-*` case.

### Pack B — Seam repair
Use when the main harm appears at a transfer, handoff, or cross-system join. Start with `70`, `109`, `114`, `125`, and cases `WX-02`, `WX-30`, `WX-32`, `WX-50`.

### Pack C — Metric discipline
Use when a threshold, score, or triage rule is doing hidden governance work. Start with `03`, `42`, `142`, and cases `WX-01`, `WX-04`, `WX-09`, `WX-28`, `WX-35`.

### Pack D — Halt propagation at the last harmful edge
Use when a stay, hardship flag, or live review exists on paper but the irreversible event can still occur. Start with `31`, `36`, `82`, `105`, `252`, and cases `WX-36`, `WX-37`.

### Pack E — Real reversal, not paper reversal
Use when a court or agency has already said the person should be restored, released, or cleared but stale state survives elsewhere. Start with `36`, `53`, `67`, `127`, `253`, `254`, and cases `WX-38`, `WX-39`.

### Pack F — Public accountability across vendor seams
Use when outsourcing or subcontracting makes it hard to find the real owner. Start with `31`, `38`, `57`, `110`, `127`, `256`, and cases `WX-33`, `WX-40`, `WX-49`.

### Pack G — Proof under contest
Use when the institution cannot produce the notice, delivery proof, or basis record it claims justifies the adverse outcome. Start with `31`, `82`, `115`, `255`, `257`, and case `WX-43`.

### Pack H — Safe-time defaults and deadline repair
Use when a missed deadline or no-show may actually be an accessibility, outage, closure, delivery, or timing failure. Start with `31`, `36`, `82`, `98`, `108`, `258`, and case `WX-45`.

### Pack I — Temporary-state discipline
Use when “pending,” “provisional,” or a bridge authorization is functioning like a hidden final decision or expiring before the next state is real. Start with `31`, `82`, `108`, `109`, `251`, `259`, and cases `WX-44`, `WX-46`.

### Pack J — Carry-forward protection at renewal seams
Use when hardship flags, accommodations, priority classes, or safety protections disappear during periodic review, migration, or recertification. Start with `82`, `109`, `127`, `140`, `260`, and case `WX-47`.

### Pack K — Valid authority chains and voidable acts
Use when a rights-affecting action may have been signed or executed by someone whose acting order, delegation, or role authority is missing, expired, or unclear. Start with `31`, `36`, `78`, `141`, `261`, and case `WX-48`.

### Pack L — Lossless handoffs and support-state carry-forward
Use when a file transfer, provider change, migration, or jurisdiction seam drops language, disability, confidentiality, representative, or safety state. Start with `82`, `98`, `109`, `127`, `262`, and case `WX-50`.

### Pack M — Tiered review without shadow finality
Use when screening, recommendation, contractor review, or lower-tier triage is being treated like a final decision without visible ratification. Start with `31`, `36`, `82`, `141`, `263`, and cases `WX-49`, `WX-51`.

### Pack N — Same-person continuity across alias, transliteration, and duplicate seams
Use when one person is being rendered several ways across systems or duplicate cleanup is creating denial, delay, or fraud suspicion. Start with `31`, `44`, `53`, `109`, `125`, `264`, and cases `WX-52`, `WX-53`.

### Pack O — Household graph and representative continuity
Use when the wrong household edge, dependent relationship, or representative link is carrying consequences across people. Start with `47`, `64`, `98`, `109`, `125`, `262`, `265`, and case `WX-54`.

### Pack P — High-consequence false-positive kill switches
Use when a severe match (death, detention, departure, sanctions, or similar) is being used faster than the institution can prove it. Start with `43`, `125`, `252`, `253`, `254`, `257`, `266`, and case `WX-55`.

### Pack Q — Address-role and unit-level integrity
Use when notice, delivery, inspection, service, or jurisdiction is being routed through the wrong address role or the wrong unit. Start with `47`, `98`, `109`, `136`, `267`, and case `WX-56`.

### Pack R — Boundary and coverage seam repair
Use when district, territory, catchment, or service-area files are deciding access without a visible map or grace routing rule. Start with `71`, `82`, `109`, `140`, `268`, and case `WX-57`.

### Pack S — Place resolution and no-fixed-address fallbacks
Use when parcel, geocode, frontage, or unit ambiguity is driving action at the wrong place, or when no-fixed-address status is being mistaken for no-contact. Start with `47`, `71`, `98`, `136`, `269`, `270`, and cases `WX-58`, `WX-59`.

## Companion memos

Use `238` to diagnose the pattern before choosing a fix pack, `241` to rehearse the new workflow, `247` when you want build-ready sequences, `250` when the first move is protection rather than redesign, `252` for in-flight stop design, `253` for restoration checks, `255` for proof failures, `256` for vendor-accountability design, `258` for usable deadline repair, `259` for temporary-state redesign, `260` for renewal seams, `261` for invalid authority chains, `262` for lossless support-state transfer, `263` for shadow-finality repair, `264` for alias/transliteration and duplicate seams, `265` for household and representative continuity, `266` for severe false-positive controls, `267` for address-role integrity, `268` for boundary-based access seams, `269` for place-resolution fallbacks, `270` for no-fixed-address continuity, and `248` when one fix should interrupt several linked harms at once.
