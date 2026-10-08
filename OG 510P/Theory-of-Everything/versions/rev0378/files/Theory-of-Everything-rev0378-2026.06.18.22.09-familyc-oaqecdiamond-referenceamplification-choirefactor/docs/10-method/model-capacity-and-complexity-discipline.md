# Model capacity and complexity discipline

This surface owns `OQ-0068` for fit, simplicity, parsimony, compression, and best-model language.

A candidate route may fit a record because it has learned, selected, tuned, truncated, compactified, reparametrized, or otherwise absorbed the record. That is not yet support. The route must first declare a model-capacity row and a complexity-penalty row.

Executable rule:

```text
fit + flexible family != support
fit + capacity declaration != promotion
fit + complexity penalty != closure
fit + holdout success != ToE identification
```

A capacity row asks what the route could have fit. A complexity row asks what penalty or cap is charged for that freedom. A route with unknown capacity remains capped at the most restrictive surviving route state.

Metadata/provenance rows are custody-only. They may improve replay and auditability, but they do not create physical simplicity, compression, or model capacity credit.
