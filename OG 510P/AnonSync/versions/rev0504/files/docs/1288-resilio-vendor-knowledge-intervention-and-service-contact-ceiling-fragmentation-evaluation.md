# Resilio vendor-knowledge, intervention ceiling, and service-contact fragmentation evaluation

## What current official docs still make clear

Another current Resilio pass strengthens the archive's clone-veto line rather than weakening it.

Current official docs still say several things that are operationally real and worth borrowing:

- current `Can Resilio team see and block/remove any Sync folders?` docs still say Resilio neither hosts nor caches content, cannot see link-specific data placed after `#`, cannot control decentralized peer-finding enough to block certain peers, and cannot modify or remove data except through devices that already hold it
- current `Can others see my files? How secure is sharing by Resilio Sync?` docs still say the team cannot see user files, while tracker, relay, update check, link landing, and license-purchase services each expose different classes of information
- current `What ports and protocols are used by Sync?` docs still say the client fetches `sync.conf`, then tells trackers its IP addresses, listening port, and share list so it can find peers
- current `What is a Relay Server?` docs still say relay is a distinct fallback carrier and that peers visibly show a relay icon when that route is in use
- current `Power user preferences` docs still say anonymous statistical metrics are separately controllable through `send_statistics`
- current `Collecting debug logs manually` and companion crash/log collection docs still say staffed direct technical support is lane-limited, and that diagnostic visibility into a user install depends on the user explicitly enabling capture and then sending evidence
- current `How to Report Security Vulnerabilities to Resilio, Inc.` docs still say security disclosure itself is a separate vendor-contact lane from ordinary product sync behavior

That is real candor.
It is useful product truth.

## What still should not be cloned

The operator is still asked to reconstruct one practical answer to:

> what can Resilio infrastructure learn here, what can it carry, what can it count, what can it inspect only if I explicitly send evidence, and what can it simply never revoke or delete on my behalf?

Current Resilio docs still scatter that answer across security FAQs, tracker/relay architecture notes, telemetry settings, link-fragment explanations, support-log articles, and vulnerability-reporting instructions.

That means several materially different questions remain merged unless the operator does their own synthesis:

1. **what facts are service-visible during ordinary operation?**
2. **what facts remain opaque because they never leave the device or stay after a URL fragment?**
3. **what encrypted bytes can still be carried by third-party infrastructure without being inspectable there?**
4. **what visibility can vendor staff gain only after explicit user-initiated evidence send?**
5. **what intervention powers are absent even if the vendor can observe some metadata?**

That page-contract gap is exactly why AnonSync should not clone the behavior.

## Why this matters for AnonSync

AnonSync should borrow six habits directly:

- **say openly when service contact, service-visible metadata, service carriage, and vendor inspection are different truths**
- **say openly when a browser landing server never sees the capability-bearing fragment**
- **say openly when tracker metadata exists even though content does not**
- **say openly when relay can carry ciphertext without decrypt authority**
- **say openly when telemetry is optional and narrower than operational metadata**
- **say openly when vendor non-control is a first-class ceiling rather than implied by marketing language**

But AnonSync should reject six weaker habits:

- one flat `private` badge that hides tracker, relay, update, landing, telemetry, and support-send differences
- one flat `cloudless` sentence that hides real service-visible metadata classes
- one flat `we cannot see your files` reassurance that hides what the vendor can still count, receive, or inspect after explicit evidence send
- silent merging of routine service contact with optional diagnostics disclosure
- silent merging of `cannot see` with `cannot intervene`
- any revocation or abuse-language surface that overclaims vendor power the product does not actually possess

## Replacement pages added for this seam

This revision therefore adds six narrower replacement pages:

- `1289` — Vendor-ceiling contract sheet
- `1290` — Service-visible-facts review
- `1291` — Intervention-authority proof
- `1292` — Vendor-contact timeline
- `1293` — Vendor-ceiling lineage receipt

These pages keep the Resilio candor and reject the scattered vendor-knowledge contract.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor that tracker metadata, relay carriage, link-fragment opacity, update/license service contact, anonymous telemetry, user-sent diagnostics, and true vendor non-control are different truths; refuse any interface contract where `what can the vendor know or do about this share right now?` still makes the operator merge security FAQs, settings tables, and support articles instead of one explicit vendor-ceiling object.
