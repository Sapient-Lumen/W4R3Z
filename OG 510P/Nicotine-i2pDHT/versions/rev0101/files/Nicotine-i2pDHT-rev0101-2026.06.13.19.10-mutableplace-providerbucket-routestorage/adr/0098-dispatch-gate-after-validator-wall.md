# ADR 0098 — dispatch gate after validator wall

A payload can be parse-safe, signed, semantically valid, namespace-allowed, and admitted while still lacking a safe handler target. Handler dispatch is a separate gate keyed by namespace, message kind, and payload role.

Status: accepted in rev0024.
