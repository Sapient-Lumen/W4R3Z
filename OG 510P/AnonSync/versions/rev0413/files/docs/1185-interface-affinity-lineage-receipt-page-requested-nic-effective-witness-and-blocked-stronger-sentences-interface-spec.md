# Interface-affinity lineage receipt page — requested NIC, effective witness, and blocked stronger sentences interface spec

## Purpose

This receipt preserves what was requested, what was observed, and what the product refused to overclaim.

## Receipt fields

### `interface_affinity_receipt`

- `interface_affinity_receipt_id`
- `scope_ref`
- `created_at`
- `runtime_class`
- `requested_interface_handle`
- `requested_interface_presence`
- `effective_interface_handle` nullable
- `fallback_policy`
- `listener_audience_class`
- `proof_rung` (`preference`, `current-witness`, `cutoff-witness`, `continuity-window`)
- `startup_boundary_notes[]`
- `strongest_safe_sentence`
- `blocked_stronger_sentences[]`
- `related_review_refs[]`

## Required sections

1. **Requested interface**
2. **Effective interface witness**
3. **Fallback policy**
4. **Listener audience**
5. **Proof rung**
6. **Blocked stronger sentences**
7. **Reopen conditions**

## Reopen conditions

The receipt must name what would invalidate or weaken it, such as:

- requested interface disappears
- runtime class changes
- host starts with different active-interface set
- new bridge/VPN/virtual adapter appears
- current-only witness ages out

## Example safe sentences

- `eth0 was requested; wlan0 was observed effective; fallback remained allowed.`
- `eth0 was requested and remained effective through the reviewed window, with hard cutoff in force.`
- `service runtime may widen audience across active interfaces; current witness is insufficient for a narrower sentence.`

## Acceptance bar

The receipt is good enough when a later operator can answer, without log archaeology:

- what NIC was requested
- what NIC was actually observed
- how strong the proof was
- which stronger claim was intentionally blocked
