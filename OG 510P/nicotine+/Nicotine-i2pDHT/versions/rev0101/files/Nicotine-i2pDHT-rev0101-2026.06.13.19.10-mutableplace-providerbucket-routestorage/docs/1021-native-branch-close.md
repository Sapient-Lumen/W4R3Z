# Native branch close

`nativebranchclose.py` joins archive replay, held promotion review, promotion archive, shadow-only policy, and native fold-spine evidence.

The accepted state is `shadow_only_closed`: Python fallback remains authoritative, native load/dispatch/result authority remain denied, and future promotion requires a new branch rather than piggybacking on accumulated shadow matches.

The key risk tested here is quiet authority drift after a long native investigation.
