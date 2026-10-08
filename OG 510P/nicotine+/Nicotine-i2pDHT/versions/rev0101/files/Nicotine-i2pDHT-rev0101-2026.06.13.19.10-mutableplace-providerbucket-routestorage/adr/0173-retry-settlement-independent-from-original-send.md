# ADR 0173 — retry settlement is independent from original send

Retry delivery, retry abort-by-late-ACK, and withdraw repair settle independently from the original send. Shared boundary does not imply shared terminality.
