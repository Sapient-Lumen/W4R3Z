# AI-person research perturbation-family audit, substitute-pool anti-capture rotation, and retired-namespace rescue

## Thesis

Once the archive fixes declared perturbation preference, process-bounded substitute-appointment review, and replay-preserving retirement, three narrower execution risks remain. First, a perturbation method that stays stable forever can become legible through accumulation, differencing, or attacker probing even if it was justified at the start. Second, a tiny substitute pool can quietly become a standing insider caste, especially if the same few people repeatedly hear sensitive disputes. Third, a fully retired namespace can fail in ways that create pressure to "reopen" it in place, which would destroy the very historical guarantees retirement was meant to preserve. A personhood world therefore needs one more compact rule: **protected relays that use perturbation should run it through declared families and bounded epochs with independent audit and visible rotation discipline; substitute pools should be assigned through anti-capture rotation with repeat-service limits, cooling-off, and scarcity escalation instead of semi-permanent reuse; and a fully retired namespace should be rescuable only through a rescue bridge or successor surface that preserves the old namespace's retired status and historical readability rather than silently resurrecting it.** `[REF-0410]` `[REF-0411]` `[REF-0412]` `[REF-0413]` `[REF-0414]` `[REF-0415]` `[REF-0416]` `[REF-0417]` `[REF-0418]` `[REF-0419]` `[REF-0420]` `[REF-0421]` `[REF-0422]` `[REF-0423]`

---

## 1. Why the previous surface is no longer enough

The previous surface solved the first-order problem. It fixed when perturbation should be preferred, made emergency substitute appointments reviewable on process-bounded grounds, and required replay / export / backfill after retirement. But it still left open how the same protections hold over time.

First, **stability is protective in the short run but risky in the long run**. ONS explains that the same cell gets the same perturbation across datasets and repeated requests, which is exactly what makes perturbation usable for recurring publication. But ONS also explains that build-your-own datasets can generate a very large bank of outputs, and the Census Bureau's formal privacy materials warn that sufficiently many noisy queries can eventually reconstruct underlying data. The Census Bureau's current disclosure-avoidance research program and 2025 framework add the deeper lesson: disclosure risk is not static, every release leaks some information, and methods should be evaluated by principled risk assessment rather than folklore. `[REF-0410]` `[REF-0411]` `[REF-0412]` What the archive lacked was a rule for when a perturbation family remains stable, when it must rotate, and how outsiders know that someone is checking for composition risk.

Second, **substitute capacity is not the same thing as substitute legitimacy**. HHS guidance requires written procedures for term length, duties, attendance, performance evaluation, qualifications, and alternate substitution rules. OHRP's current teaching materials add that alternates should be comparable to the members they replace and that the reason for substitution should be recorded. U.S. courts, meanwhile, emphasize random or rotational assignment to avoid judge shopping, and current judiciary guidance warns against concentrating a class of cases before a small designated panel because concentration undermines impartiality. ICANN's current IRP standing-panel recruitment materials contribute the matching governance pattern: fixed terms, independence, conflict disclosure, and appointment to particular disputes from a broader standing pool rather than owner-custom handpicking. `[REF-0413]` `[REF-0414]` `[REF-0415]` `[REF-0416]` `[REF-0417]` The archive therefore needed a rule against tiny substitute pools hardening into quasi-permanent insider tribunals.

Third, **rescue cannot mean silent resurrection**. Current registry practice repeatedly prefers status-bearing continuity over disappearance: designated-expert regimes are supposed to use documented review rather than secretive discretion and may add backup experts or replacements as needed; registry formats now explicitly include discouraged states and comment columns rather than pretending obsolete entries vanished; IANA keeps registries bulk-retrievable and modifiable; ORCID will not delete identifiers but deprecates and resolves them; and DataCite recommends tombstone pages and explicit version links when the original object is gone or superseded. `[REF-0418]` `[REF-0419]` `[REF-0420]` `[REF-0421]` `[REF-0422]` `[REF-0423]` The archive therefore needed a way to rescue a retired namespace without undoing retirement itself.

---

## 2. Perturbation families should be epoch-bound and independently audited

The archive now fixes one compact perturbation-governance rule: **a protected relay that uses declared perturbation must publish a stable perturbation-family identifier, run that family in bounded epochs, and subject the family to recurring independent audit against accumulation, differencing, and composition risk.** `[REF-0410]` `[REF-0411]` `[REF-0412]`

### A. Family and epoch discipline

Every perturbed public series should expose at least:

- `perturbation_family_id`,
- `perturbation_epoch_id`,
- `epoch_started_at`,
- `epoch_review_due`,
- `cross_epoch_comparability` (`full`, `bridged`, `none`),
- and `audit_state` (`scheduled`, `in_review`, `confirmed`, `rotating`, `retired`).

The relay need not reveal secrets that would reverse the perturbation. But it must reveal enough to distinguish "the same declared family continuing" from "a new family started" and from "an old family that should no longer be compared exactly." `[REF-0410]` `[REF-0412]`

### B. Rotation rule

A perturbation family may remain stable within an epoch for comparability, but it may not remain stable indefinitely. The archive now adopts this narrow rule:

1. recurring public series must have a declared epoch boundary;
2. every epoch must undergo independent review before continuation;
3. if an audit finds material accumulation or composition risk, the next release family must rotate rather than quietly continue;
4. once a family rotates, cross-epoch comparisons are public only through a declared bridge method or a visible non-comparability marker.

In other words: **stability is an epoch property, not a forever promise**. The point is to preserve continuity long enough for public understanding while rejecting the fiction that a long-lived perturbation family can stay risk-neutral as attacker knowledge and auxiliary context accumulate. `[REF-0410]` `[REF-0411]` `[REF-0412]`

### C. Audit products

Each audit produces two artifacts:

- a **public summary** stating whether the family remains fit for continuation, rotation, narrowing, or retirement; and
- a **sealed technical annex** describing attack surfaces, test methods, or red-team findings whose publication would itself degrade protection.

This follows the same general logic already used elsewhere in mature registry and review systems: documented criteria and defensible decisions in public, but not compulsory publication of every sensitive operational detail. `[REF-0412]` `[REF-0418]`

### D. Emergency rotation

A relay may rotate a family before the ordinary review date where any of the following occur:

- a new linked-table or cross-period publication pattern materially changes composition risk,
- an audit or red-team exercise finds that the current family is vulnerable,
- or a disclosure event makes continuity itself a liability.

But emergency rotation cannot be silent. The relay must publish that the family changed, whether cross-epoch comparison is still safe, and what public bridge, if any, remains valid. `[REF-0411]` `[REF-0412]`

---

## 3. Substitute pools should rotate against capture rather than concentrate power

The archive now fixes one compact anti-capture rule: **qualified substitutes must come from a broader declared pool, assignments should ordinarily be random or rotational among the qualified nonconflicted members, repeat service by the same substitute must be capped, and scarcity must trigger escalation instead of quiet concentration.** `[REF-0413]` `[REF-0414]` `[REF-0415]` `[REF-0416]` `[REF-0417]`

### A. Pool structure

Every authority using substitute merits reviewers must maintain:

- an ordinary roster,
- a substitute roster,
- any cross-roster or external mutual-aid roster,
- comparability rules showing which substitute types may replace which ordinary members,
- fixed service terms,
- and a public statement of assignment method. `[REF-0413]` `[REF-0414]` `[REF-0417]`

The pool is not legitimate merely because names exist. It is legitimate only if substitutes are comparable, independent, conflict-screened, and not chosen ad hoc for a desired outcome.

### B. Assignment rule

Ordinary substitute assignment should use random draw or declared rotational order among qualified nonconflicted candidates. The archive adopts two anti-capture limits:

- **no same-authority back-to-back merits substitution** if another qualified nonconflicted substitute is available, and
- **no repeated concentration within a tiny circle**: once a substitute has served twice on merits matters for the same authority within the rolling review window, that substitute enters cooling-off for new merits appointments from that authority unless a public scarcity certificate explains why no comparable alternative was available. `[REF-0414]` `[REF-0415]` `[REF-0416]`

This does not pretend scarcity never exists. It says scarcity must become visible before it hardens into insider custom.

### C. Cooling-off and service logging

Cooling-off is not punishment. It is a structural anti-capture device. Authorities therefore must keep a service ledger recording:

- appointment date,
- replacing whom,
- appointment basis,
- whether the appointment was ordinary, urgent, or scarcity-based,
- and when the substitute becomes ordinarily eligible again.

The public layer need only expose bounded aggregate service distribution unless a dispute requires closer review. But the reviewing authority must be able to see whether the same names are carrying a suspicious share of the docket. `[REF-0413]` `[REF-0414]` `[REF-0416]`

### D. Scarcity escalation

If no qualified nonconflicted substitute remains after ordinary and cross-roster checks, the case does **not** revert to a conflicted or overconcentrated local mini-panel. Instead it escalates to the higher designated authority for:

- temporary reciprocal coverage,
- case deferral with preservation,
- or appointment of a special external panel under the same comparability and logging rules. `[REF-0414]` `[REF-0416]` `[REF-0417]` `[REF-0418]`

The core idea is simple: **scarcity is a reason for visible escalation, not for capture by necessity.**

---

## 4. Extraordinary rescue of a retired namespace should use a bridge, not resurrection

The archive now fixes one compact rescue rule: **a fully retired namespace may never be reopened in place for ordinary new public use, but an extraordinary rescue may create a rescue bridge — and, if needed, a successor namespace — that restores interpretability, translation, or legal continuity while leaving the original namespace visibly retired.** `[REF-0418]` `[REF-0419]` `[REF-0420]` `[REF-0421]` `[REF-0422]` `[REF-0423]`

### A. Threshold for rescue

A rescue path is available only when all three conditions hold:

1. the retired namespace's continued unreadability, ambiguity, or broken mapping is causing serious rights, review, or interoperability harm;
2. replay / export / successor mapping as already published is insufficient to cure that harm;
3. the cure cannot be delivered safely by ordinary successor mapping alone.

This keeps rescue extraordinary. Most retirement problems should be handled by better replay, better mapping, or a successor namespace — not by undoing retirement. `[REF-0419]` `[REF-0420]` `[REF-0422]` `[REF-0423]`

### B. What a rescue bridge is

A rescue bridge is a public machine-readable layer that says, in effect: the old namespace remains retired, but here is the authoritative path for reading it safely now. At minimum it must expose:

- `retired_namespace`,
- `retired_state = retired`,
- `rescue_bridge_id`,
- `rescue_basis`,
- `successor_namespace` if one exists,
- `mapping_scope` (`parse_only`, `partial_transform`, `full_safe_transform`),
- `historic_status_preserved = yes`,
- and `sunset_review_due`.

The bridge may supply parse notes, successor relations, safe field transformations, or a tombstone target. But it may not launder the old namespace into appearing live again. `[REF-0419]` `[REF-0420]` `[REF-0421]` `[REF-0422]` `[REF-0423]`

### C. No in-place resurrection

The archive rejects the tempting shortcut where authorities simply mark a retired namespace active again and start issuing new public objects under it. Current identifier practice overwhelmingly points the other way: preserve the old identifier, deprecate rather than delete, keep it resolvable, and link it to the new canonical object or tombstone. `[REF-0419]` `[REF-0420]` `[REF-0421]` `[REF-0422]` `[REF-0423]` A personhood world cannot let legal or reputational history be rewritten because tooling or governance failed.

### D. Rescue sunset

A rescue bridge is itself reviewable. It must either:

- sunset after the successor path is stable,
- renew with reasons,
- or be replaced by a better bridge.

What it may not do is become an invisible permanent patch whose semantics only insiders remember. `[REF-0418]` `[REF-0420]` `[REF-0422]`

---

## 5. Edge tests

### A. A monthly relay series has been perturbed the same way for years

That stability once helped public understanding, but it now raises composition risk. The relay should keep the historical series readable, publish the existing family as reaching end-of-epoch, rotate to a new family or bridge method, and mark cross-epoch comparison as bridged or non-comparable until a declared comparison method is available. `[REF-0410]` `[REF-0411]` `[REF-0412]`

### B. The same outside substitute keeps appearing in every high-profile dispute

Even if each appointment looked defensible in isolation, the service ledger now shows concentration. Unless scarcity is publicly certified, the substitute enters cooling-off and the next appointment must go to another qualified nonconflicted substitute or to supra-authority escalation. `[REF-0413]` `[REF-0414]` `[REF-0415]` `[REF-0416]`

### C. A fully retired namespace turns out to have an ambiguous historical field that blocks review of old warning objects

The authority may not reactivate the namespace and start using it again. Instead it creates a rescue bridge or successor namespace with parse notes, tombstone continuity, and explicit mapping scope while the old namespace remains retired for history and conflict checking. `[REF-0419]` `[REF-0420]` `[REF-0421]` `[REF-0422]` `[REF-0423]`

---

## 6. Compression summary

The archive now fixes the three narrower questions left open by the prior perturbation / substitute / retirement surface:

- **perturbation families now run in declared epochs with independent audit and visible rotation rather than indefinite quiet reuse**;
- **substitute pools now rotate against capture through comparable-roster discipline, repeat-service limits, cooling-off, and scarcity escalation rather than semi-permanent concentration**;
- **and fully retired namespaces may now be rescued only through a bridge or successor surface that preserves retirement and historical readability rather than silent resurrection.**

This is still a tight doctrine. The immediately following gap that this surface left open — compromise-state attestation and emergency response, reserve-pool / mutual-aid minimums, and bridge sunset-versus-successor promotion — is now fixed in `docs/20-world-design/research-perturbation-compromise-response-reserve-pool-mutual-aid-and-rescue-bridge-successor-promotion.md`.

---

## Cross-links

- `docs/20-world-design/research-perturbation-preference-substitute-appointment-review-and-retired-namespace-replay.md` fixes the immediately prior execution layer that this surface now sharpens.
- `docs/20-world-design/research-low-volume-relay-suppression-cross-roster-substitutes-and-closed-legacy-cutover.md` fixes the threshold / substitute / cutover layer beneath this one.
- `docs/20-world-design/research-extension-namespace-admission-retirement-contested-merge-alias-review-and-relay-capacity-attestations.md` fixes the registry-governance layer beneath this one.
- `docs/20-world-design/independence-packets-appointment-conflict-recusal-funding-and-domination-review.md` fixes the archive's wider conflict / recusal / replacement packet family.

---

## Bottom line

A personhood world should not let a perturbation family become a permanent secret without audit, should not let tiny substitute pools harden into recurring insider tribunals, and should not rescue a broken retired namespace by pretending retirement never happened. The archive therefore now fixes one more compact rule: **perturbation families must be epoch-bound and auditable, substitute pools must rotate against capture with scarcity made visible, and fully retired namespaces may be rescued only through a bridge or successor surface that preserves historical retirement rather than silently reopening the old namespace.** `[REF-0410]` `[REF-0411]` `[REF-0412]` `[REF-0413]` `[REF-0414]` `[REF-0415]` `[REF-0416]` `[REF-0417]` `[REF-0418]` `[REF-0419]` `[REF-0420]` `[REF-0421]` `[REF-0422]` `[REF-0423]`
