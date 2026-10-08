from pathlib import Path

root = Path(__file__).resolve().parent


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise SystemExit(f'missing pattern: {old[:80]!r}')
    return text.replace(old, new, 1)

# README
p = root / 'README.md'
text = p.read_text()
text = replace_once(text, '- Revision: `rev0077`', '- Revision: `rev0078`')
text = replace_once(text, '- Timestamp: `2026.03.17.19.36` (America/New_York)', '- Timestamp: `2026.03.17.19.58` (America/New_York)')
text = replace_once(text, '- Codename: `mergeproofreconcileharbor`', '- Codename: `fetchproofpresenceharbor`')
old_block = """This revision continues directly from `rev0076` and does seven things:

1. Re-checks **Resilio Sync** again with extra emphasis on the non-empty-target seam: current docs still let `Folder not empty`, reconnect, pre-populated-folder adoption, and encrypted-target intake hide meaningfully different outcomes behind one small confirmation step.
2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let a non-empty-path bind imply one stable behavior when the honest answer may instead be same-lineage reuse, harmless merge, same-path divergence, timestamp-risky replacement, or encrypted-target mismatch.
3. Adds a dedicated **pre-existing-material reconciliation and timestamp-authority spec** so the archive now says what a real operator surface must literally show before binding or repairing a share into a populated path.
4. Extends the **interface and daemon/API contract** with explicit reconciliation cases, chronology posture, target-lineage posture, and receipts rather than leaving merge truth to compare counts plus folklore about clicking through warnings.
5. Extends the **workbench/interface pattern language** so operators can see separately which bytes are identical, local-only, remote-only, same-path divergent, or incompatible with encrypted/annex reuse.
6. Adds an additional **canonical interface flow** for reconciling a pre-populated target without pretending `latest timestamp wins` is a trustworthy operator contract.
7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep non-empty-target reconciliation explicit whenever adoption, repair, relocate, encrypted intake, or reconnect semantics appear.
"""
new_block = """This revision continues directly from `rev0077` and does seven things:

1. Re-checks **Resilio Sync** again with extra emphasis on the fetchability seam: current docs still let placeholders, selective-sync visibility, and delayed warnings hide the harder question of whether any durable full copy still exists.
2. Sharpens the **non-clone rationale** into a stricter rule: AnonSync should not let `visible here` or `available on demand` imply one stable truth when the honest answer may instead be fully backed, remotely backed, local-last-copy, offline-source-guarded, or stale-announcement/ghost-only.
3. Adds a dedicated **fetchability and full-copy-witness spec** so the archive now says what a real operator surface must literally show before evicting, clearing, pinning, or trusting placeholder-visible content.
4. Extends the **interface and daemon/API contract** with explicit fetchability contracts, source-backing posture, ghost-announcement handling, and receipts rather than leaving operators to reconstruct byte availability from placeholder state plus troubleshooting lore.
5. Extends the **workbench/interface pattern language** so operators can see separately which names are visible, which bytes are local, which peers still witness a full copy, and whether an item is fetchable now, guarded, or no longer honestly retrievable.
6. Adds additional **canonical interface flows** for evicting only when another full-copy witness exists and for handling stale/ghost announcements without pretending they are ordinary delayed downloads.
7. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, and **reading order** so future revisions keep fetchability, last-full-copy risk, and ghost-announcement honesty explicit whenever selective materialization or placeholder-visible content appears.
"""
text = replace_once(text, old_block, new_block)
needle = '- a first-class pre-existing-target / reconciliation / chronology surface so operators can tell whether a non-empty bind is same-lineage reuse, harmless merge, same-path divergence, timestamp-risky replacement, or encrypted-target mismatch before apply\n'
insert = needle + '- a first-class fetchability / full-copy-witness / ghost-announcement surface so operators can tell whether a visible path is actually backed by retrievable bytes before they evict, pin, clear, or trust on-demand access\n'
text = replace_once(text, needle, insert)
needle = '- `docs/89-observer-readonly-local-write-and-serve-rights-spec.md` — fixed observer-rights review anatomy for requested posture, visibility reality, local-write behavior, onward serving, projection/class limits, and observer-rights receipts\n'
insert = needle + '- `docs/91-fetchability-and-full-copy-witness-spec.md` — fixed fetchability review anatomy for requested materialization intent, source-backing, full-copy witnesses, ghost/stale-announcement handling, and fetchability receipts\n'
text = replace_once(text, needle, insert)
needle = 'then `88-share-authority-epoch-and-stale-capability-rotation-spec.md`, then `89-observer-readonly-local-write-and-serve-rights-spec.md`, then `41-report-and-intervention-language.md`'
insert = 'then `88-share-authority-epoch-and-stale-capability-rotation-spec.md`, then `89-observer-readonly-local-write-and-serve-rights-spec.md`, then `91-fetchability-and-full-copy-witness-spec.md`, then `41-report-and-intervention-language.md`'
text = replace_once(text, needle, insert)
p.write_text(text)

# Status overwrite for coherence
status = root / 'docs/00-status.md'
status.write_text("""# Status

## Scope of this revision

This revision is an in-place continuation of `rev0077`, driven by the current request:

- continue research and tighten the archive without letting it sprawl
- evaluate Resilio Sync further with enough care that the non-clone case stays evidence-based
- spend more time on interface specs rather than leaving selective-materialization and placeholder-visible truth trapped in mode labels and troubleshooting lore
- keep Linux-first, overlay-first, and least-privilege assumptions intact unless evidence truly breaks them
- keep turning support-lore seams into explicit product contracts
- make sure the archive has a better reason not to clone current Resilio placeholder/on-demand semantics as though visibility and retrievability were the same fact
- make sure namespace visibility, local residency, full-copy witnesses, ghost-announcement risk, and eviction safety stay visibly separate

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- a deeper Resilio-derived warning that current placeholder / Selective Sync behavior still depends on scattered articles about Selective Sync, `.rsls` placeholder handling, `Clear synced files`, ghost-file warnings, and power-user preferences rather than one operator contract
- a dedicated **fetchability and full-copy-witness spec** that says what a real operator surface must literally show before evicting, pinning, clearing, or trusting placeholder-visible content
- stronger interface and daemon/API requirements so source-backing posture, full-copy witnesses, retrievability state, ghost/stale-announcement handling, and fetchability receipts become explicit public objects rather than folklore about placeholders and delayed downloads
- stronger workbench and pattern-language rules so operators can see separately which names are visible, which bytes are local, which peers still witness a real full copy, and whether an item is fetchable now, guarded, or no longer honestly retrievable
- additional canonical flows for (a) evicting only when another full-copy witness exists and (b) handling stale/ghost announcements without pretending they are ordinary delayed downloads
- roadmap, ADR, status, open-question, and README updates so future revisions keep fetchability, last-full-copy risk, and stale-announcement honesty explicit whenever selective materialization or placeholder-visible content appears

## The main shift

`rev0077` proved that non-empty-target bind and reconnect behavior needed one explicit reviewed reconciliation contract rather than warning-box folklore.

`rev0078` applies the same discipline one layer closer to on-demand materialization itself:

> a serious Linux-first workbench still is not specified tightly enough if the archive can define projection, custody, observer posture, and storage budgets honestly, yet still leave one ordinary operator question loose: when a name is visible as placeholder or announced in the tree, is there actually a durable full copy somewhere to fetch, or has the product slipped into local-last-copy risk, offline-source hope, or ghost-announcement folklore?

That changes the archive in six specific ways:

- fetchability now renders as its own reviewed contract instead of hiding behind placeholder visibility or `available on demand` language
- namespace visibility and byte retrievability can no longer masquerade as the same fact
- full-copy witnesses and local-last-copy risk stay visible before evict, clear, or pin changes apply
- ghost/stale announcements can no longer masquerade as ordinary delayed downloads
- workbench and CLI now have one explicit place to compare local residency, source-backing posture, fetchability confidence, and admissible actions before apply
- the Resilio comparison now lands a sharper non-clone argument: the weak seam is not merely an awkward warning, but the lack of one honest reviewed contract for what placeholder-visible content is actually backed by in practice

## What still remains unresolved

This revision intentionally does **not** overclaim closure on several important questions:

- how much of transport identity and overlay publication should be device-wide, share-scoped, or policy-scoped
- how strong disclosure-narrowing guarantees should be before the product becomes noisy or dishonest about residue
- how aggressive the default review queue should be before it becomes noisy
- how much UI simplification is safe without recreating the hidden coupling the archive is trying to escape
- how much one-click automation an exit surface should allow before it starts hiding scope, residue, or follow-up obligations
- how aggressive default compromise freezes should be before the product starts turning suspicion into disruptive magic
- when long-offline or clock-uncertain peers should be allowed to resume writable participation without first-class re-entry review
- when remote delete or overwrite waves should always force destructive-replay review instead of ordinary sync progress
- when non-trivial conflicts should always force full reviewed adjudication instead of a safely compressed resolution path
- when same-host derivations should always force full local-derivation review instead of a safely compressed path
- when live authority changes should always force full authority-mutation review instead of a safely compressed access-change path
- when nested, overlapping, or root-boundary-sensitive topology changes should always force full topology review instead of a safely compressed path
- when writer contention, burst-save delay, or mixed external-writer risk should always force full contention review instead of a safely compressed path
- when RAM pressure, watcher ceilings, indexing cost, or path blockers should always force full capacity-fit review instead of a safely compressed path
- when discovered state, recovery material, or reviewed control exposure should always force full bring-up review instead of a safely compressed startup path
- how broad one reviewed mutation grant may be in v1 before explicit authority becomes either too reusable or too noisy
- when an obviously same-lineage local target may use a safely compressed custody review versus always opening the full ownership-and-lineage sheet
- how much low-risk cross-channel continuation may stay compressed before channel-parity honesty becomes either noisy or too magical
- how much low-risk runtime-seat switching may stay compressed before state continuity, path reachability, and freshness honesty become either noisy or too magical
- how much low-risk relabeling may stay compressed before the product starts hiding meaningful authority replacement or same-person continuity fallout behind harmless-looking naming affordances
- how much low-risk layout cleanup or annex migration may stay compressed before the product starts hiding meaningful data/control separation fallout behind harmless-looking hidden-file cleanup affordances
- how much low-risk semantic optimization may stay compressed before the product starts hiding meaningful guarantee weakening behind harmless-looking speed or compatibility affordances
- how much low-risk recall or retained-copy attestation may stay compressed before the product starts hiding meaningful byte-retention fallout behind harmless-looking revoke/remove affordances
- how much low-risk epoch rotation may stay compressed before the product starts hiding meaningful stale-capability fallout behind harmless-looking key-change, re-share, or share-upgrade affordances
- how much low-risk observer/read-only compression may stay compressed before the product starts hiding meaningful write, serve, or projection differences behind harmless-looking `viewer` or `read only` affordances
- how much low-risk non-empty-target reconciliation may stay compressed before the product starts hiding meaningful lineage, chronology, or encrypted-target differences behind harmless-looking `Add anyway` affordances
- how much low-risk fetchability review may stay compressed before the product starts hiding meaningful source-backing, local-last-copy risk, or ghost-announcement drift behind harmless-looking `available on demand` affordances

## Files added in this revision

- `docs/91-fetchability-and-full-copy-witness-spec.md`
- `update_rev0078.py`

## Files updated in this revision

- `README.md`
- `docs/00-status.md`
- `docs/10-resilio-sync-evaluation.md`
- `docs/30-interface-spec.md`
- `docs/31-daemon-api-spec.md`
- `docs/32-interface-flows.md`
- `docs/38-operator-workbench-interface-spec.md`
- `docs/39-interface-pattern-language.md`
- `docs/40-architecture-decisions.md`
- `docs/50-roadmap.md`
- `docs/64-critical-open-questions.md`
- `docs/91-fetchability-and-full-copy-witness-spec.md`
""")

# Evaluation
p = root / 'docs/10-resilio-sync-evaluation.md'
text = p.read_text()
needle = """If the safe answer is still “click OK”, “ignore the warning”, or “latest timestamp wins”, the interface is not explicit enough.

### Requirement 11 — linked-device convenience must preserve least privilege
"""
insert = """If the safe answer is still “click OK”, “ignore the warning”, or “latest timestamp wins”, the interface is not explicit enough.

### Requirement 10b — placeholder visibility and retrievable bytes must be separate public facts

Resilio's newer docs make this seam unusually explicit too. `Selective Sync` says enabling it means the device receives placeholder information rather than full bytes, and that linked-device Selective Sync can leave all new files presented as `.rsl` placeholders. `What Is an RSLS File?` then says reverting a file to placeholder preserves copies on other peers — but warns that if you and all other peers do this, you can end up with placeholders only and no actual file. `Sync Interface on iOS devices` adds that `Clear synced files` can turn all synced files on the device back into placeholders. Finally, the ghost-file warning article says a peer may announce new or updated files, other peers may merge that tree later, and by then the source may already have reverted to placeholder or removed the bytes entirely, leaving a stale announcement that no peer can now satisfy.

That means one apparently simple user-facing state can hide several operator-different realities:

- visible name plus a confirmed durable full-copy witness elsewhere
- visible name backed only by this local full copy
- visible name backed only by an offline source that may or may not return
- visible name announced in the tree even though no peer now has the bytes
- placeholder-clearing or eviction action that would silently create a placeholder-only universe

AnonSync should therefore expose fetchability and source backing as their own reviewed object.
At minimum the product should expose:

- namespace/materialization posture separately from byte retrievability posture
- full-copy witness summary (`local-only`, `remote-confirmed`, `multi-source-confirmed`, `offline-only`, `none-known`)
- fetchability posture (`fetchable-now`, `fetchable-when-source-returns`, `local-last-copy`, `ghost-risk`, `not-fetchable`)
- eviction safety posture and whether the requested action would remove the last known full copy
- whether a stale announcement should be preserved, re-witnessed, quarantined, or retired from visibility claims
- which admissible actions exist: keep pinned, fetch now, evict safely, defer until another witness exists, or mark as ghost/stale announcement

If the safe answer is still “it shows up, so it must be available”, “just clear synced files”, or “ignore the warning and hope a source returns”, the interface is not explicit enough.

### Requirement 11 — linked-device convenience must preserve least privilege
"""
text = replace_once(text, needle, insert)
p.write_text(text)

# Interface spec
p = root / 'docs/30-interface-spec.md'
text = p.read_text()
needle = """- `pin` means keep local data across space-reclamation passes
- `history` lists restorable prior states with provenance, retention horizon, and allowed scope
"""
insert = """- `pin` means keep local data across space-reclamation passes
- `file availability` should render namespace visibility, local materialization, full-copy witness summary, fetchability posture, ghost/stale-announcement risk, and eviction safety for the selected path or subtree
- `evict` should normally require `--plan` when the target may be the last known full-copy witness or when fetchability is only guarded
- `fetch --require fetchable-now` should fail closed when the path is only announcement-visible, ghost-risk, or backed only by offline/uncertain witnesses
- `history` lists restorable prior states with provenance, retention horizon, and allowed scope
"""
text = replace_once(text, needle, insert)
needle = """#### Pin / unpin

```text
anonsync file pin media Podcasts/
anonsync file unpin media Podcasts/
```

#### History / restore
"""
insert = """#### Pin / unpin

```text
anonsync file pin media Podcasts/
anonsync file unpin media Podcasts/
```

#### Availability / fetchability

```text
anonsync file availability media Podcasts/
anonsync file availability media Episodes/ep001.mp3 --view review
anonsync file fetch media Episodes/ep001.mp3 --require fetchable-now
anonsync file evict media Episodes/ep001.mp3 --plan
```

#### History / restore
"""
text = replace_once(text, needle, insert)
p.write_text(text)

# API spec
p = root / 'docs/31-daemon-api-spec.md'
text = p.read_text()
text = replace_once(text, "POST /v1/files/pin\nPOST /v1/files/unpin\nGET  /v1/files/state?share_id=...&path=...\n", "POST /v1/files/pin\nPOST /v1/files/unpin\nPOST /v1/files/availability/query\nGET  /v1/files/availability?share_id=...&path=...\nGET  /v1/files/state?share_id=...&path=...\n")
needle = """`POST /v1/files/check` should generate a preservation report for actions such as `evict`, `remove-local`, `remove-share`, or `restore-share`.
That report should include remaining plaintext coverage, encrypted-only coverage, history coverage, and any blockers caused by weak rollback posture.

`GET /v1/files/history` should return candidate restore points with provenance, capture cause, retention horizon, confidence, and allowed restore scopes.
"""
insert = """`POST /v1/files/check` should generate a preservation report for actions such as `evict`, `remove-local`, `remove-share`, or `restore-share`.
That report should include remaining plaintext coverage, encrypted-only coverage, history coverage, and any blockers caused by weak rollback posture.

`GET /v1/files/availability` and `POST /v1/files/availability/query` should expose namespace visibility, current local materialization, full-copy witness summary, fetchability posture, ghost/stale-announcement risk, and eviction safety for one path or a reviewed subtree.
Clients should not have to infer “available on demand” from placeholder state alone.
If the only known full copy is local, the response should say so explicitly.
If the path is announcement-visible but no peer now has the bytes, the response should classify it as `ghost-risk` or `not-fetchable`, not merely `pending`.

`GET /v1/files/history` should return candidate restore points with provenance, capture cause, retention horizon, confidence, and allowed restore scopes.
"""
text = replace_once(text, needle, insert)
p.write_text(text)

# Workbench spec
p = root / 'docs/38-operator-workbench-interface-spec.md'
text = p.read_text()
needle = """Those three lines may all start from `read only`, but the product should never force operators to assume they are the same action.

## Danger-zone rules
"""
insert = """Those three lines may all start from `read only`, but the product should never force operators to assume they are the same action.

## Fetchability and full-copy-witness surface

A fetchability surface exists so placeholder-visible, names-only, selectively materialized, or recently evicted content compiles to one reviewed truth instead of a vague `available on demand` label.

A fetchability page should show one fixed review grammar in this order:

1. requested materialization intent
2. visibility and local-residency reality
3. source backing and full-copy witnesses
4. fetchability, ghost risk, and admissible actions
5. collateral effects on eviction, pinning, and serve value
6. receipt promise

Inside those sections the page should still answer at least:

- what exact share/path/subtree is being reviewed and whether the request is inspect-only, fetch, evict, clear, pin, or stale-announcement handling
- whether the subject is visible by full bytes, placeholder, names-only projection, or tree announcement only
- whether the current device holds the only known full copy, one of several confirmed full copies, or no confirmed full copy at all
- whether remote witnesses are online now, merely last-known, or absent entirely
- whether the honest retrievability posture is `fetchable now`, `fetchable when source returns`, `local last copy`, `ghost-risk`, or `not fetchable`
- whether the requested action would remove the easiest remaining recovery path or merely change local residency without risk
- what receipt will later prove the reviewed fetchability truth and the action taken

The page should make one difference visually unavoidable:

- **Proceed because another full-copy witness exists**
- **Proceed only after preserving or pinning the last known full copy**
- **Escalate because this path is visible but not honestly fetchable anymore**

Those three lines may all start from `placeholder` or `available on demand`, but the product should never force operators to assume they are the same action.

## Danger-zone rules
"""
text = replace_once(text, needle, insert)
p.write_text(text)

# Pattern language
p = root / 'docs/39-interface-pattern-language.md'
text = p.read_text()
text += """

## Pattern 22q — visible names are not a fetch promise

A path that is visible in the tree, visible as a placeholder, or visible as a selective-materialization stub must not automatically read as `the bytes are safely fetchable later`.
The product should show whether the bytes are locally present, remotely witnessed, only last-seen on an offline source, or no longer honestly retrievable at all.

This matters because Resilio's own docs now make two dangerous states explicit: placeholder-only universes where nobody still has the full file, and ghost announcements where the tree still advertises a file even though no peer now has the bytes.
A safer product must keep namespace visibility, local residency, full-copy witnesses, and fetchability posture as separate truths.
"""
p.write_text(text)

# ADRs
p = root / 'docs/40-architecture-decisions.md'
text = p.read_text()
text += """

## ADR-080 — Visibility and retrievability are separate public contracts

**Decision:** Introduce explicit fetchability/full-copy-witness objects so placeholder visibility, names-only visibility, and durable byte retrievability never collapse into one casual `available on demand` claim.

**Why:** Current Resilio docs say Selective Sync can expose placeholders without full bytes, reverting files to placeholders can leave nobody with a real file if every peer does it, `Clear synced files` can dematerialize an entire local share, and ghost announcements can persist after no peer still has the bytes. AnonSync should not force operators to reconstruct whether a visible path is actually fetchable from placeholder state plus troubleshooting warnings.

**Consequences:**

- fetchability, full-copy witnesses, local-last-copy risk, and ghost-announcement posture become explicit reviewed state
- evict/clear/pin/fetch actions can fail closed when they would remove the last known full copy or rely on stale announcement-only visibility
- workbench, CLI, and API can render the same honest answer to `can I still get the bytes later?` without support-article archaeology
"""
p.write_text(text)

# Roadmap
p = root / 'docs/50-roadmap.md'
text = p.read_text()
needle = '- operators can tell whether a so-called read-only or observer replica really means names only, placeholders, full bytes, local-write suspension, auto-revert, or serve-clean-bytes-only without support-lore reconstruction\n'
insert = needle + '- operators can tell whether a visible or placeholder-backed path is actually fetchable now, backed only by this local copy, backed only by offline/guarded witnesses, or no longer honestly retrievable at all\n'
text = replace_once(text, needle, insert)
needle = '- capability-aware placeholder strategy selection\n'
insert = needle + '- explicit fetchability/full-copy-witness inspection and receipts\n'
text = replace_once(text, needle, insert)
p.write_text(text)

# Open questions
p = root / 'docs/64-critical-open-questions.md'
text = p.read_text()
text += """

## 59) How much low-risk fetchability review can stay inline before on-demand honesty becomes either noisy or too magical?

The archive is now clearer that placeholder-visible or selectively materialized paths should use first-class fetchability reviews and receipts, but one policy seam remains open:

- when should an obviously multi-witness, online-backed path show inline fetchability chips versus always opening the full fetchability sheet
- whether evicting a path that is currently the only confirmed full copy should always force full review or whether any bounded exceptions are safe
- how much last-seen/offline witness evidence may count before the product starts hiding real local-last-copy risk behind `available later` language
- when ghost/stale-announcement handling should stay one-step versus always forcing preserve, re-witness, or retirement review

This matters because weak defaults recreate placeholder folklore and ghost-file warnings, while overly strict defaults could make harmless fetch/pin/evict work feel ceremonial instead of trustworthy.
"""
p.write_text(text)

# New spec file
spec = root / 'docs/91-fetchability-and-full-copy-witness-spec.md'
spec.write_text("""# Fetchability and full-copy-witness spec

The archive already has projection, file intent, storage budgets, observer posture, and transfer explanations.
This document answers the narrower practical question those abstractions still left open:

> what must a real operator surface literally show before an operator evicts, pins, clears, or trusts placeholder-visible content, so AnonSync does not drift back into `available on demand`, placeholder, or ghost-file folklore?

This is the materialization-truth companion to `44-file-intent-deviation-and-restore-spec.md`, the namespace companion to `46-namespace-projection-and-placeholder-spec.md`, the storage-safety companion to `51-space-pressure-reclaim-and-retention-budget-spec.md`, and the observer-posture companion to `89-observer-readonly-local-write-and-serve-rights-spec.md`.

## Why this needs its own spec

Resilio's docs are strong enough to make the problem unusually clear.
`Selective Sync` says enabling it means the device receives placeholder information rather than full bytes, and that linked-device Selective Sync can leave new files presented as `.rsl` placeholders.
`What Is an RSLS File?` then says reverting a file to placeholder preserves copies on other peers — but warns that if you and all other peers do this, you can end up with placeholders only and no actual file.
`Sync Interface on iOS devices` adds `Clear synced files`, which turns all synced files on that device into placeholders.
Finally, the ghost-file warning article says a peer may announce new or updated files, others may merge the tree later, and by then the source may already have reverted to placeholder or removed the bytes, leaving a stale announcement that no peer can now satisfy.

The lesson is not that selective materialization is bad.
The lesson is that a useful product can still hide too many materially different truths behind one casual `available on demand` story.

AnonSync should therefore make these differences explicit before apply:

- visible name plus confirmed durable full-copy witness elsewhere
- visible name backed only by this local full copy
- visible name backed only by an offline/uncertain source
- visible name announced in the tree even though no peer now has the bytes
- eviction, clear, or placeholder conversion that would silently create a placeholder-only universe

## Core rule

Placeholder visibility, namespace visibility, and durable retrievability are separate public facts.
A path should compile to a reviewed fetchability surface whenever any of these are true:

- the requested action would remove the last known full-copy witness
- remote full-copy witnesses are offline, stale, or unconfirmed enough that future fetch is only guarded
- the subject is visible in namespace but current byte backing is only announcement-level or `ghost`-risk
- a bulk `clear synced files` or subtree eviction would materially weaken the easiest recovery path
- local serve/reseed value still matters even though ordinary local materialization is being reduced

A channel may compress the review when risk is truly low.
It may not replace the meaning with `available on demand`, `placeholder only`, `clear synced files`, or `remove from this device` success language.

## Entry points that must converge

The product may offer several ergonomic entry points:

- workbench file card `Open fetchability`
- storage page `Review last-full-copy risk`
- observer page `Inspect byte backing`
- CLI `anonsync file availability ...`
- CLI `anonsync file evict ... --plan`
- API-backed automation that prepares, shows, and applies fetchability reviews explicitly

But these must all converge on the same public fetchability model.
The operator should never have to wonder whether one surface is merely showing placeholder state while another silently knows there are no real bytes left anywhere.

## Fixed review order

Every non-trivial fetchability review should render the same sections in the same order:

1. **Requested materialization intent**
2. **Visibility and local-residency reality**
3. **Source backing and full-copy witnesses**
4. **Fetchability, ghost risk, and admissible actions**
5. **Collateral effects on eviction, pinning, and serve value**
6. **Receipt promise**

### 1) Requested materialization intent

This section should show:

- triggering share, mount, or path
- requested action (`inspect`, `fetch`, `evict`, `clear`, `pin`, `unpin`, `retire stale announcement`, or similar)
- requested scope (one file, subtree, mount, or whole share)
- whether the operator is changing local residency only or also changing a broader policy/default

The operator must be able to answer: **what exact byte-presence question am I asking, and what action am I about to take?**

### 2) Visibility and local-residency reality

This section should show:

- whether the subject is full-bytes-visible, placeholder-visible, names-only, or announcement-only
- whether bytes are currently local on this device
- whether the current local state is pinned, ordinary, evictable, or already absent
- whether the currently visible name came from ordinary share visibility, local projection, or stale remote announcement

The operator must be able to answer: **what is visible here right now, and how much of it is actually local?**

### 3) Source backing and full-copy witnesses

This section should show:

- whether the current device holds a full copy
- which other peers recently confirmed a full copy
- whether those witnesses are online now, recently seen, stale, or absent
- whether the strongest honest summary is `local-only`, `remote-confirmed`, `multi-source-confirmed`, `offline-only`, `announcement-only`, or `none-known`

The operator must be able to answer: **who, if anyone, still definitely has the bytes?**

### 4) Fetchability, ghost risk, and admissible actions

This section should show:

- fetchability posture (`fetchable-now`, `fetchable-when-source-returns`, `local-last-copy`, `ghost-risk`, `not-fetchable`)
- whether the product is relying on fresh witness evidence, stale witness evidence, or tree-announcement residue only
- whether the requested action may proceed directly, must preserve/pin first, or should block and escalate
- whether stale announcement should be preserved, re-witnessed, retired, or explicitly left visible with a guarded warning

The operator must be able to answer: **can I still get these bytes later, and what honest actions are available from here?**

### 5) Collateral effects on eviction, pinning, and serve value

This section should show:

- whether evicting or clearing would remove the last known full copy
- whether pinning would materially improve recovery or serve posture
- whether local bytes still matter for reseed or other peers even if this mount is not authoritative
- whether a bulk action changes ordinary local convenience only or materially weakens the easiest recovery path

The operator must be able to answer: **what operational value do these bytes still have if I keep or remove them?**

### 6) Receipt promise

This section should show:

- which fetchability receipt will exist after apply
- what it will later prove about visibility, local residency, full-copy witnesses, fetchability posture, and chosen action
- whether witness quality was strict or guarded
- what later audit survives after the placeholder badge or warning row is gone

The operator must be able to answer: **what later evidence will prove why I trusted, pinned, evicted, or retired this visible path?**

## What the surface must never imply

The fetchability surface must never imply that these are the same thing:

- visible name vs durable retrievable bytes
- placeholder-visible vs remotely backed by a confirmed full copy
- offline witness hope vs current fetchability
- local clear/evict convenience vs removing the last known full copy
- stale announcement vs delayed but still honest download availability

If the product compresses those differences, it has recreated the ritual it is trying to replace.

## CLI projection expectation

A textual projection should be able to render the fixed review order directly, for example through `anonsync file availability <share> <path> --view review` or `anonsync file evict <share> <path> --plan`.
That output should be good enough that a headless operator does not need a richer workbench merely to learn whether a placeholder-visible path is safely backed elsewhere, safely fetchable only when an offline source returns, or no longer honestly retrievable.

## Why this is worth the trouble

AnonSync only justifies its extra complexity if the safer model also becomes easier to read.
A fixed fetchability grammar is how the archive avoids rebuilding a system where placeholders, clear-synced-files actions, offline warnings, ghost-file warnings, and support guidance are individually documented, yet the full meaning of `can I still get the bytes later if I do this now?` still depends on which help article the operator happened to remember first.
""")

# Flows append
p = root / 'docs/32-interface-flows.md'
text = p.read_text()
text += """

## Flow 135 — evict a local copy only when another full-copy witness exists

Problem: a laptop in selective mode needs to free space, but one project subtree is also the only copy the operator actually trusts. The product should show whether eviction is ordinary local convenience or whether it would silently create a placeholder-only universe.

```text
$ anonsync file availability research datasets/2025/ --view review
Fetchability review: ftr_01QA...

Requested materialization intent:
  action: inspect before evict
  scope: subtree research/datasets/2025/

Visibility and local-residency reality:
  visibility: placeholder-visible mixed with 14 full local files
  local residency: current device holds full bytes for 14 files

Source backing and full-copy witnesses:
  witness summary: local-only for 11 files, remote-confirmed for 3 files
  remote witnesses online now: 1 peer for 3 files
  none-known for 11 files beyond local device

Fetchability, ghost risk, and admissible actions:
  posture: local-last-copy for 11 files
  admissible actions:
    - pin subtree
    - fetch/re-witness on another peer before evict
    - evict only the 3 remotely backed files now

Collateral effects on eviction, pinning, and serve value:
  full subtree evict would remove the last known full copy for 11 files: yes
  safe whole-subtree evict now: no

Receipt promise:
  frc_01QB... will prove local-last-copy findings and any bounded evict action chosen

$ anonsync file evict research datasets/2025/ --plan
Blocked.
Reason: 11 paths are local-last-copy and not currently remotely witnessed.
Suggested next action: pin subtree or create another full-copy witness first.
```

What this proves:

- placeholder visibility is not treated as proof that the bytes remain safely fetchable later
- the operator can distinguish ordinary eviction from `you are about to remove the last known full copy`
- CLI and richer surfaces can tell the same honest fetchability story without drift

## Flow 136 — retire a ghost announcement without pretending it is just a slow download

Problem: a peer can still see a file name in the tree, but every known source has already dematerialized or removed the bytes. The product should show that this is stale announcement residue, not an ordinary pending transfer.

```text
$ anonsync file availability media Episodes/ep042.mp3 --view review
Fetchability review: ftr_01QC...

Requested materialization intent:
  action: inspect failed fetchability
  scope: file media/Episodes/ep042.mp3

Visibility and local-residency reality:
  visibility: placeholder-visible
  local residency: no full local bytes
  announcement origin: remote tree merge 14m ago

Source backing and full-copy witnesses:
  local full copy: no
  remote confirmed witnesses: none
  last known source posture: now placeholder-only

Fetchability, ghost risk, and admissible actions:
  posture: ghost-risk
  requested fetch: cannot satisfy now
  admissible actions:
    - keep visible with guarded warning pending re-witness
    - retire stale announcement from local view with receipt
    - preserve current name-only visibility and wait for a real witness

Collateral effects on eviction, pinning, and serve value:
  local serve value: none
  destructive byte loss if retired now: none known

Receipt promise:
  frc_01QD... will prove ghost-risk posture and whether local visibility was retired or preserved

$ anonsync file resolve-ghost media Episodes/ep042.mp3 --mode retire-local-visibility --plan
Prepared.
Review says the path is announcement-visible but not honestly retrievable from any current witness.
```

What this proves:

- a ghost announcement is rendered as stale visibility truth, not a fake pending-download spinner
- the operator can choose between preserving guarded visibility and retiring it with a receipt
- placeholder-visible names and retrievable bytes stay visibly separate
"""
p.write_text(text)

print('rev0078 patch set applied')


# Note: rev0079 was produced by continuing the archive in-place and adding concrete file-availability interface work.
