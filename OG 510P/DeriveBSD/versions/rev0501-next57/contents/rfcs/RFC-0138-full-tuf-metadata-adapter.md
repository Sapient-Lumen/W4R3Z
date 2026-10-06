# RFC-0138: Full TUF metadata adapter for channels

Status: **Draft**  
Last updated: 2026-02-24

## Problem

DeriveBSD uses TUF-inspired invariants for channel metadata (anti-rollback, anti-freeze, consistent snapshots).

But full TUF support has practical benefits:
- compatibility with existing TUF repos and tooling
- a mature delegation model for community repositories
- well-defined key rotation/threshold patterns

## Proposal

Add an **optional adapter lane** that can:

1) **Publish** a DeriveBSD channel as a standard TUF repository (root/timestamp/snapshot/targets + delegations).
2) **Ingest** a standard TUF repository and produce a DeriveBSD channel view.

This does not replace DeriveBSD trust policy; it provides interoperable “repository currentness + signature correctness” inputs.

## Scope

In-scope:
- translating Derive “channel views” to/from TUF roles
- optional delegation support for “ports-like” trees
- producing Derive evidence about TUF verification decisions

Out-of-scope:
- turning DeriveBSD into a general-purpose package manager
- binding store-path identity to TUF metadata (policy decides)

## References

- TUF spec (latest): https://theupdateframework.github.io/specification/latest/
- TUF security overview: https://theupdateframework.io/docs/security/
- Delegations overview (FAQ): https://theupdateframework.io/docs/faq/

## Rollout plan

1) Start with publish-only for a DeriveBSD channel (no delegations).
2) Add ingest-only path for upstream TUF repos.
3) Add delegations and role separation for community repos.

## Open questions

- does the adapter store TUF role files verbatim in the Derive store, or translate into a Derive-native channel format?
- how do we expose “limited mode” or offline update flows while keeping evidence intact?
