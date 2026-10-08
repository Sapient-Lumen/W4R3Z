# rev0041 — routerstop-sessionresume-exitjournal

rev0041 moves the cube into the boundary after a service exit decision has been accepted.

The dangerous false assumption is:

```text
service exit accepted
  therefore router/session side effects are safe
  therefore future resume is safe
  therefore local restart memory can be trusted
```

rev0041 makes those three separate control-plane surfaces:

- `routerstop.py`: no-network router/session stop shadows after service exit;
- `sessionresume.py`: joined resume gates across exit, breaker, lease, announcement, relay, router-session, and hard-negative signals;
- `exitjournal.py`: append-only signed local restart memory for operator/service-exit/router/resume facts;
- `controlfold.py`: current-revision audit preserving rev0040 operationsfold as predecessor history.

The core sentence:

```text
Stopping, retaining, or resuming a router-backed garden service is a protocol boundary, not cleanup.
```

This is still pure Python lab work. No live I2P/SAM socket is opened and no bundled i2pd process is started.
