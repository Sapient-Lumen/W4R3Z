# RFC-0077: Ports/pkg adapter lane (bootstrap breadth)

- Status: draft
- Author(s):
- Created: 2026-02-23
- Last updated: 2026-02-23

## Summary

Define a compatibility lane that imports ports/pkg ecosystems into DeriveBSD plans while enforcing sandboxing and recording impurities.

## Motivation

DeriveBSD needs early breadth without inheriting nondeterminism permanently.

Poudriere shows an effective pattern: build packages in jails with pinned inputs.

## Goals / Non-goals

Goals:
- pin ports snapshot + distfiles
- translate build options into plan fields
- run under Derive sandbox policy
- emit closure proofs and provenance like native builds

Non-goals:
- permanently treating ports metadata as authoritative

## Proposal

- Importer takes:
  - ports tree snapshot id
  - selected ports + options
  - toolchain id

- Produces:
  - Lock inputs
  - Plan build steps
  - “impurity report” object (time/network/env)

## Alternatives considered

- rewrite everything as native specs immediately

## Backwards compatibility

Additive.

## Security considerations

- deny network inside build jail by default
- treat ports infrastructure as untrusted; verify distfiles

## Open questions

- best representation of ports options in Plan
- how to model pkg repo publishing as a channel
