# Revocation impact page: future updates, retained bytes, and successor paths interface spec

## Purpose

This page answers one ordinary question:

> if I revoke, disconnect, or downgrade this seat, what future motion stops, what already-arrived material remains, and what later cleanup or successor path is still separate?

The page exists because `revoke access` often sounds stronger than the product can honestly guarantee.

## Core decision

Every revoke, disconnect, or future-update cutoff action must pass through a first-class **Revocation impact** page.

## Fixed page order

1. revocation strip
2. future-motion cutoff card
3. retained-material card
4. downstream residue card
5. successor / cleanup paths card
6. revocation receipt rail

### 1) Revocation strip

Show:

- seat being changed
- current grant class
- requested resulting state
- strongest next-safe action

### 2) Future-motion cutoff card

Publish exactly what stops:

- future reads
- future writes back
- future arrivals
- future delegation
- admin mutation rights

### 3) Retained-material card

Publish exactly what remains after cutoff:

- bytes already present
- metadata or names already present
- local derivatives already present
- receipts or attestations already held

This card must also say what stronger erasure claim is forbidden.

### 4) Downstream residue card

Show whether revoking this seat affects:

- downstream derivatives
- already-issued artifacts
- linked sibling seats
- preserved local exports
- orphaned but still-held data

### 5) Successor / cleanup paths card

Show separate follow-on paths, such as:

- reclaim later by successor issuance
- request local cleanup proof
- preserve retained residue as evidence only
- no automatic remote deletion claim available

### 6) Revocation receipt rail

The page must emit and link a durable receipt containing:

- cutoff time
- rights removed
- rights retained
- retained-material warning
- follow-on path ceiling

## Rules

### Rule 1 — revoke must not imply erase unless erase is truly owned

`future updates stop` and `existing local bytes remain` must be publishable together.

### Rule 2 — retained residue is not silent

If local bytes, exports, or derivatives survive, the review must say so before commit.

### Rule 3 — successor paths stay separate from revocation itself

The product must not imply that downgrade, reconnect, remote cleanup, and successor issuance are one action.

## Acceptance criteria

A later operator can:

- tell what rights stopped at revocation time
- tell what material still remains with the former seat
- tell what downstream residues still exist
- tell which later cleanup or successor path would still be needed
