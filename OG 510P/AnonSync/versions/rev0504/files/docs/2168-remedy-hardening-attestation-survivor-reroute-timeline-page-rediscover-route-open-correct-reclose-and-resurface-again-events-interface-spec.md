# Remedy-hardening-attestation survivor-reroute timeline page — rediscover, route, open, correct, re-close, and resurface-again events

## Purpose

This page makes survivor self-routing legible over time.
It exists so the archive can show not only that a survivor resurfaced, but whether the rediscovery path itself led the finder to current truth and restored closure.

## Timeline events the page must support

The page must support at least:

- stale survivor first declared latent
- durable-closure claim issued
- rediscovery carrier annotated with reroute target
- late survivor rediscovered
- supersession explanation shown
- reroute followed successfully
- reroute failed or dead-ended
- manual operator assist invoked
- corrected replacement opened
- closure re-opened
- closure re-closed for finder
- survivor resurfaced again through another carrier

## Event requirements

Each event row must preserve:

- timestamp or bounded time window
- actor / finder class / carrier
- event class
- reroute target if any
- whether the event strengthened, narrowed, contradicted, reopened, or re-closed the claim
- whether the strongest honest sentence changed

## Self-routing rule

The timeline must not allow `rediscovery self-routed and re-closed` unless it also records:

- the carrier that resurfaced
- the supersession explanation actually available on that carrier or adjacent to it
- the target reached
- whether operator help was needed
- the stronger sentence still blocked anyway

## Visual emphasis

The page should visually distinguish:

- latent-survivor setup events
- rediscovery events
- route-success events
- route-failure / dead-end events
- operator-assist events
- re-closure events
