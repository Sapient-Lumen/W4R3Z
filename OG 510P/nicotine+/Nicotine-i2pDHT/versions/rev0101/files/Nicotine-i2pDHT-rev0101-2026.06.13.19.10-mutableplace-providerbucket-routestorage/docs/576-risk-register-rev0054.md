# Risk register — rev0054

Risks attacked:

- restart replay silently accepting stale component reports;
- handler traffic that almost passes repeatedly and burns metadata budget;
- useful-refusal loops laundering themselves into healthy service;
- adapter fuzz coverage treated as ephemeral test output;
- fold/registry drift hiding the current public-edge path.

Risks still open:

- no live I2P/SAM transport;
- no production DHT;
- no production persistence/database;
- no production handler dispatcher;
- no production fuzz engine;
- no private retrieval guarantee;
- no global reputation;
- no mutable-head consensus;
- no Sybil/anonymity guarantee.
