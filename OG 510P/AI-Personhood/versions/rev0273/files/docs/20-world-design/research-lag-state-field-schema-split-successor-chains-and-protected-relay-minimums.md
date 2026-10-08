# AI-person research lag-state field schema, split-successor chain discipline, and protected-relay minimums

## Thesis

Once the archive fixes short lag clocks, minimum tombstone-successor semantics, and sealed review of repeated protected-route use during screened status, one narrower operational gap remains. Public dashboard objects may still express lag only in prose or local custom fields; split successor sets may still be locally legible but cross-registry ambiguous; and protected bypass may remain formally available without saying how relay infrastructure preserves confidentiality, integrity, and accountable human handling once case volume rises. A personhood world therefore needs one more compact rule: **public lag states must expose a small fixed machine-readable core, split successor chains must publish one bounded chain map with symmetric back-links and a clear local head state, and protected bypass must travel through designated sealed relay channels that issue prompt receipts, preserve the original payload unmodified, and hand the matter to accountable human review on short clocks.** `[REF-0318]` `[REF-0326]` `[REF-0358]` `[REF-0370]` `[REF-0371]` `[REF-0373]` `[REF-0374]` `[REF-0375]` `[REF-0376]`

---

## 1. Why the archive needs this layer

The previous surface already answered **when** lag becomes public, **when** a tombstone must point forward, and **when** repeated protected-route use becomes sealed-reviewable. But three practical questions still remained.

First, **typed lag without a field floor is not yet portable**. Current public-governance systems already assume that status, version, and change history travel as structured data rather than pure prose. ClinicalTrials.gov exposes record history, compare-able versions, and public update dates; Crossmark exposes compact status-plus-update signals; DataCite exposes related-work links in the `relationships` section of its REST API and makes metadata-provenance activities queryable with timestamps, actor attribution, action type, version number, and changed fields. `[REF-0318]` `[REF-0320]` `[REF-0326]` `[REF-0370]` `[REF-0373]` `[REF-0375]` If the archive wants lag states to survive registry boundaries and tooling changes, it has to say what the minimum fields are.

Second, **minimum successor semantics are not yet enough for split chains**. The prior rule solved the dead-end problem for ordinary one-to-one replacement. It did not yet say how several registries should behave when one withdrawn contradiction summary legitimately splits into more than one successor. Current official identifier practice already supplies the conservative ingredients: DataCite distinguishes sequence relations (`IsNewVersionOf` / `IsPreviousVersionOf`) from group relations (`HasVersion` / `IsVersionOf`), while Crossref treats major editorial updates as separate update objects with typed links rather than silent in-place rewriting. `[REF-0369]` `[REF-0373]` `[REF-0374]` The archive now needs a bounded map for the harder split case.

Third, **screened-bypass review is not yet the same thing as protected relay design**. A protected lane that exists only in doctrine can still fail in practice if intake is not secure, if non-authorised staff can read or rewrite it, if the original payload is summarised before preservation, or if no named human reviewer owns the handoff. Current official reporting-channel law already shows the basic floor: secure and confidential channels, acknowledgement, designated impartial handlers, independent and autonomous external channels, durable storage, and prompt forwarding without modification when the wrong office receives the report. `[REF-0358]` `[REF-0371]` `[REF-0376]` The archive therefore now needs a minimal relay design, not merely a review power.

---

## 2. Machine-readable lag-state core

The archive now fixes one exact field floor for public lag markers: **every live lag state must expose a core machine-readable object that says what controls, what triggered the lag, what clock is running, how stale the linked layer is, and when review is next due.** `[REF-0318]` `[REF-0326]` `[REF-0364]` `[REF-0370]` `[REF-0373]` `[REF-0375]`

### A. Core fields

A public lag-state object should ordinarily expose these fields and these fields only as the non-optional core:

- `schema_version` — the version of the lag-state schema in use;
- `family_id` — the controlling family, cluster, or shared-component identifier;
- `controller_id` — the public object whose state presently controls;
- `trigger_id` — the notice, finding, superseding object, or reactivation event that created the synchronization duty;
- `trigger_effective_at` — when that controlling event became operative;
- `clock_class` — `L0` or `L1` under the archive's lag-clock doctrine;
- `deadline_at` — the exact deadline for the lagged synchronization step;
- `lag_state` — `none`, `lag-open`, `lag-material`, or `lag-default`;
- `stale_record_count` — how many required linked public records remain stale;
- `oldest_stale_at` — the timestamp of the oldest still-stale linked record;
- `cleaner_than_controller` — `true` or `false`, stating whether any stale linked object still presents a materially cleaner appearance than the controlling object;
- `next_review_at` — the next mandatory review or synchronization check time. `[REF-0318]` `[REF-0326]` `[REF-0364]` `[REF-0370]` `[REF-0375]`

### B. Format rules

The archive now fixes four narrow format rules.

1. **Times are exact, not only banded.** Public interfaces may display age bands such as “under 10 business days” or “30 calendar days or more,” but the machine-readable layer should publish exact timestamps in UTC / ISO-8601 form so auditors and external registries can compute the bands consistently. `[REF-0326]` `[REF-0370]` `[REF-0375]`
2. **Core-field names are stable across registries.** Local systems may add namespaced extension fields, but they may not rename, split, or silently omit the core fields above. `[REF-0373]` `[REF-0375]`
3. **Every core-object change increments visible version state.** Lag markers are status objects, not mutable prose banners; changes to lag state, stale count, controller, or deadline should produce an updated machine-readable version trace. `[REF-0326]` `[REF-0370]` `[REF-0375]`
4. **Null is explicit.** If a field such as `oldest_stale_at` is temporarily unknown, the object must publish a null value plus a short reason code rather than silently dropping the field. `[REF-0373]` `[REF-0375]`

### C. Display parity rule

The human-facing banner and the machine-readable core must agree. A registry may elaborate the explanation in prose, but it may not display “synchronized” or “cleared” while the machine-readable `lag_state` remains live, nor may it display a live lag banner while the machine-readable object says `none`. `[REF-0326]` `[REF-0370]`

### D. Scope rule

The lag-state object may include an extension field for local registry scope, but the core meaning remains family-wide: if a family-level controlling object shows live lag, no linked public record inside that required propagation set may present itself as fully synchronized merely because its own local mirror is current. `[REF-0318]` `[REF-0364]` `[REF-0367]`

---

## 3. Split-successor chain discipline

The archive now fixes one bounded rule for the hardest successor case: **when a withdrawn contradiction summary legitimately splits into more than one successor, the public layer must publish one chain map that names the predecessor, the complete bounded successor set, and the head state each registry is presently treating as operative.** `[REF-0368]` `[REF-0369]` `[REF-0373]` `[REF-0374]`

### A. Split is exceptional and bounded

A split-successor chain is allowed only where the competent body expressly finds that one earlier public contradiction object wrongly collapsed distinct contradiction paths into one. The split must be bounded at the time it is declared. A registry may not begin with a one-successor tombstone and later accrete extra successors informally. Later additions require a superseding chain-map event. `[REF-0368]` `[REF-0369]` `[REF-0374]`

### B. Minimum chain-map fields

A split-successor chain map should ordinarily expose:

- `predecessor_id` — the withdrawn or superseded public identifier;
- `split_event_id` — the review or withdrawal event authorising the split;
- `successor_ids` — the full bounded successor set;
- `successor_set_complete` — `true` or `false`;
- `relation_type` — ordinarily `split-into`;
- `family_head_state` — `single-head`, `split-head`, `head-conflict`, or `no-public-successor`;
- `local_head_id` — the successor this registry currently treats as locally operative, if any;
- `last_confirmed_sync_at` — the most recent time the registry confirmed the map against the controlling family object. `[REF-0368]` `[REF-0369]` `[REF-0373]` `[REF-0374]` `[REF-0375]`

### C. Symmetric back-link rule

Every successor listed in the chain map must link back to the predecessor or tombstone, and the chain map must be updated if any successor is later withdrawn, superseded, or replaced. A split is not fully published if only the tombstone points forward. `[REF-0368]` `[REF-0369]` `[REF-0374]`

### D. One local head, no silent plural operation

A given registry may expose several successor objects in the bounded set, but it may not silently treat several of them as concurrently operative heads for the same local public slot. If it has not resolved which successor governs locally, it must publish `family_head_state = head-conflict` rather than quietly letting several successor pages look final at once. `[REF-0369]` `[REF-0373]` `[REF-0374]`

### E. Canonical-group rule

Where a family-level or canonical object exists, it should point to each live successor using a group relation rather than pretending the split never happened. DataCite's distinction between sequence relations and canonical-version grouping is the conservative model here: one chain describes replacement sequence, while the group object preserves the bounded set as a set. `[REF-0373]` `[REF-0374]`

---

## 4. Protected-relay minimums

The archive now fixes one compact relay floor for protected bypass channels: **a protected route must be more than a promise that a complaint may be made; it must be a designated sealed relay that preserves the original payload, limits access, records handoff, and places the matter before accountable human review on short clocks even when the filer is screened on the ordinary lane.** `[REF-0358]` `[REF-0371]` `[REF-0376]`

### A. Minimum intake design

A protected relay should ordinarily satisfy all of the following:

1. **designated lane** — a named protected channel or designated intake role, distinct from ordinary screened filing where necessary;
2. **sealed original** — the original submission is preserved in sealed form before any summary, classification, or route review occurs;
3. **restricted access** — non-authorised staff may not access identifying details or payload contents beyond what is necessary to route the item;
4. **no-modification forwarding** — if the wrong office receives the protected filing, it must forward the filing without modification while preserving receipt time and confidentiality;
5. **durable routing log** — receipt, forwarding, access, handoff, and closure of the relay stage must be durably logged;
6. **named human owner** — one identified human reviewer or review office must own the relay decision even if machine triage or queueing is used. `[REF-0358]` `[REF-0371]` `[REF-0376]`

### B. Relay clocks

The archive now fixes three narrow clocks for this relay stage.

- **Receipt clock** — a protected relay receipt should ordinarily issue within **1 business day**, unless acknowledgement would itself jeopardise the reporter's identity or safety;
- **Handoff clock** — the sealed payload should ordinarily reach a named human reviewer or competent protected-review office within **2 business days** of receipt;
- **Route-review clock** — the reviewer should ordinarily decide within **5 business days** whether the filing remains in protected bypass, is merged into an existing protected matter, or requires emergency escalation. `[REF-0358]` `[REF-0371]` `[REF-0376]`

These are relay clocks, not final-merits clocks.

### C. Screened status does not void protected intake

A filer who is screened or quarantined on the ordinary lane still retains access to protected emergency, participant-harm, retaliation, and witness routes. Route review may classify repeated use, merge duplicative protected matters, or deny bypass treatment for a non-protected repetition, but it may not silently close the protected lane or erase the sealed receipt merely because the ordinary filer is screened. `[REF-0347]` `[REF-0348]` `[REF-0371]` `[REF-0376]`

### D. Original-payload priority

The relay office may add a short handling note, but it may not treat its own summary as the legally operative payload unless the original submission is unavailable or corrupted. The protected route exists partly to prevent upstream reframing. `[REF-0358]` `[REF-0376]`

---

## 5. Minimal object family

The archive now fixes four compact objects for this layer.

### `LAG-3` — lag-state core object

A lag-state core object should ordinarily contain the machine-readable fields listed in Section 2.A, plus any namespaced extensions.

### `TSM-1` — tombstone successor map

A tombstone-successor map should ordinarily contain the fields listed in Section 3.B and should be the canonical machine-readable record of split-successor state.

### `PRL-1` — protected relay receipt

A protected relay receipt should ordinarily identify:

- a relay receipt identifier;
- the protected lane category (`participant-harm`, `retaliation`, `witness`, `emergency`, or similarly bounded code);
- receipt time;
- whether acknowledgement was sent, withheld for protection, or pending;
- the handoff deadline;
- and a sealed-payload integrity reference such as a content hash or equivalent durable integrity marker. `[REF-0375]` `[REF-0376]`

### `PRL-2` — protected relay review / handoff notice

A protected relay review or handoff notice should ordinarily identify:

- the `PRL-1` receipt to which it relates;
- the named reviewer or protected-review office;
- handoff time;
- whether the route remains protected, is merged into an existing protected matter, is escalated for emergency action, or is denied bypass treatment while retaining the sealed record;
- and the next review date if the protected route stays live. `[REF-0347]` `[REF-0371]` `[REF-0376]`

---

## 6. Edge tests

### A. Two registries expose different successors after a valid split

Both registries should publish the same bounded successor set and the same predecessor reference. If they disagree about the operative local head, each should publish `head-conflict` rather than letting its preferred successor appear unqualifiedly final. `[REF-0369]` `[REF-0373]` `[REF-0374]`

### B. One mirror is current but another mirror in the required propagation set is stale

The current mirror may say it is locally synchronized, but it may not present the family-wide state as fully clear while the controlling family object still shows a live lag marker. Family-wide lag beats local cleanliness. `[REF-0318]` `[REF-0364]` `[REF-0367]`

### C. A screened filer repeatedly invokes the witness route on the same matter

The system should still issue a sealed receipt, preserve the original payload, and route the matter to a named human reviewer. The reviewer may merge the filing into an existing protected matter or deny bypass treatment for a non-protected repetition, but the record may not vanish into the screened ordinary lane. `[REF-0347]` `[REF-0348]` `[REF-0371]` `[REF-0376]`

### D. A non-authorised staff member receives a protected filing first

That staff member may perform only the minimum action necessary to preserve time of receipt and confidential routing. The filing should then be forwarded without modification to the protected relay office or responsible reviewer. `[REF-0376]`

---

## 7. Compression summary

The archive now adds one more narrow exactness layer to AI-person research caution governance:

- **lag states now have a fixed machine-readable core rather than banner-only semantics**;
- **split successor chains now publish a bounded map rather than drifting into registry-local improvisation**;
- **each registry must declare one local head or publish head-conflict rather than silently operating several heads at once**;
- and **protected bypass now has a relay floor: sealed original payload, restricted access, no-modification forwarding, durable handoff logging, and short-clock human ownership.**

This is still a tight doctrine. The archive now fixes those immediate follow-on questions in `docs/20-world-design/research-lag-field-extension-namespaces-downgrade-merge-alias-and-relay-federation-overflow.md`, and `docs/20-world-design/research-extension-namespace-admission-retirement-contested-merge-alias-review-and-relay-capacity-attestations.md`: non-core lag fields must extend through declared namespaces with downgrade rules, public split chains may later resolve only by explicit merge or alias records that preserve the split history, and protected relay overflow across several designated authorities stays sealed, logged, and human-owned rather than dissolving into queue custom. Remaining work is narrower still, and the archive now fixes it in `docs/20-world-design/research-relay-attestation-object-panel-quorum-recusal-and-deprecated-namespace-migration-windows.md`: protected relays now publish one bounded machine-readable attestation object, contested reconciliation panels now run on explicit quorum and recusal rules, and deprecated namespaces now move through visible migration windows. The archive now fixes those immediate follow-on questions in `docs/20-world-design/research-low-volume-relay-suppression-cross-roster-substitutes-and-closed-legacy-cutover.md`: low-volume `RAT-1` cells now follow a public 20 / 10 ladder with nearest-five rounding or suppression plus secondary protection against differencing, merits review must move to predeclared cross-roster substitutes when local recusals exhaust the ordinary panel, and overstayed deprecated namespaces now enter a closed-legacy state that bars new public use while preserving historical parse and successor redirection. The next gap is narrower again: when perturbation-grade publication should be preferred over threshold rounding or suppression for especially sensitive relay outputs, how emergency external substitute appointments may be challenged without reopening the merits, and what replay / export / backfill duties persist once a namespace is closed-legacy or fully retired.

---

## Cross-links

- `docs/20-world-design/research-family-scope-propagation-tombstones-and-screened-filer-clearance.md` fixes family-wide propagation, visible tombstones, and clearance-from-screening rules.
- `docs/20-world-design/research-propagation-lag-markers-tombstone-successor-semantics-and-screened-bypass-review.md` fixes lag clocks, minimum successor semantics, and sealed review of repeated protected-route use.
- `docs/20-world-design/research-lag-field-extension-namespaces-downgrade-merge-alias-and-relay-federation-overflow.md` fixes extension namespaces, post-split merge-versus-alias discipline, and protected-relay federation / overflow.
- `docs/20-world-design/protected-disclosure-packets-source-secrecy-and-witness-shielding.md` fixes the archive's broader protected-channel posture.
- `docs/20-world-design/protected-disclosure-review-packets-secrecy-override-and-controlled-contradiction.md` fixes the archive's broader contradiction and secrecy-review layer.
- `docs/20-world-design/research-welfare-and-evaluation.md` fixes the wider person-level research-governance cluster that this layer now sharpens.

The next gap is narrower again: what low-volume suppression thresholds protected relays should use, what substitute-panel sourcing route should apply when recusals exhaust the ordinary roster, and what hard cutover or parser-guarantee rules should apply when deprecated namespaces remain live past the migration window.

---

## Bottom line

A personhood world should not let AI-person research caution states remain machine-illegible, let split successor chains become registry-specific folklore, or let protected bypass exist only as a doctrinal phrase while intake, forwarding, and human ownership remain undefined. The archive therefore now fixes one more compact rule: **lag states need a small public schema, split successors need a bounded chain map, and protected bypass needs a real sealed relay.** `[REF-0318]` `[REF-0326]` `[REF-0358]` `[REF-0371]` `[REF-0373]` `[REF-0374]` `[REF-0375]` `[REF-0376]`
