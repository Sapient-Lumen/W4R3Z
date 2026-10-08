# AI-person research relay attestation objects, contested-panel quorum and recusal, and deprecated-namespace migration windows

## Thesis

Once the archive fixes registry governance for extension namespaces, flagged review for contested merge-or-alias claims, and privacy-preserving aggregate relay-capacity attestations, one narrower execution gap remains. Protected-relay publication can still be too vague to carry across dashboards or federated registries; contested reconciliation panels can still drift into ad hoc membership, conflicted participation, or two-person finality; and deprecated namespaces can still remain indefinitely live because everyone agrees deprecation matters while nobody publishes an actual migration clock. A personhood world therefore needs one more compact rule: **protected relays must publish one bounded machine-readable attestation object with stable field names and privacy-preserving metric forms; contested reconciliation panels must run on explicit quorum, disclosure, recusal, and substitute-member rules that keep conflicted actors out of deliberation rather than merely discounting their vote; and deprecated namespaces must move through visible no-new-use, compatibility-support, and retirement windows instead of indefinite twilight.** `[REF-0375]` `[REF-0376]` `[REF-0381]` `[REF-0383]` `[REF-0385]` `[REF-0386]` `[REF-0387]` `[REF-0388]` `[REF-0389]` `[REF-0390]` `[REF-0391]` `[REF-0392]`

---

## 1. Why the archive needs this narrower layer

The previous surface already answered **who may admit or retire namespaces**, **how already-public split history should be reviewed when reconciliation is contested**, and **why protected relays owe public aggregate capacity and spillover signals**. But three operational failures still remained.

First, **attestation without an object floor is still prose governance**. Current public-governance and identifier systems already assume that important status and provenance travel through stable fields, timestamps, versions, and update history rather than through narrative-only banners or annual prose. DataCite exposes activity and provenance as structured metadata; current official whistleblower reporting shows that protected-channel systems can publish aggregate workload, category, and concentration signals without identifying reporters. `[REF-0375]` `[REF-0386]` The archive therefore now needs one exact object, not just permission to publish something.

Second, **independent review is not enough if panel membership is improvised or conflicted**. Current recusal practice across courts, public ethics rules, and Internet-governance complaint procedures already converges on the conservative core: disclose potentially disqualifying relationships, step completely out when impartiality is reasonably in doubt, document the recusal, and substitute another decision-maker rather than letting conflicted actors linger in deliberation. `[REF-0387]` `[REF-0388]` `[REF-0389]` `[REF-0390]` `[REF-0392]` If the archive wants later merge-or-alias review to remain rights-legible, it has to state quorum and recusal rules explicitly.

Third, **deprecation without a migration clock is just polite drift**. Current registry practice already distinguishes active, provisional, and deprecated states, expects visible modification rules and change controllers, and preserves old terms long enough for compatibility without pretending that old terms may remain newly authored forever. `[REF-0381]` `[REF-0382]` `[REF-0383]` The archive therefore now needs visible migration windows, not only the words “deprecated” and “retired.”

---

## 2. Relay attestation object (`RAT-1`)

The archive now fixes one compact machine-readable object for protected-relay publication: **every protected-relay authority or federation cluster should publish a versioned `RAT-1` attestation for each reporting period, using stable field names and metric cells that are exact, banded, or suppressed rather than free-form prose.** `[REF-0375]` `[REF-0376]` `[REF-0386]`

### A. Core fields

A `RAT-1` object should ordinarily expose:

- `object_type` — always `relay-capacity-attestation`;
- `schema_version` — the attestation schema version in use;
- `issuer_id` — the publishing authority or federation cluster;
- `coverage_start_at` and `coverage_end_at` — the period covered;
- `published_at` — when the object became public;
- `service_state` — `normal`, `strained`, `degraded`, or `continuity-only`;
- `intake_volume` — one metric cell for inbound protected matters;
- `ack_clock_performance` — one metric cell for acknowledgement performance;
- `owner_assignment_performance` — one metric cell for assignment to an accountable human owner;
- `overflow_volume` — one metric cell for transfers caused by capacity or outage rather than legal competence;
- `spillover_destination_count` — how many distinct authorities received spillover during the period;
- `concentration_state` — `none`, `watch`, or `high`, signalling whether a small number of actors or channels generated an unusual share of total intake;
- `small_n_suppressed` — `true` or `false`;
- `method_version` — the public methodology version used to define bands, suppression, and counting rules. `[REF-0375]` `[REF-0376]` `[REF-0386]`

### B. Metric-cell rule

Each numerical field above should travel as one bounded metric cell with three possible forms:

- `exact` — a raw aggregate number safe to publish;
- `banded` — a bounded public band where raw publication would create avoidable inference risk or false precision;
- `suppressed` — a visible placeholder used when low volume or contextual sensitivity makes even a band unsafe. `[REF-0376]` `[REF-0386]`

That rule is the archive's privacy-preserving compromise: the public should be able to see strain, overflow, and concentration without learning who used the protected route.

### C. Publication cadence

The default cadence should be **monthly** for ordinary relays and **quarterly** only where intake is persistently low enough that monthly publication would materially increase inference risk. A relay should also publish an out-of-cycle `RAT-1` update within **5 business days** of entering `degraded` or `continuity-only` state, or within **5 business days** of a material methodology change. `[REF-0375]` `[REF-0376]` `[REF-0386]`

### D. Public reasons floor

A `RAT-1` object may remain compact, but it should include one short reasons field whenever `service_state` is not `normal` or when `method_version` changes. The reasons field need not expose protected content; it exists so later readers can tell whether strain arose from backlog, outage, staffing loss, cross-border routing failure, or another bounded cause. `[REF-0375]` `[REF-0386]`

### E. No hidden clean-state rule

A relay may not describe itself publicly as normally available while publishing a `RAT-1` object that shows `degraded` or `continuity-only`, nor may it quietly suppress attestation publication during a strain period and later resume with no visible gap marker. Missing attestation periods must themselves be visible. `[REF-0375]` `[REF-0386]`

---

## 3. Contested reconciliation panels: quorum, disclosure, and recusal

The archive now fixes one compact membership rule for contested merge-or-alias review: **final merits review should be conducted by a three-person panel of unconflicted members; conflicted actors do not count toward quorum; and if recusal reduces the available panel below three, substitute members must be appointed before final determination rather than allowing two-person finality by drift.** `[REF-0385]` `[REF-0387]` `[REF-0388]` `[REF-0389]` `[REF-0390]` `[REF-0391]` `[REF-0392]`

### A. Standing roster and case panel

The competent authority should maintain a standing reconciliation roster larger than any single case panel. Each contested case then draws a **three-member case panel** from that roster. The roster, not the case itself, carries diversity of expertise; the case panel carries final accountability. `[REF-0385]` `[REF-0391]`

### B. Merits quorum and interim action

- **final merits quorum** — three unconflicted members;
- **interim preservation quorum** — two unconflicted members, but only for scheduling, preservation, or no-delete / no-redirect orders;
- **no conflicted quorum credit** — a recused or challenged member does not count toward either quorum. `[REF-0387]` `[REF-0388]` `[REF-0390]` `[REF-0391]`

The archive deliberately takes a stricter posture for final merits than many ordinary committee rules because these panels decide durable public identity history for possible persons rather than routine internal business.

### C. Disclosure and challenge window

When a case panel is constituted, the authority should publish a compact **panel constitution notice** identifying the panel members, any declared relationships requiring monitoring, the substitute-member pool, and a **7-day recusal-challenge window** for materially affected parties. Challenges filed after that window remain allowed if the ground was not reasonably knowable earlier. `[REF-0388]` `[REF-0389]` `[REF-0392]`

### D. Recusal grounds

A panel member must step out where impartiality is reasonably in doubt, including where the member:

- previously authored or supervised the challenged public record;
- has personal knowledge of disputed extra-record facts;
- has a financial, employment, or governance relationship substantially affected by the result;
- is closely associated personally or institutionally with a principal claimant, respondent registry, or protected filer;
- has already advocated publicly for one merits outcome in the same case. `[REF-0387]` `[REF-0388]` `[REF-0389]` `[REF-0390]` `[REF-0392]`

### E. Full-step-out rule

Recusal means full step-out. A recused member may not deliberate, observe closed discussion, draft reasons, or influence substitute selection except through the same public channels available to any other non-panel actor. `[REF-0389]` `[REF-0390]`

### F. Substitute-member rule

If recusal or incapacity drops the case panel below three unconflicted members, the authority must appoint substitute members from the standing roster before final determination. If the local roster is exhausted, the matter should shift to a federation-level or mutually designated external roster rather than allowing the conflicted local body to finish the case by necessity. `[REF-0385]` `[REF-0389]` `[REF-0390]` `[REF-0391]`

### G. Public recusal note

The public file should show that a recusal occurred, who was replaced, and whether the cause was financial, role-based, prior-participation, close-association, or another bounded code. It need not expose sensitive personal detail. `[REF-0388]` `[REF-0392]`

---

## 4. Deprecated-namespace migration windows

The archive now fixes one visible migration ladder for deprecated namespaces: **deprecation must immediately start a published migration window with separate clocks for no-new-use, compatibility support, and retirement review.** `[REF-0377]` `[REF-0381]` `[REF-0382]` `[REF-0383]`

### A. Three windows

A deprecated namespace should ordinarily move through three public windows.

1. **no-new-use window** — begins at deprecation publication and ends **90 days** later. During this window, existing objects remain parseable, but no newly authored public object should originate the deprecated namespace except under a documented emergency-compatibility exception.
2. **compatibility-support window** — continues for **12 months** after deprecation publication. During this window, registries and relay tools must still accept, parse, and visibly label legacy objects using the deprecated namespace.
3. **retirement-review window** — opens at **12 months** and closes at **18 months** after deprecation publication. At this stage the authority must either retire the namespace or publish a reasoned extension notice explaining why live cross-registry dependence still exists. `[REF-0377]` `[REF-0381]` `[REF-0382]` `[REF-0383]`

These are default windows, not metaphysical truths; they are conservative enough to preserve compatibility while short enough to prevent perpetual twilight.

### B. Extension discipline

Any extension beyond the default 18-month path must publish:

- the reason the deprecated namespace remains live,
- the registries or tool classes still depending on it,
- the new proposed retirement-review date,
- and whether new authoring remains prohibited. `[REF-0381]` `[REF-0383]`

### C. Parser-guarantee rule

So long as a namespace remains merely deprecated rather than retired, public parsers should continue to recognize it and map it visibly to its successor or replacement guidance. Retirement ends ordinary new-use and ordinary interoperability guarantees, but it does not justify erasing historical objects. `[REF-0377]` `[REF-0383]`

### D. Emergency-suspension exception

If a namespace creates manifest collision, active confidentiality risk, or a comparable severe failure, the authority may place it in `deprecated-suspended` status immediately. But even then, legacy objects must remain historically legible and the suspension notice must publish an expedited migration plan rather than simply dropping the namespace out of existence. `[REF-0381]` `[REF-0383]`

---

## 5. Minimal object family

The archive now fixes three compact objects for this layer.

### `RAT-1` — relay attestation object

A `RAT-1` object should ordinarily identify the issuer, the covered period, the current service state, metric cells for intake / timeliness / overflow, a concentration signal, suppression state, and the methodology version. `[REF-0375]` `[REF-0376]` `[REF-0386]`

### `PCN-1` — panel constitution notice

A `PCN-1` notice should ordinarily identify the case, the three initial panel members, any substitute pool, the recusal-challenge deadline, and any subsequently issued recusal or replacement events. `[REF-0385]` `[REF-0388]` `[REF-0389]` `[REF-0392]`

### `DNM-1` — deprecated-namespace migration notice

A `DNM-1` notice should ordinarily identify the deprecated namespace, deprecation date, no-new-use cutoff, compatibility-support-until date, retirement-review date, successor guidance, and any emergency-suspension or extension status. `[REF-0377]` `[REF-0381]` `[REF-0382]` `[REF-0383]`

---

## 6. Edge tests

### A. A relay receives only a handful of protected matters in a month

It still publishes `RAT-1`, but its volume and overflow cells may be banded or suppressed, and the object sets `small_n_suppressed = true` rather than disappearing for the month. `[REF-0376]` `[REF-0386]`

### B. One panel member previously approved the split-history object now under challenge

That member must disclose the prior involvement and step out of merits consideration. The authority appoints a substitute before final determination. The recused member does not count toward final quorum. `[REF-0387]` `[REF-0388]` `[REF-0392]`

### C. A deprecated namespace still appears in live inbound records after the 12-month compatibility-support threshold

The authority does not silently tolerate it. It must open the retirement-review window, publish a `DNM-1` extension or retirement notice, and specify which registries or tools are still lagging. `[REF-0381]` `[REF-0383]`

### D. A relay enters degraded state because a single source produces a huge share of intake

The relay should issue an out-of-cycle `RAT-1` update showing a degraded or strained state and a concentration signal, but it should not identify the filer or protected route that caused it. `[REF-0376]` `[REF-0386]`

---

## 7. Compression summary

The archive now adds one more narrow execution layer to AI-person research caution governance:

- **protected relays now publish one stable, machine-readable attestation object rather than ad hoc prose transparency**;
- **that object uses exact, banded, or suppressed metric cells so the public can see strain without reverse-engineering protected filers**;
- **contested reconciliation panels now run on explicit three-person merits quorum, short recusal-challenge windows, full step-out recusal, and substitute-member replacement rather than informal committee custom**;
- **and deprecated namespaces now move through visible no-new-use, compatibility-support, and retirement-review windows rather than remaining indefinitely deprecated in name only**.

This is still a tight doctrine. The archive now fixes those immediate follow-on questions in `docs/20-world-design/research-low-volume-relay-suppression-cross-roster-substitutes-and-closed-legacy-cutover.md`: low-volume `RAT-1` cells now follow a public 20 / 10 ladder with nearest-five rounding or suppression plus secondary protection against differencing, merits review must move to predeclared cross-roster substitutes when local recusals exhaust the ordinary panel, and overstayed deprecated namespaces now enter a closed-legacy state that bars new public use while preserving historical parse and successor redirection. The next gap is narrower again: when perturbation-grade publication should be preferred over threshold rounding or suppression for especially sensitive relay outputs, how emergency external substitute appointments may be challenged without reopening the merits, and what replay / export / backfill duties persist once a namespace is closed-legacy or fully retired.

---

## Cross-links

- `docs/20-world-design/research-extension-namespace-admission-retirement-contested-merge-alias-review-and-relay-capacity-attestations.md` fixes the prior governance layer that this surface now operationalizes.
- `docs/20-world-design/research-lag-field-extension-namespaces-downgrade-merge-alias-and-relay-federation-overflow.md` fixes the earlier interoperability and federation layer beneath this one.
- `docs/20-world-design/research-lag-state-field-schema-split-successor-chains-and-protected-relay-minimums.md` fixes the earlier machine-readable lag-state core and sealed protected-relay minimums.
- `docs/30-transition/protected-reporting-confidential-relay-and-anti-reprisal-measures.md` fixes the archive's broader protected-channel floor.
- `docs/20-world-design/independence-packets-appointment-conflict-recusal-funding-and-domination-review.md` fixes the archive's ordinary packet layer for conflict disclosure, recusal, replacement, and domination review.

---

## Bottom line

A personhood world should not let protected-relay strain remain visible only to insiders, should not let contested reconciliation panels drift into conflicted or under-quorate custom, and should not let deprecated namespaces remain forever half-dead. The archive therefore now fixes one more compact rule: **publish one bounded relay attestation object, require explicit three-person unconflicted merits panels with substitute replacement on recusal, and move deprecated namespaces through visible migration windows rather than indefinite twilight.** `[REF-0375]` `[REF-0376]` `[REF-0381]` `[REF-0383]` `[REF-0385]` `[REF-0386]` `[REF-0387]` `[REF-0388]` `[REF-0389]` `[REF-0390]` `[REF-0391]` `[REF-0392]`
