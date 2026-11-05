# 0opschan

0opschan is a local-first forum for making a considered edition of shared conversation. Instead of accepting a single platform's universal ranking, a reader can work with signed selections from curators, make local choices about those selections, and publish their own judgment for others to consider. Conversation is the point; curation helps decide which conversation is worth attention.

The project distinguishes a community, which coordinates shared conversation, from an edition, which selects what a reader sees and keeps. Current source composes an edition from up to 64 independently signed sources and preserves provenance for cross-source replies. The fuller many-community, many-edition switching experience remains a target, not a claim about the present interface.

## Inheriting judgment without inheriting control

A curator publishes signed choices of content or other curators. A local root names the signer, scope and depth; the graph can attenuate authority as choices pass through it. Local overlays can add or exclude content or clamp a curator's scope. The source places explicit bounds on roots, depth, nodes and paths: recursion is a controlled selection mechanism, not an invitation for a remote feed to run commands or govern the machine.

Trust, connection, subscription and custody are separate. Trusting a curator does not by itself contact a peer, schedule checks, keep incoming bytes or publish them. An owner can review a bounded relationship and separately enable recurring inventory or automatic hold. A signature identifies the key that signed particular bytes; it does not establish a person's identity, the quality of their choices or a reason to grant them more authority.

## Carrying a forum

A source, complete composed edition, database snapshot or exact update can be carried as a file. Offline inspection verifies the relevant package; receipt of bytes is not the same as admitting them into a local edition. A static “dumb host” can serve content-addressed objects and packs without running the node itself. These alternatives matter when two people cannot or do not wish to maintain a live connection between their nodes.

Contexts separate local choices over shared admitted data; they are not separate machines, browser profiles or anonymity identities. Private node recovery is also distinct from portable public forum data: it contains owner authority, and the default one-file recovery is encrypted. It does not preserve Tor onion-service keys.

The interface separates the local Forum for reading and posting from Manage for curation, updates, custody, contexts and publishing; Host and Ops have their own roles. A separately configured public Forum can receive posts without exposing local owner controls. The carried project describes supported behaviors and tests, but this review has not operated a live node, tested a browser journey or verified network reachability.

## The supplied file

The supplied Linux x86-64 executable is the self-contained Datacube foundation. It carries the project source, documentation, tests and an exact 0opschan core binary. Its own commands let readers inspect the project and extract the core, so the carrier and forum program are distinct. The carrier's SHA-256 is `b9a54f0a2556119dd5b89b6c51e883898683bc00f32a3d6c290dc15dd02ea074`. The carried core has SHA-256 `9e86609a15bc7d787784c33f987a51070d39be79ef260feddeca36209090e965`.

The carried release metadata identifies these bytes by checksum; it does not authenticate the publisher. No anonymity, general reachability or production-capacity guarantee follows from a successful local inspection. The project source and documentation state AGPL-3.0-or-later, with separate notices for dependencies. The complete license and operating details are carried in the executable.

The carrier's `--help`, `inspect`, `project-summary`, `project-list` and `project-read` interfaces were exercised locally; the extracted core's help was also inspected. Those checks establish the observed interfaces, not the full operational or security claims in the project. Read `README.md`, `docs/CLAIMS_STATUS.md`, `docs/PROJECT_DATACUBE_DISTRIBUTION.md` and the relevant source inside the carrier for details and current limitations.

[Download the single foundation executable](../Maintained%20Tools/0opschan). On x86-64 Linux, make the downloaded file executable and inspect it. To extract the embedded core into a separate working file:

```sh
chmod u+x 0opschan
./0opschan inspect
./0opschan project-read docs/PROJECT_DATACUBE_DISTRIBUTION.md
./0opschan project-read bin/0opschan-core-x86_64-linux > 0opschan-core
chmod u+x 0opschan-core
./0opschan-core --help
```

The core does not include Tor or i2pd. Consult the carried distribution and operating documents before configuring a node or a listener. The single file on this shelf is the foundation carrier; extracting the core is a local choice, not an additional file in the distribution.

[Maintained Tools](../Maintained%20Tools/README.md) · [W4R3Z](../README.md)
