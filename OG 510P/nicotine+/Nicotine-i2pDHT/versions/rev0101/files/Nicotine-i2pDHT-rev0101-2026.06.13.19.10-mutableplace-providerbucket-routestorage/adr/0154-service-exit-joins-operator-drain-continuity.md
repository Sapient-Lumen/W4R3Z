# ADR 0154 — service exit joins operator, drain, and continuity

Decision: pause, demotion, bridge-disable, freeze, and resume are joined decisions over exact service/scope/request evidence.

Reason: an accepted operator intent, a clean drain, or a breaker report can each be valid locally but unsafe as a side effect alone.

Consequence: service lifecycle changes remain local and auditable instead of becoming unscoped authority.
