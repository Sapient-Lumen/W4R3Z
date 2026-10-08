# Resilio requester proof, human-label collision, and linked-family trust fragmentation evaluation

## Why this seam matters

Another current official Resilio pass sharpens the no-clone line around **who the operator is really trusting**.
The useful distinctions are real:

- a human-readable identity name exists
- a device name exists
- a certificate fingerprint exists
- approval can widen from one reviewed requester to **all linked devices** in that family

The current Resilio contract is still too fragmented because the ordinary operator must reconstruct those distinctions from identity docs, link-flow docs, and settings pages rather than from one owned interface family.

## What current official docs still say

Current official Resilio materials still openly say all of the following:

- every Sync installation gets a **unique digital certificate** and a **random fingerprint** generated around the chosen identity setup
- even if two independent Sync instances use the **same identity name**, their certificates remain different
- the fingerprint can be viewed in identity settings and is meant to help peers recognize which Sync installation is connecting
- during link-based approval, the requesting peer sends a public key; the approving peer is shown the requester's **user name** and **public key fingerprint**
- Resilio's own link-flow docs still say the approver can compare the fingerprint before granting access, after which the owner issues an **X509 certificate** and signs an ACL entry for the requester
- current identity docs still say that once a remote user approves one of your devices, they can choose to **automatically approve all your linked devices** for future sharing
- mobile settings pages still expose identity name, device name, and certificate fingerprint together as part of what other users recognize

Those are useful distinctions.
They are also a strong reason not to clone the present contract.

## Why this still fails the clone test

To answer one ordinary operator question — **`who exactly am I approving right now, and how far will that trust travel?`** — current Resilio still makes the operator combine:

- identity creation/linking docs
- the link structure/approval flow doc
- settings pages that expose fingerprint and device name
- separate prose about linked-device auto-approval

That is too much archaeology for a core trust boundary.
A product can absolutely have names, device labels, fingerprints, and linked families.
It should not make the operator remember which of those is a label, which is a proof handle, and which one silently widens approval scope.

## Hard decisions now locked in for AnonSync

AnonSync should keep the real distinctions and refuse the fragmentation.
This tranche locks in five harder decisions:

1. **human-readable labels are hints, not trust handles**  
   Identity name and device label may help recognition, but neither may stand alone as the authoritative answer to `who is this requester?`

2. **approval memory binds to the reviewed requester handle**  
   Reusable trust must attach to an explicit reviewed handle bundle, not just a remembered display name.

3. **linked-family widening is a second decision**  
   Approving one requester and approving the whole linked family are different acts and must not share one silent default.

4. **proof handle and social label stay separate**  
   The interface must preserve the difference between `what humans call this requester` and `what cryptographic or lineage evidence was actually reviewed`.

5. **receipts must preserve trust scope and blocked overstatement**  
   Any approval receipt must say whether the operator approved a single seat, a reviewed family expansion, or declined that widening.

## Resulting interface family

That is why this tranche adds:

- a **Requester identity contract sheet**
- a **Requester collision review**
- a **Proof handle** page
- a **Trust expansion review**
- a **Requester lineage receipt**

The point is not to glorify fingerprints.
The point is to stop the ordinary operator from having to infer whether a remembered name, a device label, a fingerprint, and a linked family all mean the same thing when making an access decision.