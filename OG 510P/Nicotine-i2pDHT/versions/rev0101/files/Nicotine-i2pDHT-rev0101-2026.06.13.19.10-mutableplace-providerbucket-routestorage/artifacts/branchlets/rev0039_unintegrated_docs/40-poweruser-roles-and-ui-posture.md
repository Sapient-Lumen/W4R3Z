# Power-user roles and UI posture

## Role hints, not authority

The DHT should allow users to contribute in visible ways without creating trusted supernodes.

Roles:

- **gate**: helps new nodes bootstrap;
- **scout**: maintains broader routing knowledge;
- **archivist**: stores records longer and accepts more sloppy/hot records;
- **sentinel**: spends budget on cross-checking and anomaly detection;
- **mirror**: caches hot immutable/provider records;
- **publisher**: runs high-volume region sweep queues.

Every role is voluntary, local, and revocable.  Other nodes can treat advertised roles as hints, never proof.

## Suggested user postures

```text
quiet_leaf          minimal metadata, mostly consume/read/watch
sticky_contributor  gate+scout, moderate storage and uptime
power_archivist     gate+scout+archivist+sentinel+mirror+publisher
lab_maximalist      high-leakage experimental mode for operators and testers
```

## Product guess

Power mode should feel like a contribution dashboard:

```text
DHT contribution: ON
I2P identity age: 37 days
Router uptime: 18h today
Routing contacts: 4,212
Provider records carried: 122,000
Mutable watches: 9,440
Sloppy hot-cache: 1.8 GiB
Sentinel checks: 612, 4 suspicious
Sweep queue: healthy, next region in 11m
```

This dashboard is not just UX.  It gives operators feedback, makes contribution sticky, and turns mysterious P2P behavior into inspectable local state.

## Python surface

`power.py` defines role/profile hints and capability tags.
