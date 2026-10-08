# Mutable namespace-policy epoch heads

rev0023 made namespace policies local dispatch safety. rev0024 adds the missing mutability surface: how does a node learn that a namespace policy advanced without turning the DHT into global governance?

The implemented guess is `PolicyEpochHead`:

```text
namespace
policy_digest
epoch
previous_head_digest
purpose
issued_at / expires_at
authority_public_key
signature
```

Acceptance is local:

```text
signature-valid + time-live + policy-digest-bound + family-diverse + monotonic + previous-link-valid
```

The tests cover genesis acceptance, linked advance, rollback rejection, same-epoch fork quarantine, previous-link mismatch quarantine, digest mismatch, family monoculture, and “accept with watch” when a node sees a plausible epoch but lacks earlier local history.

This is not a banlist or governance system. It is a way for a local node to follow a chosen policy head without accepting a stale or forked pointer merely because it is signed.
