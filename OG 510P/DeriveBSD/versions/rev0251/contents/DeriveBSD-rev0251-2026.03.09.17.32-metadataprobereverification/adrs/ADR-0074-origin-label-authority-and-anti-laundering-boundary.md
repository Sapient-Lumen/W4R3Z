# ADR-0074: Origin label authority and anti-laundering boundary

Date: 2026-03-07
Status: Accepted

## Context

DeriveBSD already had the right instincts for inbound bytes:
`content.origin`, `content.import.plan`, `content.import.receipt`,
quarantine-first removable-media flows, sanitize-first portals, and export policies.

What remained unresolved was the **authority boundary** for provenance metadata.
The archive kept saying some combination of “xattrs, sidecars, store-backed metadata”
should preserve origin labels, but that ambiguity was doing real damage:

- xattrs are useful for local UX but are easy to strip or lose on some filesystems and archive workflows,
- query/index layers need a stable upstream truth or they become folklore,
- portalized copy/export flows need to know whether they are preserving metadata or rehydrating it,
- and incidents need one compact answer to **which provenance record is authoritative, and did the label survive the workflow or get laundered?**

Without a crisp boundary, the archive drifts toward mystery bytes, app-specific warnings,
or false confidence in file-local metadata that cannot actually survive common workflows.

## Decision

DeriveBSD will treat **content provenance / quarantine metadata** as a small typed contract, not a best-effort convention.

The accepted v0 boundary is:

1. `content.origin` is the authoritative provenance record.
2. Filesystem quarantine/origin labels are **pointer/cache only**. They may carry current state and a reference to the authoritative record, but they are not the source of truth.
3. `content.import.receipt` must carry a `metadata` block that states:
   - the accepted authority model,
   - how metadata reached the imported result,
   - whether it was preserved, rehydrated, cleared-by-policy, or looks laundered,
   - and the authoritative `content.origin` digest.
4. Preservation of provenance across lossy filesystems, raw archive tools, or compatibility exports is only promised through official **portal / bundle** lanes that can rehydrate labels from authoritative records.
5. If inbound bytes cannot prove preserved or rehydrated provenance, the result remains quarantined and the receipt must say `laundering-suspected` rather than pretending the metadata is intact.
6. Metadata query/index layers are **derived surfaces**, not the authority boundary. They consume the authoritative `content.origin` record and current label pointers; they do not replace them.

## Consequences

### Positive

- The archive now has a compact answer to “what is the authoritative provenance object?”
- Query/index work can proceed without reopening the xattr-vs-CAS argument every time.
- Portalized copy/export/import flows can explain whether metadata was preserved or rehydrated.
- “Origin laundering” becomes a receipted condition instead of an invisible failure mode.
- The existing import pipeline becomes more implementable without inventing a large metadata subsystem.

### Negative / trade-offs

- Some traditional copy/archive workflows are now explicitly outside the guaranteed provenance-preserving lane.
- Import receipts have a little more structure to keep wired and explained.
- Implementations still need a practical rehydration path for non-preserving filesystems and transports.

## Non-goals

This ADR does **not** decide:

- the final filesystem attribute names,
- the final UX for label inspection in file managers,
- the full metadata-query language,
- or the full privacy policy for metadata indexing and subscriptions.

Those remain follow-on implementation work or future ADR material.

## Why this shape

The coherence win is deliberately narrow:

- keep `content.origin` as the semantic authority,
- let file-local labels stay tiny and cheap,
- make imports state how provenance survived,
- and treat portal/bundle rehydration as the only supported escape hatch for lossy transports.

That is enough to stop provenance from becoming folklore,
without inventing a giant content-management subsystem too early.
