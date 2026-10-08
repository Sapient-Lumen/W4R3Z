# PB-01 bounded public-context review — rev0074

Checked 2026-06-17 America/New_York against official Nicotine+ project pages.

## Current branch and protocol

- The supported `3.3.x` branch still points at `98089ac` (May 18, 2026),
  matching the supplied exact-current source lane.
- The protocol documentation, updated May 10, 2026, says modern clients attempt
  indirect and direct peer connection paths in the same sequence and that only
  one P connection should ultimately remain active.
- The same document says a direct `PeerInit` token is zero and ignored today.
  This supports the conclusion that the message alone does not provide an
  authenticated connection generation.

## Adjacent public history

- Commit `34b442a` says that less aggressive rejection of indirect connections
  fixes connectivity with some SoulseekQt users and relates the change to issue
  #2829.
- Immediate child commit `4932ef9` promotes the retained secondary when that
  socket actually carries a message.
- Issue #2829 reports first-attempt share-browse failures; issue #653 contains a
  real interoperability trace with simultaneous direct/indirect message
  connection negotiation; issue #663 discusses connection supersession,
  dropped in-flight messages, reuse, and socket-exhaustion concerns.

These items are adjacent and materially constrain policy. They do not describe
this cube's exact two-peer split-primary counterexample or establish that every
possible same-user replacement is correct. The search is bounded and makes no
novelty claim.

## Sources

- <https://github.com/nicotine-plus/nicotine-plus/commits/3.3.x/>
- <https://nicotine-plus.org/doc/SLSKPROTOCOL.html>
- <https://github.com/nicotine-plus/nicotine-plus/issues/2829>
- <https://github.com/nicotine-plus/nicotine-plus/issues/653>
- <https://github.com/nicotine-plus/nicotine-plus/issues/663>
