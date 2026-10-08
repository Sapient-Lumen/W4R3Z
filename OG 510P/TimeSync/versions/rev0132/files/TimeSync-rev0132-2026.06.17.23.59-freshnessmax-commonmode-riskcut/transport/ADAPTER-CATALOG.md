# TimeSync rev0132 transport adapter catalog

The machine-readable catalog remains six abstract carriage patterns: JSON fixture, in-band claim, management pull, telemetry push, detached export, and relay gateway.

These are envelope/transport semantics, not implementation adapters. The current implementation proofs live under `tools/`: chrony replay/capture and ntpq replay. They demonstrate management-surface ingestion into TimeState, while the abstract transport catalog remains unchanged.

Transport integrity checks validate declared protection/coverage relationships. They do not perform cryptographic signature verification.
