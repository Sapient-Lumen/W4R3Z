# ADR 0201 — Record-plane oracle after native close

Accepted for rev0099.

The native/GCC branch was closed as shadow-only, but that close is not enough by itself. The DHT record plane now has an explicit Python-owned oracle. Native code cannot own record parsing, mutable latestness, provider semantic proof, crypto, transport, or persistence finality.
