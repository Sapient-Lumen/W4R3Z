# Scenario — Cargo build-dir layout v2 breaks target-dir spelunking

This scenario exists to keep **artifact route** separate from mere artifact existence.

The project’s release helper currently finds a built binary by walking Cargo’s internal build-dir / target-dir layout.
Cargo’s March 2026 build-dir-layout-v2 call-for-testing explicitly says many projects rely on unspecified build-dir details because Cargo is missing features they need.

The right lesson for P-0484 is not “Cargo broke us”.
It is:

- the route was **real**,
- the artifact still existed,
- but the discovery path was **brittle** and should have been classified as such.

A serious support-contract crate should therefore produce an `artifact-route.receipt.json` that makes the route visible, classifies its stability posture, and suggests a reviewer prefer stable Cargo message JSON or another documented interface when possible.
