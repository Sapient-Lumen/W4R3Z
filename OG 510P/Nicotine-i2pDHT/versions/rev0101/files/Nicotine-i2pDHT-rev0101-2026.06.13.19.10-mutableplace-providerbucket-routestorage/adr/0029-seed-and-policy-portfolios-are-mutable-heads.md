
# ADR 0029: Seed and policy portfolios are mutable heads

Status: accepted-for-rev0008-guessing

Decision: model entrance seed lists and subjective policy lists as signed mutable heads pointing at compact referenced records.

Reason: entrances and policies must change after churn, compromise, and abuse. Mutable heads allow official defaults and community alternatives to evolve without hardcoding every update.

Guardrail: clients should combine multiple portfolios and cached/direct contacts; one head must not become mandatory bootstrap truth.
