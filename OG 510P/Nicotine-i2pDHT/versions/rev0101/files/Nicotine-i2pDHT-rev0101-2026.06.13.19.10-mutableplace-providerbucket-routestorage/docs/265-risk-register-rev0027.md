# Risk register — rev0027

Still risky / unfinished:

- no durable database format, compaction journal, or crash-safe fsync story;
- deterministic fuzz fixtures are not real property-based fuzzing;
- refusal-loop pressure is local and toy, not a production garden scheduler;
- parseguard covers cube bencode fixtures only;
- branchlet merge preserves history but does not simplify the growing fold-module surface;
- no live I2P/SAM transport;
- no production DHT;
- no private retrieval guarantee;
- no global reputation;
- no Sybil/anonymity guarantee.

Next hard guesses:

- persist local evidence with a journal and crash-cut snapshots;
- generate malformed inputs rather than hand-listing them;
- connect refusal-loop state to garden scheduling and work-meter reports;
- collapse fold modules into a smaller revision-aware audit spine;
- begin a no-network SAM transcript harness that consumes the same canonical frames.
