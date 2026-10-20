# 4UR4C10WN

## A private post office you can carry, inspect and continue building

4UR4C10WN is being built around a simple ambition: a person should be able to carry their own encrypted post office, send a letter while its recipient is away, and return after an interruption without having to guess what happened. The object combines a native runtime, an encrypted Office model, recipient-absent postal storage, an embedded I2P router and an unusually detailed account of custody and recovery. It also carries the source, build graph, tests, documentation and development history from which another person can continue the work.

That last property changes what is being handed over. This is not merely a mail application to consume. It is an executable Datacube: a working foundation that can explain and materialize its carried project. The supplied dynamically linked build still needs a compatible Linux environment and its runtime dependencies; carrying the project does not eliminate that requirement. A recipient can develop a different descendant rather than wait for the original author to choose every next step.

**Current supplied revision: rev0294.** This is its continuing reading page. Cube and bootstrap downloads are pending clarification of the “MCGSI Public License” named by `libi2pd/Siphash.h` in the carried upstream source. The original pair remains unchanged; the project’s current owner declaration does not replace third-party terms.

The supplied object is a Linux development build. Its ordinary first-letter journey is still under construction; the underlying mail, custody and recovery mechanisms are considerably broader than that unfinished entrance. The sections below distinguish the mechanisms from the current state of their integration.

## The Office is more than an inbox

An Office brings together cryptographic identity, contacts and relationship authority, encrypted mail stores, an immutable Library, drafts, sender queues, Sent evidence and recovery records. An encrypted Office can be appended as a separate state layer to the carrier. The software foundation and a person's private Office are different things: the distributed development cube is not a populated personal mailbox.

Opening an Office is a controlled tenure over that state, not blanket permission for every activity available to the program. Profile coordination, active encrypted generations, local locks and recovery checks establish which authority is open. Network work, imports, history application and consequential changes have their own admission paths. A screen being reachable does not silently authorize the effect it describes.

This separation also matters when a person moves their work. Recovering identity authority, restoring mutable mail state and transporting historical evidence are different operations. A copy of a private key does not by itself recreate every message, receipt or unfinished task. The project makes those differences inspectable instead of hiding them behind a single reassuring “restored” label.

## Postal custody makes absence ordinary

A private conversation should not require both people to be online at the same moment. In 4UR4C10WN, a configured **Posthouse** can accept an opaque encrypted package under a bounded storage grant and sign evidence that it accepted those exact bytes. The recipient can retrieve the package later.

The storage service is not thereby the reader. Its custody receipt says something important and limited: a named service accepted the package under the protocol. It does not say the recipient retrieved it, authenticated it, opened it, or understood it. Nor does knowing a Contact automatically confer every storage or sending permission needed for the next package.

The distinction produces a useful delivery vocabulary:

**prepared → queued locally → attempted → signed storage custody → retrieved → authenticated software opening → explicit acknowledgement**

These are distinct facts, not stages the interface may fill in optimistically. A Sent copy establishes the sender's retained copy. An acknowledgement is a separate event. Human reading and understanding are not manufactured from either one.

Ordinary opening is not an automatic read-receipt mechanism. Where acknowledgement is deliberately requested and supported, it supplies its own evidence. A missing acknowledgement does not prove that delivery failed, so uncertainty is not converted into an automatic resend.

## A route is not a relationship

The embedded i2pd core supplies the routing layer and local destination state. The Office's human/mail identity, Contact authority and storage grants remain separate from that transport identity. Reaching a network destination does not establish what the person at that destination has authorized.

The runtime can observe local transport, peer, NetDB, LeaseSet and tunnel conditions. Those observations help explain whether a route is ready for work. Public reachability and a completed transfer to an independent machine are different questions. This is why the product can present an unknown Route condition honestly instead of converting a configuration file or a running process into a success claim.

The design is more than “put email through I2P.” It asks how routing, relationship authority, recipient absence, storage custody and local durability compose into a postal service the owner can reason about.

## Safe letters and useful local work

The Office supports explicit composition, encrypted saved drafts, preview and commit, attachments drawn from the immutable Library, Outbox and Sent views, filing and attention controls, and reviewed recovery of a Sent item into a draft or Library object. These are operations on the actual production Office, not merely a sketch of a future inbox.

Presentation is intentionally conservative about what a letter can do. Requested content is authenticated and rendered as safe text; active HTML and remote image fetching are not treated as ordinary mail display. Terminal controls, malformed text, invisible formatting and attachment boundaries are inputs to defend, not opportunities for a correspondent to program the recipient's interface.

Local organization also remains distinct from historical truth. Marking attention, filing an item or changing a view must not rewrite authenticated opened history. Turning a Sent item back into a draft does not itself grant permission to resend it.

A separate local automation handoff illustrates the same approach. The optional Morrow launcher can export authenticated unread presentations into an owner-private plaintext handoff. That is a deliberate plaintext boundary, not encrypted-at-rest storage by another name. Its ordering makes the durable handoff exist before local opened bookkeeping, so a launcher death cannot leave only the bookkeeping and no delivered handoff.

## Recovery begins with what survived

The most distinctive engineering runs through interrupted work. A process may finish an effect and die before reporting success. Two cooperating writers may race. A name may remain after its contents changed. The project refuses to treat those situations as interchangeable failures.

Its bounded history mechanisms preserve exact transfer plans, content-addressed objects, resumable spools, authenticated stream evidence and separately reviewed application into another state. A completed resident-transfer receipt can prevent duplicate work when it is validated before a new connection. But network completion and later receipt publication are not one transaction: absence of that receipt may leave a genuine uncertain interval.

The recovery principle is stronger than “try again”: preserve the strongest surviving evidence, derive only what it uniquely establishes, and do not reconstruct an authenticated event from a weaker summary. An exact retained completion can justify recognizing completed work. A missing completion cannot justify pretending the external effect never happened.

The ordinary interface is being built to carry that rigor without demanding that a person memorize record formats. History and sign-in Recovery share a path-free evidence center. Normal presentation names consequences; an explicit expert view exposes bounded technical identity. Inspecting a remnant, applying history, remembering a result, reopening an Office and removing one reviewed staging file remain separate decisions.

Even the terminal is part of this responsibility. A small Linux lifetime guard watches the exact launcher and admitted terminal modes so named launcher deaths can restore the original terminal baseline without overwriting a different foreground owner's later state. That is a concrete response to a discovered raw-terminal failure, not an assertion that every crash or physical power loss has been solved.

## What rev0294 changes

The latest supplied revision adds **First Letter** to the F4 Office menu. Its five rows are Office, Route, Posthouse, Contact and Letter. The overview gathers existing observations and leads into existing reviewed operations; it does not create another mailbox or invent a new mail protocol.

The design makes an important distinction between orientation and accomplishment. An open encrypted Office is not a verified backup. A count of configured Posthouses is not a grant for the next package. The evidence-definition view explains what terms mean; it is not a live tracking screen for a selected letter. Some native setup detours exist while attached portable setup adapters remain incomplete.

A separate, explicitly invoked **First Letter laboratory** exercises actual synthetic encrypted Offices, recipient absence during signed Posthouse custody, a storage restart, later retrieval, recipient-key rotation, historical-key opening and deliberately requested acknowledgement over loopback. That is substantive integration evidence for those mechanisms. It is not the missing ordinary end-to-end onboarding journey, nor a public-I2P campaign.

The remaining product task is therefore intelligible: make the full create-or-recover, route, Posthouse, Contact, send and recovery journey ordinary without weakening the boundaries that make its evidence meaningful.

## The cube is also the means to make its successor

The carrier contains a native runtime prefix and a compressed resource set with the project. Complete-carrier identity, runtime identity, resource identity and private Office identity are separately checked. The bootstrap names the maintained product, architecture, threat-model and construction documents, so a new reader need not mistake an old release note for the present design.

Exact source and historical preimages make disagreement productive. A recipient can inspect why a boundary exists, trace a change, reproduce a relevant check under suitable conditions, or choose another direction. Retained negative results and incomplete qualifications are construction materials too. They identify where a seemingly plausible shortcut already failed and where the next claim still needs evidence.

That is the Foundry role of this drop: a substantial private-post-office project offered while it is still becoming itself, with the means of further construction carried inside rather than replaced by a promotional description.

## Reading inside the object

Begin with the matching bootstrap, then the carried `docs/CURRENT-PRODUCT.md`, `docs/CURRENT-ARCHITECTURE.md`, `docs/CURRENT-THREAT-MODEL.md` and `docs/HUMAN-QUICKSTART.md`. For this revision, read `docs/REV0294-FIRST-LETTER-READINESS-V1.md` together with its evidence and human-use audit. The durable-writer inventory distinguishes reviewed publication contracts from remaining work. Historical protocol documents must be read with their dates and later revisions, not flattened into one simultaneous capability claim.

This page remains the continuing explanation. Later supplied cubes and bootstraps replace the current pair; the account is revised where the object changes, and the compact log below preserves the salient movement. Original authorship and embedded dependency notices remain with the work. The [current owner declaration](../../LEGAL-NOTICE.txt) is external to the original cube; `docs/LICENSE-PROVENANCE.md` retains its dated licensing history, including the earlier absence of an outbound project license.

## Changelog

- **Received 2026-10-20 · rev0294 (source 2026-10-19)** — First Letter readiness/evidence UI + explicit local recipient-absent delivery/ACK assay; ordinary onboarding remains open.

## Exact current pair

- `4UR4C10WN`: 85,624,643 bytes; SHA-256 `76eea89c82c20c6067e1f41e32d0fc905b9c9b77df225e1b38ab0a212075fbac`.
- `BOOTSTRAPROSE.md`: 35,826 bytes; SHA-256 `d91cd8f259d3105a2febc2d6a545b99aef579d3d3085c4a6523adf74ace3343e`.

The matching original bytes are retained for publication without repacking the cube. Its source, tests and history remain inside it; they are not duplicated as an expanded repository tree. These hashes identify the supplied pair, not a security certification.

[▓▒░ FOUNDRY ░▒▓](../README.md) · [W4R3Z](../../README.md)
