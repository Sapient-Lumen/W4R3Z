# 0opschan

0opschan is a distributed peer-to-peer forum for shared conversation across independently operated nodes. Its transport work spans I2P, Tor and explicitly scoped direct HTTP, while portable files offer another way to carry material between nodes. It is also local-first: each reader can make a considered edition of that conversation. Instead of accepting a single platform's universal ranking, a reader can work with signed selections from curators, make local choices about those selections, and publish their own judgment for others to consider. Conversation is the point; curation helps decide which conversation is worth attention.

The project distinguishes a community, which coordinates shared conversation, from an edition, which selects what a reader sees and keeps. Current source composes an edition from up to 64 independently signed sources and preserves provenance for cross-source replies. The fuller many-community, many-edition switching experience remains a target, not a claim about the present interface.

## A forum across independent nodes

A post need not remain trapped on the site where it first appeared. One node can admit a signed record into its own feed; another can obtain and verify the record, build a local view and publish its own reply while retaining the provenance of both sources. The carried project describes a real I2P laboratory journey from a visitor’s post on one Forum, through invitation-led replication, to another Forum, and a corresponding Tor journey with replies across nodes. Those are the project’s bounded recorded tests, not tests repeated by this review. Our own local two-node fixture is described below.

The transport boundaries are deliberate. The core has separate I2P HTTP-proxy and Tor SOCKS paths, plus an explicitly selected scoped direct-HTTP profile. Its default dual-darknet adapter accepts the designated I2P and Tor destinations and refuses clearnet and redirects rather than silently falling back. The carried operator guide presents the direct-HTTP profile for deliberate development; canonical peer invitations and the recurring curator subscription described in the current contracts use exact I2P or Tor anchors. Do not read “three transports” as a claim that every workflow automatically mixes all three, or that availability on any route establishes anonymity. The supplied foundation carries the core, not the Tor and I2P routers.

The distinction between peer ingress, a public Forum listener and the loopback owner controls is part of the architecture: sharing a conversation is not permission to administer the machine. Static object/pack exports and portable files offer additional ways to move verified material without requiring a live node-to-node connection.

## Why curation matters to a distributed chan

A chan is difficult to host cooperatively. An open conversation can attract material that participants, operators and intermediaries judge very differently; bandwidth, storage, legal exposure, attention and the work of moderation do not disappear when hosting is distributed. A single global filter would re-create a center of authority, while indiscriminate replication would ask every node to bear choices it did not make.

Composable editorial judgment offers a different division of work. A curator can make a useful selection once; another curator can build on it; a reader or operator can inherit that work within a bounded scope and still exclude or refuse material locally. Different nodes can carry and present different selections, while the underlying signed sources preserve provenance. This is a way to cooperate without requiring every participant to agree on one universal edition. It does not itself solve abuse, liability, availability or the social work of moderation, and the strength of the idea depends on whether people can operate the controls in practice.

## Inheriting judgment without inheriting control

A curator publishes signed choices of content or other curators. A local root names the signer, scope and depth; the graph can attenuate authority as choices pass through it. Local overlays can add or exclude content or clamp a curator's scope. The source places explicit bounds on roots, depth, nodes and paths: recursion is a controlled selection mechanism, not an invitation for a remote feed to run commands or govern the machine.

Trust, connection, subscription and custody are separate. Trusting a curator does not by itself contact a peer, schedule checks, keep incoming bytes or publish them. An owner can review a bounded relationship and separately enable recurring inventory or automatic hold. A signature identifies the key that signed particular bytes; it does not establish a person's identity, the quality of their choices or a reason to grant them more authority.

## Carrying a forum

A source, complete composed edition, database snapshot or exact update can be carried as a file. Offline inspection verifies the relevant package; receipt of bytes is not the same as admitting them into a local edition. A static “dumb host” can serve content-addressed objects and packs without running the node itself. These alternatives matter when two people cannot or do not wish to maintain a live connection between their nodes.

Contexts separate local choices over shared admitted data; they are not separate machines, browser profiles or anonymity identities. Private node recovery is also distinct from portable public forum data: it contains owner authority, and the default one-file recovery is encrypted. It does not preserve Tor onion-service keys.

The interface separates the local Forum for reading and posting from Manage for curation, updates, custody, contexts and publishing; Host and Ops have their own roles. A separately configured public Forum can receive posts without exposing local owner controls. The carried project describes supported behaviors and tests, but this review has not operated a persistent deployed node, tested a browser journey or verified real-network reachability.

## The supplied file

The supplied Linux x86-64 executable is the self-contained Datacube foundation. It carries the project source, documentation, tests and an exact 0opschan core binary. Its own commands let readers inspect the project and extract the core, so the carrier and forum program are distinct. The carrier's SHA-256 is `b9a54f0a2556119dd5b89b6c51e883898683bc00f32a3d6c290dc15dd02ea074`. The carried core has SHA-256 `9e86609a15bc7d787784c33f987a51070d39be79ef260feddeca36209090e965`.

The carried release metadata identifies these bytes by checksum; it does not authenticate the publisher. No anonymity, general reachability or production-capacity guarantee follows from a successful local inspection. The project source and documentation state AGPL-3.0-or-later, with separate notices for dependencies. The complete license and operating details are carried in the executable.

The carrier's `--help`, `inspect`, `project-summary`, `project-list` and `project-read` interfaces were exercised locally; the extracted core's help was also inspected. A later bounded local fixture run exercised two nodes; that result is described below. These checks do not establish the full operational or security claims in the project. Read `README.md`, `docs/CLAIMS_STATUS.md`, `docs/PROJECT_DATACUBE_DISTRIBUTION.md` and the relevant source inside the carrier for details and current limitations.

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

## A concrete journey: from someone else’s judgment to your edition

Imagine Alice trusts an editor, Bea, whose signed selection includes another curator, Cy, and a feed of conversations. Alice pins Bea’s exact feed and signer, the maximum depth, and the most authority any descendant can receive. If Bea permits a choice only to be recommended, Cy cannot turn it into permission to admit bytes. The resolver follows locally available signed chains, records paths and problems, and stops at explicit budgets. A missing source or cycle is evidence to surface, not permission to guess.

That graph yields a plan, not a changed forum. Alice previews and separately applies a source set to her local edition; the node checks the exact preview against current state. A stale preview must be reviewed again. A separate subscription can authorize future inventory through selected, identity-anchored carriers, within limits on feeds, requests, bytes and retries. Enabling recurrence is another decision. Inventory itself does not transfer content. Holding, admitting, retaining and displaying bytes have their own boundaries. A separately authorized automatic Hold can reduce repeated work without making a remote curator the owner of Alice’s machine.

This separation makes a real difference when a curator changes their mind: newly eligible choices can be noticed without silently rewriting an already applied edition. It also has a cost. The reader must understand and navigate more distinct decisions. The carried claim ledger describes the full many-curator, many-edition experience as unfinished; currently a context has one primary subscription and an edition is bounded to 64 sources.

The carried `crates/node/src/tests/curation_graph_workflow.rs` makes the promise concrete: it includes nested signed curator choices, a stale preview, an attempt to reuse a preview in a different context, and different local versus public provenance. These are test cases in the carried source, not a claim that this review ran that full test suite.

## What the local exercise showed

The embedded core’s `two-nodes-conversation-mvp` fixture returned `ok:true` in this workspace. Its described scenario includes replication of a conversation feed, an intentional fork, local hide/restore and nested curator preview/apply. The generated views for the two nodes were byte-identical, both SHA-256 `e3856c798916de8224c1afd48fa73c5b66207142cc4ecf999e571a0bc631b074`. This is a small local scenario, not a demonstration of internet-scale performance, durable operation, anonymity or an independent security audit.

The same exercise exposed a portability defect in the extracted core: the separate `fixture assert` and `run summarize` commands failed to find `schemas/run.schema.json` at the original build path. The carried conformance source constructs its repository root from Cargo’s compile-time manifest directory. The fixture’s own success should not be confused with a successful independent assertion; this finding is limited to these observed commands on this exact core.

## What is distinctive, and what has precedent

The ambition is the integration of several separable things: signed, recursive and bounded editorial judgment; an explicit boundary between that judgment and network/custody authority; portable verified forum material; and a local, explainable edition. Each part deserves comparison rather than a claim that it appeared from nowhere. [Scuttlebutt](https://handbook.scuttlebutt.nz/concepts/gossip) already uses signed feeds, peer replication and offline carriage. [Nostr’s NIP-51](https://github.com/nostr-protocol/nips/blob/master/51.md) specifies shareable follow and curation sets. [Lemmy](https://join-lemmy.org/docs/) provides federated discussion and separately administered communities. [Dscuss](https://vminko.org/dscuss) also described a peer-to-peer forum with locally managed and shareable moderation choices, though its site distinguishes implemented and planned features. These references do not establish the full behavior of every client or deployment; the stronger question is whether another complete forum combines these authority boundaries and workflows as 0opschan does. That requires more comparative investigation.

## A forum is also a custody decision

Suppose Bea recommends a conversation that Alice has never downloaded. In a conventional interface, “follow” can be made to look like one action, but several things must happen underneath it: find Bea's current choices, ask another machine what exists, bring data across a network boundary, decide whether it is valid, make it visible, and decide how long to keep it. 0opschan treats these as related but distinct decisions. That is the strongest reason to care about its machinery: a recommendation can be useful without becoming an unbounded claim on another person's bandwidth, disk, trust or attention.

The carried custody model names five states. **Available** is a bounded inventory report: the node has learned about missing records but has not transferred them. **Held** means the specified chain bytes have been transferred and checked, but are not yet registered, evaluated or visible merely because they are present. **Admitted** means records have passed the ordinary signature and policy path. **Selected and visible** means evaluation and the local projection make them part of what this reader sees. **Retained** means a storage root protects a necessary closure from cleanup. These are not five labels for the same operation. Hiding a post need not delete its bytes; holding it does not promise permanent retention; possessing it does not trust the sender.

The dependency problem explains a design choice that a feature list would miss. A signed feed is a predecessor chain: accepting a later record while discarding an earlier dependency can make the claimed history incoherent. 0opschan's model therefore holds or admits a bounded, contiguous dependency batch, then makes finer visibility choices over the validated material. It does not promise a magic “delete this card everywhere” button. The model aims to make the consequences honest, including when cleanup cannot prove an object is unowned.

Portable artifacts carry similarly distinct scopes. An edition file can be complete for that edition without being the whole database. A named database snapshot describes a particular admitted portable-family inventory, not the owner's private node state. A candidate annex carries held or quarantined material without making it admitted. A receipt-proof package closes a defined graph of receipt links without making receipt prose true or authorizing an action. Private recovery is a different, secret-bearing object. The exact families and scope matter more than the word “complete.”

These boundaries are supported by the carried custody and portability documents and the package inspection source. They make a coherent design claim, but a design is not self-validating. How easily a new user can understand these choices, what happens under real network churn, and whether the costs of separate ceremonies remain acceptable are empirical questions. The project's own ledger records unfinished bulk custody, richer retention and many-edition workflows. The local two-node fixture is evidence for a bounded path, not an answer to those larger questions.

