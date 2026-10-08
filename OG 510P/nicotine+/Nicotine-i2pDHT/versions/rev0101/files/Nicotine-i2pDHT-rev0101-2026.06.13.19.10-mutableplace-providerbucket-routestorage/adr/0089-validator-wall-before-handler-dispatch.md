# ADR 0089 — Validator wall before handler dispatch

Status: accepted in rev0022.

A signed frame is not enough.  The DHT will dispatch only after guarded parse, namespace checks, message-kind/payload-role binding, scope checks, digest checks, and request-id conflict pressure.
