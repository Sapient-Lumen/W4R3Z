# ADR 0153 — service breaker before resume

Decision: a service that tripped open must half-open or close only under diverse recovery evidence.

Reason: false service, refusal-only loops, active withdrawal, or hard negatives should not be erased by one convenient success.

Consequence: resume becomes slower but less likely to relaunch a poisoned public service.
