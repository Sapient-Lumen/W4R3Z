# ADR 0172 — late ACK is evidence, not finality

A late original ACK after a retry fence is accepted only as scoped local evidence. It may abort retry settlement, but it cannot erase retry fence memory.
