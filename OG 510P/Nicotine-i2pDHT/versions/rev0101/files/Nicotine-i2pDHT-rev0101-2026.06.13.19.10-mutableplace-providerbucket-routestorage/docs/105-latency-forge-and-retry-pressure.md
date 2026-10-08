# Latency forge and retry pressure

I2P latency, churn, and useful refusal should shape the DHT before live SAM transport exists. Otherwise the first real transport implementation will accidentally decide security policy.

## rev0013 additions

`latencyforge.py` creates deterministic fake endpoints with states:

```text
ok
slow
refusing
timeout
lying
```

and events:

```text
send
response_ok
response_refusal
response_lie
timeout
retry
```

The forge can accept a lookup when enough path families respond, continue when the fast window is captured, or fail when retry budget is exhausted.

## Useful refusal

A useful refusal counts as reachable capacity when policy permits it. This preserves the garden-node idea: a generous node that says “not now, retry later” should be treated very differently from a lying or silent node.

## Hard guess

```text
Retry policy is part of the DHT’s trust surface.
Fastest response must not automatically become best response.
```
