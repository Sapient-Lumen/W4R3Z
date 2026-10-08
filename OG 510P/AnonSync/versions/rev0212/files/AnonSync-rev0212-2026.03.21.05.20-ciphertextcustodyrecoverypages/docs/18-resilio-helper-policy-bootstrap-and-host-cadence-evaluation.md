# Resilio helper-policy, bootstrap, and host-cadence evaluation

## Purpose

The archive already has stronger answers for visibility, service role, state root, route evidence, egress-only posture, watcher pressure, and memory pressure.
What still remained under-specified was a more operational but still highly ordinary class of non-clone reason:

> current Resilio docs are reasonably honest about helper use and background activity, but the operator still has to reconstruct one coherent answer from folder preferences, global preferences, configuration mode, power-user keys, and troubleshooting pages.

This document tightens that line.
It does not argue that Resilio lacks route control or host-tuning power.
It argues that the power is still described in too many separate places to earn direct interface cloning.

## Bottom line

Resilio still deserves credit here.
Current official docs still show all of the following are real and useful:

- per-folder helper choices really exist: `Use relay server when required`, `Use tracker server`, `Search LAN`, and `Use predefined hosts`
- global proxy posture is explicit, including the fact that two peers behind proxies can end up relay-only while a single proxied peer can still connect directly to non-proxied peers
- vendor bootstrap is documented explicitly through `config.resilio.com/sync.conf`
- troubleshooting docs are candid that tracker reachability, listening-port reachability, multicast, multiple NIC routing, and proxy posture all materially change what path is possible
- background host cadence is also documented explicitly: filesystem notifications, periodic rescan, watcher exhaustion, config refresh/save cadence, and logging can all affect freshness or disk wakefulness

Those are good instincts.
But the same docs also show why AnonSync should not clone the page contracts.

## The four load-bearing non-clone seams in this pass

### 1) Helper policy is powerful, but still scattered across scope layers

Current official docs still say all of the following at once:

- folder preferences control relay use, tracker use, LAN search, and predefined hosts
- those preferences are desktop-only
- proxy posture is configured elsewhere, globally
- some LAN-only or no-Internet postures require changes in both share preferences and power-user/config settings
- troubleshooting then adds more route truth again through separate articles

That is real control.
It is still not one ordinary page answering the operator question:

> for this subject on this seat right now, what helper stack is actually in force after folder policy, seat policy, proxy posture, cache, and environment have all been combined?

### 2) Bootstrap/catalog truth is explicit, but still too article-shaped

Current official docs still say all of the following at once:

- Sync learns tracker and relay addresses from `config.resilio.com/sync.conf`
- inability to download that file blocks ordinary bootstrap
- LAN-only guidance may require config edits and then explicit cache clearing on each desktop
- known/predefined hosts can substitute for ordinary public helper discovery in some environments

That is useful honesty.
It is still not one ordinary page answering:

> what helper catalog did this seat actually use, what cache or learned residue still survives, and what private or local override displaced the default bootstrap path?

### 3) Pairwise helper dependence is reconstructable, but not one page

Current official docs still say all of the following at once:

- direct connection is preferred when possible
- relay is used when direct connection is not possible
- tracker helps peers learn one another's addresses and share IDs
- proxies can create asymmetric directness and, if both peers are behind proxies, relay inevitability
- multiple NICs, blocked listening ports, multicast failure, or blocked relay/tracker access all change what path is possible

That means route dependence is reconstructable.
It is not one ordinary page that proves:

- whether this subject/peer pair currently depends on tracker, relay, LAN multicast, predefined hosts, proxy egress, or cached endpoints
- whether relay is optional, probable, or inevitable
- what counterfactual would make the path direct, local-only, or blocked

### 4) Host cadence and quiet-host tuning are still support-lore shaped

Current official docs still say all of the following at once:

- filesystem notifications are fastest, but some storage classes or deep trees weaken them
- periodic folder scan runs every 600 seconds by default and can be changed, including to zero
- watcher exhaustion can force the system back to periodic rescan
- NAS sleep guidance recommends changing `folder_rescan_interval`, `config_refresh_interval`, and `config_save_interval`, and even disabling logging
- peer demand can still wake the host despite local quieting attempts

That is honest operational guidance.
It is still not one ordinary page answering:

> why is this host awake or quiet right now, which cadence knobs are active, what freshness cost did they buy, and which background behaviors still remain intentionally alive?

## Borrow / adapt / reject line for this pass

### Borrow directly

AnonSync should borrow these ideas without embarrassment:

- real helper-policy control instead of fake `auto` magic
- explicit documentation that proxies, relays, trackers, multicast, and known hosts change route possibilities in different ways
- explicit bootstrap/catalog disclosure instead of pretending helper discovery is mystical
- explicit admission that rescan/watcher/logging cadence affects host sleep and freshness

### Adapt instead of clone

AnonSync should adapt these families into stronger public pages:

- helper policy as one scope-aware page
- bootstrap source and cache residue as one page
- pairwise helper dependence as one route-dependence page
- host cadence and quiet-host posture as one freshness-versus-wakefulness page

### Refuse the clone line

AnonSync should not clone:

- route-helper meaning split between folder prefs, global prefs, power-user toggles, config JSON, and troubleshooting articles
- LAN-only or no-Internet recipes that require article-hopping and cache-clearing ritual without one policy page owning the result
- pairwise route dependence that must be inferred from relay icons, proxy notes, and failure articles
- NAS quieting or rescan tuning that still reads like support folklore instead of one explicit cadence contract

## Replacement pages AnonSync now owes

This pass therefore claims four more ordinary pages:

1. **Helper policy** — one page showing tracker, relay, LAN, proxy, known-host, and scope-stack truth
2. **Bootstrap source** — one page showing catalog origin, learned residue, cache state, and override source
3. **Helper dependence** — one page showing which helpers a given subject/peer pair actually needs now and which counterfactual would remove that dependence
4. **Host cadence** — one page showing notification coverage, rescan cadence, refresh/save cadence, logging wake cost, and quiet-host tradeoffs

## Result

The archive now has a sharper seventh-wave answer to `why aren't we cloning Resilio here either?`

The answer is no longer just `the knobs are hidden`.
It is also:

> because current Resilio still leaves too much ordinary operator meaning spread across separate policy scopes and troubleshooting pages whenever the user asks what helper stack is actually in force, what bootstrap source is active, which helpers a route really depends on, or what background cadence is keeping a host awake.

That is a solid reason to borrow the flexibility while replacing the page contracts.
