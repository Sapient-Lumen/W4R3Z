# Router-stop shadow boundary

`routerstop.py` models future I2P/router side effects without performing them.

It separates:

- stop only this service session;
- stop the bundled router;
- keep the router running for cover/contribution;
- disable public bridge exposure;
- enter an offline profile.

The risky cases are pinned first:

- stopping a public bridge without a drain report;
- stopping a bundled router while using an ephemeral Destination;
- quietly setting `notransit` while claiming to keep the router running;
- accepting a router action before the service exit report has accepted;
- replaying, rolling back, or forking stop plans.

A router-stop plan is a signed observation. It is not a side effect.
