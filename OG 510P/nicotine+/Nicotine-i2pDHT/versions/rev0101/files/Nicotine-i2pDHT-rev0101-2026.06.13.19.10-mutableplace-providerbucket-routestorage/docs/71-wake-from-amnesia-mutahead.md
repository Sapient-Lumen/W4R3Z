
# Wake-from-amnesia notes — rev0008

The cube is a DHT design lab above I2P. Nicotine remains a distant possible consumer, not the current center.

Current north star:

```text
small signed mutable heads + provider records + garden witnesses
```

rev0008 focused on open questions and mutability dreams. It added executable sketches for seed portfolios, policy portfolios, and local head observation analysis.

Important vocabulary:

- **seed portfolio**: a mutable list of contact-card references used for bootstrap diversity;
- **policy portfolio**: a mutable list of subjective policy capsule references;
- **head witness**: local/garden evidence about highest sequence, stale heads, and same-sequence forks;
- **garden node**: a giving supernode that provides capacity, not truth;
- **mutable control plane**: DHT heads that point to larger content-addressed or feed-based systems.

The deepest unresolved question: how to preserve mutability's gift — stable names that change — while preventing amnesia, rollback, capture, and accidental recentralization.
