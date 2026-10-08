# retention proof and hard-negative carry

Retention proof asks whether a compact closure seal still has the minimum evidence classes needed after restart.

Required classes currently include:

```text
closure seal
closure audit
archive journal
prune replay
contradiction memory, when the seal carried contradiction
redacted operator summary, by default
hard-negative memory, when hard-negative pressure exists
```

The lane treats evidence deletion as a side effect. A retained item can be parse-safe and digest-bound while still failing if it crosses scope, drops contradiction memory, drops live hard-negative memory, or comes from one family/path monoculture.

This keeps cleanup from laundering away the uncomfortable facts that caused the repair closure to be trustworthy in the first place.
