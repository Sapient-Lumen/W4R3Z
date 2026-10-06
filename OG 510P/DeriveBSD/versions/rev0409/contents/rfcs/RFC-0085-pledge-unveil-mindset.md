# RFC-0085: Pledge/unveil mindset for low-friction sandboxing

Status: Draft

## Summary

Adopt the *ergonomics* lesson from OpenBSD pledge/unveil: make least-authority restrictions easy to apply widely.

Reference: pledge/unveil paper (BSDCan 2018). https://www.openbsd.org/papers/BeckPledgeUnveilBSDCan2018.pdf

## Goals

- Named, reviewable sandbox profiles.
- Descriptor-oriented “preopen then restrict” workflows.
- Policy-bound exceptions.

## Design sketch

- Define a library + CLI helpers to apply profiles to:
  - jail services
  - fetchers
  - long-running daemons
- Prefer Capsicum capability mode and filesystem-by-construction (mount allowlists).

See: `docs/117-pledge-unveil-mindset.md`.
