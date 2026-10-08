# Resilio remedy hardening attestation verdict legitimacy, burden, threshold, and rulebook-version fragmentation evaluation

## What current Resilio gets right

Current official Resilio materials still deserve credit for being candid that `the surface looked green`, `the queue looked short`, `the warning opened a KB article`, `the folder icon looked like a normal full-sync folder`, `the service world looked empty`, and `the stronger sentence is therefore justified` are not one flat truth.
That candor is useful.

The strongest present ingredients are:

- current `Sync Main View (Desktop)` docs still say the green checkmark means files are synced with all connected peers, and peers offline for 7 days get disconnected from the folder
- current `My files don't sync` docs still say operators should inspect Status warnings, click them through to KB explanations, inspect History, and inspect upload or download queues
- current `Folder Types and Management` docs still say pending, disconnected, selective, full, read-only, and encrypted folders each denote different behaviors
- current `Sync Service Troubleshooting on Windows` docs still say switching the service to Local System can create a different storage world where the old added folders are absent, and WebUI exposure can depend on config plus restart
- current `Updating installation to Resilio Sync v3` docs still say update behavior depends on installation style, same command-line parameters, same user, and same storage continuity, and that Business installs cannot be updated to v3
- current `File download priority` docs still say prioritized behavior has limitations, that some high-priority arrivals do not preempt active downloads, and that the visible queue may appear alphabetical rather than in actual priority order
- current `Resilio Sync 3.0 change log` still records warning, WebUI, context-menu, and UI changes, plus a new file download priority feature

## Where the current contract still fragments

The problem is not that Resilio hides semantics.
The problem is that it still does not produce one first-class, case-scoped **verdict-legitimacy and adjudication-policy** object.

Today an operator can often infer only weaker truths such as:

- this surface currently shows a green check
- this warning currently links to a KB explanation
- this folder currently presents as one folder type rather than another
- this service instance currently sees an empty or different world
- this queue currently looks ordered or calm in one way even though the operative priority rule is more complex
- this version or installation path currently carries different upgrade or continuity caveats

Those are useful clues.
They are not the same as an explicit answer to `under which current rulebook, for which world, under which burden and threshold, by which authorized adjudicator, is the stronger sentence actually legitimate?`

## Why that matters for AnonSync

AnonSync needs a stronger sentence than `the trusted evidence looks good enough`.
It needs to support claims such as:

- the witnesses are trustworthy, but only enough for a warning-class sentence, not for still-governing closure
- the visible status is green, but the current burden only covers connected peers and named slice rather than the broader world
- the queue is visible, but queue order is not the same thing as operative priority under the current rulebook
- the rulebook that governs this case changed with product version, install mode, or world selection, so the older interpretation no longer controls
- the evidence would satisfy the threshold under one adjudication rule, but not under the current authorized rulebook
- the product can justify a narrow verdict for this world and audience, but the broader stronger sentence remains blocked

AnonSync therefore needs first-class objects for **current rulebook version, rulebook scope, authorized adjudicator, admitted and excluded evidence, sentence-specific burden class, threshold rule, tie-break rule, override state, highest honest verdict sentence, and blocked stronger sentence** rather than leaving operators to infer judgment legitimacy from a green icon, a KB article, queue appearance, service-world happenstance, or version folklore.

## Non-clone conclusion

Borrow the candor.
Do not clone the contract shape.

Resilio's current docs still answer the key question — `does this trusted witness set actually meet the current burden for this sentence?` — only by making the operator combine several partially overlapping mechanics:

- status semantics scoped to connected peers and visible folder state
- KB-linked warnings and troubleshooting branches
- folder-type semantics that change what one icon or path actually means
- service-user and storage-world shifts that change the observed world entirely
- version and update caveats that affect continuity and configuration meaning
- queue and priority behavior whose visible order is not always the actual operative order
- changelog memory about warning, UI, and feature semantics evolving over time

That diffusion is exactly what AnonSync should avoid.

## Design consequence for AnonSync

AnonSync should model **verdict legitimacy, burden, threshold, and rulebook version** directly.
Its interface family should let the product separate at least these truths:

- trusted witness, burden not yet chosen
- current rulebook ambiguous
- current rulebook chosen, threshold not met
- threshold met for named slice only
- threshold met but override or exception review still open
- adjudicator authority disputed
- threshold met under deprecated rulebook only
- verdict ratified under current rulebook
- broader stronger sentence blocked
