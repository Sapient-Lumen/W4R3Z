from pathlib import Path
import re

root = Path(__file__).resolve().parent

REV = 'rev0080'
TIMESTAMP = '2026.03.18.01.20'
CODENAME = 'actionmatrixtruthharbor'


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise SystemExit(f'missing pattern: {old[:120]!r}')
    return text.replace(old, new, 1)


def insert_after(text: str, needle: str, insert: str) -> str:
    if needle not in text:
        raise SystemExit(f'missing insert anchor: {needle[:120]!r}')
    return text.replace(needle, needle + insert, 1)


# README
p = root / 'README.md'
text = p.read_text()
text = replace_once(text, '- Revision: `rev0079`', f'- Revision: `{REV}`')
text = replace_once(text, '- Timestamp: `2026.03.18.01.04` (America/New_York)', f'- Timestamp: `{TIMESTAMP}` (America/New_York)')
text = replace_once(text, '- Codename: `witnessinterfaceclarityharbor`', f'- Codename: `{CODENAME}`')
old_block = """This revision continues directly from `rev0078` and does six things:

1. Re-checks **Resilio Sync** one more time from the interface angle: current official docs still show a maintained v3 line and still document selective-sync placeholders, mobile `Clear synced files`, and ghost-file warnings, so the non-clone case has to be about truth and operator control rather than pretending the product is dead or feature-poor.
2. Adds a dedicated **file-availability and materialization interface spec** so the archive stops speaking only in abstract fetchability grammar and starts defining the actual answer strip, chips, tables, verbs, and receipts a real surface should render.
3. Tightens the **workbench and pattern language** so file/subtree availability reads as one sentence-shaped answer across GUI and CLI, and mixed-risk batch actions split by witness risk instead of flattening everything into one `remove from device` story.
4. Extends the **object model and daemon/API contract** with explicit full-copy witness records, fetchability reports, and fetchability receipts instead of leaving clients to reconstruct retrievability from placeholder state alone.
5. Adds additional **canonical interface flows** for mixed-risk subtree eviction and parity between the workbench availability drawer and the CLI review projection.
6. Refreshes the **evaluation**, **ADR numbering/decisions**, **roadmap**, **open questions**, **status**, **sources**, and **reading order** so future revisions keep concrete interface truth central whenever selective materialization appears.
"""
new_block = """This revision continues directly from `rev0079` and does six things:

1. Re-checks **Resilio Sync** again with a fairer clone/no-clone lens: current docs still show a maintained v3 line and full non-commercial functionality, but they also still tie linked-device convenience to broad visibility/approval, route custom-location and read-only outcomes through `Disconnected` or manual-key workarounds, and leave placeholder truth scattered across `.rsls`, `Clear`, and ghost-file warnings.
2. Adds a dedicated **file-availability action-matrix and surface-contract spec** so the archive stops at neither abstract fetchability grammar nor generic answer strips and instead defines the exact per-row states, primary verbs, batch bars, restore-vs-fetch distinctions, and dense/mobile compression rules a real surface should honor.
3. Tightens the **workbench and pattern language** so mixed selections never get one misleading destructive button, stale visibility uses retirement language rather than progress language, and history-backed-only cases surface `Restore` instead of pretending ordinary `Fetch` is still honest.
4. Extends the **object model and daemon/API contract** with availability row/action contracts, selection summaries, and explicit action-offer fields so GUI, CLI, and automation can all render the same next-safe-action answer.
5. Adds an additional **canonical interface flow** for the sharpest remaining edge case: a path that is still history-backed but no longer swarm-fetchable, where the product must offer restore semantics rather than vague on-demand language.
6. Refreshes the **evaluation**, **ADRs**, **roadmap**, **open questions**, **status**, **sources**, and **reading order** so future revisions keep action truth — not just state truth — central whenever selective materialization appears.
"""
text = replace_once(text, old_block, new_block)
needle = '- a first-class file-availability answer strip and reviewed subtree table so every surface can answer visibility, local bytes, witness posture, fetchability, and safest next step in one place\n'
insert = needle + '- a first-class file-availability action matrix so every row and every batch bar can say exactly which action is safe, which action is blocked, and when `restore` is the honest next verb instead of `fetch`\n'
text = replace_once(text, needle, insert)
needle = '- `docs/92-file-availability-and-materialization-interface-spec.md` — concrete interface contract for answer strips, witness/fetchability chips, subtree tables, batch splitting, and receipt-backed materialization actions\n'
insert = needle + '- `docs/93-file-availability-action-matrix-and-surface-contract-spec.md` — per-row availability state tuple, action admissibility matrix, selection-bar rules, dense/mobile compression rules, and CLI parity for next-safe-action rendering\n'
text = replace_once(text, needle, insert)
needle = 'then `89-observer-readonly-local-write-and-serve-rights-spec.md`, then `91-fetchability-and-full-copy-witness-spec.md`, then `92-file-availability-and-materialization-interface-spec.md`, then `41-report-and-intervention-language.md`'
insert = 'then `89-observer-readonly-local-write-and-serve-rights-spec.md`, then `91-fetchability-and-full-copy-witness-spec.md`, then `92-file-availability-and-materialization-interface-spec.md`, then `93-file-availability-action-matrix-and-surface-contract-spec.md`, then `41-report-and-intervention-language.md`'
text = replace_once(text, needle, insert)
p.write_text(text)

# Status rewrite
(root / 'docs/00-status.md').write_text(f"""# Status

## Scope of this revision

This revision is an in-place continuation of `rev0079`, driven by the current request:

- continue researching and tightening the archive without letting it sprawl
- evaluate Resilio Sync further so the non-clone case stays evidence-based rather than rhetorical
- spend more time on interface specs, especially the actual per-row and per-batch action contract for file availability
- keep Linux-first, overlay-first, and least-privilege assumptions intact unless the evidence actually breaks them
- preserve the useful parts of Resilio's convenience model without inheriting the ambient trust, workaround-heavy path selection, or scattered placeholder truth
- make sure the archive can answer not only `what is true about this path now?` but also `what exact verb is honest now, and why?`

## Honesty note

This package **does** build directly on the immediately previous revision mounted in the working filesystem for this run.
The work therefore reflects a real continuation pass.

## Immediate output of this pass

The archive now contains:

- a fairer Resilio comparison that explicitly grants current strengths — maintained Sync v3, full non-commercial feature availability, strong selective materialization, and encrypted replicas — while also naming the sharper reasons not to clone its convenience model wholesale
- a dedicated **file-availability action-matrix and surface-contract spec** that defines exact row states, primary verbs, batch labels, restore-vs-fetch distinctions, and dense/mobile compression rules
- stronger interface and daemon/API requirements so availability rows, selection summaries, and action offers become explicit public objects rather than client-side guesswork
- stronger workbench and pattern-language rules so destructive batch bars only speak for the rows they can honestly mutate, stale visibility uses retirement language, and history-backed-only cases surface `Restore` rather than vague `Fetch` language
- an additional canonical flow for the sharp edge case where bytes are no longer swarm-fetchable but still restorable from history, so the product does not lie by offering ordinary on-demand retrieval
- README, roadmap, ADR, open-question, source, and status updates so future revisions keep **action truth** central wherever selective materialization appears

## The main shift

`rev0079` proved that file availability needed a concrete answer strip, risk buckets, and subtree review grammar.

`rev0080` pushes that one level deeper:

> it is not enough for the archive to say which state a file is in. A serious operator product must also specify which verb is honest in that state, how mixed selections label only the safe subset they can affect, and when a supposedly on-demand path has crossed the line from `fetch` territory into `restore`, `re-witness`, or `retire stale visibility` territory.

That changes the archive in five specific ways:

- file availability is no longer just a state-reporting contract; it is also an action-offer contract
- a path that is history-backed but not swarm-backed no longer pretends to support ordinary `fetch`
- mixed selections no longer get one bulk action whose label quietly overclaims scope
- dense and mobile surfaces now have stricter rules about what can compress and what must stay explicit
- the non-clone case against Resilio gets tighter: the missing piece is not Selective Sync itself, but the absence of one explicit per-row/per-batch action contract that always tells the operator which next step is honest

## What still remains unresolved

This revision intentionally still leaves important questions open, including:

- how much low-risk availability review can stay inline before the product starts hiding real action differences again
- how aggressive dense/mobile compression may become before it recreates `available on demand` folklore
- when a history-backed-only path may offer one-step restore versus always forcing a fuller timeline review
- how broad one reviewed mutation grant may be in v1 before explicit authority becomes either too reusable or too noisy
- when long-offline or clock-uncertain peers should be allowed to resume writable participation without first-class re-entry review
- when remote delete or overwrite waves should always force destructive-replay review instead of ordinary sync progress
- how aggressive default compromise freezes should be before the product starts turning suspicion into disruptive magic
- how aggressive the default review queue should be before it becomes noisy

## Files added in this revision

- `docs/93-file-availability-action-matrix-and-surface-contract-spec.md`
- `update_rev0080.py`

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
- `docs/92-file-availability-and-materialization-interface-spec.md`
- `docs/93-file-availability-action-matrix-and-surface-contract-spec.md`
- `docs/sources.md`
""")

# Resilio evaluation
p = root / 'docs/10-resilio-sync-evaluation.md'
text = p.read_text()
insert_after_anchor = "## Bottom line\n\nResilio Sync is still a serious reference point.\nIts official help center shows Sync v3 releases through `3.1.2.1076` on `31/Oct/2025`, and Resilio's v3 rollout documents also say that Sync v3 functionality is fully available for non-commercial use behind v3 licensing/activation.\nSo any AnonSync case that depends on “Resilio is abandoned”, “its good features are still gated away from most users”, or “it has no control surface” is weak.\n\nThe better question is this:\n\n> Which Resilio ideas are strong enough to preserve, and which exact semantics are the strongest reasons not to clone it?\n\nThis revision answers that more operationally.\n"
insert = """

## Fair preserve / adapt / reject matrix

### Preserve almost as-is

- selective materialization as a first-class product idea
- encrypted-untrusted replicas as an important topology, not a niche afterthought
- device identity and fingerprint legibility
- the basic idea that a personal-device mesh can be made very convenient

### Adapt heavily

- linking, because Resilio's own docs still say linked devices automatically make all folders visible everywhere and allow broader future approval reach than AnonSync should want
- default location and path adoption, because current custom-location flows still require `Disconnected` workarounds on linked devices
- per-device read-only behavior, because linked-device convenience still pushes operators toward manual key/disconnect rituals when they want narrower rights
- file availability, because placeholders, `Clear`, and ghost-file warnings still tell the truth in pieces instead of through one action contract

### Reject outright

- identity takeover semantics when linking already-initialized devices
- ambient share visibility as the default blast radius of personal convenience
- any UI contract that lets `visible here` masquerade as `durably fetchable later`
- any action surface that preserves the same `Fetch` or `Remove from device` verb across unlike risk classes
"""
text = replace_once(text, insert_after_anchor, insert_after_anchor + insert)
needle = "### Requirement 71 — file availability must be a concrete interface contract, not just a conceptual model\n\nIt is not enough for AnonSync to say, in the abstract, that namespace visibility, local residency, full-copy witnesses, and fetchability are different truths.\nThe operator surface should also define exactly how that answer is rendered.\n\nAt minimum every serious file/subtree availability surface should provide:\n\n- one compact answer strip that always states visibility, local residency, witness posture, fetchability posture, and safest next step in the same order\n- one review drawer/page that expands into requested action, current truth, witness evidence, admissible actions, and receipt promise\n- one subtree table that preserves per-row risk classes instead of flattening a mixed subtree into one bulk label\n- one batch rule that splits `safe to evict`, `re-witness first`, and `ghost/stale` classes before apply\n- one receipt model proving later which witness/fetchability truth was reviewed when a fetch, evict, pin, or stale-announcement action was taken\n\nIf the operator still has to infer from a placeholder icon, a grayed-out row, a mobile `Clear synced files` command, and a later warning whether the bytes are safely retrievable, the interface is not explicit enough.\n"
insert = """

### Requirement 71a — the primary verb must change when the availability risk class changes

A truthful availability surface does not stop at reporting state.
It must also change its offered action when the meaning changes.

At minimum that means:

- `fetchable-now` may offer `Fetch now` or `Evict safe rows`
- `local-last-copy` should change the primary verb to `Pin locally` or `Create another witness`
- `ghost-risk` should change the primary verb to `Retire stale announcement` or `Keep visible with warning`
- `history-backed-only` should surface `Restore from history` rather than pretending ordinary swarm `Fetch` is still honest
- mixed selections should label only the safe subset they can mutate, for example `Evict 24 safe rows`, instead of overclaiming with one cheerful `Apply to all`

If the operator still sees the same optimistic action label after the product has already discovered that the path is guarded, last-copy, ghosted, or history-only, the interface is not explicit enough.
"""
text = replace_once(text, needle, needle + insert)
p.write_text(text)

# Interface spec object model additions
p = root / 'docs/30-interface-spec.md'
text = p.read_text()
needle = "- `recommended_next_step`\n- `generated_at`\n- `decision_trace_ref` nullable\n"
insert = "- `selection_summary` nullable (`uniform`, `safe-subset-only`, `mixed-risk`, `stale-only`)\n- `primary_action_offer` nullable (`fetch-now`, `evict-safe-rows`, `pin-locally`, `create-witness`, `restore-from-history`, `retire-stale-announcement`, `keep-visible-with-warning`)\n- `secondary_action_offers[]`\n"
text = replace_once(text, needle, "- `recommended_next_step`\n" + insert + "- `generated_at`\n- `decision_trace_ref` nullable\n")
anchor = "### Fetchability receipt\n\nA durable record proving which fetchability/witness truth was reviewed when a file or subtree action completed, was blocked, or was retired as stale.\n"
insert = """

### Availability action contract

A compact row-level contract describing which next action is honest for one visible file/subtree row.
This exists so clients do not improvise primary verbs from raw posture fields.

Fields:

- `availability_action_contract_id`
- `report_ref`
- `path`
- `selection_class` (`safe-now`, `re-witness-first`, `history-restore`, `stale-visibility`, `blocked`)
- `danger_class` (`none`, `guarded`, `high`, `stale`)
- `primary_action_offer` (`fetch-now`, `evict-safe-rows`, `pin-locally`, `create-witness`, `restore-from-history`, `retire-stale-announcement`, `keep-visible-with-warning`, `none`)
- `secondary_action_offers[]`
- `review_required`
- `receipt_kind` (`fetchability-receipt`, `file-intent-receipt`, `rollback-receipt`, `none`)
- `generated_at`
"""
text = replace_once(text, anchor, insert + anchor)
anchor = "- `reviewed_fetchability_posture`\n- `requested_action`\n- `chosen_action`\n- `outcome` (`applied`, `blocked`, `cancelled`, `retired-stale`, `deferred`)\n"
insert = "- `reviewed_selection_summary` nullable\n- `offered_primary_action` nullable\n"
text = replace_once(text, anchor, "- `reviewed_fetchability_posture`\n" + insert + "- `requested_action`\n- `chosen_action`\n- `outcome` (`applied`, `blocked`, `cancelled`, `retired-stale`, `deferred`)\n")
# CLI examples
needle = "- `file availability` should render namespace visibility, local materialization, full-copy witness summary, fetchability posture, ghost/stale-announcement risk, and eviction safety for the selected path or subtree\n- every serious availability view should be able to render one compact answer strip in this order: visibility, local residency, witness summary, fetchability, safest next step\n- subtree availability should preserve mixed-risk rows instead of collapsing the whole selection into one optimistic bulk state\n- `evict` should normally require `--plan` when the target may be the last known full-copy witness or when fetchability is only guarded\n- `fetch --require fetchable-now` should fail closed when the path is only announcement-visible, ghost-risk, or backed only by offline/uncertain witnesses\n"
insert = "- history-backed-only cases should surface `restore` as a distinct next step instead of pretending ordinary swarm `fetch` is still honest\n- mixed selections should label only the safe subset they can mutate, for example `evict 24 safe rows`, rather than overclaiming with `apply to all`\n"
text = replace_once(text, needle, needle + insert)
p.write_text(text)

# API spec additions
p = root / 'docs/31-daemon-api-spec.md'
text = p.read_text()
needle = "Responses should include witness records or witness summaries that say whether backing is local-current, remote-confirmed, remote-last-known, history-backed, or none-known.\n`GET /v1/fetchability-receipts` and `GET /v1/fetchability-receipts/{fetchability_receipt_id}` should preserve later proof of the witness posture, risk class, and action taken after review.\n"
insert = "Responses should also be able to emit row-level action contracts and a selection summary so clients can render exact labels such as `Evict 24 safe rows`, `Create witnesses for 3 guarded rows`, or `Restore 2 history-backed rows` without inventing those verbs locally.\nHistory-backed-only cases should surface `restore-from-history` rather than `fetch-now`.\nDense clients may choose a smaller presentation, but the wire contract should still keep action offer, danger class, and receipt kind explicit.\n"
text = replace_once(text, needle, needle.replace('`GET /v1/fetchability-receipts` and `GET /v1/fetchability-receipts/{fetchability_receipt_id}` should preserve later proof of the witness posture, risk class, and action taken after review.\n', '') + insert + '`GET /v1/fetchability-receipts` and `GET /v1/fetchability-receipts/{fetchability_receipt_id}` should preserve later proof of the witness posture, risk class, action offer, and action taken after review.\n')
p.write_text(text)

# Add flow 139
p = root / 'docs/32-interface-flows.md'
text = p.read_text()
flow = """

## Flow 139 — offer restore instead of fetch when history still exists but the swarm no longer does

Problem: a file name is still visible and a local history entry still exists, but no current peer now witnesses durable full bytes. The product must not keep offering ordinary on-demand fetch just because the path once belonged to a selectively materialized share.

Workbench sketch:

```text
File availability — media/Episodes/ep177.mp3

Placeholder visible · No local bytes · History backed · Not fetchable · Restore from history

Requested action
  Inspect / recover this file

Current truth
  Visible in namespace: yes (placeholder projection)
  Local bytes: none
  Current swarm witnesses: none confirmed
  History entries: 2 local restore candidates

Admissible actions
  Primary: Restore from history
  Secondary: Keep visible with warning
  Blocked: Fetch now

Receipt promise
  frc_01QH... will prove history-backed-only posture and that restore, not swarm fetch, was the honest next verb
```

CLI sketch:

```text
$ anonsync file availability media Episodes/ep177.mp3 --view review

Placeholder visible · No local bytes · History backed · Not fetchable · Restore from history

Blocked actions:
  fetch-now  (no current full-copy witness)

Allowed actions:
  restore-from-history
  keep-visible-with-warning
```

Rules proven by this flow:

- history-backed-only is not equivalent to fetchable-now
- the presence of a placeholder or old namespace visibility does not keep `Fetch` honest after witnesses disappear
- the primary verb must switch from transfer language to restore language when the recovery path moved from swarm state to timeline state
- later receipts must prove that the product knew this distinction at decision time
"""
if '## Flow 139 — offer restore instead of fetch when history still exists but the swarm no longer does' not in text:
    text = text.rstrip() + flow + '\n'
p.write_text(text)

# Workbench spec additions
p = root / 'docs/38-operator-workbench-interface-spec.md'
text = p.read_text()
needle = "### Batch-action rule\n\nBulk actions from this surface should inherit the most conservative meaning that still stays honest.\nThat means:\n\n- `Evict safe rows now` may be primary for a mixed subtree\n- `Create witnesses for guarded rows` should be a separate companion action\n- `Retire stale announcements` should never be silently bundled into ordinary evict\n\nThe workbench should prefer three explicit groups over one big cheerful `Apply to all` button.\n"
insert = """

### Selection bar

Whenever the operator multi-selects rows from this surface, the selection bar should summarize risk classes before it offers any mutation.
At minimum it should show:

- selected row count
- safe-now row count
- guarded / re-witness row count
- history-restore row count
- stale-visibility row count

Primary destructive labels should name only the rows they can honestly affect, for example:

- `Evict 24 safe rows`
- `Review 3 guarded rows`
- `Restore 2 history-backed rows`
- `Retire 1 stale row`

The bar should not collapse those into one misleading `Apply to 30 rows` affordance.

### Dense-view rule

A dense list row may compress counts and provenance, but it must still keep three truths separate:

- whether bytes are local
- whether another current witness exists
- what the safest next action is

A small client may shorten `3 remote-confirmed witnesses` to `remote-confirmed`, but it may not collapse `history-backed-only` into `fetchable later`.
"""
text = replace_once(text, needle, needle + insert)
p.write_text(text)

# Pattern language additions
p = root / 'docs/39-interface-pattern-language.md'
text = p.read_text()
append = """

## Pattern 22u — a batch bar may only speak for the safe subset it can actually mutate

When a mixed selection contains safe rows, guarded rows, and stale rows, the primary batch label should only name the subset it can truthfully change right now.
A label such as `Evict 24 safe rows` is acceptable.
A label such as `Evict 30 selected rows` is not, if 6 rows still require re-witness, restore, or stale-retirement review.

This matters because overclaiming scope in the action bar is just a more polished form of the same ambiguity that old `remove from device` language created.

## Pattern 22v — history-backed-only must switch the verb from transfer to restore

When no current peer now witnesses the bytes, but local or reviewed history still can restore them, the primary verb should become `Restore from history`.
The product should not keep using `Fetch` merely because the path is still visible in a selectively materialized tree.

This matters because `fetch` implies live source backing, while `restore` implies timeline-backed recovery.
Those are different promises and should not share one optimistic label.

## Pattern 22w — dense and mobile surfaces may compress counts, not risk classes

A dense list row or mobile card may shorten wording and move details behind expansion, but it must still preserve separate cues for:

1. local bytes
2. witness posture or its absence
3. safest next action

If compression merges witness posture and fetchability posture into one vague adjective such as `available`, the surface has crossed from dense into misleading.
"""
if '## Pattern 22u — a batch bar may only speak for the safe subset it can actually mutate' not in text:
    text = text.rstrip() + append + '\n'
p.write_text(text)

# ADR addition
p = root / 'docs/40-architecture-decisions.md'
text = p.read_text()
append = """

## ADR-093 — Availability surfaces need an explicit action matrix, not just state chips

**Decision:** Availability reports must carry explicit per-row and per-selection action offers so the primary verb changes with the risk class instead of being invented independently by each client.

**Why:** `rev0079` made file availability a concrete interface contract, but an honest answer strip still leaves one dangerous gap if clients can keep rendering the same optimistic `Fetch` or `Evict` button after the posture has already changed to local-last-copy, history-backed-only, or stale visibility. The product needs an explicit action contract, not just posture chips.

**Consequences:**

- clients receive row-level action offers such as `fetch-now`, `pin-locally`, `restore-from-history`, or `retire-stale-announcement`
- mixed-selection bars may only label the safe subset they can mutate honestly
- history-backed-only rows no longer masquerade as ordinary on-demand fetch cases
"""
if '## ADR-093 — Availability surfaces need an explicit action matrix, not just state chips' not in text:
    text = text.rstrip() + append + '\n'
p.write_text(text)

# Roadmap additions
p = root / 'docs/50-roadmap.md'
text = p.read_text()
text = replace_once(text, '- concrete file-availability answer strips, subtree tables, and mixed-risk batch splitting rules\n', '- concrete file-availability answer strips, subtree tables, and mixed-risk batch splitting rules\n- explicit availability row/action contracts so clients can render exact next-safe-action labels without inventing them locally\n')
text = replace_once(text, '- operators can read the same five-part availability answer in workbench and CLI without semantic drift or optimistic bulk flattening\n', '- operators can read the same five-part availability answer in workbench and CLI without semantic drift or optimistic bulk flattening\n- operators can tell when a path moved from swarm fetch into history restore, and the product changes its verb accordingly\n')
p.write_text(text)

# Open questions additions
p = root / 'docs/64-critical-open-questions.md'
text = p.read_text()
append = """

## 60) When may the product offer one-step restore from history instead of a fuller timeline review?

This revision makes history-backed-only availability more explicit, but one policy seam remains open:

- when a local history candidate is strong enough that `Restore from history` may stay inline
- when provenance gaps or stale retention evidence should force a fuller rollback/timeline sheet first
- whether restoring from history into a still-visible placeholder path should automatically require settlement or collision checks
- how much restore convenience is safe before the product starts hiding that the swarm no longer backs the bytes

This matters because weak defaults recreate optimistic on-demand folklore, while overly strict defaults could make obviously safe local recovery feel ceremonial instead of trustworthy.
"""
if '## 60) When may the product offer one-step restore from history instead of a fuller timeline review?' not in text:
    text = text.rstrip() + append + '\n'
p.write_text(text)

# File availability interface spec additions
p = root / 'docs/92-file-availability-and-materialization-interface-spec.md'
text = p.read_text()
insert = """

## Additional action-contract rule

The surface should not stop at chips and posture summaries.
It should also determine which verb is honest for the current row or selection.
For the stricter per-row and per-batch matrix, see `93-file-availability-action-matrix-and-surface-contract-spec.md`.

Two concrete consequences follow immediately:

- a history-backed-only row should surface `Restore from history`, not ordinary `Fetch`
- a mixed selection should label only the safe subset it can mutate, not the whole selection by convenience
"""
text = insert_after(text, 'The order should not.\n', insert)
insert2 = """

## Dense-view and small-client rule

Dense or mobile surfaces may compress counts, hide some provenance behind expansion, or stack the answer strip across two lines.
They may not merge witness posture and fetchability posture into one vague adjective such as `available` or `offline`.
At minimum a compressed surface must still keep visible:

- whether local bytes exist
- whether another current witness exists
- what the safest next step is
"""
text = insert_after(text, 'The bad example is too optimistic because it erases witness and fetchability truth.\n', insert2)
p.write_text(text)

# New doc 93
(root / 'docs/93-file-availability-action-matrix-and-surface-contract-spec.md').write_text("""# File-availability action matrix and surface contract spec

## Purpose

`92-file-availability-and-materialization-interface-spec.md` defined the shared reading order, chips, tables, and review grammar for file availability.
What it still left slightly too loose was the actual action contract:

> once the product knows the current availability posture, which verb is honest now, and how should that verb appear for one row versus a mixed selection?

This document fixes that gap.
It defines the per-row state tuple, action admissibility matrix, selection-bar rules, and dense/mobile compression rules that every serious availability surface should inherit.

## Core decision

Availability is not only a reporting surface.
It is also an action-offer surface.

That means every row should carry one explicit answer to all three of these questions:

1. what is true here now
2. what action is honest now
3. what receipt will later prove why that action was offered

## Canonical row contract

Every rendered row or single-path review should be derivable from one canonical tuple:

- `path`
- `visibility_posture`
- `local_residency_posture`
- `witness_summary`
- `fetchability_posture`
- `selection_class`
- `danger_class`
- `primary_action_offer`
- `secondary_action_offers[]`
- `receipt_kind`

### Selection class vocabulary

Allowed values:

- `safe-now`
- `re-witness-first`
- `history-restore`
- `stale-visibility`
- `blocked`

### Danger class vocabulary

Allowed values:

- `none`
- `guarded`
- `high`
- `stale`

The selection class is what the batch layer groups by.
The danger class is what default sort and emphasis should group by.

## Single-row action matrix

### Case A — remotely backed and not currently local

Example posture:

- `placeholder-visible`
- `none-local`
- `remote-confirmed`
- `fetchable-now`

Primary action:

- `Fetch now`

Secondary actions may include:

- `Keep placeholder`
- `Pin after fetch`

This is the cleanest on-demand case.
The product may stay inline here.

### Case B — local bytes exist and another witness exists

Example posture:

- `full-visible` or `placeholder-visible`
- `full-local`
- `remote-confirmed` or `multi-source-confirmed`
- `fetchable-now`

Primary action depends on intent:

- `Evict safe rows` for reclaim intent
- `Pin locally` for preservation intent

An ordinary local-evict action is honest here because another durable witness exists.

### Case C — no local bytes, witness only last-seen or offline

Example posture:

- `placeholder-visible`
- `none-local`
- `offline-only`
- `guarded-fetch`

Primary action:

- `Wait for witness` or `Create another witness first`

Secondary actions may include:

- `Keep visible with warning`

Ordinary `Fetch now` should not remain the primary verb.
It overclaims current source availability.

### Case D — local bytes are the only confirmed full copy

Example posture:

- `full-local` or `partial-local`
- `local-only`
- `local-last-copy`

Primary action:

- `Pin locally`
- `Create another witness`

Blocked action:

- ordinary `Evict` unless the operator goes through a stronger review path

The important rule is that the product must change the verb when it discovers last-copy risk.

### Case E — no live witness, but restorable history exists

Example posture:

- `placeholder-visible` or `announcement-only`
- `none-local`
- `history-backed-only`
- `not-fetchable`

Primary action:

- `Restore from history`

Secondary actions may include:

- `Keep visible with warning`

Blocked action:

- `Fetch now`

This is one of the most important distinctions in the archive.
A history-backed recovery path is not the same promise as a current swarm-backed fetch path.

### Case F — stale or ghost visibility

Example posture:

- `announcement-only` or `placeholder-visible`
- `none-local`
- `none-known`
- `ghost-risk` or `not-fetchable`

Primary action:

- `Retire stale announcement`

Secondary actions may include:

- `Keep visible with warning`

Blocked action:

- `Fetch now`

The product should use retirement language here, not progress language.

## Requested-action matrix

### Requested action: `fetch`

Allowed as the primary action only when posture is `fetchable-now`.
When posture is `guarded-fetch`, the product may offer a wait/re-witness path instead.
When posture is `history-backed-only` or `ghost-risk`, `fetch` should be blocked and replaced with `restore` or `retire stale announcement`.

### Requested action: `evict`

Allowed inline only when another durable full-copy witness exists.
When the local device is the only confirmed witness, the product should pivot to `Pin locally` / `Create another witness` and require a stronger review path for any destructive exception.

### Requested action: `pin`

Allowed whenever local bytes exist.
It should become the primary action automatically for `local-last-copy` posture.

### Requested action: `retire stale announcement`

Allowed when the path is `ghost-risk` or `not-fetchable` and visibility no longer matches byte reality.
It should not silently piggyback on `evict`.

### Requested action: `restore`

Allowed when history or rollback posture can actually recreate bytes.
It should not masquerade as `fetch` merely because the path still belongs to a selectively materialized tree.

## Selection-bar contract

When multiple rows are selected, the batch bar should compute counts by selection class before it renders any mutation.
At minimum it should show:

- total selected
- `safe-now`
- `re-witness-first`
- `history-restore`
- `stale-visibility`
- `blocked`

### Good labels

- `Evict 24 safe rows`
- `Review 3 guarded rows`
- `Restore 2 history-backed rows`
- `Retire 1 stale row`

### Bad labels

- `Apply to 30 rows`
- `Evict selected`
- `Fetch available files`

The bad labels overclaim scope or quietly merge unlike recovery paths.

## Default sort and grouping

For safety-sensitive views, default order should be:

1. `high` danger
2. `stale`
3. `guarded`
4. `none`
5. path name within class

A purely alphabetical default is allowed only for non-danger-sensitive browse views.

## Dense and mobile rules

Small clients may compress wording, but the following must stay explicit on the collapsed row or immediately adjacent expansion trigger:

- whether local bytes exist
- whether another current witness exists
- what the safest next action is

### Allowed compression

- shorten `3 remote-confirmed witnesses` to `remote-confirmed`
- collapse visibility plus local bytes into one explicit phrase such as `Placeholder visible, no local bytes`
- move provenance time or witness list behind expansion

### Disallowed compression

- replacing `history-backed-only` with `available later`
- replacing `ghost-risk` with `offline`
- hiding the next-safe-action slot entirely
- keeping the same destructive icon or CTA after the risk class changed

## CLI contract

A CLI should be able to render the same row tuple and batch semantics directly.
For example:

```text
$ anonsync file availability media Episodes/ --view rows

PATH                  VISIBILITY     LOCAL       WITNESS           FETCHABILITY      NEXT
Episodes/ep001.mp3    Placeholder    none        remote-confirmed  fetchable-now     Fetch now
Episodes/ep099.mp3    Placeholder    full        local-only        local-last-copy   Pin locally
Episodes/ep177.mp3    Placeholder    none        history-backed    not-fetchable     Restore from history
Episodes/ep201.mp3    Announcement   none        none-known        ghost-risk        Retire stale announcement

Selection summary:
  4 selected · 1 safe-now · 1 re-witness-first · 1 history-restore · 1 stale-visibility

Primary batch actions:
  Evict 1 safe row
  Review 1 guarded row
  Restore 1 history-backed row
  Retire 1 stale row
```

## Receipt contract

Whenever a non-trivial action is taken from an availability surface, the later receipt should be able to prove:

- which posture was reviewed
- which primary action was offered
- whether the selection was split
- which subset, if any, was actually mutated
- why another subset was deferred, blocked, or redirected into restore/re-witness/stale-retire work

## Why this matters

A lot of sync products already have the raw features needed to tell the truth.
The failure mode is usually that state is one place and action is another.
This document exists so AnonSync does not rebuild that failure mode in a more polished shell.
Once the system knows the row is `local-last-copy`, `history-backed-only`, or `ghost-risk`, the interface should not keep acting as though it were still just another cheerful on-demand file.
""")

# Sources update
p = root / 'docs/sources.md'
text = p.read_text()
if 'Sharing files with mobile devices\n  https://www.resilio.com/documentation/content/advanced-configuration/resilio-on-mobile-devices/sharing_files_with_mobile_devices_/' not in text:
    text = insert_after(text, '- Selective Sync (Mobile)\n  https://help.resilio.com/hc/en-us/articles/206217315-Selective-Sync-Mobile\n', '\n- Sharing files with mobile devices\n  https://www.resilio.com/documentation/content/advanced-configuration/resilio-on-mobile-devices/sharing_files_with_mobile_devices_/\n')
p.write_text(text)

print('updated rev0080')
