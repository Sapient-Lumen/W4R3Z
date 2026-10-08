# Next revision pointer — rev0050

Suggested rev0051 focus:

```text
commitledger-publishadapter-durabilityfuzz
```

Possible work:

- model durable commit ledgers across restart after outbox drain;
- create a no-network publication adapter seam that consumes SAM canaries;
- fuzz idempotency/sequence/previous-link state across drain, canary, journal, and commit ledger;
- continue fold-registry consolidation so branchlet history is mapped, not hidden.
