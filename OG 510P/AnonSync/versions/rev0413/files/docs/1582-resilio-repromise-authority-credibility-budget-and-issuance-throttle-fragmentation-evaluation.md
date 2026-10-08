# Resilio re-promise authority, credibility budget, and issuance-throttle fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- distinguish finish forecast from commitment
- distinguish commitment from breach
- distinguish breach from make-good duty and trust repair
- keep `motion restored`, `scope restored`, `trust repaired`, and `re-promise eligible` separate

What it still lacked was the next ordinary operator answer:

> after recovery begins or even after some trust is repaired, who is actually allowed to publish a new promise, how strong may that promise be, what scope cap or probation applies, and when is co-sign or outright blocking required?

That is the seam this pass locks.
A product that can say `trust partly repaired` but still cannot say who may promise again is still leaving real authority in side threads, team folklore, and hopeful behavior.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose several real **authority ingredients**, but mostly as separate permission, identity, version, and support surfaces rather than one operator-facing promise-authority contract:

- `User Management` still separates `Owner`, `Read-Write`, and `Read Only`, says only Owners may invite new users to a folder, and says all devices linked to one identity act as Owners.
- `Sync functionality in detail` still says a folder can be shared and approved from any linked device, that prior approval can be retained for future sharing, and that an operator can instead require approval for every peer that tries to connect.
- `Sync Private Identity & Linking My Devices` still says a remote user can choose to auto-approve all linked devices for future sharing, and still warns not to link v2 and v3 devices because license conflicts can lead to lost access to Sync UI and shares configuration.
- `Comprehensive guide to syncing (Desktop-Desktop)` still says linked devices automate folder sharing across the identity with full RW access.
- `Power user preferences` still says older versions may be missing settings or still have deprecated ones.
- `Collecting debug logs manually` still says direct technical support is available only for Sync Business and not Sync v3.

## What current Resilio still gets right

### 1) It distinguishes some real authority classes

Owner, Read-Write, and Read Only are real authority classes.
That matters and is worth borrowing.

### 2) It makes trust propagation and approval reuse real

Approval can be reused across future sharing and can travel across linked devices.
That is a real operational convenience and also a real risk surface.

### 3) It admits that version and tier matter

Mixed-version identity links can conflict, some settings are version-sensitive, and support posture differs by product tier.
That honesty is valuable.

## Where current Resilio still fragments the operator answer

### A) Share authority is not promise authority

Current docs can tell an operator who may invite, approve, or write.
They still do not define who may publish a new delivery commitment after recent misses or degraded trust.

### B) Recovery and trust repair do not compile into scoped future authority

Current docs can help with approval, linking, and permissions.
They still do not turn `trust partly repaired` into one explicit answer to whether the next promise may be autonomous, must be co-signed, must be narrowed, or is blocked entirely.

### C) Linked-family trust can silently over-expand authority

Auto-approval across linked devices is useful.
It also shows why AnonSync should avoid a contract where prior trust silently broadens future authority without a new operator review.

### D) There is no durable receipt for promise authority after degradation

Current docs still do not preserve one canonical answer to what promise class is currently allowed, by whom, for what scope, under what probation window, with what invalidators.

## Resulting product decision

AnonSync should borrow Resilio's candor that permissions, approvals, linked identities, mixed-version risk, and support tier all shape real operational authority.
It should **not** clone a contract where the operator still has to improvise who may promise again after degraded trust and under what caps.

AnonSync should instead expose:

- one first-class **Re-promise authority contract sheet**
- one **Promise issuance review**
- one **Re-promise authority proof** page
- one **Promise authority timeline**
- one durable **Promise authority lineage receipt**

## Hard decisions locked by this pass

- **trust repair is weaker than restored promise authority**
- **autonomous promise authority, co-sign-required authority, scope-capped authority, target-only authority, and blocked authority stay separate**
- **credibility budget is first-class and repeated misses must degrade authority explicitly**
- **restored authority may be narrower than the old authority and may remain on probation**
- **authority receipts must preserve basis, scope cap, promise-class cap, probation window, co-sign rule, and restoration triggers**
