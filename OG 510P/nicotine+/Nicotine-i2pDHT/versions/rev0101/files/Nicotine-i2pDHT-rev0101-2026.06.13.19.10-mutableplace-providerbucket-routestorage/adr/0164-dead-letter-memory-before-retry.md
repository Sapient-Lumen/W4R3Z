# ADR 0164 — Dead-letter memory before retry

Status: accepted in rev0057.

A prepared-only or ambiguous side effect must become signed local dead-letter memory before retry, cleanup, or reconciliation can reinterpret it.

Reason: without a sticky dead-letter lane, restart recovery can accidentally turn uncertainty into progress or trash.
