# rev0038 PB-01 public-overlap notes

Classification: **no exact direct public duplicate captured**.

Useful public context retained:

- Nicotine+ protocol documentation: `https://nicotine-plus.org/doc/SLSKPROTOCOL.html`
  - Peer init messages initiate P/F/D TCP connections.
  - PierceFireWall is the response to an indirect ConnectToPeer request and carries the server token.
  - PeerInit currently carries a zero token that is ignored today; the old SendConnectToken cross-check mechanism is obsolete.
  - Peer-message section says only one active P connection to a peer is allowed.
- GitHub issue #3078: `https://github.com/nicotine-plus/nicotine-plus/issues/3078`
  - Connection lifecycle logs include PeerInit removal and indirect request timeout adjacency.
- GitHub issue #2978: `https://github.com/nicotine-plus/nicotine-plus/issues/2978`
  - General connection-closed / connectivity symptoms.

I did not capture a public issue that directly describes the narrower PB-01 chain: a later direct PeerInit replacing an already-established primary by username/type, plus the generic post-init secondary-promotion rule mutating `init.sock` while an established primary remains alive.
