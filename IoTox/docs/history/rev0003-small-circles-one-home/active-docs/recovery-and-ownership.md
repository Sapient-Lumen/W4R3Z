# Recovery and ownership design

**Revision status:** accepted direction with a compiled `RecallRoot-v1` derivation contract; owner-key and Tox-key sub-derivation remain unimplemented design work.

## The decision

IoTox keeps a permanent printed and memorizable owner credential.

The credential is not an online password and there is no server-side password-reset ceremony. It is input to a fixed, versioned Argon2id key-derivation contract. The same canonical phrase must produce the same 32-byte recall root on every conforming implementation for as long as IoTox supports contract version 1.

This deliberately enables:

> A person who remembers the phrase can reproduce the owner root even after losing every controller, backup file, profile database, and vendor relationship.

It deliberately does **not** prevent an attacker who obtains or guesses the phrase from doing the same thing.

## Vocabulary

**Recall phrase**  
The eight-word printed and memorized bearer secret accepted by contract v1.

**Recall root**  
The 32-byte Argon2id output. It is never transmitted and should not ordinarily be displayed.

**Owner identity**  
A future application-level signing identity derived from the recall root under a separately frozen, domain-separated contract.

**Tox controller identity**  
A future Tox secret key and no-spam value derived from the recall root under a separate domain. It is a transport endpoint, not the authorization ledger itself.

**Device identity**  
A stable application-level identity belonging to a physical IoTox device. It is distinct from its replaceable route endpoints.

**Authorization ledger**  
Device-local records defining owner roots, controller keys, roles, capabilities, ownership epochs, and revocations.

## Frozen RecallRoot-v1 contract

| Field | Value |
|---|---|
| Contract ID | `iotox-recall-root-v1` |
| Phrase profile | exactly 8 uniformly selected words |
| Word list | pinned EFF long list, 7,776 entries |
| Canonical form | lowercase ASCII words joined by one ASCII space |
| Accepted punctuation | internal hyphen only, when present in the pinned list |
| Argon2 variant | Argon2id |
| Argon2 version | 19 / `0x13` |
| Memory | 65,536 KiB |
| Iterations | 3 |
| Lanes and threads | 4 |
| Salt bytes | ASCII `IoToxRecallRoot1` |
| Output | 32 bytes |
| Word-list SHA-256 | `addd35536511597a02fa0a9ff1e5284677b8883b83e986e43f15a3db996b903e` |

Eight independent selections from 7,776 entries provide approximately 103.4 bits of generation entropy. That claim applies only when the words are selected uniformly by dice or a cryptographically secure generator. It does not apply to eight words invented by a person.

## Why the fixed public salt is intentional

Ordinary password databases use a random per-record salt. RecallRoot-v1 has no record to retrieve: stateless reproduction is the feature. The v1 salt is therefore public, global, and part of the permanent contract.

Consequences:

- the same phrase produces the same recall root everywhere;
- attackers can test guesses offline;
- work for a guessed phrase can be amortized across users using the same contract;
- the contract cannot rely on rate limiting, account lockout, or a hidden server value;
- phrase entropy is structural and cannot be treated as a friendly recommendation.

Argon2id raises the resource cost of each guess. It does not transform a quotation, lyric, slogan, or human-created sentence into a strong root.

## Supported creation path

The initial product must generate the phrase. It should not invite the owner to make one up.

A conforming generator must:

1. use the pinned 7,776-entry list;
2. select eight indices independently and uniformly;
3. use an operating-system CSPRNG or physical five-dice method;
4. display and print the canonical words;
5. require a complete re-entry check before activating ownership;
6. make the bearer nature of the phrase unmistakable;
7. never send the phrase or recall root to an IoTox service.

Importing an existing v1 phrase is valid because re-entry is a core feature. Arbitrary custom phrases are not part of v1 creation.

## Intended re-entry flow

The desired recovery path is:

```text
remembered/printed phrase
        ↓ RecallRoot-v1
stable recall root
        ↓ domain-separated key contracts (not frozen yet)
owner signing identity + Tox controller identity
        ↓
recreated owner-side IoTox node
        ↓
devices reintroduce themselves and prove prior authorization
        ↓
controller roster is rebuilt from the devices
```

The new controller should not need a vendor-held inventory of devices. A device can retain:

- the owner's application public key;
- the owner's complete Tox address used for re-entry;
- its own owner-signed device certificate;
- the current ownership epoch;
- a policy for sending a bounded recovery knock or friend request.

A recovered controller can validate the presented device certificate using the owner key derived from memory, then reconstruct its local roster.

This sequence is still an experiment. Real c-toxcore behavior must establish whether a controller created from a secret key but without its old friend list can reliably receive and accept the required device-originated re-entry request. The two-node native fixture is the next place to prove or reject this mechanism.

## Tox savedata and deterministic re-entry

c-toxcore supports constructing an identity from a 32-byte Tox secret key through its savedata options. IoTox intends to derive a Tox controller secret deterministically rather than attempting to reproduce the opaque full savedata file from memory.

The full savedata remains useful for fast normal startup because it contains friend and network state. It is a cache and convenience state, not the sole representation of owner identity.

The exact subkey derivation is intentionally not frozen in rev0002. It must use a reviewed KDF and explicit domains such as owner signing, native Tox, Tor-routed Tox, I2P-routed Tox, no-spam, and local data protection. No raw recall-root bytes should be reused directly for multiple cryptographic purposes.

## Phrase compromise

Possession of the phrase is intended to reproduce owner authority. Therefore:

```text
phrase disclosure = owner-root compromise
```

There is no honest design in which the phrase remains a universal re-entry secret while a thief who has it is somehow unable to re-enter.

Mitigations concern prevention, detection, and deliberate transition—not denial of this fact:

- a physically protected printed card;
- memorization without casual digital copies;
- clear controller alerts when a new root-derived controller appears;
- audit events on every device;
- optional multi-controller approval for high-consequence capabilities;
- an owner-root transition protocol with monotonically increasing ownership epochs;
- route-specific transport identities where correlation matters;
- local physical interlocks for dangerous actions.

An owner who believes the phrase was exposed must be able to migrate devices to a new recall root and revoke the old ownership epoch. The old phrase is permanent only while the owner keeps that root active; no vendor can rotate it on the owner's behalf.

## Lost phrase

There is no vendor reset. Losing both memory and the printed phrase means the owner cannot reproduce that root.

A product may separately support a physical factory reset that erases prior ownership and user data. That is reclamation of the hardware, not recovery of the old owner identity. Whether a specific device class permits such reset is a product policy and physical-security decision.

## Stable identity and privacy

One stable Tox identity across native, Tor, and I2P routes improves re-entry simplicity but creates correlation. Separate route-specific Tox identities improve unlinkability but complicate device reintroduction.

The likely hierarchy is:

```text
Recall root
    ├── application owner identity
    ├── native Tox controller identity
    ├── Tor-routed Tox controller identity
    └── I2P-routed Tox controller identity
```

Devices would authorize the application owner identity and accept signed bindings to route endpoints. This remains planning until the KDF and binding formats are reviewed and frozen.

## Authorization remains independent of Tox

A Tox friendship is a transport relationship. The authorization ledger must separately express:

- owner;
- administrator;
- operator;
- viewer;
- automation controller;
- time-limited service role;
- per-capability grants;
- ownership epoch;
- revocation state.

The recall root is capable of rebuilding owner authority, but ordinary controllers should use delegated keys. The high-value root should not need to remain resident on every daily-use controller after delegation.

## What rev0002 proves

The C++ test facility now proves that:

- the pinned word list has exactly 7,776 ordered entries;
- v1 accepts exactly eight valid list words;
- ASCII case and whitespace canonicalize deterministically;
- foreign, short, malformed, and non-ASCII phrases fail closed;
- the Argon2 ABI is isolated behind a runtime adapter;
- the adapter sends the frozen version, memory, iteration, lane, salt, and output parameters;
- the real system `libargon2.so.1` produces the retained known-answer root;
- password copies used inside the adapter are explicitly wiped;
- IoTox-owned implementation and tests remain C++20.

It does not prove that the phrase-entry UI is safe, that compiler/runtime memory cannot retain copies, that the key hierarchy is correct, or that Tox re-entry without old friend savedata works. Those remain explicit work.
