# AI-person research perturbation-compromise response, reserve-pool mutual aid, and rescue-bridge successor promotion

## Thesis

Once the archive fixes bounded perturbation epochs, anti-capture substitute rotation, and rescue bridges for retired namespaces, three narrower execution questions remain. First, a relay can now discover or reasonably suspect that a declared perturbation family has become unsafe, but the archive had not yet fixed what minimal public attestation, temporary publication discipline, or emergency rotation sequence follows from that discovery. Second, anti-capture rotation can fail in practice if several authorities face substitute scarcity at the same time and there is no predeclared reserve or mutual-aid floor. Third, a rescue bridge can remain permanently half-temporary unless the archive states when it must sunset, when it may renew, and when it should be promoted into the ordinary canonical successor path. A personhood world therefore needs one more compact rule: **when a perturbation family is suspected or confirmed compromised, the relay must publish a bounded compromise attestation, move through a declared emergency response and rotation sequence, and stop implying exact continuity until a reviewed bridge is in place; authorities using substitute pools must maintain a reserve-pool or mutual-aid minimum with documented reliance and reporting duties rather than treating scarcity as a one-off excuse; and every rescue bridge must carry an explicit sunset review that either ends the bridge, renews it with reasons, or promotes a successor surface into the canonical path while the old namespace remains visibly retired.** `[REF-0410]` `[REF-0411]` `[REF-0412]` `[REF-0424]` `[REF-0425]` `[REF-0426]` `[REF-0427]` `[REF-0428]` `[REF-0429]` `[REF-0430]` `[REF-0431]` `[REF-0421]` `[REF-0422]` `[REF-0423]`

---

## 1. Why the previous surface is no longer enough

The previous surface solved the structural problem. It bounded perturbation epochs, prevented tiny substitute pools from silently hardening into insider tribunals, and allowed retired namespaces to be rescued without pretending retirement never happened. But three execution failures still remained.

First, **audit without a compromise state is incomplete**. ONS and Census materials already support the idea that repeated outputs and auxiliary information can turn a stable perturbation method into an information leak. NIST's current incident-response recommendations add the missing operational lesson: institutions need a prepared response sequence that reduces impact, supports detection and analysis, and improves recovery rather than improvising after the fact. ORCID's current trust commitments contribute a narrower public-duty analogue in identifier governance: where a security breach affects non-public data, affected users and members are to be notified promptly with a description of the issue, the response, and any user action needed. `[REF-0410]` `[REF-0411]` `[REF-0412]` `[REF-0424]` `[REF-0431]` The archive therefore needed a public minimal state for "suspected compromise" and "confirmed compromise" rather than leaving those situations to sealed folklore.

Second, **rotation is not real unless scarcity planning is real**. OHRP's current cooperative-research guidance requires reliance on a single IRB for many U.S. cooperative projects and explicitly allows joint review or similar anti-duplication arrangements where the single-IRB mandate does not apply. OHRP's current registration materials also allow primary members from one IRB to serve as alternates for comparably qualified members on another IRB under the same organizational umbrella, while requiring equivalence, quorum preservation, and minute-level documentation of the substitution. The current IRB Authorization Agreement adds the decisive mutual-aid governance point: the designated reviewer reports findings and actions to the relying institution, relevant minutes are available on request, and the relying institution remains responsible for compliance. `[REF-0425]` `[REF-0426]` `[REF-0427]` The archive therefore needed a reserve-floor rule that makes anti-capture rotation feasible when several authorities are short at once.

Third, **a rescue bridge is not a stable end state by itself**. Current deprecation standards separate three distinct acts: first warn that a resource is deprecated, then provide migration documentation, and only later announce or reach sunset. RFC 9745 makes deprecation machine-discoverable without changing behavior; RFC 8594 makes eventual unresponsiveness explicit and linkable to policy or mitigation documentation. DataCite's current guidance adds the successor-side pattern: major versions should get a new DOI with explicit `IsNewVersionOf` / `IsPreviousVersionOf` or `HasVersion` / `IsVersionOf` relations, and a canonical DOI may represent grouped versions when that is actually useful. Current DataCite deprecation guidance for legacy endpoints sharpens the practical lesson by advertising a concrete deprecation date and naming the successor endpoints. `[REF-0428]` `[REF-0429]` `[REF-0430]` `[REF-0423]` The archive therefore needed a rule distinguishing a temporary bridge from a canonical successor path.

---

## 2. A perturbation compromise should trigger one bounded public attestation and a forced response sequence

The archive now fixes one compact compromise-response rule: **when a protected relay has credible reason to think that a declared perturbation family is unsafe, it must publish a bounded compromise attestation, move the affected family into emergency review, stop overstating comparability, and either rotate, bridge, or retire the affected public series on a short clock.** `[REF-0410]` `[REF-0411]` `[REF-0412]` `[REF-0424]` `[REF-0431]`

### A. Compromise-attestation object

Every declared perturbation family now has one additional public-minimal object with at least:

- `perturbation_family_id`,
- `compromise_state` (`suspected`, `confirmed`, `contained`, `bridged`, `retired`),
- `first_public_notice_at`,
- `affected_scope` (`single_series`, `family_subset`, `whole_family`),
- `publication_interim_mode` (`hold`, `coarsened`, `bridge_only`, `rotating`),
- `cross_period_comparability` (`suspended`, `bridged`, `still_safe`),
- `next_update_due`,
- and `sealed_annex_present` (`yes` / `no`).

The object stays narrow on purpose. It tells outsiders that the relay is no longer treating the old perturbation family as ordinary, what surface is affected, and when a further public update is due. It does **not** publish the secret that would make exploitation easier. `[REF-0424]` `[REF-0431]`

### B. Emergency sequence

Once the compromise state is `suspected`, the relay must do four things at once:

1. stop claiming ordinary continuity for the affected series;
2. move new public releases for that family to `hold`, `coarsened`, or already-reviewed `bridge_only` mode;
3. open sealed technical review on whether the family can be contained or must rotate; and
4. publish the first public compromise attestation on the short clock.

If the state becomes `confirmed`, ordinary exact-family publication ends. The relay must either rotate to a new family with explicit bridged or non-comparable status, retire the affected series until a bridge exists, or withdraw the unsafe comparison claims from future publication. `[REF-0410]` `[REF-0411]` `[REF-0412]` `[REF-0424]`

### C. Past outputs and comparability claims

The archive does **not** assume that every compromised family forces total republication. But it now fixes the minimum rule: once compromise is confirmed, previously published outputs must carry one visible public status stating whether they remain usable only as historical artifacts, remain usable solely through a declared bridge, or should no longer be treated as safely comparable. In other words, the archive rejects silent quiet-fix practice. A compromised family is a public-state event, even when the technical details remain sealed. `[REF-0410]` `[REF-0412]` `[REF-0424]` `[REF-0431]`

### D. Public update clock

A compromise notice may begin as a hint-like public warning, but it cannot remain indefinitely unresolved. The public object therefore owes a `next_update_due` marker and must eventually move into one of three states: `contained` (ordinary publication may resume under stated limits), `bridged` (a replacement family exists and comparison is only through the bridge), or `retired` (the affected family is no longer a live publication basis). `[REF-0428]` `[REF-0429]` `[REF-0431]`

---

## 3. Anti-capture rotation needs a reserve pool or mutual-aid floor

The archive now fixes one compact capacity rule: **any authority that uses substitute reviewers for protected-relay or contested-merits work must maintain either an internal reserve pool large enough to respect cooling-off and anti-concentration limits or a predeclared mutual-aid compact with external authorities that can lawfully and competently supply comparably qualified substitutes on short notice.** `[REF-0425]` `[REF-0426]` `[REF-0427]` `[REF-0416]` `[REF-0417]` `[REF-0418]`

### A. Minimum reserve architecture

Each authority must declare, for every protected-review lane:

- the ordinary roster,
- the substitute roster,
- the reserve roster or mutual-aid partners,
- the comparability matrix for cross-appointment,
- the short-clock activation method,
- and the reporting path back to the relying authority.

A reserve arrangement is not real if it exists only as a phone tree or a list of friendly names. It is real only if qualifications, conflict rules, activation rights, and reporting duties are already documented before scarcity arrives. `[REF-0425]` `[REF-0426]` `[REF-0427]`

### B. Mutual-aid compacts

Where a local reserve is too small, authorities may satisfy the rule through a mutual-aid compact. The compact must identify:

- which authority may request help,
- who may authorize deployment,
- which substitute classes are interchangeable,
- how minutes, findings, and actions flow back,
- and which institution retains compliance responsibility after reliance.

This borrows the conservative logic already used in cooperative research: reliance may reduce duplication, but it does not erase assignment discipline or responsibility. `[REF-0425]` `[REF-0427]`

### C. Scarcity does not cancel anti-capture

The reserve rule does not abolish scarcity. It changes what scarcity means. A shortage is now a trigger for reserve activation, reciprocal coverage, or a documented inability notice to the higher authority — not a reason to keep reusing the same familiar substitute until the docket becomes effectively captive. `[REF-0426]` `[REF-0416]` `[REF-0417]`

### D. Reserve exhaustion state

If both the local substitute pool and the declared reserve or mutual-aid pool are exhausted, the authority must publish a bounded scarcity marker and move the matter into preservation-plus-escalation status. It may not quietly waive cooling-off, comparability, or conflict rules just because the bench is thin. `[REF-0416]` `[REF-0418]` `[REF-0425]` `[REF-0427]`

---

## 4. Every rescue bridge must sunset, renew, or promote a canonical successor

The archive now fixes one compact bridge-governance rule: **every rescue bridge for a retired namespace must carry an explicit sunset review, and that review must end in one of three visible outcomes — sunset, renewed bridge, or canonical-successor promotion — while the original namespace remains retired throughout.** `[REF-0428]` `[REF-0429]` `[REF-0430]` `[REF-0421]` `[REF-0422]` `[REF-0423]`

### A. Bridge state is not successor state

A rescue bridge exists because the old namespace is retired but still needs an authoritative reading path. That is different from saying the bridge itself is now the ordinary canonical path for new use. RFC 9745 and RFC 8594 make the distinction vivid: deprecation and sunset are lifecycle signals, while migration guidance tells clients what to do next. DataCite's versioning guidance adds the exact machine-linking pattern for successor relations and grouped canonical objects. `[REF-0428]` `[REF-0429]` `[REF-0423]`

### B. Required review outcomes

Every rescue bridge therefore carries at least:

- `bridge_status` (`active`, `renewed`, `sunsetting`, `promoted`, `closed`),
- `bridge_review_due`,
- `successor_namespace` if one exists,
- `promotion_basis` (`none`, `traffic_convergence`, `mapping_completion`, `legal_designation`, `other`),
- and `retired_namespace_status = retired`.

At review, exactly one of three things happens:

1. **Sunset** — the bridge ends because replay and successor mapping are now sufficient without it;
2. **Renew** — the bridge remains temporary, but only with reasons and a new review date;
3. **Promote** — a successor namespace or canonical surface becomes the ordinary path, with explicit version or successor relations and without reviving the retired namespace itself. `[REF-0428]` `[REF-0429]` `[REF-0430]` `[REF-0422]` `[REF-0423]`

### C. Promotion standard

Promotion is appropriate only when three conditions hold:

- the successor surface is stable enough for ordinary new public use,
- old-to-new mapping is sufficiently complete for the rights and review functions that justified the bridge,
- and the promotion can be expressed through explicit successor or version relations rather than tacit custom.

The model here is DataCite's distinction between specific versions and a canonical DOI representing versions as a group, alongside current deprecation practice that tells users the date and the successor endpoint instead of leaving them to infer both. `[REF-0430]` `[REF-0423]`

### D. No silent withdrawal and no silent promotion

A bridge cannot simply vanish because operators believe migration is done, and it cannot quietly become the permanent canonical path because everyone has started using it. Both changes are public lifecycle events. The archive therefore requires visible bridge review and visible successor designation. `[REF-0428]` `[REF-0429]` `[REF-0430]` `[REF-0422]`

---

## 5. Edge tests

### A. A relay audit finds that a long-running perturbation family may be inferable through accumulated linked releases

The relay publishes a compromise attestation with `compromise_state = suspected`, stops claiming ordinary continuity, switches new releases to hold or coarsened mode, and opens sealed technical review. If the risk is confirmed, the old family becomes `bridged` or `retired`; it does not simply continue while engineers work privately on a fix. `[REF-0410]` `[REF-0411]` `[REF-0412]` `[REF-0424]` `[REF-0431]`

### B. Three authorities lose several panel members to conflict at once

None of them may quietly waive cooling-off and keep reusing the same trusted outsider. Each must activate its reserve roster or mutual-aid compact, document the cross-authority substitution, and continue reporting actions back to the relying authority. If the reserve is exhausted too, the matter escalates under preservation rather than collapsing into improvised local reuse. `[REF-0425]` `[REF-0426]` `[REF-0427]`

### C. A rescue bridge has existed for years and most public traffic now routes through the successor mapping

The bridge must not stay permanently "temporary" by habit. At review the authority either sunsets the bridge because the successor path is enough or promotes the successor surface into the canonical role with explicit successor / version relations. The original namespace remains retired in either case. `[REF-0428]` `[REF-0429]` `[REF-0430]` `[REF-0423]`

---

## 6. Compression summary

The archive now fixes the three narrower execution questions left open by the prior perturbation-audit / anti-capture / rescue surface:

- **a perturbation compromise now triggers one bounded public attestation plus a forced review / rotation / bridge sequence rather than sealed improvisation**;
- **anti-capture rotation now requires a real reserve-pool or mutual-aid minimum rather than optimistic assumptions about scarcity never arriving**;
- **and every rescue bridge now carries a visible sunset / renewal / successor-promotion decision rather than drifting into permanent ambiguity.**

This is still a tight doctrine. The archive now fixes those narrower questions in `docs/20-world-design/research-compromise-backfill-republication-burden-sharing-and-successor-promotion-review.md`: confirmed compromise now triggers visible post-compromise status for already-issued outputs through historical-only, tombstone-withdrawal, republication, or bridge-only comparability; reserve systems now run on a compact standing-capacity plus mission-cost burden-sharing formula that resists both free-riding and dominance-by-donation; and contested rescue-bridge promotion now follows a bounded reconsideration-plus-independent-review route while continuity is preserved and the retired namespace remains retired. The next gap is narrower again: what machine-readable supersession graph and query-default rules should govern multi-generation compromise republications, what cure / suspension / re-entry rules should apply when an authority chronically undercontributes to the reserve pool or dominates donated capacity, and what interim-stay and label-effect rules should govern bridge traffic while successor-promotion review is pending.

---

## Cross-links

- `docs/20-world-design/research-perturbation-family-audit-substitute-pool-anti-capture-rotation-and-retired-namespace-rescue.md` fixes the immediately prior execution layer that this surface now sharpens.
- `docs/20-world-design/research-perturbation-preference-substitute-appointment-review-and-retired-namespace-replay.md` fixes the perturbation / appointment / replay layer beneath this one.
- `docs/20-world-design/research-relay-attestation-object-panel-quorum-recusal-and-deprecated-namespace-migration-windows.md` fixes the attestation / panel / migration layer beneath this one.
- `docs/20-world-design/independence-packets-appointment-conflict-recusal-funding-and-domination-review.md` fixes the wider conflict / recusal / replacement packet family beneath this one.

---

## Bottom line

A personhood world should not discover perturbation compromise in secret, should not pretend anti-capture rotation is possible without reserve capacity, and should not let a rescue bridge drift forever between temporary patch and true successor. The archive therefore now fixes one more compact rule: **compromised perturbation families owe a bounded public attestation and forced response sequence, substitute systems owe reserve-pool or mutual-aid minimums, and rescue bridges owe visible sunset, renewal, or canonical-successor promotion while the old namespace remains retired.** `[REF-0410]` `[REF-0411]` `[REF-0412]` `[REF-0424]` `[REF-0425]` `[REF-0426]` `[REF-0427]` `[REF-0428]` `[REF-0429]` `[REF-0430]` `[REF-0431]` `[REF-0421]` `[REF-0422]` `[REF-0423]`
