# ADR 0295: Add tree-v2 sparse content custody

- Status: accepted and implemented first vertical slice
- Date: 2026-09-02

## Context

ADR 0278 made tree-v2 projection selective, but a subscriber still fetched every file object in the
authenticated branch graph. A node showing only one subtree therefore consumed complete-replica
storage and bandwidth while status, repair, and GC had no vocabulary for partial custody. Simply
skipping objects was unsafe: widening a selection could reinterpret a formerly unprojected missing
path as a local deletion, and a partial node could be mislabeled as converged or a backup.

## Decision

Use the existing recipient-local canonical include/exclude prefixes as the first custody-interest
contract. Add `sync-interest NAMESPACE [include=PATH|exclude=PATH...]` and
`sync-interest-clear NAMESPACE`; advance owner-local control to v1.53 operations 120--121. No peer
frame, feature bit, Ratox frame, authority capability, or destination-path authority changes.

`sync-interest` without rules inspects the current policy. With rules it atomically replaces both
rule sets after canonical validation; `sync-interest-clear` restores empty rules, meaning complete
projection and custody intent. The peer never supplies a path. A policy update waits for an active
tree pull and publisher replay state to drain and refuses an interrupted worktree exchange. It may
remain enabled under ordinary writable/bidirectional automation.

The subscriber always retrieves and verifies the complete signed branch-record and manifest
closure. It validates every file digest/size declaration, but schedules file objects only when at
least one selected path needs that digest. Completion now reports complete or partial custody plus
exact declared, selected, skipped, requested, committed, reused, byte, path, branch, and conflict
facts. A sparse node can therefore understand every candidate and conflict while not possessing
every candidate's bytes.

Bind the private worktree projection marker to both the merged manifest and the exact local metadata
mode/include/exclude policy. If the policy changed, the first scan preserves absent baseline paths
instead of manufacturing tombstones. Present newly selected local files remain ordinary local
events. After selected remote objects arrive, the existing journaled directory exchange writes the
new policy-bound marker; subsequent absence again has ordinary deletion meaning. Pull no longer
performs a redundant pre-inventory reconcile; the mandatory post-transfer reconcile publishes local
changes and projects the accepted frontier in one transaction.

Repair verifies the current signed metadata frontier and only its selected unique file-object
closure. Tree-v2 GC roots every reachable record/manifest plus selected unique file objects; an
unselected locally present file object becomes a recoverable quarantine candidate. Pins retain full
signed metadata and the locally selected content closure, not an independent complete backup.

## Consequences

Narrow nodes save transfer and live-CAS capacity without losing causal provenance. Widening interest
is an on-demand fetch: update interest, then explicitly pull from an authorized peer or let
bidirectional automation do so. If no selected source holds the bytes, projection/repair fails
closed; it never invents content or silently turns absence into deletion.

The current tree-v2 wire has no availability bitmap or multi-source object scheduler. A sparse source
truthfully returns an absent/unavailable object result, so choosing and combining complementary
tree-v2 sources remains the next part of workstream 7. Namespace health must also aggregate partial
custody over time. Until then, a successful sparse pull proves the selected closure from that source,
not that every authorized source or every desired future prefix is recoverable.

Owned tests cover selective transfer, skipped-CAS absence, policy-marker transition, on-demand
widening, preservation of excluded local files, partial GC/quarantine/restore, live Agent policy
inspection/clear/restore, malformed CLI input, and frozen local-control values. These are
deterministic same-host construction proofs, not a long-running or independent backup qualification.
