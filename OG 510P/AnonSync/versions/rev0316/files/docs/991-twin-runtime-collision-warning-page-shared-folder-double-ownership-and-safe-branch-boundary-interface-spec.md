# Twin-runtime collision warning page — shared folder double ownership and safe branch boundary

## Purpose

Stop a second runtime, seat, or local instance from silently claiming the same folder's control substrate.

This page exists because `same bytes on disk` does not imply `safe shared control ownership`.

## Trigger conditions

Show this page when the system detects any of:

- the same bound path is being claimed by another local runtime
- imported control substrate appears to belong to another active seat
- external/removable storage has been seen from multiple local runtimes
- the operator tries to add a tree already carrying foreign capsule evidence

## Core questions answered

1. **Who currently owns this capsule?**
2. **Is this second attachment continuation, takeover, or collision?**
3. **Can this be made safe by rebinding, branching, or import-with-regeneration?**
4. **What corruption or ambiguity risk exists if we proceed naïvely?**

## Required panels

### A. Ownership evidence

List:

- observed owner / runtime fingerprint
- last-seen activity
- subject identifier match / mismatch
- path match / mismatch
- capsule lineage confidence

### B. Unsafe path

State plainly:

- `Proceeding as a second owner risks corrupting service state or making future sync impossible.`

### C. Safe alternatives

Offer explicit branches such as:

- `Rebind to existing owner`
- `Import bytes only and regenerate new capsule`
- `Create a deliberate forked successor`
- `Abort and inspect current owner`

### D. Not offered

When unsafe, the UI must withhold any button labeled merely:

- `Add folder`
- `Continue`
- `Fix automatically`

## Receipt obligations

If the operator chooses a safe alternative, preserve:

- collision evidence summary
- chosen branch or rebind path
- whether original capsule continuity was kept, abandoned, or forked
- blocked stronger sentence such as `second attach was harmless`
