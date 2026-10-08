
# Seed and policy portfolios as mutable heads

rev0008 promotes two concrete mutable-head families.

## Seed portfolio

A seed portfolio is a signed mutable record containing compact references to contact cards:

```text
seed_head = mutable(pubkey, salt="seed_portfolio:<label>")
value = {
  kind: seed_portfolio,
  label,
  seq,
  issued,
  expires,
  prev,
  entries: [
    { card_hash, node_id, channel, capabilities, issued, expires, weight }
  ]
}
```

It is intentionally not a universal phone book. It is a bootstrap portfolio. Clients should combine several portfolios and cached/direct contacts.

## Policy portfolio

A policy portfolio is a signed mutable record containing references to policy capsules:

```text
policy_head = mutable(pubkey, salt="policy_portfolio:<label>")
value = {
  kind: policy_portfolio,
  label,
  seq,
  issued,
  expires,
  prev,
  pointers: [
    { capsule_hash, authority_key, authority_name, seq, scope_hint }
  ]
}
```

The policy remains subjective. A client may subscribe to it for official defaults, bridge access, or garden service selection, but the DHT does not treat it as protocol truth.

## Portfolio diversity

A healthy seed portfolio should mix:

- direct invites;
- buddy/friend exchange;
- garden seed gates;
- cached last-good nodes;
- public/community seed heads;
- maybe central-side-loaded hints while central entrances still exist.

A single mutable seed head is useful but dangerous. A portfolio of heads is resilient.


## Size-budget rule

If the manifest is too large for the mutable value budget, the head stores a compact manifest digest and summary instead of inlining every entry.  This keeps the DHT head small while letting gardens/providers serve the larger signed manifest elsewhere.
