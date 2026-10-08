# rev0066 — repairpublish-ackclosure-duplicatefinality

rev0066 moves one boundary past rev0065.  A remote duplicate conflict can now be witnessed, staged into a repair outbox, and cooled down; this revision asks what happens before that staged repair becomes a public side effect and before any ACK of that repair becomes local finality.

The working guess is:

> A staged repair is not publish permission; an ACKed repair is not duplicate finality until contradiction memory survives the join.

New surfaces:

- `repairpublishgate.py` gates repair publication after repair outbox and conflict cooldown agree.
- `repairackledger.py` records ACK/NACK/absence observations for the repair publication itself.
- `duplicateclosure.py` joins remote witness, repair outbox, cooldown, repair publish, and repair ACK into local closure.
- `repairpublishfold.py` audits the current path and keeps rev0065 predecessor history visible.

Nonclaims remain unchanged: no live I2P/SAM transport, no production DHT, no production repair publication protocol, no production remote ACK protocol, no global reputation, no mutable-head consensus, no private retrieval guarantee, no Sybil/anonymity guarantee, and no Nicotine+ patch.
