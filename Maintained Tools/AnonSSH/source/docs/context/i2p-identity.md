# I2P Identity Contract

This document covers compatibility-critical destination derivation only. RouterInfo
bootstrap selection and product router ownership are documented in the
[README](../../README.md#i2p-bootstrap) and [architecture](architecture.md#i2p-bootstrap).

AnonSSH v1 deterministically emits a standard 384-byte Destination body with an
EdDSA-SHA512-Ed25519 signing key and a type-0 encryption field, followed by a key
certificate and the corresponding private-key material expected by SAM. This byte
layout is compatibility-critical because changing any byte changes the `.b32.i2p`
destination.

Bond router-pool destinations are separate from that primary v1 identity. A nonzero
32-bit slot is encoded in network byte order after the `i2p-bond-router-v1` derivation
label, producing a slot seed from the v1 master seed; the normal I2P identity derivation
then operates on that seed. Slot zero is invalid. Slot numbers are compatibility
material and must not be silently renumbered after endpoint descriptors are published.

The I2P common-structures specification states that the 256-byte ElGamal public-key
field is unused for Destinations, even though it remains the type-0 compatibility
layout. Current LeaseSet encryption is selected and managed by the router. Do not
replace the v1 layout merely to modernize that field; introduce a versioned identity
protocol and migration plan if evidence requires a different Destination format.

Primary references:

- <https://i2p.net/en/docs/specs/common-structures/#publickey>
- <https://i2p.net/en/docs/specs/common-structures/#key-certificates>
- <https://github.com/PurpleI2P/i2pd_docs_en/blob/master/docs/user-guide/tunnels.md#leaseset>
