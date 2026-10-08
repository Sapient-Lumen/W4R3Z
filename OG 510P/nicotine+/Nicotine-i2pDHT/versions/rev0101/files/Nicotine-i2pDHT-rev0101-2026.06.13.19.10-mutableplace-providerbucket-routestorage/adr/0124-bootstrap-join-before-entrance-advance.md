# ADR 0124 — bootstrap join before entrance advance

Status: accepted for rev0030 baby cube.

A diverse peerbook view is not enough to advance local bootstrap state. rev0030 joins peerbook, live-probe/live-smoke, negative-space, and egress-budget reports before treating an entrance window as locally usable.

Rationale: entrance growth is a capture surface. Many contacts can still arrive through one family, one channel, one stale cache, or one metadata-expensive probe path.
