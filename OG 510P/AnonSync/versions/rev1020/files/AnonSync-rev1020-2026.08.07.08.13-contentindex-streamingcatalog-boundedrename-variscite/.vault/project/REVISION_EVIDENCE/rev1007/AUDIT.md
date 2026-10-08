# Rev1007 audit

Rev1007 moves source-side content-defined manifest construction out of one
unbounded authenticated request. The retained reconciliation service advances at
most 32 MiB of exact rooted source bytes per request, releases the descriptor,
and resumes one process-local projection across fresh serve sessions. Protocol
generation 9 exposes a typed `SourcePayloadPreparing` cutpoint. TLS collapses
consecutive preparation turns inside the existing authenticated round-trip
budget so one-shot operation can reach a wire range without restarting its
source process.

The adjacent audit corrected duplicate TLS preparation accounting and replaced
stale session-owned cache oracles with the actual service-owned exact-payload and
inode fence. The focused audit passed 26/26 and the complete structural authority
audit passed 592/592.
