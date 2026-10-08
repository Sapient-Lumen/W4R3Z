# SEARCH-AGAIN-EPOCH-01 current disposition — rev0079

## Decision

```text
current Search Again semantics: same-token Retry/Merge
replacement Refresh architecture: unresolved
minimum defensible local acknowledgement:
  every request in the exact epoch fan-out has been prepacked and staged in
  network-owned server output state, and matching admission state is installed
selected implementation: none
status: open public design research
security route: not applicable; ordinary product correctness and architecture
```

Rev0079 does not select a patch. It narrows the cross-thread boundary and corrects an under-modeled assumption in rev0078.

## What rev0078 got right

A true replacement refresh cannot be implemented by clearing the existing page or changing one token field. The current integer token is simultaneously a wire response capability, a core search key, a GUI page key, a notification target, and part of close/show and self-search bookkeeping. A durable replacement design therefore needs a stable logical search identity and a replaceable wire-epoch token.

Queue acceptance is also not application. The ordinary queue callback has no rejection result while disabled, and disconnect drains accepted commands and response admissions.

## What rev0079 corrects

The rev0078 candidate direction said that the network should acknowledge after admission changes but before request serialization. That is too early for the current source shape.

Search requests are server messages. The network thread packs each message and appends bytes to the server connection's output buffer before the event loop handles writable sockets. Packing can return no payload, server-message permission can stop a batch, and closed/disabled states can drop work. Existing helpers expose no per-message success result.

A naive composite wrapper could therefore acknowledge a buddy epoch after only part of its recipient fan-out was retained—or after one request silently failed to pack. Rev0079 adds executable counterexamples for both cases.

The minimum meaningful *local* applied acknowledgement is now:

```text
1. Validate transaction ID, network generation, authentication, and connection.
2. Resolve and freeze the exact recipient set for this epoch.
3. Prepack every outgoing request without mutating visible or network state.
4. Reject the entire epoch if any request cannot be packed.
5. Install the new response admission and retire the old admission as one
   network-thread transaction.
6. Stage every prepacked request in network-owned server output state.
7. Queue one matching epoch-applied event before the event loop processes
   writable/readable sockets.
8. Commit the page token switch and clear only on the matching main-thread event.
```

The exact mutation order needs implementation-level exception safety, but partial fan-out must never produce a success acknowledgement.

## What this acknowledgement still does not mean

It does not prove an operating-system socket write, remote receipt, remote processing, a result, or completion of every peer in a fan-out. A later disconnect can discard buffered bytes after the main thread receives the acknowledgement.

That leaves a product-policy choice rather than a missing boolean:

```text
commit on local output ownership
  simple, but a post-ack disconnect can leave a newly cleared empty page

retain stale rows until first fresh result
  resilient, but zero-result searches have no protocol completion signal

replay the committed epoch after reconnect
  can recover, but needs generation, deduplication, audience, and user-intent rules

surface a failed/stale refresh state
  honest, but requires new UI and plugin semantics
```

The safest present conclusion is that Retry/Merge should remain the behavior until maintainers choose replacement semantics and a disconnect/zero-result policy.

## Evidence boundary

Executable tests use the bundled master proxy `f4e17d59783dbc48ea31d2e899a681e2dd1ed500`. Public master was reviewed at `a96406e7aa285a3fb2a3e35900686d164a22bf02`; the relevant search, GUI, queue, and server-output flow remains equivalent for this analysis. Whole-tree exactness is not claimed for public master.

The broad idea that a true repeat needs a fresh token is already present in public Search Again discussion. The cube claims only its source-backed owner map, transaction counterexamples, and local-publication boundary.

All generated material is research-only and is not upstream contribution content.
