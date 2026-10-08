# Resilio freshness-claim, detection downgrade, and rescan ritual evaluation

## What current official docs still make clear

Another current Resilio pass again strengthens the main archive conclusion rather than weakening it.

Current official docs still show real product substance:

- a live v3 line with `3.1.2.1076`
- explicit admission that synchronization does **not** start from magic; it starts after file-change detection, indexing, and delivery work
- explicit admission that filesystem notifications are the fastest lane, but that some storages and path families do not support them well
- explicit admission that periodic folder scan is a real discovery mechanism, runs every 600 seconds by default, and also runs on Sync start
- explicit admission that the rescan interval can be changed, even to zero, which disables rescans even on restart
- explicit admission that Linux watcher exhaustion downgrades freshness to manual or periodic rescans until the limit is raised and Sync restarted
- explicit admission that a Windows-service UNC workaround can keep the path reachable while losing file-update notifications and falling back to rescan or restart
- explicit admission that `Some internal tasks are taking time to complete` may simply mean merge / scan / transfer / write work under load rather than a hard failure
- explicit admission that generic `My files don't sync` diagnosis still relies on checking status, history, queues, warnings, permissions, ignored files, notification loss, and sometimes restart / `touch` ritual

That is not fake candor.
It is very useful operator truth.

## What still should not be cloned

The ordinary operator answer is still fragmented.
Current docs still require cross-reading at least six places to answer four basic questions:

1. **What basis currently supports the claim that this subject is fresh?**
2. **Did real-time change detection quietly degrade into periodic or manual rediscovery?**
3. **What exactly will a rescan improve, and what will it definitely not fix?**
4. **Where is a newly changed file right now between local detection, indexing, publication, and remote availability?**

Resilio still has strong ideas here.
It still does **not** earn direct interface cloning.

The reason is the same clone-veto rule now applied to another seam:

> one ordinary operator question should have one stable page answer.

Current Resilio still spreads the ordinary freshness answer across the synchronization-start FAQ, power-user preferences, watcher-limit warning, service troubleshooting, internal-task warning, and generic no-sync checklist.
So the product idea stays strong while the page contract still fails.

## Why this matters for AnonSync

AnonSync should borrow four important habits directly:

- **say what freshness depends on**
- **say when live detection is gone**
- **say that rescan is real work, not a secret incantation**
- **say that busy merge/scan/write phases can be healthy without pretending they are already-done transfer**

But AnonSync should refuse four weaker habits:

- `starts syncing immediately` language that later depends on several caveat pages
- warning-first discovery of freshness downgrade
- restart / rescan folklore as the real explanation layer
- generic `not syncing` diagnosis that does not publish the active freshness basis and the next proof point

## Replacement pages added for this seam

This revision therefore adds four narrower replacement pages:

- `402` — Freshness basis
- `403` — Detection downgrade
- `404` — Rescan review
- `405` — Change publication

These pages keep the Resilio candor and reject the FAQ-plus-warning reconstruction path.

## Sharper non-clone line after this pass

The archive now has one tighter sentence for this seam:

> borrow Resilio's candor about notifications, rescans, and recoverable background work; refuse any interface contract where `is this actually fresh yet?` still depends on reading a FAQ, a warning article, a power-user table, a service workaround, and a generic troubleshooting page.
