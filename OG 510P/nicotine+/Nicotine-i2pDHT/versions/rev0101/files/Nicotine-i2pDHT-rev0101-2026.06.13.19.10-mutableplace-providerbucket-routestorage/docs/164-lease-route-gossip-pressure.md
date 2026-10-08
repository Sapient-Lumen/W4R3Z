# rev0019: lease-route gossip pressure

Route-gossip repairs are only useful when selected contacts are backed by fresh, route-purpose contact leases. This surface joins route-gossip repair with contact-lease freshness, monotonicity, and family coverage.

The risk under test is a beautiful route-gossip batch that looks close and fresh but was not authorized by the advertised nodes. rev0019 treats that as unleased selection pressure, not routing truth.
