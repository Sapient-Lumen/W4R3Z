# Resilio remedy-hardening attestation outsider actionable reliance and operator-free remediation fragmentation evaluation

## Why this seam matters now

The archive can already say:

- the corrected replacement is discoverable
- the corrected replacement can name what it supersedes
- a late outsider may understand why the corrected thing is the legitimate successor
- authority proof may now be explicit enough that trust no longer depends entirely on operator memory

That is still weaker than a harder question:

**if the late outsider trusts the corrected replacement, can they actually remediate their stale reliance from that surface without operator intervention, hidden client knowledge, or side-channel support?**

Trust is not yet action.
A self-explaining successor is weaker than a self-sufficient remedy path.
Without an explicit actionability contract, `they know this is the right thing` quietly expands into folklore about `they can now fix their own stale state from here`.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several actionability ingredients, but it still spreads them across separate pages:

- `Link structure and flow` says the landing page hands off to Sync only if Sync is installed and the link may also be added manually
- `Configuring WebUI` says clicking the link or typing it into the browser address bar does not add the share in WebUI and the user must instead use `+` then `Enter a key or link`
- `Sync doesn't start when opening Link in browser` says browser handoff may fail and again prescribes manual paste into `+` then `Enter a key or link`
- `Quick guide to syncing` says the receiver must copy the delivered link or key, paste it into `+` then `Enter key or link`, choose a folder location, click `Connect`, and may still depend on sender-side approval
- `Sharing single file` says receivers again paste the link through `+` then `Enter a key or link`, choose a location, and that everyone with the link can download the files without device- or use-count restrictions
- `Syncing between a desktop computer and a mobile device` says Android users must disable `Simple mode` if they want to choose the destination and that mobile arrivals default to placeholders until the user taps the specific items they want
- `Synchronization Modes` says `Disconnected`, `Selective Sync`, and `Synced` are distinct arrival states so visibility is not the same thing as full local remedial availability

This is good implementation candor.
It is not yet one first-class answer to **if the outsider trusts the correction, what exactly do they do next, in which client, with what dependencies, and with what residual stale-state risk?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the outsider can verify the corrected replacement
- the link can open in some environment
- the user can manually paste the link somewhere else if browser handoff fails
- the sender can approve the request if needed
- the outsider can choose a location if they already know which client settings to change
- placeholders can later be fetched by tapping the right items
- the outsider therefore has an operator-free remediation path

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **outsider late-arrival trust and self-explaining supersession are weaker than outsider actionable reliance and operator-free remediation**
- **a corrected replacement that explains itself is weaker than a corrected replacement that also tells the outsider what to do next and lets them do it without support**
- **manual client rituals, hidden mode toggles, approval gates, or placeholder defaults may never impersonate `the outsider can remediate themselves from here`**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- required client and environment
- remediation affordance class
- required manual step count
- approval dependency class
- operator-support dependency class
- stale-local-residue risk class
- action confirmation class
- strongest honest action sentence
- blocked stronger operator-free sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **actionable-remedy contract sheet**
- **actionable-remedy review**
- **actionable-remedy proof**
- **actionable-remedy timeline**
- **actionable-remedy lineage receipt**
