# ADR 0017: Garden nodes are giving supernodes

## Decision

Accept supernodes as a natural and useful DHT role, but define them as garden nodes: voluntary high-resource participants that give service capacity without protocol authority.

## Rationale

Anonymous overlays and file-sharing populations have uneven resources.  Some people want to donate bandwidth, disk, RAM, and uptime.  A DHT that cannot use those gifts will be weaker.  The risk is centralization through convenience, so all garden services must be optional, cross-checkable, and locally selected.

## Consequences

- Garden nodes can advertise service offers and budgets.
- Garden nodes can help bootstrap, reprovide, cache, steward mutable heads, and witness anomalies.
- Garden nodes cannot define truth, issue mandatory reputation, or become a required registration path.
- Future tests must simulate garden capture and overload.
