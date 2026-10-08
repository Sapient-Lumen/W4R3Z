# Resilio transport-profile, protocol-overlap, cipher-overlap, and bind-residue fragmentation evaluation

## Why this pass exists

The archive already had strong work on discovery, relay fallback, LAN-only posture, ingress mutation, and route exposure.
What the current revision chain still lacked was one tighter current Resilio pass about a more operational question:

> what transport lanes can these peers still actually use, what cryptographic overlap do they still share, and what happens when an allegedly pinned interface disappears?

Current official Resilio docs are useful here precisely because they are candid.
Today those docs still show that:

- `What ports and protocols are used by Sync?` still describes a staged transport story: config fetch, tracker, direct TCP/UDP over the listening port, relay fallback, and LAN multicast/broadcast discovery.
- that same current ports article still says LAN discovery uses multicast UDP `239.192.0.0:3838` and may also use broadcast, while automatic UPnP / NAT-PMP mapping uses separate router-facing packets.
- `Power user preferences` still publishes `tunnel_protocols`, explicitly saying peers must have **some common protocols configured** to connect.
- the same current power-user table still publishes `tunnel_ciphers`, again saying peers need **some common ciphers** to connect.
- `Power user preferences` still says `bind_interface` is operating-system dependent and that if the defined interface is unavailable Sync will switch to the **next active interface**.
- the same current page still says `use_only_bind_interface` blocks connection attempts unless the bound interface is available.
- `Power user preferences` still says `lan_encrypt_data` forces encryption for all Sync data flowing in LAN.
- `Sync Preferences` still says proxy servers prohibit incoming connections, and if **both** peers are behind proxies they will be able to talk **only via relay**.
- `Peers aren't connecting` still says the listening port, tracker reach, relay reach, and multiple-NIC routing all materially affect the actual tunnel established.
- `What is a Relay Server?` still says relay is the fallback when direct connection is not possible and that it is slower than direct.

That is a strong operator-truth corpus.
It is also a good reason not to clone the exact product contract.

## What current Resilio still gets right

### 1) It admits that transport is negotiated, not singular

Resilio still openly documents that a peer pair can move through several transport classes:

- tracker-mediated discovery
- direct TCP/UDP tunnel
- relay tunnel
- LAN multicast / broadcast discovery
- proxy-constrained egress-only posture

That honesty is worth borrowing.

### 2) It admits that `allowed` and `actually shared in common` are different truths

The current power-user table is refreshingly candid that protocol and cipher configuration only matter if peers still share some common overlap.
That is more honest than a flat `secure` or `advanced` badge.

### 3) It admits that interface pinning has residue and fallback behavior

Current docs still say a chosen interface can silently fall forward to the next active one unless `use_only_bind_interface` is also enforced.
That is a real contract truth, not an advanced footnote.

## Why AnonSync still should not clone it

### 1) One ordinary answer still spans too many articles

To answer `what transport lane is actually possible between these peers now?` the operator may still need to combine:

- ports and protocols
- power-user preferences
- sync preferences
- peers aren't connecting
- relay server
- sometimes LAN-only guidance

That is too much archaeology for one ordinary answer.

### 2) transport profile is still scattered between route, crypto, and bind knobs

Current Resilio docs keep these as separate surfaces:

- protocol set
- cipher set
- bind interface
- use-only-bind cutoff
- LAN encryption
- proxy asymmetry
- relay fallback

The product truth is one compiled transport profile.
AnonSync should not inherit the split.

### 3) `bound to interface` is still weaker than `will not fall forward`

Resilio's current docs still leave room for a weaker reality:

- an interface may be preferred
- a different active interface may be used instead
- only `use_only_bind_interface` makes disappearance a hard cutoff

AnonSync should surface that difference before commit, not after surprise reachability drift.

## Hard decisions now locked for AnonSync

1. **Transport profile is a first-class compiled object, not a bag of advanced toggles.**
2. **Configured protocol set, effective common protocol set, configured cipher set, and effective common cipher set are separate truths.**
3. **Interface preference is weaker than bind witness, and bind witness is weaker than hard cutoff.**
4. **Proxy-constrained egress, relay fallback, direct listener reach, and LAN-only discovery remain different route classes even when the same share is involved.**
5. **Every transport-affecting action needs one receipt that preserves protocol overlap, cipher overlap, bind residue, and the blocked stronger sentence.**

## Replacement page family

This pass therefore adds five more ordinary product-owned pages:

- **Transport profile contract sheet**
- **Protocol overlap review**
- **Bind witness review**
- **Transport hardening review**
- **Transport profile lineage receipt**

## Bottom line

Resilio's current docs deserve credit for admitting that transport class, common protocol overlap, common cipher overlap, interface-binding fallback, and proxy / relay posture are materially different.
But AnonSync should still refuse a contract where the operator must stitch together several articles to answer:

> what tunnel classes are still possible here, what overlap do these peers actually share, and what happens if the preferred interface disappears?
