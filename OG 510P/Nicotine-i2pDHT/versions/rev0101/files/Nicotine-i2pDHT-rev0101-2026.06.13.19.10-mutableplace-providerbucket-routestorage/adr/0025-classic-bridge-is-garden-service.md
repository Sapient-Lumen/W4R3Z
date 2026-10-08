# ADR 0025 — Classic-client bridge is a garden service

## Decision

Model compatibility with classic clients as an optional garden service, not as DHT authority.

## Rationale

Serving legacy clients helps migration and mutual aid.
But public bridges are abuse and metadata surfaces.
They need budgets, rate limits, policy capsules, and explicit labeling as translated gateway results.

## Consequences

- First bridge should be localhost/private before public.
- Provider-announcement writes should be invite-gated.
- Bridges can refuse keys according to subscribed policy capsules.
