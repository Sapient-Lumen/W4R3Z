# Resilio identity-action, subject-fate, and mobile-delete asymmetry evaluation

## Why this pass exists

The archive already had strong doctrine for seat lineage, identity replacement, severance ladders, and mobile storage.
What it still lacked was one direct evaluation for a sharper seam:

> when a product says `unlink`, `rename identity`, `link this running install`, or `uninstall`, is it describing credential housekeeping, or hiding a subject-class and platform-specific local-fate contract?

Current official Resilio docs make that seam much sharper than a generic `identity changes have side effects` story.
Across current linking, identity-rename, and uninstall docs they still say all of the following:

- Linking two devices that are already running Sync can cause one device to lose its certificate and take over the certificate of the other.
- When that happens, Advanced folders on the acquiring device are removed from the app and new folders from the other instance are copied.
- On iOS, those Advanced folders are not only removed from the app; they are also deleted from the file system because of platform architecture.
- Renaming identity is not a label edit; the current FAQ still says it requires unlinking the current identity and creating a new one so a new certificate is generated.
- That same rename FAQ still says Advanced folders are removed from the instance, Standard folders remain in the instance, and folders remain in the system except on iOS and Windows Phone devices.
- Current uninstall guidance still says operators should unlink from identity first and then remove the remaining Standard shares.
- That same uninstall guidance still says uninstall on iOS and Windows Phone removes synced files from the device because of platform architecture, while desktop uninstall generally does not delete previously shared folders from the file system.
- Current official Sync v3 docs still show the live line through `3.1.2.1076`.

That is strong candor.
It is also a very good reason not to clone the verb contract.

## What Resilio gets right

### 1) It admits that identity verbs are not purely abstract

Current docs do not pretend that identity work is only cosmetic.
They still admit that linking, unlinking, renaming, and uninstalling can affect real local subjects.
That is worth borrowing.

### 2) It admits that subject classes do not all survive the same way

The current rename and uninstall docs are especially useful because they do not flatten Advanced and Standard folders into one fate sentence.
They still distinguish different local outcomes.
That is the right instinct.

### 3) It admits that platform architecture changes byte survival

Current iOS and Windows Phone caveats still say local byte survival is not universal.
That honesty is important.
A weaker product would hide the mobile delete cliff until after the action.

### 4) It admits that uninstall and unlink are not the same housekeeping story

Current uninstall guidance still prescribes an identity action first and a share-removal action second.
That sequencing implicitly admits that different verbs cut different parts of continuity.

## Why this is still a strong reason not to clone them

The ordinary operator answer is still too fragmented.
Current official docs still force too much reconstruction before the product fully owns these questions:

- is this verb only changing identity lineage, or also evicting local subjects from app governance?
- which local subject classes survive differently here?
- are bytes staying on disk, disappearing from the app only, or being deleted because of platform architecture?
- is the safer next move to preserve first, branch first, use another seat, or proceed now?
- what later receipt proves the actual local fate after the action?

That should not require stitching together linking docs, an identity FAQ, and uninstall guidance.

## The tighter AnonSync conclusion

AnonSync should borrow the following from current Resilio more boldly:

- explicit candor that identity verbs can have real local consequences
- explicit candor that subject classes do not all survive the same action the same way
- explicit candor that platform architecture changes the honest byte-survival sentence
- explicit candor that some identity actions should be sequenced with preserve/remove work rather than treated as one abstract account operation

But AnonSync should refuse the exact verb contract whenever one ordinary answer still depends on several articles.
The product should not let `unlink`, `rename`, `link`, or `uninstall` stand without one owned surface that states:

- requested identity verb
- affected subject classes
- app-removal effect
- local-byte survival by platform
- preserve-first alternatives
- strongest safe sentence and stronger forbidden sentence

## Replacement pages added for this seam

This pass therefore adds four more page-shaped obligations:

1. **Identity-action review** — what verb is being attempted, what subject classes it changes, and what local-byte fate follows here.
2. **Subject-fate matrix** — what survives in app governance, what stays on disk, and what is deleted on this platform.
3. **Preserve-before-identity-action** — what safer export / branch / alternate-seat sequence is available before a destructive identity verb.
4. **Identity-action receipt** — what later proves the requested verb, actual subject fallout, platform basis, and follow-up obligations.

## Bottom line

The tighter no-clone reason is now this:

> Resilio is current evidence that identity verbs have real operator consequences and should be described honestly; it is also current evidence that one account-looking action can still hide subject-class fallout and platform delete cliffs. AnonSync should copy the candor and refuse the overloaded housekeeping contract.
