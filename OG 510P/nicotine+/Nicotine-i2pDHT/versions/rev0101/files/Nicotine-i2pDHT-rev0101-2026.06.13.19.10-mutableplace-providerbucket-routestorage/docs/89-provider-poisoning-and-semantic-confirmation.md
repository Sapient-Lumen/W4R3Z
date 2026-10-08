# Provider poisoning and semantic confirmation

A provider record is a signed claim. It is not proof of possession, reachability, willingness, or current ability to serve.

rev0011 implements two related provider surfaces:

```text
providerpoison.py   -> challenge/receipt analysis for a batch of provider claims
provider_poison.py  -> local provider memory, useful-refusal backoff, and quarantine
```

## Challenge/receipt guess

The `providerpoison.py` path models a content-key challenge. Providers can answer with signed probe receipts:

```text
can_serve
cannot_serve
refused_gracefully
wrong_content
```

Analysis keeps these separate:

```text
valid signed record + can_serve           -> true provider evidence
valid signed record + cannot/wrong        -> false-provider pressure
valid signed record + graceful refusal    -> useful capacity signal, not availability
valid signed record + no probe            -> hint, not acceptance
bad signature / wrong challenge / expiry  -> invalid-proof pressure
```

The acceptance rule requires true-provider family diversity. Many confirmations from one garden/operator family are not enough.

## Local-memory guess

The `provider_poison.py` path records encounter memory:

```text
content_match       -> positive semantic evidence
content_mismatch    -> quarantine pressure
useful_refusal      -> bounded backoff, not punishment
unreachable/timeout -> soft availability pressure
bad_protocol        -> quarantine pressure after repetition
```

The strongest rule is:

```text
Semantic lies cost more than silence.
```

## Current open risk

Provider probing leaks interest. Future revisions need sampled/private probe variants, garden-assisted sentinel probing, and delegated reprovide so high-resource gardens can help without becoming replay loopholes or global reputation oracles.
