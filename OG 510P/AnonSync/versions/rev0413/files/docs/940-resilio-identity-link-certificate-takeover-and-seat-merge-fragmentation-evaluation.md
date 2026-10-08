# Resilio identity linking, certificate takeover, and seat-merge fragmentation evaluation

## Why this seam matters

Current official Resilio docs are candid that linked-device identity is not a cosmetic convenience layer.
It is a certificate-bearing seat-adoption system with blast radius.
The direction of the M-key matters, the incoming seat can inherit another seat's identity and configured shares, version-mixed linking can break license/share control, linking already-running seats can replace certificate lineage, Advanced folders can disappear from the adopting seat's app, and iOS can pay a stronger filesystem price.

That is exactly why this seam is worth studying and exactly why it should not be cloned as-is.

## What current official docs still get right

They still say plainly that:

- each installation has its own digital certificate and fingerprint
- linked devices automatically expose all folders across the linked set
- M-key direction matters because the adopting seat can take the source seat's identity/fingerprint/shares
- version-mixed v2/v3 linking is risky
- linking already-running seats can replace a certificate and evict Advanced folders from the adopting seat
- iOS can delete those folders from the filesystem in that scenario
- unlink is local-only
- clearing an offline linked device only hides it and the device can reappear later

That candor is valuable.

## Why AnonSync still should not clone it

One ordinary operator question remains too fragmented:

> what exactly happens to this seat, its certificate, its subjects, and its later residue if I link, hide, or unlink it?

In current Resilio, the operator still has to assemble that answer from:

- the identity guide
- the hide-offline-device article
- the Standard-vs-Advanced architecture article
- platform-specific deletion caveats

That is too much documentation archaeology for an operation this consequential.

## Hard decisions for AnonSync

1. **Identity linking is a reviewed adoption contract, not a lightweight pairing action.**
2. **Seat lineage and subject lineage must remain separate but adjacent truths.**
3. **Certificate takeover must preview before apply.**
4. **Version-mixed seat adoption is blocked by default unless the operator escalates through a stronger review.**
5. **Hide, unlink, revoke, and forget are different verbs.**
6. **Latent hidden members remain visible as residue until actually detached or otherwise made harmless.**
7. **Every serious seat-link mutation emits a durable receipt.**

## Interface family implied by this evaluation

AnonSync should own this seam with:

- **Identity merge contract sheet**
- **Identity adoption review**
- **Certificate takeover impact**
- **Unlink and hidden-device boundary**
- **Identity merge receipt**
