# Risk register — rev0064

Risks attacked:

- retry publication treating settlement as send permission;
- idempotency key reuse hiding duplicate delivery;
- late ACK + retry delivered contradiction becoming compacted away;
- remote witness monoculture choosing repair state;
- payload/key drift across otherwise accepted components.

Nonclaims remain: no live I2P/SAM transport, no production DHT, no production retry publication protocol, no production remote witness protocol, no global reputation, no mutable-head consensus, no Sybil/anonymity guarantee.
