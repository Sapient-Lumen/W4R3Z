# What makes FreeBSD special (and why it compounds DeriveBSD)

DeriveBSD is **FreeBSD-first** on purpose. FreeBSD has primitives that make a Derive-style pipeline safer and cleaner.

## Unfair advantages

### 1) Jails (confinement as a native primitive)
**DeriveBSD gain:** “hermetic by default” becomes culturally and technically natural.

### 2) ZFS boot environments
**DeriveBSD gain:** system generations map to boot environments. Upgrades become *boringly safe* (atomic switch + instant rollback).

### 3) Base system coherence
**DeriveBSD gain:** model base as a pinned closure without fighting a thousand distro conventions.

### 4) Security primitives and culture
Capsicum/Casper, pf anchors, OpenBSM, etc.

**DeriveBSD gain:** enforce least privilege and composability at the system-module layer.

## Design rule

FreeBSD features should attach via stable interfaces:
- sandbox backend interface
- activation backend interface
- networking/firewall module interface

But v0 does **not** treat portability as a goal: the product is “Derive, on FreeBSD, done right.”

Last updated: 2026-02-23
