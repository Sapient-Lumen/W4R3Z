# ADR 0103 — shadow transport before live SAM

Decision: report digests get canonical signed shadow frames before live SAM/I2P transport work.

Reason: transport noise can hide parser, digest-binding, role/kind, and TTL mistakes.

Consequence: `transportshadow.py` validates parse-safe, signed, fresh, kind-bound report payloads without opening a SAM socket.
