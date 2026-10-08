# rev0045 — bridgeepoch-keyreceipt-shadowfire

This revision moves the public bridge question from a Boolean into an epoch boundary.

A garden can launch, pass a firewall, and satisfy subjective policy, but a public bridge can still become dangerous later: stale announcements can keep routing users to a closed bridge, an operator-key succession can be half-known, and local receipt memory can be replayed across restart. rev0045 makes those seams executable in Python before live I2P/SAM side effects exist.

New surfaces:

- `bridgeepoch.py` — signed public bridge open/renew/close/withdraw epochs.
- `keyreceiptlane.py` — operator/key authority receipts tied to the public bridge boundary.
- `shadowfire.py` — joined gate across bridge epochs, key receipts, subjective policy, authority receipts, and announcement repair.
- `bridgeepochfold.py` — current revision audit/refactor fold preserving rev0044 branch-seal predecessor history.

Strong sentence: **public bridge state is not current because one component says so; it is current only when epoch, key authority, policy, receipts, and repair agree at the same boundary.**

Nonclaims remain: no live I2P/SAM transport, no production DHT, no production bridge protocol, no global reputation, no mutable-head consensus, no Sybil/anonymity guarantee, and no Nicotine+ patch.
