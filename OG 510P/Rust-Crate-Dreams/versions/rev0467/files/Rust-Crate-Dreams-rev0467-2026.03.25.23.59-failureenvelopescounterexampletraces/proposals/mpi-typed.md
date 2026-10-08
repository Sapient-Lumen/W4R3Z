---
id: P-0021
title: mpi-typed — safer, more ergonomic typed MPI on top of rsmpi
status: idea
domains: [hpc, distributed, safety]
last_reviewed: 2026-03-01
evidence:
  - https://github.com/rsmpi/rsmpi
  - https://docs.rs/mpi
  - https://arxiv.org/html/2509.10803v1
needs:
  - HPC teams want Rust’s type safety to reduce MPI type/tag mismatches without paying runtime overhead.
  - rsmpi is powerful but low-level; a “typed communicator” abstraction could become the default ergonomic layer.
  - A library that integrates well with arrays (ndarray/array-api) would unlock more scientific workloads.
risks:
  - MPI environments vary; must avoid overly opinionated runtime requirements.
  - Needs careful API design to preserve zero-cost abstractions and not regress performance.
---

# Problem

MPI is ubiquitous in HPC. Rust has bindings via rsmpi, but everyday MPI code still risks mismatched types, tags, and buffer assumptions. Research proposes typed abstractions to enforce stronger guarantees.

The “missing crate” is a polished, production-oriented typed layer that:
- Enforces type compatibility at compile time where possible,
- Keeps overhead low,
- Improves ergonomics for common patterns (collectives, scatter/gather, halo exchange).

# Users & user stories

- **HPC developers**: “I want typed send/recv where the compiler prevents mismatched payload types.”
- **Library authors**: “I want to write distributed algorithms that work over generic `T` with safe buffer handling.”
- **Scientific users**: “I want to ship arrays without hand-rolling unsafe conversions every time.”

# Prior art (and why it’s insufficient)

- rsmpi provides safe-ish wrappers, but many patterns still feel low-level and error-prone.
- Ad-hoc typed wrappers exist in projects but aren’t standardized.

# Design goals

- Typed communicator wrapper:
  - `TypedCommunicator<T>` where `T: Equivalence` (or safer derived).
- Safe message patterns:
  - point-to-point, collectives, and nonblocking operations with lifetimes that prevent use-after-free.
- Interop:
  - bridging with `ndarray` / future `array-api` (contiguous layouts, strides).
- Diagnostics:
  - better error contexts (rank, tag, datatype).

# Non-goals

- Implementing MPI itself.
- Providing an async runtime (though optional adapters are fine).

# Architecture & API sketch

**Crate layout**
- `mpi_typed` (library)
  - `datatype` module: safer derive for Equivalence-like mapping
  - `comm` module: typed communicators and groups
  - `collective` module: typed collectives
  - `buffers` module: safe buffer wrappers (slice, vec, pinned)

**API examples**
- `let world = mpi::initialize()?.world();`
- `let comm: TypedComm<MyType> = TypedComm::new(world.duplicate());`
- `comm.send(&payload, Rank(3), Tag(7))?;`
- `let x: Vec<MyType> = comm.recv(Rank(3), Tag(7))?;`

Nonblocking:
- `let req = comm.isend(&payload, Rank(3), Tag(7))?;`
- request type ties lifetime to payload to avoid drop-before-complete.

# Security / safety model

- Favor safe wrappers; isolate `unsafe` to small, audited modules.
- Provide “audit-friendly” code layout and doc’d invariants.

# Maintenance & governance plan

- Start with rsmpi as a dependency; keep optional features for ndarray.
- Provide benchmark suite comparing rsmpi vs mpi-typed overhead.

# Milestones

## 0.1
- Typed point-to-point send/recv + nonblocking API with safe lifetimes.
- Minimal derive helper for basic structs.

## 0.2
- Typed collectives (broadcast, reduce, allgather) for common `T`.
- ndarray contiguous array support.

## 0.3
- Halo exchange helpers + error context improvements.

## 1.0
- Stable API, performance validation, real-world examples.

# Open questions

- How to represent complex datatypes (struct-of-arrays, nested types) ergonomically?
- How to integrate with multi-threaded MPI configurations safely?

# Sources

- https://github.com/rsmpi/rsmpi
- https://docs.rs/mpi
- https://arxiv.org/html/2509.10803v1
