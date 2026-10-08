# Local evidence retention page: debug storage, expiry, and hidden artifact attestation interface spec

## Purpose

Operators need one ordinary answer to:

> what debug and crash artifacts currently exist on this node, where are they, how large are they, and when will they go away?

## Core decision

AnonSync should therefore model local evidence custody as a first-class **local evidence retention page**.

## Required sections

1. **Artifact inventory**
2. **Storage roots**
3. **Retention / rotation rules**
4. **Current footprint**
5. **Cleanup and attestation**

## Artifact inventory

Enumerate at least:

- active debug log
- rotated debug log(s)
- profiler traces
- crash dumps / mini dumps
- incident bundles prepared but unsent
- mobile-hidden evidence folders if applicable

## Storage roots

The page should distinguish:

- primary application storage
- service-account or alternate runtime storage
- mobile sandbox / hidden folder
- exported-copy location

Never make the operator infer that a different runtime principal implies a different evidence root.

## Retention / rotation rules

For each family show:

- time-based expiry
- size-based rotation
- manual cleanup requirement
- whether mobile / desktop parity differs

## Current footprint

Render:

- approximate bytes per family
- oldest/newest artifact time
- whether current capture is still writing
- whether retention policy is already clipping history

## Cleanup and attestation

Offer explicit actions:

- clear expired only
- clear selected family
- export before deletion
- attest `no local evidence remains in known storage roots`

Where attestation is partial, say exactly why.

## Anti-clone rule

Do not leave evidence custody spread across hidden folders, support articles, and folklore about service-account paths.
