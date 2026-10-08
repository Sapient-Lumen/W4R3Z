# Risk register rev0059

Open risks intentionally remain:

- no live I2P/SAM transport,
- no production DHT,
- no durable settlement database,
- no production attestation protocol,
- no production tombstone repair protocol,
- no global finality or mutable-head consensus,
- no global reputation,
- no private retrieval guarantee,
- no Sybil/anonymity guarantee,
- no Nicotine+ patch.

Newly tested risk surfaces:

- branch split between finality and settlement interpretations,
- retry-held settlement that drops dead-letter memory,
- duplicate or drifted attestation roles,
- tombstone resurrection pressure,
- terminal receipt replay and digest drift.
