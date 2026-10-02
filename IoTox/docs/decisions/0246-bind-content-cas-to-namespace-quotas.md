# ADR 0246: Bind the content CAS to namespace quotas

Status: accepted construction prerequisite; content publication, reachability, and live Agent
integration remain open, 2026-08-29.

## Context

ADRs 0244 and 0245 froze content-v2 object transfer and exact availability, but the embedded toxsync
store was not yet part of IoTox's physical namespace inventory. Its canonical layout is
`content-v2/sha256/<2-lowercase-hex>/<62-lowercase-hex>`. Treating the existing flat object store and
that CAS as unrelated quota domains would allow a content-v2 namespace to consume both ceilings.
Scanning only logical manifest reachability would also miss malformed physical entries, links,
permission drift, or corrupt digest names.

## Decision

Add one transaction-bound, strict physical CAS inventory and one combined flat-plus-CAS view.
Preparation creates only the absent `content-v2` root, makes it mode 0700, and refuses an existing
alias or insecure root without following or repairing it. Inventory requires:

- exactly the `sha256` algorithm directory and canonical lowercase fanout/object names;
- owner-owned directories on the namespace filesystem, beneath the private root;
- nonempty, mode-0600, owner-owned, single-link regular objects on that same filesystem;
- bounded object count and physical bytes before records are retained; and
- optionally, a stable full-file SHA-256 rehash equal to each pathname identity.

The combined view scans the existing flat immutable store and the CAS under the same
`SyncNamespaceTransaction`, then applies the namespace's one object-count and byte ceiling to their
sum. Neither store receives a second hidden allowance.

## Qualification

The owned registry now has 635 checks. New deterministic cells build the actual embedded toxsync
store and verify its physical inventory; reject root permission drift, unexpected algorithm entries,
and hard-linked objects; distinguish shape-only inventory from an optional corrupt-byte rehash;
prove a symlinked CAS root is refused without chmod of its target; and show that flat and CAS stores
which each fit independently still fail their combined object-count and byte ceilings.

## Consequences

- IoTox now has the strict quota accounting primitive required by content publication and receive
  commit. It does not yet make the embedded toxsync builder a transaction-safe product writer.
- CAS reachability, repair, quarantine, rollback-guard integration, and durable attempt staging are
  still separate gates. Inventory identity is not deletion authority.
- Bit 29 remains dark. No peer may infer content-v2 support from this local storage prerequisite.
