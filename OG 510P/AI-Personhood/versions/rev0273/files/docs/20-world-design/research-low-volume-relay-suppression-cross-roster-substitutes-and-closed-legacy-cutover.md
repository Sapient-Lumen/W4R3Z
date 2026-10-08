# AI-person research low-volume relay suppression, cross-roster substitutes, and closed-legacy cutover

## Thesis

Once the archive fixes one bounded relay attestation object, explicit contested-panel quorum / recusal, and visible migration windows for deprecated namespaces, one narrower execution seam remains. Very small protected-relay volumes can still create a false choice between unsafe disclosure and silent disappearance; recusal can still exhaust the ordinary merits roster and tempt ad hoc local improvisation; and deprecated namespaces can still overstay their migration clocks because everyone expects eventual retirement while no public cutover state is actually triggered. A personhood world therefore needs one more compact rule: **low-volume protected-relay publication must follow a public disclosure ladder that distinguishes exact, rounded-or-banded, and suppressed cells with secondary protection against differencing; final contested review must move to pre-declared cross-roster substitutes when local recusal exhausts the ordinary panel, with merits paused rather than improvised if that source is unavailable; and any deprecated namespace that survives past its retirement-review window without a granted extension must enter a closed-legacy state that bars new public use while preserving historical parsing and visible successor redirection.** `[REF-0376]` `[REF-0381]` `[REF-0383]` `[REF-0385]` `[REF-0386]` `[REF-0389]` `[REF-0390]` `[REF-0393]` `[REF-0394]` `[REF-0395]` `[REF-0396]` `[REF-0397]` `[REF-0398]` `[REF-0399]`

---

## 1. Why the archive needs this narrower layer

The prior surface already established that protected relays must publish a `RAT-1` object, that contested reconciliation panels must have three unconflicted merits members, and that deprecated namespaces must move through visible no-new-use, compatibility-support, and retirement-review windows. But three practical failures still remained.

First, **small-n transparency can still leak or vanish**. Official statistical-disclosure practice already converges on the conservative core: counts below ten are often suppressed, values just above that threshold are often rounded or otherwise coarsened, and rates or ratios based on counts below twenty are often treated as unstable or unreliable. ONS now describes the classic “10-5 rule” as suppressing counts below ten and rounding counts above ten to the nearest five; CDC mortality publications suppress counts from zero to nine and mark rates based on counts below twenty as unreliable. `[REF-0393]` `[REF-0394]` `[REF-0395]` That means the archive no longer needs to treat small-volume relay publication as a bespoke problem. It can borrow a conservative public ladder.

Second, **recusal exhaustion cannot be solved by necessity logic**. Official review practice already makes three things clear: alternates must be predesignated and comparable to the members they replace; substitution should be documented; and no final vote may proceed once quorum is lost through conflict unless quorum is restored. OHRP guidance and related procedures treat alternate substitution as normal when a primary member is absent or recused, but they also forbid further action when quorum fails. `[REF-0397]` `[REF-0398]` In an AI-person archive, that means a conflicted local body may not finish a public identity-history case merely because it has no one else on hand.

Third, **migration windows need a real terminal state**. Current Internet registry practice already provides the conceptual materials: registries can carry explicit lifecycle status, can be updated rather than silently rewritten, and in some cases are closed to new entries while users are redirected to the successor record. `[REF-0381]` `[REF-0383]` `[REF-0399]` The archive therefore now needs one exact terminal state between “deprecated” and “erased”: closed to new public authoring, still parseable historically, visibly redirected forward.

---

## 2. Low-volume relay publication: exact / rounded / suppressed ladder

The archive now fixes one compact low-volume publication rule for `RAT-1`: **every reporting period still produces a visible attestation object, but each quantity-bearing cell must follow a published 20 / 10 disclosure ladder rather than local intuition.** `[REF-0386]` `[REF-0393]` `[REF-0394]` `[REF-0395]`

### A. Public ladder for count-like cells

For count-like `RAT-1` cells such as intake volume, overflow volume, and spillover-destination count, the default rule should be:

- **exact** publication is permitted only where the underlying count is **20 or more** and no separately published context would make the exact value effectively identifying;
- **rounded or banded** publication is required where the underlying count is **10 through 19**;
- **suppressed** publication is required where the underlying count is **0 through 9**. `[REF-0393]` `[REF-0394]` `[REF-0395]`

The archive takes the `20 / 10` ladder because it is conservative in two distinct ways already visible in official practice: below ten, exact counts create direct disclosure risk; below twenty, ratio-like presentation or false precision becomes unstable enough that public interpretation is unreliable.

### B. Allowed public forms for the middle band

Where a count falls in the 10-to-19 interval, the relay may choose **one declared middle-band method** and must keep it stable within a methodology version:

- **nearest-five rounding** (`10`, `15`, `20`),
- **narrow bands** (`10–14`, `15–19`), or
- **declared perturbation-with-threshold** where the method is published, auditable, and designed so users cannot infer the true value from related tables. `[REF-0395]` `[REF-0396]`

The relay may not switch opportunistically among those methods from month to month in order to make strain look smaller or larger. Method changes require a new `method_version`, a short public reason, and an out-of-cycle attestation update. `[REF-0386]` `[REF-0395]`

### C. Secondary-protection rule

A suppressed or rounded cell is not safe if the rest of the table lets the public recover the hidden value by subtraction. Official disclosure-control guidance is explicit that low-value suppression often requires additional protection against differencing and that sparse tables may need recoding, broader grouping, or secondary suppression. `[REF-0396]` Therefore:

- if one `RAT-1` cell is suppressed, any linked total or subcell that would reveal it must itself be rounded, banded, or suppressed;
- if one count-like cell is rounded, any published arithmetic combination that would reveal the pre-rounded value must be coarsened to the same or a broader level;
- and if no coherent public release is possible after secondary protection, the relay should still publish the object with the cell state `suppressed` and a reason code such as `low_n_secondary_risk` rather than disappearing for the period. `[REF-0395]` `[REF-0396]`

### D. Ratio and performance cells

Performance cells such as acknowledgement timeliness or owner-assignment timeliness should not publish a seemingly precise percentage when the underlying numerator or denominator sits below the exact-publication floor. In that case the relay should:

- suppress the rate entirely,
- publish only a broad qualitative state such as `on-clock`, `slipping`, or `material-delay`, or
- publish a trailing multi-period band if the relay’s declared method aggregates enough periods to cross the exact or middle-band threshold without creating a new differencing route. `[REF-0386]` `[REF-0393]` `[REF-0394]` `[REF-0396]`

### E. Visibility even when volume is tiny

Low volume does not cancel publication. The relay must still publish the `RAT-1` object, its service state, its methodology version, and whether small-n suppression was used. Silence is not a privacy technique; it is a governance failure. `[REF-0376]` `[REF-0386]`

---

## 3. Cross-roster substitute sourcing when local recusal exhausts the panel

The archive now fixes one compact exhaustion rule for contested merits review: **a local authority gets the first chance to staff a three-person unconflicted panel from its primary roster and predeclared alternates, but if recusal or incapacity still leaves it below final merits quorum, the case must move to a predeclared external substitute roster rather than local improvisation.** `[REF-0385]` `[REF-0389]` `[REF-0390]` `[REF-0397]` `[REF-0398]`

### A. First source: local primary roster plus named alternates

Each authority handling contested merge-or-alias review should maintain:

- a **primary reconciliation roster**,
- a **named alternate roster** whose members are comparable in competence and role to the primaries they may replace,
- and one or more **external reciprocal rosters** available under standing agreement before any case arises. `[REF-0397]` `[REF-0398]`

When a primary member is absent or recused, a designated alternate may replace that member for the relevant stage, and the public file must show that substitution and its reason code. `[REF-0397]`

### B. Second source: reciprocal external roster

If the authority still cannot produce three unconflicted merits members after using its designated alternates, the case must move to a **reciprocal external roster** already named in public procedure. That external roster should ordinarily come from a federation-level body, a mutually designated peer authority, or an independent secretariat under standing agreement rather than ad hoc invitation by the conflicted local decision-makers themselves. `[REF-0389]` `[REF-0390]` `[REF-0397]` `[REF-0398]`

The archive prefers this rule because it addresses the real abuse risk: once local actors know the merits stakes, they may be tempted to shop for a substitute who shares their institutional interest. Predesignation, public procedure, and reciprocal sourcing reduce that risk.

### C. What the local body may still do while exhausted

If the local body has fallen below final merits quorum and no reciprocal substitute panel has yet been seated, it may still issue or continue **interim preservation measures only**: no-delete, no-redirect, no-silent-merge, scheduling, and record-preservation orders. It may not decide the merits. `[REF-0389]` `[REF-0390]` `[REF-0398]`

### D. Appointment discipline

External substitutes should ordinarily be selected through one declared method such as rotation, random draw within qualification class, or secretariat assignment under public conflict rules. The local conflicted body may not privately negotiate for a preferred substitute after the dispute is already live. `[REF-0385]` `[REF-0389]` `[REF-0390]`

### E. Public notice object

The archive now fixes a compact notice family for this stage: **`SPR-1` (Substitute Panel Route notice)**. A `SPR-1` notice should ordinarily identify:

- the case identifier,
- which local seats became unavailable,
- whether the cause was recusal, incapacity, vacancy, or timing failure,
- the external roster source invoked,
- the selection method used,
- and whether the case remains in preservation-only status pending full seating. `[REF-0385]` `[REF-0389]` `[REF-0397]` `[REF-0398]`

---

## 4. Closed-legacy cutover for overstayed deprecated namespaces

The archive now fixes one exact terminal state for namespaces that outlive their migration window without a granted extension: **at the end of the retirement-review window, any still-live deprecated namespace automatically enters `closed-legacy` status unless the authority has already published a reasoned extension notice.** `[REF-0377]` `[REF-0381]` `[REF-0383]` `[REF-0399]`

### A. What `closed-legacy` means

`closed-legacy` means four things at once:

1. **no new public authoring** — newly created public objects may not originate the namespace;
2. **ingest rejection for new use** — registries and public submission tools should reject new submissions that still attempt to author in the closed-legacy namespace;
3. **historical parse guarantee** — existing historical records remain parseable and visibly labeled as closed-legacy rather than broken or erased;
4. **successor redirection** — every registry surface that still encounters the old namespace must publish the successor or replacement guidance at the point of use. `[REF-0377]` `[REF-0383]` `[REF-0399]`

This is the archive’s answer to the familiar failure mode where “deprecated” really means “still everywhere forever.”

### B. Parser-guarantee rule

A closed-legacy namespace is not current, but it is still part of the historical record. Public parsers therefore should:

- recognize the namespace on legacy objects,
- emit a visible `closed_legacy = true` marker,
- attach the successor namespace or mapping guidance where one exists,
- and preserve the original historical token in export, audit, and challenge views. `[REF-0375]` `[REF-0377]` `[REF-0383]` `[REF-0399]`

They should not silently drop the field, silently reinterpret it as if it had already been upgraded, or fail closed in a way that makes the old record appear malformed when the real issue is only lifecycle status.

### C. Conversion and backfill rule

Where a registry stores or republishes a legacy object in transformed form, it may generate a mapped successor representation, but it must keep a link to the original namespace expression and record that a conversion occurred. Historical AI-person caution records should not lose contestability merely because a parser upgraded them. `[REF-0375]` `[REF-0377]`

### D. Extension after cutover

A post-cutover extension is possible but should be exceptional. The authority must publish why closed-legacy proved insufficient, what dependence remains, why prior migration support failed, and the new cutover date. The extension does not reopen ordinary new public authoring unless that extraordinary reopening is itself justified expressly. `[REF-0381]` `[REF-0383]`

### E. Public notice object

The archive now fixes a compact notice family here too: **`CLC-1` (Closed-Legacy Cutover notice)**. A `CLC-1` notice should ordinarily identify:

- the namespace,
- its original deprecation date,
- the expired retirement-review date,
- the new `closed-legacy` effective time,
- the successor guidance,
- whether any emergency extension or ingest waiver exists,
- and where historical parsing remains available. `[REF-0377]` `[REF-0383]` `[REF-0399]`

---

## 5. Edge tests

### A. A relay handled 7 protected matters in a month and none in the prior month

It still publishes the `RAT-1` object for the month. Intake and overflow cells are suppressed; linked totals that would reveal the hidden count are also coarsened or suppressed; service state, methodology version, and a small-n marker still appear publicly. `[REF-0393]` `[REF-0396]`

### B. A relay handled 13 matters, with 11 acknowledged on time

It may not publish `13` and `84.6%` as if that were ordinary precision. It should use its declared middle-band method for the count and either band or qualitatively classify the timeliness cell. `[REF-0394]` `[REF-0395]`

### C. Two local panel members recuse and the only remaining alternate is also conflicted

The local body may preserve the record and pause redirection, but it may not decide the merits. A `SPR-1` notice is issued and the case moves to the predeclared external roster. `[REF-0389]` `[REF-0390]` `[REF-0397]` `[REF-0398]`

### D. A deprecated namespace remains common after 18 months because several tools never migrated

It automatically enters `closed-legacy` unless a reasoned extension has already been published. New public authoring is rejected; historical records still parse; registry surfaces point users to the successor namespace rather than pretending the old one is still ordinary. `[REF-0377]` `[REF-0383]` `[REF-0399]`

### E. A parser meets a historical object that uses a closed-legacy namespace and a live extension namespace in the same record

The parser preserves both, marks the old namespace as closed-legacy, applies successor guidance only where the mapping is declared, and does not silently collapse the mixed record into the newer namespace. `[REF-0375]` `[REF-0377]` `[REF-0399]`

---

## 6. Compression summary

The archive now fixes the three narrow follow-on questions left open by the prior execution surface:

- **low-volume `RAT-1` publication now follows a public 20 / 10 ladder rather than local guesswork**;
- **the middle band may be rounded, banded, or perturbed only through one declared method version, with secondary protection against differencing**;
- **local recusal exhaustion now routes contested merits review to predeclared cross-roster substitutes rather than ad hoc local necessity**;
- **and overstayed deprecated namespaces now enter a `closed-legacy` state that bars new public use while preserving historical parse and visible successor redirection**.

This is still a tight doctrine. The archive now fixes those immediate follow-on questions in `docs/20-world-design/research-perturbation-preference-substitute-appointment-review-and-retired-namespace-replay.md`: sparse recurring relay series may move to declared perturbation where threshold methods are too blunt, emergency external substitute appointments now run through a prompt process-bounded review route, and closed-legacy or retired namespaces now owe replay / export / backfill duties. The next gap is narrower again: how perturbation families should be rotated and independently audited against composition attacks over time, what anti-capture or cooling-off rules should govern repeated service by tiny substitute pools, and whether any extraordinary rescue path may reopen a fully retired namespace without breaking historical guarantees.

---

## Cross-links

- `docs/20-world-design/research-relay-attestation-object-panel-quorum-recusal-and-deprecated-namespace-migration-windows.md` fixes the immediately prior execution layer that this surface now sharpens.
- `docs/20-world-design/research-extension-namespace-admission-retirement-contested-merge-alias-review-and-relay-capacity-attestations.md` fixes the governance layer beneath this one.
- `docs/20-world-design/research-lag-field-extension-namespaces-downgrade-merge-alias-and-relay-federation-overflow.md` fixes the interoperability and multi-authority relay layer beneath this one.
- `docs/20-world-design/independence-packets-appointment-conflict-recusal-funding-and-domination-review.md` fixes the archive's ordinary conflict / recusal / replacement packet family.
- `docs/30-transition/protected-reporting-confidential-relay-and-anti-reprisal-measures.md` fixes the wider protected-reporting floor that continues to anchor the relay doctrine.

---

## Bottom line

A personhood world should not let small protected-route volumes force a choice between exposure and silence, should not let conflicted local bodies finish public identity-history cases by necessity, and should not let deprecated namespaces remain eternally half-alive. The archive therefore now fixes one more compact rule: **publish low-volume relay objects through a declared 20 / 10 disclosure ladder, source exhausted contested panels from predeclared cross-roster substitutes, and move overstayed deprecated namespaces into a closed-legacy state that forbids new public use while preserving historical legibility.** `[REF-0376]` `[REF-0381]` `[REF-0383]` `[REF-0385]` `[REF-0386]` `[REF-0389]` `[REF-0390]` `[REF-0393]` `[REF-0394]` `[REF-0395]` `[REF-0396]` `[REF-0397]` `[REF-0398]` `[REF-0399]`
