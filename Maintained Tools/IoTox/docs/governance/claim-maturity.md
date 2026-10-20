# Claim maturity vocabulary

Use the narrowest label supported by retained evidence.

| Label | Required evidence |
|---|---|
| idea | prose only |
| planned | ordered work and acceptance criteria |
| compiled | compiler and linker success in a named environment |
| unit-verified | deterministic direct tests |
| adapter-verified | external boundary tested against an exact double |
| binary-verified | separate built processes complete an end-to-end fixture |
| network-verified | real implementations communicate over a named network fixture |
| route-verified | route containment and leak behavior measured |
| target-verified | intended hardware and operating conditions measured |
| production | support, update, security, legal, and operational acceptance |

A component can have multiple qualified claims. For example:

```text
local control protocol: unit-verified
local daemon/client lifecycle: binary-verified over mock toxcore
Tox/native: network-verified for the retained founding-host normal-native and TCP-only fixtures
Tox/Tor: route-verified for bounded single- and two-IoTox actual-Tor samples, including exact sync-carrier attribution, immutable-object failover, detached-terminal explicit resume across external process loss, and continuous-process Ratox circuit churn; anonymity and diversity remain unclaimed
actual-Tor Ratox circuit-churn soak: route-verified on one host/date across two public relay records, with both Tor transition labels and both same-epoch continuity/explicit-resume outcomes; exit/time diversity, anonymity, and an SLA remain unclaimed
adversarial local SOCKS boundary: adapter-verified for exact chained attribution and held-byte release; live Tor/Ratox route qualification pending
```

Never use “implemented” alone when the maturity boundary matters.
