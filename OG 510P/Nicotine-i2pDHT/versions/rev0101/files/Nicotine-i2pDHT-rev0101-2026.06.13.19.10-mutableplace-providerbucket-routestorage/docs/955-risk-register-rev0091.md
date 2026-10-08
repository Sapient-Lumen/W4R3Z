# Risk register — rev0091

Risks explored:

- Relaunch evidence accidentally becoming dispatch permission.
- Python fallback memory being dropped during native reconsideration.
- Parser/crypto/transport/persistence authority leaking into native leaves.
- Restart rediscovery treating a previously held candidate as fresh.
- Native branch audit sprawl hiding a missing predecessor.

Current answer: quarantine hard, journal the route, and keep Python as oracle.
