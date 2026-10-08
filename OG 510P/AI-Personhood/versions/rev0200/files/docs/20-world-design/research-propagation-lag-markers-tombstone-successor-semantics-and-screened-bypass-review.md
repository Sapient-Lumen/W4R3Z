# AI-person research propagation-lag markers, tombstone-successor semantics, and screened-bypass review

## Thesis

Once the archive fixes family-scope propagation, visible tombstones for withdrawn contradiction summaries, and expiry / reinstatement rules for screened or quarantined filing status, a narrower operational gap remains. A family object may still admit that linked records are stale without saying exactly when lag becomes a public mismatch state; a tombstone may still preserve history without making the successor chain legible enough for ordinary readers and machines; and protected emergency, participant, or witness routes may remain formally open during screened status without any rule for repeated attempted use of those routes as an end-run around ordinary screening. A personhood world therefore needs one more compact rule: **propagation lag must mature on short visible clocks, withdrawn contradiction summaries must expose a minimum predecessor / successor chain rather than a dead end, and repeated use of protected bypass routes during screened status must trigger sealed review of route use without closing the protected route itself.** `[REF-0318]` `[REF-0326]` `[REF-0347]` `[REF-0358]` `[REF-0364]` `[REF-0367]` `[REF-0368]` `[REF-0369]` `[REF-0370]` `[REF-0371]` `[REF-0372]`

---

## 1. Why the archive needs this layer

The previous surface already fixed the high-level duty: family-wide findings must propagate, withdrawn contradiction summaries must leave tombstones, and screened filing status must clear by stated terms rather than by drift. But three practical ambiguities still remained.

First, **a propagation-lag marker without a lag clock is too soft**. Current official governance already treats rectification and downstream notification as time-sensitive rather than optional. GDPR Articles 16 and 19 require rectification without undue delay and communication of rectification, erasure, or restriction to recipients unless that proves impossible or disproportionate. `[REF-0367]` CTIS and public trial-versioning practice likewise assume identifiable record versions and short public-update expectations rather than leisurely silent divergence. `[REF-0326]` `[REF-0364]` A personhood archive therefore needs an exact visible lag ladder, not just the word “lag.”

Second, **a tombstone without successor semantics can still mislead**. Public history is not preserved merely by leaving a dead label behind. PMC policy says corrected-and-republished articles should carry updated citation metadata, a unique DOI, details of the changes, and a visible link from the original to the updated version, while the original remains in the archive. `[REF-0368]` Crossref's current guidance similarly says significant updates should ordinarily issue as separate update objects with typed update metadata linking the changed item and the updating item, and warns that in-situ changes obscure the scholarly record. `[REF-0369]` `[REF-0370]` If the archive wants contradiction-tombstone history to remain legible, it must say what successor information a tombstone has to expose.

Third, **protected bypass routes need review rules once ordinary screening exists**. Current protected-complaint systems already show the conservative ingredients. Complaints may often be filed by a representative, in any language, orally or in writing, and with any responsible office rather than only the formally preferred inbox. `[REF-0358]` `[REF-0371]` At the same time, administrative systems still preserve tools for dismissing repetitious or insufficient filings, for screening abusive conduct, and for addressing frivolous or bad-faith use after review. `[REF-0360]` `[REF-0361]` `[REF-0362]` `[REF-0371]` The archive therefore needs a rule that protects the bypass lane without letting it become either a silent loophole or a silent target.

---

## 2. Exact propagation-lag clocks and public mismatch semantics

The archive now fixes one exact timing rule for public propagation mismatch: **once a family-wide or shared-component finding becomes controlling, linked public records must either synchronize on short clocks or move into typed visible lag states that prevent any stale record from looking cleaner than the controlling family state.** `[REF-0318]` `[REF-0326]` `[REF-0364]` `[REF-0367]` `[REF-0370]`

### A. Two clocks, not one

The archive now distinguishes two clocks.

1. **Immediate-control clock (`L0`)** — the controlling family object and any directly affected protocol or deployment-facing record that a current participant, purchaser, deployer, or reviewer is likely to rely on in real time must be updated within **1 business day** of the controlling finding.
2. **Ordinary linked-sync clock (`L1`)** — all remaining linked lineage, protocol-history, and aggregate comparison objects that materially rely on the affected family must be synchronized within **5 business days**. `[REF-0318]` `[REF-0364]` `[REF-0367]`

This is a conservative archive rule. It does not demand instantaneous perfection across every mirror. It does demand that the most relied-on public surfaces stop looking clean almost immediately and that the rest not linger in contradiction for long.

### B. Typed lag states

If `L0` or `L1` is missed, the family object must expose one of three typed public lag states:

- `lag-open` — at least one required linked record missed its clock, but the oldest stale record is still under **10 business days** old;
- `lag-material` — one or more required linked records remain stale at **10 business days or more**, or a stale record still presents a materially cleaner state than the controlling family object;
- `lag-default` — one or more required linked records remain stale at **30 calendar days or more**, or the authority concludes the sponsor is not using reasonable efforts to synchronize the public layer. `[REF-0326]` `[REF-0364]` `[REF-0367]` `[REF-0370]`

### C. What the public mismatch marker must show

A visible lag marker should ordinarily expose:

- the controlling family or cluster identifier;
- the triggering finding or superseding-notice identifier;
- how many linked records remain stale;
- the age band of the oldest stale record;
- whether any stale record still appears cleaner than the controlling state;
- and the next required synchronization or review date. `[REF-0326]` `[REF-0364]` `[REF-0370]`

### D. Fallback display rule

A stale linked object may remain reachable for traceability, but while any lag state is live it must not display a cleaner operative status than the controlling family object. If local synchronization is not yet complete, the linked object must fall back to a short banner or header that points users to the controlling family state. `[REF-0318]` `[REF-0364]` `[REF-0367]`

### E. Lag review is about publication integrity, not merits reversal

A lag state does not reopen the underlying merits by itself. It marks a publication-integrity failure. Merits change still requires the underlying review, correction, or reactivation route. `[REF-0326]` `[REF-0359]`

---

## 3. Minimum tombstone-successor semantics

The archive now fixes one minimum successor rule for withdrawn contradiction summaries: **every tombstone must make clear whether the withdrawn object has no public successor, one successor, or a bounded set of successors, and every successor must link back to the tombstone or predecessor it supersedes.** `[REF-0326]` `[REF-0368]` `[REF-0369]` `[REF-0370]` `[REF-0372]`

### A. Minimum tombstone fields

A withdrawn contradiction tombstone should ordinarily expose:

- the withdrawn public identifier;
- the withdrawal date;
- the bounded withdrawal reason code;
- the successor relation type (`none`, `replaced-by`, or `split-into`);
- the successor identifier or identifiers if any exist;
- whether a protected fuller lane remains open, sealed, or closed;
- and the current controlling caution state affected by the withdrawal. `[REF-0326]` `[REF-0359]` `[REF-0368]` `[REF-0369]`

### B. Back-link rule

Where a successor exists, the successor object must link back to the withdrawn identifier and state the relation in the opposite direction (`replaces`, `partly succeeds`, or similar). A successor is not complete if only the tombstone points forward. `[REF-0368]` `[REF-0369]` `[REF-0370]`

### C. No silent identifier recycling

The archive now fixes a negative rule too: a withdrawn contradiction identifier may not later be silently reused for a different live summary. Crossref's current DOI guidance already treats persistence as the default, disfavors deletion, and says withdrawn items should point to a withdrawal or retraction notice rather than vanish. `[REF-0372]` The archive should follow the same discipline here.

### D. No dead-end withdrawal pages

A tombstone may protect sensitive content by withholding the substantive contradiction text, but it may not become a dead end when a public successor exists. Ordinary readers should be able to tell whether they have reached the end of the line or whether a replacement object now carries the live public meaning. `[REF-0368]` `[REF-0369]` `[REF-0370]`

### E. Limited branching only

The archive keeps this narrow: a single withdrawn contradiction summary may point to more than one successor only where the authority expressly finds that the original public object improperly collapsed distinct contradiction paths into one. Even then, the tombstone must say that the object split and list the bounded successor set. `[REF-0368]` `[REF-0369]`

---

## 4. Screened-bypass review without closure of protected routes

The archive now fixes one compact rule for protected-route use during screened status: **repeated use of emergency, participant-harm, retaliation, or witness-protection routes by a screened or quarantined filer may trigger sealed bypass review, but not automatic closure of the protected route itself.** `[REF-0347]` `[REF-0348]` `[REF-0358]` `[REF-0360]` `[REF-0361]` `[REF-0362]` `[REF-0371]`

### A. What counts as bypass use

Bypass use means filing through a protected route that remains open despite ordinary screening or channel quarantine because the filing alleges participant harm, retaliation, witness risk, urgent noncompliance, or another protected reason that the ordinary lane is not safe enough to handle.

### B. Trigger for sealed bypass review

A sealed bypass review should ordinarily open when either:

- the same screened actor or represented filing family makes **3 or more** protected-route filings within **30 days** that are found substantially duplicative and non-urgent;
- or the authority sees a reasoned pattern that ordinary dissatisfaction is being relabeled as emergency or retaliation solely to evade the screened lane. `[REF-0360]` `[REF-0361]` `[REF-0362]` `[REF-0371]`

The trigger opens review; it does not itself reject the filing.

### C. Questions the bypass review must ask

Bypass review should ask at least:

- whether any filing presented genuinely new harm, new retaliation, or new witness-risk evidence;
- whether repeated protected use reflects abuse by the filer or failure of the ordinary screened lane to provide a safe receivable path;
- whether the actor's screened status should remain unchanged, be narrowed, be renewed, or be allowed to lapse;
- and whether route design changes are needed so protected filings remain possible without uncontrolled duplication. `[REF-0347]` `[REF-0348]` `[REF-0358]` `[REF-0371]`

### D. Permitted outcomes

After review, the authority may:

- keep the protected route unchanged;
- require a single protected relay channel or designated relay representative for that filing family;
- require a short protected cover sheet classifying the asserted emergency basis;
- route future non-urgent duplicative matter back to the screened ordinary lane with a reasoned notice;
- or renew / modify the screened order in light of the new pattern. `[REF-0360]` `[REF-0361]` `[REF-0362]` `[REF-0371]`

### E. Forbidden outcomes

The authority should not:

- auto-reject protected filings unseen because the filer is screened;
- treat the opening of bypass review as proof that the new filing lacks urgency;
- or terminate every emergency, participant, or witness route for the screened actor. `[REF-0347]` `[REF-0348]` `[REF-0358]` `[REF-0371]`

At least one human-reviewed protected path must remain available while screened status remains live.

---

## 5. Edge tests

### A. The family record updates immediately, but two linked benchmark-comparison tiles and one historical protocol page remain stale for eight business days

The family object enters `lag-open` when the ordinary sync clock expires. If the stale state crosses ten business days, it becomes `lag-material`. Any stale tile must fall back to the controlling family state rather than continuing to display cleaner public status. `[REF-0326]` `[REF-0364]` `[REF-0367]`

### B. An anonymous contradiction summary is withdrawn because it was attached to the wrong family, and the authority issues a new public summary under the correct family

The old public object remains as a tombstone with the withdrawal reason and a forward link to the new summary. The new summary links back to the withdrawn one as its predecessor. `[REF-0368]` `[REF-0369]` `[REF-0370]` `[REF-0372]`

### C. A screened filer submits four protected-route filings in three weeks; three repeat old disagreement points, but one attaches fresh sealed logs showing retaliation against a participant-interpreter

The authority opens sealed bypass review because the threshold is met, but the fresh retaliation filing remains receivable on the merits. The proper response is route review and possible relay redesign, not blanket closure of the protected lane. `[REF-0347]` `[REF-0348]` `[REF-0358]` `[REF-0371]`

### D. A withdrawn contradiction summary has no public successor because the underlying protected filing proved non-authentic and the public contradiction lane should no longer carry it at all

The tombstone says `successor relation: none`, states the bounded withdrawal reason, and indicates whether the protected fuller lane is closed or separately continuing on another issue. No silent deletion and no fake successor are allowed. `[REF-0358]` `[REF-0368]` `[REF-0372]`

---

## 6. Compression summary

The archive now tightens AI-person research caution governance one step further:

- **family-wide propagation now runs on exact short clocks rather than on undefined lag**;
- **stale linked objects now mature through typed visible mismatch states rather than a generic lag label**;
- **withdrawn contradiction tombstones must now expose minimum predecessor / successor semantics rather than leaving a historical dead end**;
- **successor objects must now point back as well as tombstones pointing forward**;
- **screened or quarantined status no longer leaves protected bypass use wholly ungoverned**;
- and **repeated protected-route use now triggers sealed bypass review and possible relay redesign without shutting the protected route itself**.

This is still a tight doctrine. The archive now fixes those immediate follow-on questions in `docs/20-world-design/research-lag-state-field-schema-split-successor-chains-and-protected-relay-minimums.md` and `docs/20-world-design/research-lag-field-extension-namespaces-downgrade-merge-alias-and-relay-federation-overflow.md`, and `docs/20-world-design/research-extension-namespace-admission-retirement-contested-merge-alias-review-and-relay-capacity-attestations.md`: lag markers now have a fixed machine-readable core, split successor chains now publish bounded maps with declared head state, non-core lag fields extend through declared namespaces with downgrade rules, later public reconciliation distinguishes merge from alias while preserving history, and protected bypass now runs through sealed federated relay with one accountable owner at a time. Remaining work is narrower still, and the archive now fixes it in `docs/20-world-design/research-relay-attestation-object-panel-quorum-recusal-and-deprecated-namespace-migration-windows.md`: protected relays now publish one bounded machine-readable attestation object, contested reconciliation panels now run on explicit quorum and recusal rules, and deprecated namespaces now move through visible migration windows. The archive now fixes those immediate follow-on questions in `docs/20-world-design/research-low-volume-relay-suppression-cross-roster-substitutes-and-closed-legacy-cutover.md`: low-volume `RAT-1` cells now follow a public 20 / 10 ladder with nearest-five rounding or suppression plus secondary protection against differencing, merits review must move to predeclared cross-roster substitutes when local recusals exhaust the ordinary panel, and overstayed deprecated namespaces now enter a closed-legacy state that bars new public use while preserving historical parse and successor redirection. The next gap is narrower again: when perturbation-grade publication should be preferred over threshold rounding or suppression for especially sensitive relay outputs, how emergency external substitute appointments may be challenged without reopening the merits, and what replay / export / backfill duties persist once a namespace is closed-legacy or fully retired.

---

## Cross-links

- `docs/20-world-design/research-family-scope-propagation-tombstones-and-screened-filer-clearance.md` fixes the broader propagation, tombstone, and clearance doctrine that this surface now makes exact.
- `docs/20-world-design/research-slice-family-reactivation-correction-route-and-serial-filing-escalation.md` fixes the scope matrix and screening ladder that this surface now supplements with lag clocks and bypass review.
- `docs/20-world-design/research-reactivation-evidence-floors-anonymous-contradiction-summaries-and-post-disposition-filing-rules.md` fixes the evidence-floor and anonymous-summary layer that this surface now hardens with typed successor semantics.
- `docs/20-world-design/research-phased-reactivation-participant-contradiction-and-anti-flood-reply-controls.md` fixes phased continuation and contradiction shielding, while this surface prevents screened protected routes from becoming either unusable or unlimited.
- `docs/20-world-design/protected-disclosure-review-packets-secrecy-override-and-controlled-contradiction.md` fixes the broader secrecy / contradiction architecture that helps justify protected continuation even when public contradiction objects are withdrawn or screened.

The next gap is narrower again: what low-volume suppression thresholds protected relays should use, what substitute-panel sourcing route should apply when recusals exhaust the ordinary roster, and what hard cutover or parser-guarantee rules should apply when deprecated namespaces remain live past the migration window.

---

## Bottom line

A personhood world should not let linked public records stay stale on unspecified clocks, should not preserve a withdrawn contradiction summary only as a historical dead end, and should not answer repeated protected-route use during screened status with either automatic closure or helpless drift. The archive therefore now fixes one more compact rule: **propagation lag matures on short visible clocks, withdrawn contradiction summaries must expose minimum successor semantics, and repeated protected bypass use triggers sealed review without extinguishing the protected route.** `[REF-0318]` `[REF-0326]` `[REF-0347]` `[REF-0358]` `[REF-0364]` `[REF-0367]` `[REF-0368]` `[REF-0369]` `[REF-0370]` `[REF-0371]` `[REF-0372]`
