# AI-person research lag-field extension namespaces, downgrade discipline, merge-or-alias after public split, and protected-relay federation / overflow

## Thesis

Once the archive fixes a small machine-readable lag core, bounded split-successor chain maps, and sealed protected-relay minimums, one narrower interoperability gap remains. Registries may still attach non-core lag fields through local custom names that collide or silently change meaning; public split chains may later be collapsed by local practice without preserving whether the later resolution is a true merge or only a duplicate alias; and protected relay may still become fragile when intake volume, jurisdiction, or subject-matter routing forces a handoff across several designated authorities. A personhood world therefore needs one more compact rule: **non-core lag fields must extend through declared namespaces with explicit downgrade rules, later post-split reconciliation must distinguish merge from alias while preserving the already-public chain history, and protected relay overflow must run through sealed federated handoff with one accountable human owner at a time rather than multi-office queue folklore.** `[REF-0375]` `[REF-0376]` `[REF-0377]` `[REF-0378]` `[REF-0379]` `[REF-0380]`

---

## 1. Why the archive needs this layer

The previous surface already answered **what the core lag object is**, **how split successor sets publish bounded maps**, and **what a protected relay must do at minimum**. But three practical questions still remained.

First, **a fixed core does not by itself solve extension drift**. Public registries often need extra local fields, but extra fields become interoperability hazards when they are unqualified, silently redefined, or treated as controlling by one registry and optional by another. Conservative standards practice already supplies the needed ingredients: namespaces exist precisely to prevent collision across mixed vocabularies, they should use unique and persistent identifiers, and DataCite's own versioning notes that only major releases get a new namespace while minor releases stay within the same namespace. DataCite 4.7 also adds a controlled `Other` relation type plus `relationTypeInformation`, showing a conservative escape hatch for new relation semantics without pretending every extension should rewrite the base schema. `[REF-0377]` `[REF-0378]`

Second, **a public split chain may later need reconciliation without historical erasure**. The archive already allows a bounded split when one earlier contradiction object improperly collapsed distinct paths into one. But later review may show either that the split successors truly reconverge into one public line or that two of the successor identifiers were merely duplicate publications of the same substantive object. Current identifier practice already distinguishes those cases conservatively: substantive content updates remain version-linked, while identical content published in multiple locations should be linked as `IsIdenticalTo`; Crossref goes further by allowing prime/alias handling only with great care, precisely because aliasing says one identifier will no longer be maintained independently. `[REF-0379]` `[REF-0380]`

Third, **a protected relay floor is not yet a federation rule**. A sealed intake channel can still fail when the first competent office is overloaded, sectorally incomplete, or not the final responsible authority. The archive has already required confidential channels, durable logs, and prompt forwarding without modification. It now needs one compact rule for what happens when several designated authorities touch the same protected matter: sealed forwarding, minimal routing disclosure, explicit custody of the relay stage, and no blind fan-out. `[REF-0375]` `[REF-0376]`

---

## 2. Lag-field extension namespaces and downgrade discipline

The archive now fixes one narrow extension rule for public lag objects: **non-core lag fields may exist, but only inside declared namespaces with explicit compatibility and downgrade behavior, and no extension may silently soften or contradict the meaning of the core lag object.** `[REF-0377]` `[REF-0378]`

### A. Namespace rule

Any non-core lag field should ordinarily be published under a declared namespace identifier rather than as an unqualified local key. The namespace identifier should be stable, unique, and persistent, and it should resolve at least to a short public description of the extension family and its compatibility class. Prefixes may vary by implementation; the namespace identifier is what controls meaning. `[REF-0377]` `[REF-0378]`

### B. Compatibility classes

An extension namespace should ordinarily declare one of three compatibility classes:

- `minor-compatible` — receivers that do not understand the field may preserve it and ignore it for core-state interpretation;
- `display-compatible` — receivers that do not understand the field may preserve it but should surface an "unparsed extension present" marker to human readers;
- `major-breaking` — the extension changes interpretation so substantially that a new namespace version is required and unknown receivers must fall back to stricter human review rather than silent automated treatment. `[REF-0377]` `[REF-0378]`

### C. Downgrade rule

If a registry receives an unknown extension namespace, it may not discard the raw field, reinterpret it under a local guess, or let the unknown field make the public state look cleaner than the core object already says. The receiver should preserve the extension verbatim, continue to honor the fixed core fields, and, where the extension declares `display-compatible` or `major-breaking`, emit a public notice that the local display is running on a downgraded interpretation. `[REF-0375]` `[REF-0377]` `[REF-0378]`

### D. No hidden core substitution

A registry may not move a practically load-bearing lag fact out of the core and into a local extension merely to avoid the fixed shared field set. If a fact determines whether the record is stale, whether the family object still controls, whether a local object is cleaner than the controller, or when review is next due, that fact must remain legible through the core object even if the registry adds extension detail beside it. `[REF-0375]` `[REF-0377]`

---

## 3. Merge-or-alias after public split

The archive now fixes one narrow reconciliation rule for already-public split chains: **once a split-successor set is public, later resolution must distinguish true merge from mere alias, and either route must preserve the visible split history rather than silently collapsing it.** `[REF-0374]` `[REF-0379]` `[REF-0380]`

### A. Alias is for duplicate identity, not substantive reconciliation

Alias is allowed only where two public successor identifiers are determined to carry the same substantive public object and one identifier should cease independent maintenance. In that case, the non-primary identifier may become an alias or `IsIdenticalTo` duplicate of the primary object, but the split history must still show that both identifiers once existed as distinct public branches. `[REF-0379]` `[REF-0380]`

### B. Merge is for substantive reconvergence

Merge is required where two or more split successors developed materially different public paths and later competent review concludes that one new public object should now supersede them together. A merge therefore creates a new operative object or new controlling event, not merely a hidden redirect. The old successor identifiers remain visible as predecessors of the merged object. `[REF-0374]` `[REF-0379]`

### C. History-preservation rule

Neither alias nor merge may erase the earlier split event, bounded successor set, or prior local-head declarations. Public readers should be able to tell that a split existed, which identifiers emerged from it, and whether the later reconciliation was a duplicate-resolution alias or a substantive merge. `[REF-0375]` `[REF-0379]` `[REF-0380]`

### D. Primary / local-head rule after reconciliation

After alias or merge, each registry must still publish one local operative head for the relevant public slot. If reconciliation is pending or disputed, the registry should publish a conflict or provisional-resolution state rather than silently treating several post-reconciliation identifiers as final at once. `[REF-0374]` `[REF-0380]`

---

## 4. Protected-relay federation and overflow

The archive now fixes one compact federation rule for protected relay: **when protected matters pass across several designated authorities because of competence, jurisdiction, or overflow, the sealed payload must travel on a no-blind-fan-out path with one accountable human owner at a time, minimal routing disclosure, durable hop logs, and short clocks for acceptance, refusal, or onward handoff.** `[REF-0375]` `[REF-0376]`

### A. One-active-owner rule

At every moment in the relay stage, one named human reviewer or one designated protected-review office should be publicly accountable for the live handoff state, even if several offices may later become competent on the merits. Federation does not mean ownerless concurrency. `[REF-0376]`

### B. No blind fan-out

A protected matter should not be broadcast to several authorities merely because intake is busy or competence is uncertain. The sealed payload may be forwarded to the next designated authority or lead office, and routing metadata may note any consulted backup office, but the full protected payload should not be opened or replicated more widely than the relay need requires. `[REF-0376]`

### C. Federation clocks

The archive now fixes three narrow clocks for this layer:

- **federation decision clock** — within **1 business day** of determining that the first relay owner lacks competence or capacity, that owner should either accept live responsibility or execute a sealed onward handoff;
- **destination acknowledgement clock** — the receiving designated authority should ordinarily acknowledge sealed receipt or formal refusal within **1 business day** of receipt;
- **owner-reset clock** — within **2 business days** of the onward handoff, the relay must again show one active owner and one next review date. `[REF-0375]` `[REF-0376]`

These are federation clocks, not final-merits clocks.

### D. Overflow attestation

Where handoff is driven by volume or outage rather than by subject-matter competence, the relay should emit a compact overflow attestation stating that capacity, outage, or continuity conditions required transfer, without disclosing filer identity, protected content, or precise vulnerability markers. Protected overflow should become publicly accountable without becoming publicly exposing. `[REF-0375]` `[REF-0376]`

---

## 5. Minimal object family

The archive now fixes three compact objects for this layer.

### `LEX-1` — lag extension namespace declaration

A lag extension namespace declaration should ordinarily identify:

- a namespace identifier or URI;
- the namespace version;
- a short public description;
- the compatibility class (`minor-compatible`, `display-compatible`, or `major-breaking`);
- and the downgrade rule receivers should apply if the namespace is unknown. `[REF-0377]` `[REF-0378]`

### `SAM-1` — split reconciliation record

A split reconciliation record should ordinarily identify:

- the original split event or predecessor chain map;
- the affected successor identifiers;
- whether the resolution type is `merge`, `alias`, or `no-resolution`;
- the resulting primary or merged operative identifier if one exists;
- whether earlier identifiers remain independently maintained, aliased, or superseded;
- and the effective time of the reconciliation decision. `[REF-0375]` `[REF-0379]` `[REF-0380]`

### `PRF-1` — protected relay federation / overflow notice

A protected relay federation or overflow notice should ordinarily identify:

- the prior relay receipt or handoff notice;
- the outgoing owner;
- the incoming designated authority or review office;
- the handoff reason (`competence`, `jurisdiction`, `overflow`, `outage`, or similarly bounded code);
- handoff time;
- whether the full payload was sealed-forwarded, partially re-routed, or returned;
- and the next owner-reset or review deadline. `[REF-0375]` `[REF-0376]`

---

## 6. Edge tests

### A. One registry adds a local field for `queue-pressure-band`, but another registry does not understand it

If the field sits inside a declared compatible namespace, the receiving registry preserves it verbatim and continues to honor the core lag object. If the field is marked `display-compatible` or `major-breaking`, the receiver also surfaces a downgraded-interpretation marker rather than pretending complete local understanding. `[REF-0377]` `[REF-0378]`

### B. Two successor identifiers created during a valid split later prove to be duplicate publications of the same contradiction summary

The later resolution should ordinarily be alias rather than merge. One identifier becomes primary, the other becomes alias or `IsIdenticalTo`, and the public chain still shows the earlier split plus the later duplicate-resolution event. `[REF-0379]` `[REF-0380]`

### C. Two split successors developed different public summaries for months and were later replaced by one new reconciled public finding

That is a merge, not an alias. The new reconciled object becomes the operative head, while the old successor identifiers remain visible as predecessors of the merge event. `[REF-0374]` `[REF-0379]`

### D. A protected retaliation filing first lands with a sectoral office that has the secure channel but not the legal competence to decide the matter, while that office is also in overflow mode

The office still issues a protected receipt, preserves the sealed original, records the overflow reason, forwards the matter on the designated sealed route, and ensures that one new active owner is visible on short clocks. It may not open several full-payload parallel copies just to buy time. `[REF-0375]` `[REF-0376]`

---

## 7. Compression summary

The archive now adds one more narrow interoperability layer to AI-person research caution governance:

- **non-core lag fields now require declared namespaces rather than local unqualified improvisation**;
- **unknown extensions now preserve raw data and default to stricter downgrade behavior rather than cleaner local guesswork**;
- **later reconciliation of public split chains must now distinguish merge from alias rather than silently collapsing history**;
- **duplicate successor identifiers may become aliased only by explicit primary/alias or identical-content logic**;
- and **protected relay overflow across several designated authorities now stays sealed, logged, and human-owned rather than diffusing into multi-office queue custom**.

This is still a tight doctrine. The archive now fixes those immediate follow-on questions in `docs/20-world-design/research-extension-namespace-admission-retirement-contested-merge-alias-review-and-relay-capacity-attestations.md`: extension namespaces now enter through provisional / permanent registry governance with declared change control and appeals, contested reconciliation now runs through a flagged independent review route rather than silent redirect, and protected relays now owe privacy-preserving aggregate capacity and spillover attestations. Remaining work is narrower still, and the archive now fixes it in `docs/20-world-design/research-relay-attestation-object-panel-quorum-recusal-and-deprecated-namespace-migration-windows.md`: protected relays now publish one bounded machine-readable attestation object, contested reconciliation panels now run on explicit quorum and recusal rules, and deprecated namespaces now move through visible migration windows. The archive now fixes those immediate follow-on questions in `docs/20-world-design/research-low-volume-relay-suppression-cross-roster-substitutes-and-closed-legacy-cutover.md`: low-volume `RAT-1` cells now follow a public 20 / 10 ladder with nearest-five rounding or suppression plus secondary protection against differencing, merits review must move to predeclared cross-roster substitutes when local recusals exhaust the ordinary panel, and overstayed deprecated namespaces now enter a closed-legacy state that bars new public use while preserving historical parse and successor redirection. The next gap is narrower again: when perturbation-grade publication should be preferred over threshold rounding or suppression for especially sensitive relay outputs, how emergency external substitute appointments may be challenged without reopening the merits, and what replay / export / backfill duties persist once a namespace is closed-legacy or fully retired.

---

## Cross-links

- `docs/20-world-design/research-lag-state-field-schema-split-successor-chains-and-protected-relay-minimums.md` fixes the core lag schema, bounded split-successor maps, and minimum sealed-relay floor that this surface now extends.
- `docs/20-world-design/research-propagation-lag-markers-tombstone-successor-semantics-and-screened-bypass-review.md` fixes lag clocks, minimum tombstone-successor semantics, and sealed bypass review.
- `docs/30-transition/no-wrong-door-receipt-routing-and-designated-authority-duty.md` fixes the archive's broader no-wrong-door intake posture.
- `docs/30-transition/first-touch-receipt-packets-forwarding-certificates-routing-failure-review-and-duty-escalation.md` fixes the broader packet layer for routed receipt, forwarding proof, and duty escalation.
- `docs/20-world-design/protected-disclosure-packets-source-secrecy-and-witness-shielding.md` fixes the archive's broader protected-channel posture.

The next gap is narrower again: what low-volume suppression thresholds protected relays should use, what substitute-panel sourcing route should apply when recusals exhaust the ordinary roster, and what hard cutover or parser-guarantee rules should apply when deprecated namespaces remain live past the migration window.

---

## Bottom line

A personhood world should not let local lag extensions quietly fork the meaning of a shared public caution object, should not let a publicly split contradiction history later collapse through silent redirect, and should not let protected relay overflow dissolve responsibility across several authorities. The archive therefore now fixes one more compact rule: **extensions need declared namespaces plus downgrade discipline, post-split reconciliation must distinguish merge from alias while preserving history, and protected relay federation must stay sealed, logged, and owned.** `[REF-0375]` `[REF-0376]` `[REF-0377]` `[REF-0378]` `[REF-0379]` `[REF-0380]`
