# Resilio remedy hardening attestation successor reference rebinding, stale predecessor handle retirement, and pointer fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that `a successor world exists`, `the old world broke`, and `all practical references now safely point at the successor` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `If your device is stolen` docs still say the serious response path regenerates identity, relinks devices, and reshares folders, which implicitly acknowledges that predecessor references cannot simply be assumed to remain valid
- current `Sync Service Troubleshooting on Windows` docs still say switching to Local System creates a new storage world with no old folders visible and requires re-add plus re-share or reconnect
- current `Link structure and flow` docs still say folder links contain folder name, folder ID, temporary key, expiration, and client version, and that they are handed from browser to app
- current `Sync Share Dialog (Desktop)` docs still say sharing links can be copied to clipboard or inserted into email or messenger, which means references propagate beyond one UI surface
- current `Sharing single file` docs still say a file link can be made non-expiring, has no usage-limit or device-ban control, and recipients can share files further
- current `Key structure and flow` docs still say changing a Standard-folder key is not automatically distributed and peers with the old key continue syncing with each other
- current `What's the difference between Standard and Advanced folders?` docs still say Standard-folder peers can share their keys without limitation and that Standard cannot be upgraded in place to Advanced

## Where the current contract still fragments

The problem is not that Resilio lacks clues about successor rebinding.
The problem is that it still does not produce one first-class, case-scoped **reference rebinding and predecessor-handle retirement** object.

Today an operator can often infer only weaker truths such as:

- the successor world works, but old links, keys, bookmarks, or copied share messages may still point at predecessor-era handles
- one group has been re-shared or reconnected, but there is no single page proving which references were rebound and which stale ones remain live
- a Standard-folder key may have changed for one peer while old-key peers keep syncing among themselves, yet the product does not elevate that into a pointer-divergence receipt
- a single-file link may have been sent outward and can remain non-expiring and re-shareable, but there is no typed case object showing whether that predecessor pointer was retired, replaced, or left outside governance
- a new identity or new storage world may be real, but the operator still has to reconstruct which names, IDs, and handles now canonically represent the successor

Those are useful clues.
They are not the same as an explicit answer to `which predecessor references still resolve, which are tombstoned, which are rebound to the successor, who was informed of the canonical pointer, and which stronger discovery or reachability sentence must remain blocked?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the successor is legitimate`.
It needs to support claims such as:

- the successor world is legitimate, but only a named subset of predecessor handles have been retired
- the successor world is canonical for named slices, while old user-facing references remain live and dangerous
- old handles are blocked internally, but off-world copied links remain outside governance
- key rotation or receipt reissue happened, but dependent parties were not yet all rebound to the successor pointer

So AnonSync should not clone Resilio's present contract at this seam.
It should borrow the candor about identity regeneration, re-share and reconnect requirements, explicit link and key structure, non-expiring outward links, and old-key continuation, while replacing the fragmented operator story with one first-class family for **successor reference rebinding, stale predecessor handle retirement, and canonical-pointer truth**.
