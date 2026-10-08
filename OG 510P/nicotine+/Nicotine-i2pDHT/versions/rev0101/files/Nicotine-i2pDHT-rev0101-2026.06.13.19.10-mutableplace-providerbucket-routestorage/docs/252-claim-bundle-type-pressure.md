# Claim bundle type pressure

Garden nodes and high-capacity peers will eventually want to send compact bundles of useful evidence. That is helpful and dangerous. A bundle can mix scopes, mix incompatible evidence, hide family monoculture, or pair a positive provider/custody claim with live tombstone evidence.

`claimbundle.py` treats a bundle as a signed observation container, not truth.

It checks:

- bundle signature and validity window;
- all evidence belongs to the bundle scope;
- source-family and path-family diversity;
- positive availability/custody evidence is not bundled with live tombstone or revocation evidence;
- same kind/sequence mutable evidence does not carry conflicting digests;
- item count stays bounded.

The model intentionally keeps role tags from `evidencegc.py` rather than flattening everything into a generic proof. That keeps negative evidence negative and positive availability merely positive, not authoritative.
