# ADR 0174 — egress journal preserves contradictions

Compaction may drop soft duplicate observations, but it must preserve late ACK versus retry-delivered contradictions and hard-negative evidence.
