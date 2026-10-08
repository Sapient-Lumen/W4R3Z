# Executive summary

rev0007 keeps the cube DHT-first, but lets the distant legacy/Nicotine-shaped future push the entrance and governance design.

The strongest current guess is that a populated legacy P2P client network can become a **sovereignty seed ramp**: each willing client advertises a small signed contact card containing an I2P Destination, DHT public key, derived node id, capabilities, expiry, and bootstrap hints. While central/classic connectivity exists, it can distribute those cards through buddies, rooms, search hints, direct invites, and gardens. Over time, cached cards and garden seed gates reduce reliance on central entrances.

rev0007 adds three Python scaffolds:

```text
sovereignty.py   contact cards, entrance channels, I2P-only readiness, entrance cache
bridge.py        classic-client compatibility bridge planning
governance.py    scoped subjective key bans through signed policy capsules
```

The key social compromise is explicit: maintainers can sign policy capsules that ban keys from official seeds, public bridges, garden selection, or app defaults, but those capsules are local/app trust inputs. They do not make a valid DHT record cryptographically invalid, and users/forks can disable or replace them.

The cube still makes no production claims. It has no live I2P transport, no production DHT, no production bridge, no production moderation process, and no Nicotine+ patch.
