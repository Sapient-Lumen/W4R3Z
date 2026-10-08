# Next revision pointer — rev0040

Suggested next codename:

```text
routerstop-sessionresume-exitjournal
```

Suggested focus:

- join service exit to SAM/router stop shadows;
- persist operator-intent and breaker state across restart;
- bind resume to service leases, public announcements, and relay tickets;
- add multi-service breaker interaction so one bulk service cannot trip protected control-plane services;
- reduce fold/audit duplication now that foldregistry and foldmap both carry similar current-path state.
