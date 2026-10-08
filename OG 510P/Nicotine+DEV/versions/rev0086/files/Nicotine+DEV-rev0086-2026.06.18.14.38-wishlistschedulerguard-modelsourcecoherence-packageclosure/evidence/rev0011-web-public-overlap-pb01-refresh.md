# rev0011 web/public-overlap refresh — PB-01

## Search intent

Determine whether PB-01 duplicates a public Nicotine+ issue/PR/advisory, and separate direct public overlap from adjacent protocol/connection context.

## Captured result

No direct public report was found for the combined invariant:

```text
direct PeerInit replacement of an established primary
+ queued-message migration
+ secondary P/D/F promotion after post-init data
+ PierceFireWall secondary route into the promotion behavior
```

## Public/upstream-adjacent material

- Official protocol docs define P/F/D peer-init messages, modern direct/indirect connection order, `PeerInit` with token zero today, obsolete `SendConnectToken`, and the expectation of a single active peer/distributed connection.
- 3.3.11 RC release notes mention broad related hardening: spoofed-user uploads, peers sometimes being told our username is theirs, and distributed-search fixes.
- GitHub issue #3631 is symptom-adjacent because it shows connection-init timing logs, but it does not report direct replacement or secondary promotion.
- GitHub discussion #1772 is compatibility-adjacent because it shows maintainer caution around protocol changes and PeerInit/PierceFireWall-adjacent extension ideas.

## Classification

`candidate-no-direct-public-match-found, public/upstream-adjacent`.

This is not a novelty proof. It means the cube has not found a direct public duplicate yet, and any external wording must remain cautious.
