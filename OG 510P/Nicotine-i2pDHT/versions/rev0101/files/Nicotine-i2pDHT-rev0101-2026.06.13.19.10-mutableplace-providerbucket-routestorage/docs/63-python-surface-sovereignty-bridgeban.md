# Python surface — rev0007 sovereignty / bridgeban

New modules:

```text
sovereignty.py   signed contact cards, entrance channels, I2P-only readiness, entrance cache
bridge.py        classic-client bridge modes, operation planning, bridge guardrails
governance.py    subjective policy capsules and scoped key bans
```

New tests:

```text
tests/test_sovereignty_governance_bridge.py
```

## `sovereignty.py`

Models a `ContactCard`:

```text
destination
public_key
node_id
work_nonce
issued_at/expires_at
capabilities
context
bootstrap_hints
signature
```

It also models participation modes:

```text
off
classic_only
hybrid_entrance
i2p_only
garden
```

The important test surface is that node ids are recomputed from Destination/key/nonce and that I2P-only readiness depends on diverse, fresh, signed entrances.

## `governance.py`

Models `PolicyCapsule` and `BanEntry`.
A capsule is signed by an authority key and contains scoped entries:

```text
official_bootstrap
garden_service
classic_bridge
app_default_warn
app_default_ignore
dht_store_deny
```

The code treats these as local policy decisions.
It does not mutate DHT truth.

## `bridge.py`

Models bridge modes:

```text
off
localhost_compat_shim
private_invite_gateway
public_garden_gateway
```

And classic operations:

```text
login_compat
search
browse
peer_connect
chat_relay
provider_announce
```

The highest-risk operation is provider announce because it can poison the DHT.
The scaffold assumes public write surfaces need invites or explicit rate limits.

## Nonclaims

No real classic protocol parser.
No real I2P transport.
No real policy distribution.
No production moderation system.
No production bridge.
No legal or abuse-process recommendation.
