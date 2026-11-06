# NATrav

**Authenticated peer connectivity across difficult network boundaries.**

NATrav is a Rust connectivity engine for peers behind network address translation. It combines authenticated direct connections with relay options and explicit mapping controls, while keeping connection policy, evidence and authority over network actions distinct. It is a sibling of [NATravOverlay](../../Foundry/NATravOverlay/README.md), not another name for the overlay: NATrav owns connectivity policy; the overlay addresses the higher-level work and custody exchanged between peers.

**Current supplied executable:** NATrav v0.52.0, Linux x86-64. The original 14,649,566-byte executable is supplied here as [part 00](natrav-v0.52.0-x86_64-linux-0b6c7f8c881c.part00) and [part 01](natrav-v0.52.0-x86_64-linux-0b6c7f8c881c.part01). Joining the two parts restores the exact supplied file. No source or binary bytes have been edited.

## Why this download is split

The split is a distribution workaround for the OpenAI ChatGPT GitHub connector used to publish this copy, not a property or requirement of NATrav. The 14,649,566-byte executable becomes 19,532,756 bytes when base64-encoded for that upload. The attempted single request was rejected with `MCP request exceeds the 16 MiB limit`. OpenAI operates the ChatGPT integration through which this limit was encountered; this observation does not identify the particular team or explain the policy behind the limit. It does not establish a GitHub file-size limit: a direct GitHub upload was not tested. The two parts are a way to preserve and distribute the supplied executable despite that observed boundary.

## Reassemble and verify

In a directory containing only these two downloaded parts, join them in this order:

```sh
cat natrav-v0.52.0-x86_64-linux-0b6c7f8c881c.part00 natrav-v0.52.0-x86_64-linux-0b6c7f8c881c.part01 > natrav-v0.52.0-x86_64-linux-0b6c7f8c881c
sha256sum natrav-v0.52.0-x86_64-linux-0b6c7f8c881c
```

The expected SHA-256 is `bbb6096fb6a7c82a89aa011a74594fe6e99397242888d34b68aedeb7966b9855`. This checks the reconstructed bytes against this listing; a checksum alone does not authenticate the publisher. The parts have SHA-256 values `1a1375cbd792cb2bd19613f84d3aebabeafa5c5006f81b43fdae2c914bfda4b9` and `3c20565255bb307b986ef7577f13e7936d0d912396c997b6b2f50e4a940aa2b1` respectively.

## How it is organized

The carried project describes direct ICE and QUIC connectivity, several TURN relay transports, explicit router-mapping controls, and evidence-informed selection. These are not a promise that every peer can be reached. The documented production envelope names supported features and remaining research boundaries. An authenticated peer, a successfully delivered packet, and permission to take an external action are different claims.

This is a self-carrying executable: the project's distribution document says the launcher verifies and starts the embedded static node, while an explicit `datacube` namespace provides access to the carried project and source. The matching upstream two-member release ZIP and external bootstrap were **not** supplied with this drop; they are not silently reconstructed or claimed here. The extracted [upstream README](UPSTREAM-README.md), [distribution contract](DATACUBE-DISTRIBUTION.md), and [MIT license](LICENSE) are preserved from the carried project and checked against its index. Third-party components retain their own notices within the carried source.

The supplied file is executable code. Its documentation describes Linux x86-64, `/proc/self/exe`, sealed `memfd_create`, and `fexecve` as runtime requirements; network operation also depends on actual host policy and configuration. The source describes tests and a supported v0.52 envelope, but those tests and the executable were **not run for this listing**. The two parts were locally reassembled and matched against the supplied binary's SHA-256. The file's declared embedded Git commit is `0b6c7f8c881ccc68bde6e489a445fbd02ff390c1`.

## Change record

- **v0.52.0:** The supplied source describes the production node in a self-carrying Datacube executable, alongside explicit source-inspection and custody interfaces and route-loss handling for discovered mappings.

[Maintained Tools](../README.md) · [Catalog](../../CATALOG.md)
