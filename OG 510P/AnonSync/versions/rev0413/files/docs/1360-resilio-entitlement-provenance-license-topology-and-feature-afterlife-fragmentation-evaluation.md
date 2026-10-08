# Resilio entitlement provenance, license topology, and feature-afterlife fragmentation evaluation

## Why this pass exists

The archive already had stronger doctrine for capability floors, governance planes, participant units, admission instruments, action surfaces, and mixed-version interlock.
What it still lacked was one direct current Resilio evaluation for a narrower but still important question:

> why is this feature available here, who granted that right, what usage lane keeps it legitimate, who can revoke it, and what actually stops or degrades when that entitlement disappears?

Current official Resilio docs still show a useful, living product, but they also still show that one ordinary answer is spread across several article families at once:

- `Licensing in Resilio Sync 3.0`
- `FAQ Resilio Sync 3.0.0`
- `Important before updating to Resilio Sync 3.0.0`
- `Updating installation to Resilio Sync v3`
- `How to apply license key and share license seats`
- `What happens when Sync Business trial or license expires?`
- `What is the difference between Sync Home Pro and Sync Family Pro?`
- `Sharing a folder locally`
- `"Your Sync Business license doesn't support Windows Server or Linux (x86 or x64)."`
- `My device has lost the license and Sync has reverted to the Free version. How can I return the Pro functionality?`

## Current official Resilio evidence that matters here

Current official docs still say all of the following:

- `Licensing in Resilio Sync 3.0` still says previously purchased Home Pro and Home Pro for Family licenses continue to work in v3, while Sync Business licenses are not compatible with Sync v3 and commercial users should remain on Sync v2.
- `FAQ Resilio Sync 3.0.0` still says v3 functionality is fully available for non-commercial use, but activation still needs a license from the site; the new site-issued v3 license is associated only with the given person and cannot be shared with others; old Home Pro remains personal-use only; old Family Pro can be shared with up to 5 family members.
- `Updating installation to Resilio Sync v3` still says previously licensed Home Pro / Family installs auto-activate after upgrade, but a former Free install only gets a 7-day trial before site registration and activation are needed.
- `How to apply license key and share license seats` still says Home Pro / Free keys can be applied to several devices with the same file; Family Pro uses the same key on the necessary family devices; Business can be applied to only one identity as License Owner; linked devices under that identity inherit Pro automatically; other identities get Pro only via shared seats; and applying the Business key to another identity steals ownership from the previous owner.
- `What happens when Sync Business trial or license expires?` still says a Business license or trial expiration removes Pro features and causes shared seats to expire on the same date.
- `Sharing a folder locally` still says local shares are a Pro feature and stop working if the trial expires, the license expires, or the license is removed.
- `"Your Sync Business license doesn't support Windows Server or Linux (x86 or x64)."` still says a workstation-only Business license can be applied on a Server OS but sharing files/folders and linking devices will stop until the license includes Server support.
- `My device has lost the license and Sync has reverted to the Free version...` still says a Business seat can disappear because the owner reapplied the key elsewhere, reclaimed a seat, or over-shared beyond capacity.

So current Resilio still contains a real but scattered answer to `why does this feature exist here, is it legitimately active for this usage lane, who can take it away, and what afterlife does the feature have if the entitlement changes?`

## What Resilio still gets right

### 1) It is candid that entitlement provenance is not one thing

The docs do not pretend every feature comes from a single plan.
They openly distinguish old Home Pro, old Family Pro, site-issued v3 non-commercial activation, Business owner identity, linked-device inheritance, shared seats, and server-support add-ons.
That honesty is valuable.

### 2) It is candid that feature afterlife differs by feature

The docs still say that some entitlement loss is not just cosmetic.
Local shares stop working on license loss.
Business expiration strips Pro features from both owner and shared seats.
A workstation-only Business license on Server OS produces a specific degraded state where key parts of sharing/linking stop.
That matters.

### 3) It is candid that authority to grant or revoke is topology-shaped

The docs still say Business ownership can move if the key is applied elsewhere, that seat owners can reclaim seats, and that linked devices inherit through identity rather than separate application of the key.
That is exactly the kind of operational truth worth borrowing.

## Why this is still a good reason not to clone them

### 1) Current docs still make one ordinary entitlement answer too archaeological

An operator still has to merge multiple articles to answer:

- is this capability active because of personal-use v3 activation, legacy Home Pro, Family sharing, Business owner status, linked-device inheritance, or a shared seat?
- is the usage lane non-commercial, home-family, workstation-business, or server-capable business?
- if entitlement changes, does the feature vanish immediately, degrade, require relicensing, or continue through some narrower lane?

AnonSync should not inherit a contract where `Pro`, `licensed`, or `available` silently carry all of that.

### 2) Usage legitimacy and feature activity are still too easy to confuse

Current Resilio still says v3 non-commercial activation is free of charge but still license-gated, and still says Business users cannot update to v3.
That means `activated` and `permitted for this usage lane` are different truths.
A serious sync product should not leave that distinction implicit.

### 3) Grant authority and revocation authority are still too diffuse

Current docs still distribute ownership takeover, seat sharing, seat reclaim, expiry fan-out, server-support warnings, and feature-specific license cliffs across different pages.
That is too much archaeology for such a load-bearing truth.

## What AnonSync should do instead

AnonSync should make **entitlement provenance** first-class.
Every meaningful feature sentence needs one stable answer for:

- entitlement source
- usage lane legitimacy
- grant topology
- revocation authority
- feature-afterlife class
- weakest missing proof still blocking a stronger entitlement sentence

The product should never let `licensed`, `Pro`, `free`, `trial`, or `available` blur into one vague capability story.

## Hard decisions now locked

1. **Entitlement provenance is first-class.**
   Every serious feature claim must name whether it comes from personal v3 activation, legacy personal license, family pack, business owner grant, linked-device inheritance, shared seat, or unknown.

2. **Usage lane legitimacy, feature activity, and revocation authority are different truths.**
   A node may be activated but in the wrong commercial/server lane; it may be legitimately licensed but only through a revocable shared seat.

3. **Feature-afterlife must stay visible.**
   `licensed` is weaker than `feature remains active after this entitlement shifts`.
   `key applied` is weaker than `topology still grants this feature here`.

4. **Owner/seat topology stays visibly stronger than a local license badge.**
   If a business owner can steal ownership by reapplying the key elsewhere or reclaim seats later, the product must say so directly.

5. **Feature-specific cliffs remain first-class.**
   If a given feature stops working on entitlement loss or on wrong-support posture, the product must publish that cliff explicitly.

## What this tranche adds to the archive

This revision adds five more first-class pages:

- **Entitlement-provenance contract sheet**
- **License-topology review**
- **Feature-entitlement proof**
- **Entitlement-afterlife timeline**
- **Entitlement lineage receipt**

Together they let AnonSync answer one ordinary operator question without archaeology:

> why is this feature available here, who granted that right, what can revoke it, and what stronger entitlement sentence is still blocked?
