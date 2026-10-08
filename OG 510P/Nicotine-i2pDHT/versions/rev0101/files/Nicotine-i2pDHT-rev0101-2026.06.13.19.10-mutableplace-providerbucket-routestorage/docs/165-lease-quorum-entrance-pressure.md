# Lease quorum entrance pressure

Contact leases make entrances fresh instead of immortal. A lease says a DHT key controls a Destination-bound node id for a limited window and purpose set. That still leaves an entrance-capture problem: many valid leases can arrive through one seed source, one garden family, or one path class.

`leasequorum.py` adds local pressure over observations:

```text
node-family diversity
source-family diversity
path-family diversity
purpose coverage
same-sequence contact-lease fork pressure
```

The word quorum is deliberately local. This is not consensus and not global identity truth. It is a bootstrap/route-repair pressure object that prevents one entrance source from being mistaken for a healthy DHT view.
