# Remedy-hardening-attestation egress-governance timeline page — link issue, approval, forward, expiry, and externalization events

## Purpose

This page is the chronological spine for how the material crossed governance boundaries and how later revocation or closure attempts interacted with that history.
It exists to preserve the difference between issuing a lane, approving a recipient, enabling onward-sharing, expiring future access, and proving nothing about already externalized copies.

## Event classes

The timeline must support at least these event classes:

- share lane created
- share lane delivered
- approval rule changed
- direct recipient approved
- linked-family trust widened
- owner or reshare authority granted
- standard-key lane observed
- single-file link issued
- link configured to never expire
- link expired for new pulls
- manual relay outside product custody observed
- downstream holder confirmed
- onward-sharing suspected
- revocation attempt opened
- future access blocked
- named recipients notified
- global sentence downgraded
- global sentence ceiling acknowledged
- off-world closure evidence added
- permanent unknowability blocker receipted

## Required timeline columns

Every event row must print at least:

- event timestamp
- actor or subsystem
- event class
- affected lane or cohort
- prior off-world ceiling class
- resulting off-world ceiling class
- evidence attached
- whether the event widened spread, narrowed spread, or only changed future access

## Required chronology guarantees

The timeline must preserve:

- whether bytes could have been delivered before approval rules tightened
- whether onward-sharing rights existed before later revocation
- whether link expiry happened after a long open-access window
- whether recipient accounting happened before or after irreversible externalization
- whether a case was ever overstated globally before the off-world ceiling was acknowledged
- whether later evidence named more recipients without actually proving universal closure

## Required timeline summaries

The page must compute and print:

- first known governance-boundary crossing time
- first time onward-sharing became possible
- latest time a historically open lane could accept new pulls
- first time the current strongest global sentence became speakable
- latest time broader global language was explicitly blocked

## Blocking rules

The timeline must never flatten:

- lane issue into byte delivery
- approval into recipient enumeration
- expiry into recall
- revocation into off-world deletion
- named-recipient contact into downstream-tree closure
- governed cleanup into global forgetting
