---
id: P-0250
title: LDAPv3 Interop & Schema/Control Conformance Kit — canonical operation traces + server capability matrices
status: idea
domains: [interop, directory, identity, protocols, testing]
last_reviewed: 2026-03-05
evidence:
  - https://datatracker.ietf.org/doc/html/rfc4511
  - https://crates.io/crates/ldap3
  - https://docs.rs/ldap3
---

## What it should provide others

An **LDAP interop lab** that makes directory integration testable and portable:

- **Canonical LDAP trace IR**: Bind/Search/Modify/etc. with normalized controls and result codes.
- **Capability matrices**: which servers support which controls, schema rules, and edge behaviors.
- **Evidence bundles**: `*.ldapbundle.zip` with sanitized traces + schema snapshots + replay tooling.

## Why this is still missing

Rust has a solid LDAP client (`ldap3`), but teams still struggle with:

- behavior differences across servers (OpenLDAP/389DS/AD variants),
- controls and schema quirks,
- diagnosing auth failures and referral/chasing issues.

RFC 4511 defines the protocol, but practical interop needs a harness and reproducible artifacts.

## Design outline

### 1) Canonical model

- operations (Bind, Search, Add, Modify, Delete, ModifyDN, Compare, Abandon, Extended)
- normalize:
  - DNs (RFC 4514 form when possible)
  - filters to a stable AST
  - controls to (OID, criticality, decoded/hashed value)
- time + sequencing for replay

### 2) Scenarios and profiles

- auth (simple, SASL hook points)
- referrals + paging
- subtree search behavior + size/time limits
- modify semantics and error codes

### 3) Evidence bundle (`ldapbundle`)

- `manifest.json` (server info, TLS, auth mode, redaction policy)
- `schema/` (subschemaSubentry snapshot where possible)
- `trace.ndjson` (canonical ops)
- `verdict.json` + `notes.md`

### 4) Adapters

- client adapter for `ldap3`
- optional packet-capture import path later (pcap → IR)

## Minimum lovable MVP (4–8 weeks)

1. Trace IR + bundle IO
2. 10–15 scenario suite (bind/search/modify + paging + referrals)
3. Compatibility report generator

## De-risk plan

- Build IR from `ldap3` high-level calls first.
- Add schema snapshot second.
- Delay packet-level parsing and complex SASL until after MVP.

## Scorecard (0–5)

- Impact: 3
- Neglectedness: 3
- Feasibility: 4
- Adoptability: 4
- Sustainability: 3
- Differentiation: 4
