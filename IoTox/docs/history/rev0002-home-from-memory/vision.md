# IoTox vision: Home From Memory

IoTox is intended to make physical devices feel like peers rather than rented endpoints in somebody else's account system.

The sentence that defines this revision is:

> From memory, you can reach your devices.

That is not a recovery afterthought. It is a product capability. An owner can reproduce a stable cryptographic root from a permanently printed and memorized phrase, rebuild an owner-side identity, and re-enter the device network without an IoTox account, vendor help desk, escrow key, or surviving local database.

## What “just werx” should feel like

A device should:

- boot into an identity it owns locally;
- connect through Tox without requiring a vendor cloud;
- remain operable with ordinary Unix process supervision;
- expose a small, inspectable local control surface;
- state failures explicitly instead of silently falling back;
- let an owner run the supporting infrastructure;
- keep working if the original vendor disappears.

Ratox is the inspiration for the surface: networking becomes ordinary I/O. IoTox adds the semantics that physical control requires underneath that surface: authorization, durable messages, deadlines, receipts, replay protection, transfer integrity, and recovery.

## Tox is part of the dream

Tox remains the primary peer transport. IoTox is not planning to replace it casually or treat it as an embarrassing dependency. Tox already demonstrates the difficult thing we value: self-owned identities connecting over a living peer network without a mandatory central account.

IoTox should contribute back where it can. That may include:

- public bootstrap capacity;
- public or owner-operated TCP relay capacity;
- reproducible server deployment tooling;
- test results and bug reports;
- focused fixes in c-toxcore;
- documentation for running useful network infrastructure;
- privacy-respecting health metrics that reveal service status without revealing users.

The network should be a commons that IoTox participates in, not a free resource the product merely consumes.

## Three Tox routes, one IoTox language

The intended first family remains:

```text
IoTox protocol
    over Tox/native
    over Tox/Tor
    over Tox/I2P
```

Only the native adapter exists today. Tor and I2P are reserved routes, not claims of working connectivity. Future direct Tor and direct I2P transports remain a different family and are deliberately out of the first build scope.

## No invisible owner above the owner

IoTox will not retain a manufacturer or vendor key that can reassign customer devices. Manufacturer attestation may prove what hardware was made; it must not grant the manufacturer ownership authority.

The owner recall phrase is the ultimate reproducible owner-side secret. The device authorization ledger—not the Tox friend list—defines who can do what.

## Simple outside, disciplined inside

The desired outside is small:

```text
pair
read
write
watch
copy
revoke
recover
```

The inside must remain explicit:

```text
identity hierarchy
fixed recovery contract
authorization ledger
ownership epochs
bounded queues
idempotency
deadlines
application receipts
route policy
atomic persistence
signed updates
observable failure
```

The simplicity is real only when the software does not hide uncertainty about whether a command was authorized, delivered, executed, or merely written to a pipe.
