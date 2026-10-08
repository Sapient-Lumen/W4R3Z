# Resilio publication-audience, redaction, and reliance-grade fragmentation evaluation

## Claim

Current official Resilio docs are still admirably candid that `peer identity`, `device name`, `owner`, `notification`, `history row`, `certificate-known peer`, `encrypted peer`, and `linked-device visibility` are not one flat publication truth.
That candor is useful.
It is also exactly why AnonSync should not clone the present contract.

The missing product object is now sharper than deadline integrity:

> after the product knows **which typed act happened and whether its timing is trustworthy**, it still needs one first-class answer to **who is allowed to see which version of that act, with what redactions, and whether that viewer may rely on it for an operational, fairness, or adjudicative decision**.

Current Resilio materials still do not provide one typed publication object for:

- internal-only observations that are useful for operators but not publishable to outside parties
- participant-visible facts that remain too raw or partial for decision-grade reliance
- redacted external summaries that conceal sensitive actor or evidence details
- different viewer classes such as owner, affected participant, linked device, outside reviewer, and untrusted encrypted host
- the difference between `visible in a UI surface` and `safe to rely on as a decision sentence`
- retracted or superseded views whose operational trace remains real but whose reliance grade must narrow
- publication lineage showing why a given viewer saw this exact version and not a stronger one

Instead, the operator still has to translate peer lists, owner columns, bell notifications, history rows, linked-device visibility, and encrypted-node caveats into publication meaning.

## What current official docs still say

Current official docs still jointly show all of the following:

- `What's the difference between Standard and Advanced folders?` still says Advanced folders use certificates, can distinguish new and old peers, and can reflect user identity in the peer list, while Standard folders do not reflect user identity and instead show peer details and device names separately.
- `Sync Private Identity & Linking My Devices` still says peers recognize you by the name you choose and that when devices are linked, all folders become visible and accessible on all linked devices.
- `User Management` still says only Owners can invite new users, that different permissions can be issued to different peers, and that all linked devices under one identity act as Owners.
- `Sync Main View (Desktop)` still says the bell lights up for approval requests or other notifications and that History shows general syncing activity for the last 30 days.
- `Resilio Sync change log` still says notifications can synchronize across linked devices, that notifications exist for permission and licensing changes, that history became searchable and sortable, and that optional columns like `Owner` and `Last transferred` were added.
- `Encrypted folders` still says an encrypted peer can hold and seed data on an untrusted device without revealing readable contents.

This is strong operational candor.
It is not a first-class publication-and-reliance contract.

## Why this still fragments the decisive answer

One ordinary fairness answer still requires stitching together several docs and surfaces:

- which audiences can see the same event at all
- whether they see actor identity, only device identity, or only encrypted presence
- whether a notification is merely operational awareness or a decision-grade publication
- whether a history row is general activity trace or a durable relied-upon sentence
- whether a linked device is seeing something because it is the same principal, because it is merely a convenience mirror, or because it is a separately entitled viewer
- whether a redacted view still supports local action, external reliance, or only background awareness
- whether an encrypted or otherwise untrusted node may store bytes but may not rely on their semantic meaning

That means current official materials can help answer `who can sync this`, `who appears in the peer list`, `why did this bell light up`, or `why can an untrusted node store encrypted data?`
They still do not directly answer `who may see this exact fairness sentence, at what redaction level, and what reliance class is honest for that viewer right now?`

That gap is exactly where AnonSync should refuse cloning.

## Hard replacement line for AnonSync

AnonSync should borrow the useful ingredients:

- explicit identity distinctions between user and device where available
- visible owner and permission asymmetries
- synchronized notifications where that helps multi-device continuity
- searchable trace surfaces for operational follow-up
- explicit encrypted / unreadable storage mode for untrusted infrastructure

But AnonSync should replace the page contract with a first-class **publication audience and reliance grade** object where each typed act has its own:

- authorized audience classes
- redaction profile
- semantic fidelity class
- permitted reliance class
- supersession / retraction rule
- viewer-specific blocked stronger sentence
- publication lineage receipt

## Product decision tightened here

The new design line is:

- **visible fact is weaker than publishable claim**
- **publishable claim is weaker than reliance-grade publication**
- **internal, participant-visible, redacted external, public summary, and adjudicator-grade views are separate public truths**
- **viewer eligibility, redaction scope, and reliance permission must stay separate even when the bytes shown look similar**
- **an encrypted or otherwise untrusted host may hold durable state without receiving semantic reliance rights**

## Consequence for the non-clone score

Resilio still belongs on the borrow side for identity candor, owner asymmetry, notification continuity, searchable traces, and encrypted-host honesty.
Resilio remains on the non-clone side for the fairness-critical publication contract.

The reason is now precise:

> current Resilio docs still expose identity surfaces, owner columns, peer-list differences, bell notifications, searchable history, linked-device visibility, and encrypted-host unreadability as separate operational facts rather than one typed publication object for `internal`, `participant`, `redacted`, `public`, `adjudicator`, `retracted`, and `superseded` reliance states, so the operator still has to reconstruct who may rely on what from scattered traces instead of one owned interface family.
