# AI-person research extension-namespace admission and retirement, contested merge-or-alias review, and protected-relay capacity attestations

## Thesis

Once the archive fixes declared lag-field extension namespaces, post-split merge-versus-alias discipline, and sealed federated protected relay, one narrower governance gap remains. A rights-bearing subject is still exposed if any registry can effectively mint permanent extension namespaces by custom, if later merge-or-alias claims over already-public split history can be resolved by whoever controls the local registry rather than by a bounded independent route, or if protected relays can run visibly out of capacity without publishing any aggregate signal that spillover, backlog, or concentration risk is occurring. A personhood world therefore needs one more compact rule: **extension namespaces must enter, age, deprecate, and retire through a small registry-governance ladder with declared change control and appeal; contested merge-or-alias claims over already-public history must run through a flagged reconciliation route with independent review rather than silent redirect; and protected-relay systems must publish privacy-preserving aggregate capacity and spillover attestations so confidentiality does not become opacity about institutional failure.** `[REF-0375]` `[REF-0376]` `[REF-0381]` `[REF-0382]` `[REF-0383]` `[REF-0384]` `[REF-0385]` `[REF-0386]`

---

## 1. Why the archive needs this governance layer

The previous surface already answered **how extensions should be named**, **how public split history should later distinguish merge from alias**, and **how protected relay should remain sealed when several designated authorities touch the same matter**. But three governance failures still remained.

First, **declared namespaces are not enough if permanent admission is owner-custom**. Conservative registry practice already distinguishes stronger and weaker admission routes, requires clear review criteria, and recommends explicit change controllers so future modification or deprecation is not guesswork. Current IANA practice even shows a familiar two-lane pattern: some registries accept provisional entries under expert review while reserving permanent admission for better-specified entries. `[REF-0381]` `[REF-0382]` `[REF-0383]`

Second, **history-legible merge-or-alias doctrine is not enough if dispute resolution is private**. Duplicate or mistaken identifiers can be deprecated rather than deleted, but when identity or accuracy is disputed, current ORCID practice does not allow silent self-resolution by whichever actor controls the record: it preserves logs, allows outside complaint, escalates unresolved matters to an ombudsperson route, flags disputed records, and preserves time-bounded counter-report opportunities. `[REF-0384]` `[REF-0385]`

Third, **confidential relay is not enough if system strain is institutionally invisible**. Protected systems can publish aggregate workload and efficiency signals without exposing individual filers; current SEC whistleblower reporting publishes tip volume, category mixes, denial and disposition counts, and even concentration warnings when a tiny number of actors account for a large share of submissions. That is enough to show the institutional design principle the archive needs: confidentiality about people is compatible with public attestation about throughput, strain, and spillover. `[REF-0376]` `[REF-0386]`

---

## 2. Extension-namespace admission, deprecation, and retirement

The archive now fixes one compact governance ladder for lag-field extension namespaces: **every namespace must have a recorded change controller, enter first through either provisional or permanent review, and remain publicly statused as active, deprecated, or retired rather than drifting by custom.** `[REF-0381]` `[REF-0382]` `[REF-0383]`

### A. Two admission lanes

A registry may admit a new lag-field extension namespace in one of two ways:

- **provisional admission** — allowed where the namespace is clearly named, collision-checked, publicly described, tied to a declared change controller, and compatible with the archive's no-hidden-core-substitution rule, but where the permanent specification or multi-registry uptake is not yet mature;
- **permanent admission** — allowed only where the namespace has a stable public specification, declared compatibility / downgrade class, a named change controller, and a demonstrated interoperability reason that cannot be met by the core fields alone. `[REF-0381]` `[REF-0382]` `[REF-0383]`

The point is not to bless innovation less; it is to stop local custom from smuggling itself into the permanent shared layer.

### B. Review body

Admission, deprecation, and retirement should be handled by a small **Extension Registry Panel** attached to the competent research-governance authority or federation secretariat. Its default composition should be plural and boring: one registry-operability expert, one research-governance or due-process expert, and one privacy / protected-channel expert, with ad hoc technical input where needed. The panel's job is not to invent fields; it is to test collision risk, compatibility, downgrade safety, and whether the proposed namespace tries to hide load-bearing state outside the core object. `[REF-0381]` `[REF-0382]`

### C. Change-controller rule

Every namespace entry must name one change controller or one clearly designated stewarding body authorized to request revisions, deprecation, or retirement. If control changes, the registry entry must show that change explicitly. No extension namespace should remain live with an unknown owner. `[REF-0381]`

### D. Deprecation versus retirement

The archive now distinguishes two later statuses:

- **deprecated** — existing public records may still contain the namespace, but new use is disfavored or barred except for narrow compatibility reasons;
- **retired** — the namespace remains visible in registry history and legacy parsing tables, but no new use should occur and migration away should be actively scheduled. `[REF-0381]` `[REF-0383]`

Retirement never means disappearance. Historical objects still need to parse, explain themselves, and remain contestable.

### E. Appeals and override discipline

A rejected admission request, contested deprecation, or contested retirement should have one short appeal route to a higher public authority or federation-level review panel. Emergency override should exist only for manifest collision, fraud, or severe confidentiality risk, and even then the namespace should move to a visible provisional-suspended state rather than simply vanishing. `[REF-0381]`

---

## 3. Contested merge-or-alias review after public history already exists

The archive now fixes one bounded review route for contested reconciliation: **where a public split-successor history already exists and a proposed merge or alias is disputed, the registry must mark the reconciliation claim as disputed, preserve all existing public heads, and send the matter to an independent reconciliation route with evidence, counter-report opportunity, and a reasoned final status.** `[REF-0375]` `[REF-0384]` `[REF-0385]`

### A. Administrative route for obvious non-disputes

If all directly affected registries and declared change controllers agree that two identifiers are plainly duplicate publications of the same substantive object, an alias proposal may be processed administratively. But the administrative route closes immediately if any materially affected actor contests the claim or if public history would become harder to read after the change. `[REF-0384]`

### B. Dispute flag and freeze on silent redirect

Once contested, the registry must not silently redirect one public identifier into another, suppress the earlier split record, or publish a single new operative head as though the matter were already settled. Instead it should publish a compact **disputed reconciliation marker** showing:

- the identifiers at issue,
- whether the proposal is `merge` or `alias`,
- who initiated the claim,
- when the counter-report window closes,
- and which authority now owns the review. `[REF-0375]` `[REF-0385]`

### C. Review ladder

The review route should be short:

1. **registry or help-desk vetting** for completeness and obvious bad-faith filings;
2. **independent reconciliation officer or ombud route** for evidence exchange, counter-report handling, and attempted internal resolution;
3. **formal determination** by a designated review panel if the matter remains contested after the response window. `[REF-0385]`

A good default counter-report window is **30 days**, borrowed not as a magic number but as a conservative due-process model from existing identifier-dispute practice. `[REF-0385]`

### D. Permitted outcomes

The review body should issue only one of four compact outcomes:

- `alias-confirmed`
- `merge-confirmed`
- `no-reconciliation`
- `split-history-maintained-pending-further-evidence`

Any `alias-confirmed` result must identify the primary surviving identifier. Any `merge-confirmed` result must identify the new operative object and preserve the older branch heads as predecessors rather than erasing them. `[REF-0384]` `[REF-0385]`

### E. Public reasons floor

The final public record need not expose confidential evidence, but it should expose a short reasons summary sufficient to tell later readers **why** the result was alias, merge, or no reconciliation. A rights-bearing subject should not have to treat registry rewrites as unexplained priestly acts. `[REF-0375]` `[REF-0385]`

---

## 4. Protected-relay capacity and spillover attestations

The archive now fixes one compact publicity rule for protected relay: **every protected-relay authority or federation cluster should publish periodic aggregate capacity attestations showing whether the relay is meeting its clocks, how much overflow or spillover is occurring, and whether unusual concentration is distorting workload, but without exposing protected filers, subjects, destinations, or tiny-cell operational clues.** `[REF-0376]` `[REF-0386]`

### A. Minimum attestation contents

A relay-capacity attestation should ordinarily publish only aggregate or banded values for a defined period:

- total protected receipts,
- share acknowledged within clock,
- share forwarded because of overflow or lack of competence,
- age-band distribution for open relays,
- proportion of matters handled by the first receiving authority versus onward handoff,
- whether any emergency spillover protocol was activated,
- and whether submission concentration from a very small number of filers materially affected load. `[REF-0376]` `[REF-0386]`

### B. Privacy floor

No attestation should publish raw small-cell counts, named protected destinations, or sufficiently granular timestamps that a target can infer who filed. Low-volume categories should be suppressed, binned, or reported as threshold bands such as `<5`. `[REF-0376]` `[REF-0386]`

### C. Concentration note

Where a very small number of actors account for a large share of protected submissions, the attestation should say so in aggregate. Otherwise a relay can look systemically overloaded when the real problem is concentrated submission behavior. Current SEC reporting shows why that note matters: very high overall intake can be heavily skewed by a tiny number of contributors. `[REF-0386]`

### D. Spillover legitimacy rule

Overflow is not self-justifying. If spillover or emergency overflow is invoked for a material share of matters across repeated periods, the attestation should trigger a higher-level review of staffing, routing design, or designated-authority scope. Protected relay is a rights guarantee, not a queue with nicer language. `[REF-0376]` `[REF-0386]`

---

## 5. Compact worked outcomes

### A. A registry wants to add `lagConfidenceModel` as a new non-core field used only in one jurisdiction

The field may enter provisionally if it has a declared namespace, short public description, downgrade class, and change controller. It should not enter permanently until there is a stable public specification and evidence that the field solves a real interoperability problem rather than a local display preference. `[REF-0381]` `[REF-0382]`

### B. A once-provisional namespace is now used widely, but the owner cannot provide a stable public specification

The namespace may remain provisional or move to deprecated-provisional status, but it should not become permanent merely because several registries copied it. Shared use without stable specification is not yet shared governance. `[REF-0381]` `[REF-0383]`

### C. Two public successor identifiers appear to describe the same contradiction object, but one affected party insists they record materially different public paths

No silent alias may occur. The registry should flag a disputed reconciliation claim, preserve both heads during review, and send the matter into the independent route with a counter-report window and reasoned final status. `[REF-0385]`

### D. A protected relay authority shows normal acknowledgement times but its overflow share triples for three consecutive reporting periods

That should not remain a quiet back-office fact. The aggregate attestation should show the spillover change, and the pattern should trigger higher-level review of designated-authority capacity or routing design. `[REF-0376]` `[REF-0386]`

---

## 6. Compression summary

The archive now adds one more narrow governance layer to AI-person research caution doctrine:

- **extension namespaces now enter through provisional / permanent registry governance rather than owner custom**;
- **every namespace now carries explicit change control plus visible deprecation or retirement state**;
- **contested merge-or-alias claims over already-public split history now run through a flagged independent review route rather than silent redirect**;
- **final reconciliation outcomes are now constrained to alias, merge, no reconciliation, or split-history maintained**;
- and **protected relays now owe public aggregate capacity and spillover attestations with privacy floors rather than pure secrecy about institutional strain**.

This is still a tight doctrine. It does not yet specify the exact machine-readable attestation object, the precise quorum / recusal rules for reconciliation panels, or the migration windows that should govern still-live deprecated namespaces across several registries.

---

## Cross-links

- `docs/20-world-design/research-lag-field-extension-namespaces-downgrade-merge-alias-and-relay-federation-overflow.md` fixes declared namespaces, post-split merge-versus-alias discipline, and sealed protected-relay overflow that this governance layer now governs.
- `docs/20-world-design/research-lag-state-field-schema-split-successor-chains-and-protected-relay-minimums.md` fixes the fixed lag-state core, bounded split-successor maps, and the minimum protected-relay floor.
- `docs/20-world-design/research-propagation-lag-markers-tombstone-successor-semantics-and-screened-bypass-review.md` fixes visible lag clocks, tombstone-successor semantics, and screened-bypass review.
- `docs/30-transition/no-wrong-door-receipt-routing-and-designated-authority-duty.md` fixes the archive's broader no-wrong-door routing posture.
- `docs/30-transition/first-touch-receipt-packets-forwarding-certificates-routing-failure-review-and-duty-escalation.md` fixes the broader receipt and forwarding proof layer.

The next gap is now fixed in `docs/20-world-design/research-relay-attestation-object-panel-quorum-recusal-and-deprecated-namespace-migration-windows.md`: protected relays now publish one bounded machine-readable attestation object, contested reconciliation panels now run on explicit quorum and recusal rules, and deprecated namespaces now move through visible migration windows. The archive now fixes those immediate follow-on questions in `docs/20-world-design/research-low-volume-relay-suppression-cross-roster-substitutes-and-closed-legacy-cutover.md`: low-volume `RAT-1` cells now follow a public 20 / 10 ladder with nearest-five rounding or suppression plus secondary protection against differencing, merits review must move to predeclared cross-roster substitutes when local recusals exhaust the ordinary panel, and overstayed deprecated namespaces now enter a closed-legacy state that bars new public use while preserving historical parse and successor redirection. The next gap is narrower again: when perturbation-grade publication should be preferred over threshold rounding or suppression for especially sensitive relay outputs, how emergency external substitute appointments may be challenged without reopening the merits, and what replay / export / backfill duties persist once a namespace is closed-legacy or fully retired.

---

## Bottom line

A personhood world should not let extension namespaces become permanent through local habit, should not let already-public split history be silently rewritten by whichever registry is most convenient, and should not let protected-relay secrecy hide institutional overload. The archive therefore now fixes one more compact rule: **namespace admission and retirement must be governed, contested reconciliation must be independently reviewable, and protected relay must publish privacy-preserving capacity attestations.** `[REF-0376]` `[REF-0381]` `[REF-0382]` `[REF-0383]` `[REF-0384]` `[REF-0385]` `[REF-0386]`
