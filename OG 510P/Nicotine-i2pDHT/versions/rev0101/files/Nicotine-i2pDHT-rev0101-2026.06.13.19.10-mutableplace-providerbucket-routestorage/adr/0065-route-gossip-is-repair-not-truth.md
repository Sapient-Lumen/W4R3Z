# ADR 0065 — route gossip is repair, not truth

Route gossip may help repair stale local contact memory, but it must not become a trusted address oracle. Contacts are selected through stale eviction, family caps, introducer-capture checks, and local history.

Status: accepted for rev0016 toy surface.
