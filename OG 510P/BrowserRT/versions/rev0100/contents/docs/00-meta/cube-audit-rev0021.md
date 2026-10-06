# Cube audit rev0025

Revision: rev0028

This audit pass checks the cube after the priority/fairness slice and future-session handoff work.

## Findings

- The release tier remains browser-light by design.
- Browser/CDP probes remain available by explicit id, `browser`, or `full` tier.
- The new `scheduler:priority-fairness-proof` is Node-only and cheap enough for release.
- The new docs make non-claims and office-resume behavior harder to miss.
- The cube still avoids npm dependencies and external runtime assets.

## Cloudtainer caution

The project must continue to assume that long-running processes do not survive across turns. Future sessions should run `make turn-start`, then select narrow manifest ids instead of launching broad expensive suites.

## Current concern

The cube has many historical proof artifacts. Future sessions should not assume every historical browser proof was rerun during every package step. A proof is current only when its artifact revision matches the current cube and its non-claims remain intact.
