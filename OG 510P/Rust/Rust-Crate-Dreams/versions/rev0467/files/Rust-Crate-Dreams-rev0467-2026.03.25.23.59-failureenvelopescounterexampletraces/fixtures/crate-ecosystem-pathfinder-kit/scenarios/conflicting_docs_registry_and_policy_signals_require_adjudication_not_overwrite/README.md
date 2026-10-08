# conflicting docs, registry, and policy signals require adjudication, not overwrite

This scenario proves that a worthy Pathfinder first release should not respond to new public visibility or trust signals by silently replacing an older frozen answer.

## Situation

A team previously froze a starter set for an air-gapped + mixed-native environment.
Later they observe:
- a new release with a recent `pubtime`,
- stronger docs.rs visibility on the `latest` route,
- Trusted Publishing enabled,
- and better-looking public support posture.

However:
- the old winner still better satisfies local offline/native/source-parity constraints,
- the new public signals came from different routes than the frozen basis,
- and some support claims are visible only on hosted/default-target docs routes.

## What the workbench should do

- import the prior decision pack and basis lock,
- import the new public-surface packets,
- classify the disagreements,
- keep route identity visible,
- record one adjudication session,
- and emit one carry-forward receipt saying that the old choice still stands for the old task profile while a narrower recheck remains open.

## What it should not do

- silently replace the frozen winner,
- silently flatten `latest` docs routes into the old basis,
- or treat Trusted Publishing / Security posture as automatic task-fit authority.
