
# ADR 0028: Mutability is the control plane and civilization layer

Status: accepted-for-rev0008-guessing

Decision: treat mutable heads as the DHT's central high-value primitive, not as a side feature.

Reason: mutable heads can support seed portfolios, policy portfolios, garden catalogs, sync rosters, software updates, mutable torrents, and transparency checkpoints while keeping bulk data outside the DHT.

Nonclaim: this does not make any mutable head globally truthful.
