# Resilio artifact-family, token-opacity, and epoch-fork evaluation

## Why this pass exists

The archive already had strong work on join consequence, claim lanes, approval, mutable grants, and linked identity.
What it still lacked was one explicit evaluation of a narrower but highly consequential seam:

> where does current Resilio actually explain what an access artifact **is**, what governance it carries by itself, and what happens when that artifact is rotated?

Current official Resilio docs are still useful because they do not pretend every share token is the same thing.
They still openly say that:

- only **Standard** folders use raw keys
- the **first character** of a key identifies a different capability family (`A`, `B`, `D`, `E`, `F`, `M`)
- an `F` key is ciphertext-only custody and cannot decrypt names or content
- an `M` key links devices into one identity family rather than merely granting one folder
- share **links** are different from raw keys because the link carries a temporary key and an approval flow
- the browser landing page is only a carrier shell and the meaningful parameters live after `#`
- after approval the owner generates an **X509 certificate** and signs an ACL entry for the joining identity
- changing a raw key is **not** distributed automatically, and peers with the old key continue syncing with each other while the changed peer moves to a new epoch

That is excellent candor.
It is also a strong reason not to clone the exact contract.

## What current Resilio still gets right

### 1) Artifact family is real product meaning

Resilio is still right that a device-link artifact, a folder read-write key, a read-only key, an encrypted custody key, and an approval-bearing web link are not mere presentation variants.
They are materially different authority objects.

### 2) Browser carrier and authority artifact are different things

Resilio is still right that the web landing page is not itself the authority.
The URL shell, the hash fragment, the temporary key, the requester's public key, later certificate issuance, and ACL mutation are distinct parts of the path.

### 3) Rotation can create parallel epochs

Resilio is also right to say that a key change is not magical global replacement.
Old-key peers can continue among themselves.
That is a real and important operator truth.

## Why AnonSync still should not clone it

### 1) Too much authority meaning remains encoded inside opaque tokens

Current Resilio still expects the operator to know or learn that the first character of a raw key implies a different capability family.
That is clever engineering, but it is not a sufficient operator contract.
A token should be inspectable as a product object, not understood only by folklore or support docs.

### 2) Carrier convenience still risks hiding governance differences

A link can arrive by browser, clipboard, QR, e-mail template, or manual paste.
But current docs still leave the operator to mentally reconstruct whether the arriving thing is:

- a bearer-style raw key
- an approval-bearing temporary-key link
- a linked-identity family key
- an encrypted-custody artifact
- a successor artifact that will fork prior continuity

Carrier convenience is worth keeping.
Making it the main explanation is not.

### 3) Rotation truth still sounds too much like an implementation caveat

`Change the key` is not just maintenance.
It can produce a parallel cohort that keeps syncing on the old epoch.
That is governance truth and continuity truth, not a footnote.
A product should expose it before issuance or rotation, not after damage.

### 4) Artifact family and resulting seat role are still nearby but not owned together

Current Resilio docs still require the operator to combine `Key structure and flow`, `Link structure and flow`, identity docs, share-dialog docs, and local-share caveats before they can answer one ordinary question:

> what exact authority object am I issuing or accepting, and what parallel continuity will survive if I rotate it later?

That should belong to one stable page family.

## Hard decisions now locked for AnonSync

1. **Artifact family must be inspectable before use.** An opaque pasted token is never the only explanation of rights.
2. **Seat-link artifacts and subject-access artifacts must never share one flattened grammar.** `Join my device family` and `join this subject` are different contracts.
3. **Carrier must not determine semantics.** Browser-open, QR, paste, and local import are carriers; the inspected artifact object owns the meaning.
4. **Rotation is an epoch event.** Replacing a live artifact must preview surviving old cohorts, successor issuance, and retirement order.
5. **Issuance and intake both emit receipts.** The system must remember what artifact family, ceiling, expiry, and fork boundary existed at review time.

## Replacement page family justified by this pass

This pass therefore justifies five more product-owned surfaces:

- **Capability artifact**
- **Issuance preview**
- **Incoming artifact intake**
- **Artifact rotation / fork warning**
- **Artifact issuance receipt**

## Bottom line

The tighter no-clone reason is now this:

> Resilio is still good evidence that links, keys, encrypted-custody artifacts, and linked-identity artifacts are truly different. But it is also current evidence that too much authority meaning still lives inside opaque tokens and support prose. AnonSync should keep the candor and refuse the token-opacity contract.