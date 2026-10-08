# Resilio remedy-hardening attestation outsider remediation completion and self-verifying clean-state truth fragmentation evaluation

## Why this seam matters now

The archive can already say:

- a late outsider can find the corrected replacement
- the replacement can explain why it supersedes the stale thing
- the outsider can trust that supersession claim
- the outsider may even have a bounded self-service remediation path

That is still weaker than a harder question:

**did the outsider actually finish remediation, retire their stale local residue, and obtain a portable clean-state verdict they can verify later without reopening the operator-support loop?**

A safe path is not yet a finished remedy.
A finished remedy is not yet a self-verifying clean state.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several completion-shaped ingredients, but it still spreads them across separate pages:

- `Sync Main View (Desktop)` says the green checkmark only means files are synced with all connected peers, the peer counter distinguishes online peers from total peers including offline ones, and History only shows the last 30 days of general syncing activity
- `My files don't sync` says the operator should inspect the peers list, status warnings, history search, queue state, and file availability to troubleshoot whether sync is really finished
- `Synchronization Modes` says `Remove from this device` can revert a local copy to a placeholder and warns the operator to make sure other peers still have a copy before later download matters
- `Disconnecting and Removing Folders` says disconnect ends future syncing but leaves files in the file system, removes placeholders when Selective Sync was enabled, and reconnect can propose a different path that may create a new directory
- `Sync interface on Android`, `Sync Interface on iOS devices`, and `Syncing between a desktop computer and a mobile device` say `Clear` or `Clear synced files` can turn actual files back into placeholders while `Remove from this device` or `Disconnect` changes local presence differently across platforms
- `Using Archive for file versioning and restoring deleted files` says restore is manual, Archive lacks per-peer change attribution, and a restored file can be re-archived on rescan if Sync was not running at the right time

This is good completion candor.
It is not yet one first-class answer to **did this outsider actually finish remediation and can they later prove that their local state is clean without operator interpretation of statuses, history, placeholder state, queue state, and archive behavior?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the outsider had a bounded remediation path
- the outsider opened or downloaded the corrected material
- the UI currently looks green
- some peers are connected while others are offline
- the share details show a file count
- local bytes may have been cleared back to placeholders or disconnected copies may still remain
- the archive may still hold older versions or later restorations may reopen stale state
- the outsider therefore finished remediation and is clean now

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **bounded-exposure remediation is weaker than outsider remediation completion and self-verifying clean-state truth**
- **an outsider can safely act is weaker than an outsider actually switched, retired stale residue, and can later verify that clean state from portable evidence**
- **green status, queue emptiness, recent activity, placeholder counts, file counts, or disconnected-folder visibility may never impersonate `completed clean-state remediation`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- remediation completion class
- stale-residue retirement class
- clean-state verification class
- portable proof artifact set
- re-open risk class
- strongest honest clean-state sentence
- blocked stronger self-verifying clean-state sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **remediation-completion contract sheet**
- **remediation-completion review**
- **remediation-completion proof**
- **remediation-completion timeline**
- **remediation-completion lineage receipt**
