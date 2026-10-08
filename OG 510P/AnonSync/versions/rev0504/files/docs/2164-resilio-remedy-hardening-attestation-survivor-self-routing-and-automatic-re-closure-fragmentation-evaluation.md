# Resilio remedy-hardening attestation survivor self-routing and automatic re-closure fragmentation evaluation

## Why this seam matters now

The archive can already say:

- a closure claim may remain honest only within a named durability horizon
- rediscovery surfaces and latent survivor classes can be listed explicitly
- rediscovery can reopen or narrow the sentence instead of being silently ignored
- late-survivor resurfacing is now part of the doctrine rather than an afterthought

That is still weaker than a harder question:

**if a stale survivor is rediscovered later, can that survivor surface itself route the finder to current truth and help the archive re-close, or does the finder hit a dead end, a detached copy, or an operator-dependent support ritual?**

Knowing that rediscovery reopens the claim is progress.
It is still weaker than making rediscovery itself a canonical correction path.

## Why current Resilio still leaves this too diffuse to clone

Current official Resilio material is candid about several reroute-shaped ingredients, but it still spreads them across separate pages:

- `Link structure and flow` says shared-folder links land on a Resilio page that shows only basic folder information, and the hash parameters are not actually sent to Resilio's server
- the same page says the landing page mainly hands off into Sync, replacing `https://` with `btsync://`, rather than providing one durable outsider-visible supersession object
- `Configuring WebUI` says adding shares by clicking the link or putting it in the browser address bar does not work with WebUI and instead requires manual `+` -> `Enter a key or link`
- `Setting custom name for sync shares` says custom names are UI-only, do not propagate to other peers or linked devices, and when changed during sharing the new name is only inserted in the generated link rather than becoming shared durable metadata
- `Sharing single file` says everyone with the link can download the files, there is no device- or use-count restriction, recipients can share the files further, and removing the transfer from Sync UI does not remove it from the device
- `Sharing a folder locally` says local shares stay attached only on the configured device, only pull from the parenting folder, disappear when the source share is removed, and do not automatically reconnect later

This is useful rediscovery-surface candor.
It is not yet one first-class answer to **if a stale survivor is found later, what on that survivor surface tells the finder it was superseded, where the current correction lives, and whether following the route is enough to restore closure?**

## The non-clone line

AnonSync should not clone a contract where all of these are allowed to blur together:

- the stale artifact can still be opened
- the stale artifact can still be reshared
- the stale artifact or link reaches only a generic landing page or manual app flow
- any richer explanation lives only in operator memory or local UI labels
- rerouting the finder to current truth depends on the right client, the right support ritual, or manual operator intervention
- closure therefore supposedly becomes durable again once the old thing was merely noticed

Those are separate truths.

## Product decision frozen in this tranche

This revision freezes a stronger line:

- **durable closure and late-survivor rediscovery truth are weaker than survivor self-routing and automatic re-closure**
- **a rediscovery invalidator is weaker than a rediscovery carrier that can identify itself as superseded**
- **operator-mediated reroute is weaker than survivor-carried reroute**
- **re-opened closure is weaker than re-closure that can occur on the rediscovery path itself**

## What AnonSync should model explicitly instead

AnonSync should add one first-class family for:

- resurfacing carrier class
- supersession-explanation carrier
- canonical reroute target
- required client and manual-step dependency
- re-closure trigger class
- strongest honest self-routing sentence
- blocked stronger self-routing sentence

## Interface consequence

That is why this tranche adds five more first-class pages:

- **survivor-reroute contract sheet**
- **survivor-reroute review**
- **survivor-reroute proof**
- **survivor-reroute timeline**
- **survivor-reroute lineage receipt**
