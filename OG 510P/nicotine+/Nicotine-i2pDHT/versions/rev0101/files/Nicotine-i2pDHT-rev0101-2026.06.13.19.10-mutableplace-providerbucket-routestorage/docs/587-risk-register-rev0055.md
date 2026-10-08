# Risk register — rev0055

New risks exercised:

- crash cut after prepare but before commit/abort;
- restart memory that replays an old cut or seal;
- side-effect phase drift between journal and restart observations;
- handler quench cooldown hidden behind an otherwise accepted seal;
- fuzz compaction that drops required mutation evidence;
- fuzz compaction that preserves only watch/hold instead of quarantine;
- final effect seal with component digest drift.

Still open:

- no live SAM/I2P behavior;
- no production database/journal;
- no production fuzz engine;
- no global reputation or mutable-head consensus;
- no Sybil/anonymity guarantee.
