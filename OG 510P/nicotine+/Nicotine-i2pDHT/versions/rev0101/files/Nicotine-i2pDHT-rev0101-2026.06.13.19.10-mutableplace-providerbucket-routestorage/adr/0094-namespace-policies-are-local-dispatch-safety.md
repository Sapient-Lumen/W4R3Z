# ADR 0094 — Namespace policies are local dispatch safety

Accepted for rev0023.

A generic DHT needs per-namespace validators. rev0023 models signed namespace policies as local dispatch safety, not global governance. A node chooses which authorities/policies to load; valid policy signatures do not create universal truth.
