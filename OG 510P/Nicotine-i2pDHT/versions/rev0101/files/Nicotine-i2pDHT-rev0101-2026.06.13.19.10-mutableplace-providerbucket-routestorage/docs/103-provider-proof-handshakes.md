# Provider proof handshakes

Provider records should not be accepted as semantic truth. A provider may have signed an announcement and still fail the only thing the user cares about: serving the right bytes, at the right time, through a useful path.

## rev0013 shape

```text
ProviderAvailabilityClaim
  provider node id
  provider public key
  family id
  namespace
  content-key commitment
  expected content digest
  issued_at / ttl
  provider signature

ProviderProofChallenge
  challenger node id
  provider node id
  claim digest
  proof mode
  visibility mode
  nonce
  deadline
  challenger signature

ProviderProofResponse
  provider node id
  challenge digest
  response kind
  served digest
  proof-material digest
  retry-after, if refusing
  provider signature
```

## Why this matters

The DHT wants provider records because they are cheap and scalable. But cheap claims are poison if they become the stopping condition. The proof handshake makes semantic confirmation explicit and testable.

## Modes

`DIGEST_ECHO` is the lightest toy mode. `BLOCK_CHALLENGE` is the current main test mode. `MANIFEST_INCLUSION` is reserved for future sync/torrent-like manifests.

## Visibility

The challenge can be `COMMITMENT_ONLY` or `RAW_CONTENT_KEY`. Commitment-only challenge surfaces are preferred for witnessability, but some future protocols may spend raw-key exposure for stronger proof. rev0013 makes that a budgeted local decision, not a hidden leak.

## Useful refusal

A signed refusal with a bounded retry time is useful. It says the provider is alive but overloaded or temporarily unable to serve. That is different from lying, silence, or wrong content.

## Hard guess

```text
A provider proof transcript should be small enough to witness and cache,
but explicit enough to reject wrong-content claims and replayed challenges.
```
