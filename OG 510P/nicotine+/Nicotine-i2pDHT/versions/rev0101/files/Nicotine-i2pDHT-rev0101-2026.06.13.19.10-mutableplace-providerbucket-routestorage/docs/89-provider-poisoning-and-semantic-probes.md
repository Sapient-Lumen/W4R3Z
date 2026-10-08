# Provider poisoning and semantic probes

A signed provider record says:

```text
this key signed a claim that this node provides this content key
```

It does **not** say:

```text
the provider is reachable
the provider is honest
the provider still has the data
the provider can prove the keyed material
the lookup path was not captured
```

This revision starts implementing that distinction.

## Storage admission guess

Direct provider publication is accepted:

```text
transport sender node id == provider_node_id
provider signature verifies
record not expired
```

Naked third-party replay is rejected for now:

```text
valid signed record + different sender + no delegation => reject
```

The reason is not that reprovide is bad. Garden/bulk reprovide is likely essential. The reason is that reprovide must become an explicit delegated capability, not an accidental replay loophole.

## Retrieval guess

Provider retrieval produces observations, not truth:

```text
verified            -> semantic provider
unprobed            -> hint
unreachable         -> soft failure
refused gracefully  -> capacity signal
semantic mismatch   -> poison
invalid response    -> poison
invalid signature   -> poison/invalid record
```

The report keeps:

```text
accepted_provider_count
verified_family_count
semantic_lie_count
invalid_record_count
graceful_refusal_count
unprobed_claim_count
needs_more_paths
```

A clean acceptance currently requires at least one verified provider and at least two verified path families. If any semantic lie appears, the lookup remains pressure-positive and should continue or cross-check.

## Why this is risk-first

Provider poisoning is a cheap denial route. A captured region can return many provider-looking answers and cause a naive client to stop. The lab rule is:

```text
do not stop merely because provider-looking records arrived
```

## Hard next tests

- Challenge-response provider probes tied to provider public keys.
- Retrieval receipts that prove a provider served a block or manifest root.
- Delegated garden reprovide capability validation.
- Provider tombstones and withdrawal heads.
- Probe privacy: confirming a provider leaks interest unless batched or proxied.
