# ADR 0186 — Native dispatch needs Python oracle

Accepted for rev0083.

A native call may be accepted only when the Python reference result agrees at the exact request boundary. A mismatch quarantines native and preserves the Python result as fallback evidence.
