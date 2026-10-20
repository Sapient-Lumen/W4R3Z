# IoTox vision

## North star

> From memory, you can reach your devices.

IoTox is for physical things that belong to their owner rather than to an account
system. A device should keep its identity, local function, and owner-defined peer
relationships without requiring an IoTox cloud. The owner should be able to reconstruct
the owner side from a permanent generated phrase, replace controllers, operate their
own infrastructure, and keep using the product if IoTox disappears.

## Product feeling

Ratox supplies the aesthetic standard: complicated peer networking should feel like
ordinary local I/O. IoTox should be inspectable, scriptable, exportable, and small at
the surface.

```text
pair
read
write
watch
copy
revoke
recover
```

The inside may be rigorous, but it must not leak needless ceremony into ordinary use.
It also must not lie: writing a byte is not the same as durable acceptance, authorization,
execution, or completion.

## Four promises

### The owner can come home

RecallRoot-v1 is a permanent, public Argon2id contract for an eight-word generated
phrase. It deliberately trades offline guessability for stateless re-entry. There is
no vendor reset key and no secret IoTox account database that outranks the owner.

### Tox carries the roads

Tox remains the primary network because it already does the difficult connection work.
IoTox should measure it honestly, contribute useful bootstrap and relay capacity, and
help strengthen the commons it depends upon.

Native Tox comes first. Tor-routed and I2P-routed Tox remain explicit future paths.
Direct Tor and I2P transports are separate later experiments.

### Authority stays above connectivity

Tox friendship is not ownership. IoTox will maintain an authorization ledger for owner
roots, delegated controllers, capabilities, expiry, epochs, namespace membership, and
revocation. Transport keys may rotate without silently rewriting device authority.

### Trusted things may carry selected state for one another

The Milehigh Small Circles contribution adds a second dream: authorized devices can
form bounded namespace-specific circles, gossip small signed heads, and retain selected
immutable objects through deterministic custodians.

This is optional. A smart plug should not need a distributed object system. A household
hub, cameras, controllers, phones, and NAS may benefit from one when sharing selected
state without a vendor cloud.

## What a mature system could look like

A device boots with a local identity. The owner physically claims it. Daily controllers
receive delegated authority rather than the permanent root. Commands and state travel
through Tox with application signatures, expiry, replay protection, and durable results.
A home hub may queue work while phones sleep, but the hub remains replaceable and
owner-operated.

Selected namespaces can have different membership:

```text
home/config:       owner controllers, hub, thermostat
camera/archive:    cameras, NAS, selected backup custodian
workshop/sensors:  workshop nodes and one controller
family/shared:     explicitly authorized personal devices
```

Each namespace forms only the application relationships it needs. Custodians can retain
encrypted objects without automatically gaining read or control authority.

## Things IoTox refuses to require

- an IoTox account;
- a vendor-controlled cloud for ordinary operation;
- a vendor key capable of taking ownership;
- a public blockchain or token;
- one global chatroom or full mesh for all data;
- silent native fallback after Tor or I2P was requested;
- permanent dependence on one proprietary controller application;
- pretending research code has passed network or cryptographic gates it has not passed.

## If the full product never happens

The work can still be worthwhile. The project should leave behind buildable datacubes,
not vapor:

- a reusable C++ toxcore boundary and test facility;
- safer persistence and concurrency patterns;
- Tox infrastructure tooling and upstream contributions;
- a documented owner-recall experiment;
- an authorization-ledger design;
- the Small Circles topology and replication simulator;
- a useful ratox successor even without every future layer.

A side project is allowed to be ambitious and uncertain. The discipline is to make
each revision honest, inspectable, tested, and salvageable.

## Current sentence

IoTox is becoming:

> a small, self-owned device network in which a remembered phrase lets the owner find
> home again, Tox supplies the roads, IoTox supplies authority, ratox supplies the
> simplicity, and optional small circles let trusted devices carry selected state for
> one another.
