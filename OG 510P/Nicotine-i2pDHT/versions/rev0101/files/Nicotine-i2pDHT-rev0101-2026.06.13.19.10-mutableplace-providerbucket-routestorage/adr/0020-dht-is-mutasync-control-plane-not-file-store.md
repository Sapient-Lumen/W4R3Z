# ADR-0020: The DHT is a mutable sync control plane, not a file store

## Decision

The DHT should store compact signed heads, provider records, service offers, and validation metadata.  It should not store arbitrary file contents or large sync manifests as mutable values.

## Rationale

Mutable sync wants stable live pointers.  The DHT is good at naming and finding those pointers.  Block exchange and large manifests are separate systems.

## Consequences

- Mutable DHT values remain small.
- Large manifests are content-addressed and fetched elsewhere.
- Garden nodes can cache encrypted blocks, but this is a service above provider records, not a required DHT storage behavior.
