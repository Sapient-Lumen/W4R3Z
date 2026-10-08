# Peerbook and live-probe entrance pressure

A DHT over I2P needs sticky entrances, but address books are capture surfaces. rev0030 adds `peerbook.py` and `liveprobe.py` to model local acceptance pressure for cached contacts.

A peerbook observation contains a signed contact lease plus introducer/path/channel context. The assessment checks:

- fresh signed leases;
- destination/key/node-id binding through the contact lease;
- contact-family caps;
- introducer-family caps;
- purpose coverage such as `seed_gate` and `route`;
- optional SAM-shadow binding.

The unobvious failure is introducer capture: many contacts can look diverse while all arriving through one introducer family. rev0030 quarantines that shape.

`liveprobe.py` stays no-network by default. It can skip cleanly when no SAM router is present, and it can validate a streaming-first SAM shadow transcript against a persistent contact lease. Destination drift and invalid transcript ordering are quarantined.
