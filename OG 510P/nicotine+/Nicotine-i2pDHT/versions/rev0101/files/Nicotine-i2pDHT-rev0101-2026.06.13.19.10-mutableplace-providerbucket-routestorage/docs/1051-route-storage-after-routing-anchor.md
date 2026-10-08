# Route storage after routing anchor

`routestorage.py` models local routing-table admission after a routing anchor accepts an I2P Destination/node binding.

It checks:

- routing anchor accepted
- lease is fresh and bucket purpose is allowed
- node ID remains Destination-bound
- endpoint remains an I2P Destination; raw IP/native-transport drift quarantines
- gardens and introducers cannot claim authority over routing truth
- full buckets go to stale-eviction probe or replacement cache rather than silent overwrite
- route gossip, contact lease, stale-contact, and witness memory are preserved
