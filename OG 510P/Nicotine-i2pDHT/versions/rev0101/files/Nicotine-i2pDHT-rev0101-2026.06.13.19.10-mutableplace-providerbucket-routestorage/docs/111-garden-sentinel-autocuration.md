# Garden sentinel autocuration

`gardensentinel.py` is the new local scoring bridge. It consumes evidence from provider proof reports, witness mesh reports, and mutable-head lookup reports, then produces private sentinel scores.

The sentinel is explicitly **not global reputation**. It has no publication method. It does not make signed records invalid. It helps one local node decide whom to prefer, watch, back off, or quarantine.

## Event pressure

Positive events include:

- true provider proofs
- useful provider refusals
- diverse witness evidence
- accepted mutable-head reports

Negative events include:

- semantic provider lies
- witness contradictions
- insufficient-diversity witness pressure
- stale mutable heads
- same-sequence forks
- previous-link mismatches

The current scoring guess is intentionally asymmetric:

```text
semantic lies cost far more than slowness;
useful refusal is a small positive;
same-family positives are not enough for broad preference;
contradictions quarantine quickly.
```

## Garden-node philosophy preserved

Garden nodes give capacity, storage, bandwidth, witness memory, and refusal clarity. They do not become truth. A sentinel may prefer a garden locally, but that preference is not a consensus record.
