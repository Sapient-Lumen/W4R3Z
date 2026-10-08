# Terminal receipt after finality

A terminal receipt is a signed local observation made after the finality ledger
accepts terminal commit or terminal abort and the prune guard accepts terminal
soft prune.  It carries the finality report digest, accepted finality marker,
prune-guard digest, prune-plan digest, idempotency key, family, path family,
sequence, previous link, and time window.

The receipt rejects nonterminal finality, replay, same-sequence forks, previous
link mismatch, component-digest drift, hard-negative pressure, low family
diversity, and low path diversity.  It is not global finality and it is not a
network write.
