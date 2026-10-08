# Rev1006 research note

This slice intentionally does not add a second worker, another persistence owner,
or a new network protocol. The durable staged-prefix journal already contained
the exact continuation authority. The implementation therefore schedules that
existing authority locally, preserving bounded SHA-256 work, rooted descriptor
reproof, writer leases, fair owner-loop progress, and final complete observation.

Open scale work remains: the 4 TiB proof requires 131,072 local pulses, source
manifest construction may still read a complete file in one owner call, and the
cross-file chunk index is not yet restart-durable.
