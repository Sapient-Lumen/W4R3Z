# Benchmark Plan

This runbook exists so future revisions do not hand-wave performance.

## Goals

Measure the tradeoffs between throughput, RAM, CPU, battery-ish behavior, and discovery noise across named profiles.

## First benchmark matrix

### Profiles
- desktop-balanced
- desktop-throughput
- mobile-tor-default
- mobile-tor-frugal
- nas-balanced

### File sets
- many tiny files: 100k files in the 1 KiB to 16 KiB range
- mixed office tree: documents, images, PDFs, archives
- large media set: 1 GiB to 20 GiB files
- pre-seeded tree: identical data on both sides before first connect
- placeholder-heavy mobile tree

### Transport scenarios
- Tor only, direct-ish success path
- Tor only, degraded / slower path
- I2P only via bundled `i2pd`
- mixed desktop peers with mobile Tor peer
- LAN discovery on with no peer found
- LAN discovery on with peers already satisfied

### Metrics
- time to first peer connection
- time to first file visible
- time to full sync
- peak RSS for main process and child runtimes
- sustained throughput
- hash/index CPU time
- beacon packets per minute
- battery-proxy signals on mobile testbeds if available

## Questions this runbook should answer

- what direct-send RAM cap is worth it?
- what piece sizes are best for Tor, I2P, and mixed mode?
- how quickly should discovery back off after peer health is established?
- when does a mobile-frugal profile stop feeling responsive?
- is SQLite mmap worth enabling for trusted local state on any class of device?

## Current benchmark ranges to test first

- piece size candidates: 256 KiB, 512 KiB, 1024 KiB
- small-file direct-send RAM cap: 64 MiB, 128 MiB, 256 MiB, 512 MiB
- steady-state LAN beacon cadence: 15 s, 30 s, 60 s, 120 s
- healthy-peer backoff ceiling: 120 s, 300 s, 600 s

## Rules

- record hardware class and storage class for every run
- separate cold-cache and warm-cache runs
- keep profile names stable across revisions
- update the project state when a benchmark result graduates into a design decision
