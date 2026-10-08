# Resilio remedy hardening attestation affected-party acknowledgement, acceptance, and dispute-closure fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for acknowledging that events can be surfaced to humans and that some access-changing actions require explicit approval.
That is useful.

The strongest present ingredients are:

- current `Sync Main View (Desktop)` docs still say the bell lights up for approval requests or other notifications, while History shows general syncing activity for only the last 30 days
- current `Sync Preferences` docs still say notifications can be turned on or off entirely
- current `Sync Share Dialog (Desktop)` docs still say approval can block transfer until you confirm a peer, and unchecked approval can let a peer connect and start syncing automatically
- current `Sync Share Dialog (Desktop)` docs still say previously approved peers may be admitted automatically again unless you require approval for all peers
- current `Sync Private Identity & Linking My Devices` docs still say approvals can be issued from any linked device where the folder is present, and remote users may choose to auto-approve future sharing across linked devices
- current `Folder Types and Management` docs still say pending folders can auto-connect later if that sharer has already approved you before
- current `User Management` docs still say disconnect suspends future updates but leaves already synchronized files in place
- current `Resilio Sync 3.0 change log` still records UI and WebUI warning or interaction fixes, which matters because one visible prompt or warning is not the same thing as closure

## Where the current contract still fragments

The problem is not that Resilio lacks notifications, approvals, or permission controls.
The problem is that it still does not produce one first-class, case-scoped **affected-party acknowledgement and dispute-closure** object.

Today an operator can often infer only weaker truths such as:

- some notification probably appeared on some device
- some request probably could have been approved from one of several linked devices
- some peer probably reconnected automatically because of earlier approval memory
- some bell entry or history item probably existed for a while
- some future updates were suspended for one peer after disconnect
- some human probably saw enough to keep working, but the product cannot say who actually received the remedy notice, who acknowledged it, who accepted it, who objected, and whose objection window is still open

Those are useful clues.
They are not the same as an explicit answer to `who had to be told, which delivery attempts actually landed, who acknowledged or rejected the remedy, which objection timers are still live, and what is the highest honest closure sentence now?`

## Why that matters for AnonSync

AnonSync needs stronger post-remediation truth than `we corrected what we could`.
It needs to support claims such as:

- remediation is operationally complete for a named cohort, but notice has not yet been delivered to all materially affected parties
- delivery is proven to the required human cohort, but acknowledgement is still missing from one regulator, approver, or customer class
- acknowledgement exists for the named cohort, but the objection window is still running, so closure language must stay provisional
- one party accepted the remedy while another contested the factual summary, so the case is stabilized but not uncontested
- the strongest honest sentence is `effects remediated, delivery proven, acknowledgement partial, dispute window open`, not because remediation failed, but because closure and acceptance are distinct from restoration

AnonSync therefore needs first-class objects for **materially affected cohort, notice obligation, delivery evidence, acknowledgement class, objection window, contest state, acceptance scope, dispute owner, reopen trigger, closure ceiling, and blocked stronger closure sentence** rather than leaving operators to reconstruct closure truth from notifications, approvals, linked-device memory, history fragments, and permission changes.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `did the affected parties actually receive, acknowledge, accept, or contest this remedial outcome?` — only by making the operator combine several partially overlapping mechanics:

- bell or notification presence
- optional notification settings
- access approvals in share flows
- remembered approvals across linked devices
- pending-folder auto-connect semantics
- permission or disconnect changes
- short-horizon History and current UI state

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **affected-party acknowledgement and dispute closure** directly.
Its interface family should let the product separate at least these truths:

- notice obligation identified, no delivery attempt yet
- delivery attempted, proof incomplete
- delivery proven for named cohort only
- acknowledgement pending for named cohort
- acknowledged for named cohort, objection window open
- contested by named cohort
- accepted for named cohort only
- objection window lapsed without contest for named cohort only
- closure reopened by late objection or new evidence
- broader closure sentence blocked

That is why this revision adds five more first-class pages:
**Remedy-hardening-attestation-affected-party-closure contract sheet**, **Remedy-hardening-attestation-affected-party-closure review**, **Remedy-hardening-attestation-affected-party-closure proof**, **Remedy-hardening-attestation-affected-party-closure timeline**, and **Remedy-hardening-attestation-affected-party-closure lineage receipt**.
