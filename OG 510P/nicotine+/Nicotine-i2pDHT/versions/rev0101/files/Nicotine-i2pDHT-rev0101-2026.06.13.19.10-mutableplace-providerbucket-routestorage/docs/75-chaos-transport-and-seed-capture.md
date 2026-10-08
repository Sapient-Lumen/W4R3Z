# Chaos transport and seed capture

`chaos.py` is the first fake transport surface for riskiest DHT guesses. It deliberately does not connect to I2P. It makes adversarial lookup transcripts cheap and deterministic.

## Fake replica behaviors

```text
honest      -> returns newest local record
stale       -> returns oldest local record
fork        -> returns all local records at highest sequence
silent      -> returns no records, modeled as timeout
lie_empty   -> claims the target is empty
```

A `FakeAsyncLookupHarness` sorts replies by delay and feeds observations into `MutableHeadMemory`. If a stale or forked reply is observed, it emits witness receipts.

## Why fake first

Live transport would be seductive but low-signal right now. The hard design risks are not socket syntax. They are:

- how many stale replies are tolerated;
- whether lookup should stop early;
- whether same-sequence forks are sticky evidence;
- how gardens witness without becoming authorities;
- whether seed portfolios are too captured by one path or actor family.

Those risks need deterministic transcripts before live network noise.

## Seed capture

`assess_seed_capture()` looks at a seed portfolio and reports:

```text
total entries
captured entries
captured weight
total weight
channel diversity
garden entries
capture ratio
risk reason
```

This is not an oracle. It is a pressure gauge. A portfolio can be risky because too much weight belongs to known attacker nodes, because it has too few entrance channels, or because it has too few garden entrances.

## Current seed-portfolio guess

A resilient entrance portfolio should blend:

```text
cached last-good contacts
direct invites
buddy exchange
room/social hints
central-side leaked contacts while central still exists
garden seed gates
public seed heads
```

No one channel should dominate the default I2P-only starting portfolio.

## Next simulator pressure

The next chaos step should model path families, not just replicas. If three replicas all came from one captured seed channel, their apparent quorum should count less than three replies from unrelated channels.
