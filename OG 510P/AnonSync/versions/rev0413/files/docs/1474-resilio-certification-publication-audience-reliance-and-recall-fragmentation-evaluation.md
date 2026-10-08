# Resilio certification publication, audience reliance, and recall fragmentation evaluation

## Why this pass exists

The archive already knew how to:

- settle return-delta debt
- converge a cohort without lying about stragglers
- certify bounded estate scope with explicit exclusions
- publish freshness and revocation truth for the stronger estate sentence

What it still lacked was the next ordinary operator answer:

> now that we can certify something, who exactly may rely on that sentence, what exact version of the sentence is safe for each audience, and how do we supersede or recall that claim later?

That is the seam this pass locks.
A certification object is not self-executing.
It becomes operational only when it is **published for reliance**.

## Current official Resilio evidence that matters here

Current official Resilio docs still expose the raw ingredients an operator would use when trying to publish a trustable status update or handoff packet:

- `Sync Main View (Desktop)` still says the main UI exposes filter/search controls, a 30-day History lane, and settings/license details from the side menu. So ordinary operational truth is partly living in the UI.
- The same main-view article still says operators can enable or disable columns and inspect peer counts. So some audience-facing summary material already exists, but only as configurable UI state.
- `Collecting debug logs automatically` still says debug logging may be enabled from Preferences/Settings > Advanced, that Sync should be restarted to ensure logging is enabled, and that logs should collect for at least 15 minutes after reproducing the issue. That means some handoff-worthy evidence exists only after a staged capture ritual.
- `Collecting debug logs manually` still says technical support is available only for Sync Business customers and that Sync v3 users should instead rely on the forum and Help Center for functionality questions, with a separate web form for payments and licensing. So the correct destination for a packet already differs by audience and product posture.
- The same manual log article still says log paths vary across desktop, service, LocalService, Local System, Linux current-directory / storage-path, package installs, NAS, and Android. So a single `send the logs` instruction is not actually one stable publication lane.
- `Collecting crash reports, mini-dumps and core dumps` and `Where to collect logs on NAS?` still make crash and log artifact gathering platform-specific and support-lane-dependent. So not all evidence packets are created the same way.
- `Settings on mobile platforms` still documents a distinct Support section that links to Help Center articles, Sync Forum, and the contact-support form, and a distinct About section that shows the installed build/version. So mobile already separates support lane and build witness, but not as one unified reliance packet.
- `Running Sync in configuration mode` still says config mode is helpful for applying the same settings to many machines and that non-default `storage_path` creates new settings there. That means a handoff packet that ignores which world it came from can overclaim continuity.
- `Sync Private Identity & Linking My Devices` still warns against linking v2 and v3 devices because they may conflict on applied license and lose access to UI and share configuration. So even audience handoff across apparently related devices needs a version and world warning.

## What current Resilio still gets right

### 1) It exposes several real evidence planes

Main UI status, history, About/build/version surfaces, debug logs, crash artifacts, and support/contact routes are all real and worth borrowing.

### 2) It is candid that audience and lane matter

Business-support customers, Sync v3 self-serve users, desktop operators, mobile operators, and NAS operators do not all follow the same route.
That is important.

### 3) It preserves platform/world specificity

Service principals, config storage roots, NAS paths, and mobile settings all remind us that a published statement without world attribution can be misleading.

## Where current Resilio still fragments the operator answer

### A) There is no canonical publication object

Resilio gives the operator history, columns, logs, builds, crash dumps, forum routes, and support forms.
What it still does not give is one first-class object answering:

- which audience this packet is for
- which exact sentence that audience may rely on
- what exclusions and freshness ride with that sentence
- what evidence payload is attached versus merely referenced
- how supersession and recall will reach that audience later

### B) There is no explicit claim-envelope downgrade by audience

A working operator may be able to read nuanced status from the UI and support artifacts.
An executive, auditor, partner, or successor operator often cannot or should not receive the exact same envelope.
Current Resilio exposes the sources, but it still leaves the downgrade logic to operator folklore.

### C) There is no durable recall/supersession chain

The product exposes logs, builds, and support lanes, but not one durable answer to:

- which published statement is still current
- which newer packet supersedes an older one
- who has acknowledged the newer one
- what happens when an older forwarded screenshot or exported note keeps circulating after revocation

## Hard product decision unlocked by this pass

AnonSync should not let `estate certified` impersonate `safe for reliance by all audiences`.
It should promote any material publication of a stronger state claim into a first-class **reliance charter** that separately expresses:

- target audience
- safe claim envelope for that audience
- required inclusions and forbidden omissions
- freshness and supersession rule
- recall channel and acknowledgement state
- stronger blocked sentence that the packet must not imply

## Replacement line for AnonSync

Borrow from Resilio:

- candor that real evidence spans UI state, logs, builds, crash artifacts, and support lanes
- honesty that platform, world, and support posture matter to what a packet means
- separation of build/version witness from generic troubleshooting text

Do not clone from Resilio:

- any workflow where publication remains an improvised combination of screenshots, copied build strings, forum notes, and log attachments
- any contract where audience-specific claim downgrades are implicit rather than explicit
- any product shape where supersession and recall of earlier packets are tribal knowledge

AnonSync should instead ship explicit pages for:

- reliance charter contract sheet
- certification publication review
- reliance proof
- reliance timeline
- reliance lineage receipt
