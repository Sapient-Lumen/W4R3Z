# Runtime dreambank 031 — admission histories need oracles

Current revision: rev0055

The dream remains that BrowserRT becomes a browser userspace kernel. The grounded move in rev0036 is narrower: if the runtime is going to coordinate admission, provider health, retry, circuit breakers, bulkheads, and storage lanes, future sessions need modelable histories before they spend browser or OPFS budget.

`StorageLaneAdmissionHistoryModelOracle` is the new rung. It does not try to be the scheduler, the storage lane, or the provider-resilience runner. It is a smaller reference model for the admission wrapper:

```txt
command history
  -> predict admission gate
  -> observe real row
  -> update model state
  -> compare real/model snapshot
```

The key ambition is that every heavyweight provider eventually gets:

```txt
source primitive + model oracle + generated history proof + contract audit + non-claims
```

This is how BrowserRT can remain ambitious without making mushy claims.
