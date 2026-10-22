# Vibechat

**An encrypted-chat application carried together with the materials for its next version.**

Vibechat brings a local identity, friends, conversations, attachments and recovery into a portable HTML work. It also carries its client, cryptographic worker, native Waystation, build material and development record. The recipient gets both an application to inspect and a workshop from which to continue it, rather than a hosted interface whose implementation disappears behind the service.

**Current rev0136 / Fathom:** [Vibechat.html](https://github.com/Sapient-Lumen/W4R3Z/releases/download/Vibechat-rev0136/Vibechat.html) · [Matching BOOTSTRAPROSE.md](https://github.com/Sapient-Lumen/W4R3Z/releases/download/Vibechat-rev0136/BOOTSTRAPROSE.md) · [Current evidence supplement](https://github.com/Sapient-Lumen/W4R3Z/releases/download/Vibechat-rev0136/Vibechat-rev0136-evidence.zip) · [Release](https://github.com/Sapient-Lumen/W4R3Z/releases/tag/Vibechat-rev0136)

## A conversation has more than a connection

A person unlocks an identity, pins another person's public card, and establishes a conversation through the available transport. Public cards bind the protocol suite, signing key, key-encapsulation key and fingerprint. Pinning is a deliberate relationship decision: reaching an address or receiving a plausible display name is not enough to establish it.

The client supports encrypted messages and bounded file attachments, with review before sharing. Its local-storage modes distinguish successful encrypted saving from material held only in the unlocked tab and from a download that has merely been requested. Encrypted backup and restoration are explicit workflows. Recreating an identity does not recreate its old messages: identity recovery and restoration of saved conversations are different jobs. Device-local drafts are separate from sent messages and are not silently included in chat backups. These distinctions matter when moving between browsers or leaving a fragile workspace: a visible conversation is not itself proof of a saved copy.

The browser transport includes ordered WebRTC data channels and target-bound signed offer/answer packets. Invitations and return paths can use the default ntfy.sh rendezvous or a selected Waystation. Those services carry opaque encrypted material but still observe network and timing metadata. Selecting a different meeting place changes the route, not the pinned identity of the friend.

## Keep cryptography separate from the page's other powers

The serialized TypeScript worker holds secret keys and the profile key, while the client handles the DOM, network transport and filesystem-facing interactions. Its carried implementation has no runtime module fetch or CDN fallback. That division makes the cryptographic boundary inspectable; it is not a claim that the surrounding browser or host is trustworthy by construction.

For an event, the worker generates a fresh content key, encapsulates and wraps it separately for each pinned recipient, encrypts the content, and signs the canonical body. Opening checks the pinned sender and signature, the recipient binding, authenticated decryption and strictly validated JSON. The fixed suite combines ML-KEM-768, ML-DSA-65, AES-256-GCM and HKDF-SHA256, with Argon2id-based identity derivation. The carried, adapted implementations need their own review; an upstream component's audit would not automatically cover these adaptations or their composition.

Rooms add another layer. Membership is an owner-signed chain of epochs, not an editable label supplied by the transport. Messages bind the room, policy identity, epoch and recipient set. The worker checks continuity against its locally retained accepted chain and rejects a shorter or divergent replacement; this is not external protection against restoring an older local state. Receiving a new policy, reviewing it, declining it and recording adoption remain distinguishable operations. A successful connection does not make a policy decision on the person's behalf.

## The Waystation and the ordinary edge

The native Waystation provides a bounded storage-and-transport surface for opaque encrypted publications. SQLite publication transactions, request admission and connection lifetime are separate parts of that work. A public reverse proxy can terminate the external connection and forward requests to the strict local backend, but those two layers must agree on how a request is framed.

That is the concrete problem addressed by **Fathom**. The earlier generated edge already imposed a 20 KB request-body limit. It could nevertheless stream a valid small body of unknown length upstream using transfer coding. The strict Waystation requires a definite `Content-Length` and accepts at most 16,384 bytes. A size limit alone did not make the two interfaces compatible.

The current deployment generator adds a 20,000-byte request buffer inside the reverse proxy. Every backend-admissible body fits within it, allowing a completely buffered request to be forwarded with a definite length. This is the behavior documented by [Caddy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy#streaming) and implemented in the targeted [v2.11.7 source](https://github.com/caddyserver/caddy/blob/v2.11.7/modules/caddyhttp/reverseproxy/reverseproxy.go). Incremental requests are outside this publication protocol. The buffer is a bounded per-request compatibility measure, not a total-memory, queue-capacity or denial-of-service guarantee.

This small change is significant because it joins two otherwise reasonable components without relaxing the backend's admission rules. It also continues a broader concern with honest outcomes: losing a response is not proof that no publication occurred, and automatic retries are not a substitute for knowing what happened.

## Read and continue the carried work

Begin with bootstrap sections 360–361 for the current revision. The HTML contains 150 named source members and a manifest-bound frame. `client.js` contains the reading, sharing, storage and connection workflows; `worker.ts` makes the identity and policy boundaries explicit; `native.py` contains the Waystation and deployment generator; `vendor.json` and the original source headers retain component provenance and notices.

The evidence supplement preserves the 46 reports and test-source files from the supplied outer ZIP without duplicating the large HTML and bootstrap. Extract it beside those two files to recover the supplied regular-file layout. `reports/REV0136-RECEIPT.md`, `reports/RESEARCH.md` and the verification records explain the measured framing problem, the proposed deployment behavior and the remaining qualification boundary. The supplied probe used controlled loopback proxy modes, not an installed Caddy/systemd/cgroup deployment. Read that evidence for what it establishes rather than turning it into a general production claim.

This is an HTML carrier, not the same mechanism as a newer native binary Datacube. Its continuity comes from carrying executable interfaces, readable source, tests, explanations and prior choices together. A later descendant can keep those useful materials while changing the interface, transport or construction approach.

## Exact current files

- `Vibechat.html`: 10,933,910 bytes; SHA-256 `e48f115825f5b35b4e2b749813da028b5dadea4e6321cd71f59a5bb755897a7e`.
- `BOOTSTRAPROSE.md`: 12,374,892 bytes; SHA-256 `cd4fbccfa5aa272fb012366b00ea64582cf9d82f24e3988da8ef5bd15a1c6dfb`.
- `Vibechat-rev0136-evidence.zip`: 96,169 bytes; SHA-256 `8700b5d2eb08a41fc2b8c61c18bc779f2ca41c45f38bb82f89b7e2fa34363188`.

The primary pair and every extracted supplemental file retain their supplied bytes. The supplement's ZIP wrapper is new; the received outer ZIP is identified by SHA-256 `1024aa46da52b06d8c88f5d7b4d16a098240d3849d415e2c7e1f67b3e04928b9`. Original attribution, MIT notices and the selected BLAKE2 reference terms remain carried, alongside the [external owner declaration](../../LEGAL-NOTICE.txt).

## Changelog

- **Received 2026-10-22 · rev0136 / Fathom** — A finite request buffer makes the generated edge's framing compatible with the strict Waystation without turning a size bound into a capacity claim.

[Foundry](../README.md) · [Catalog](../../CATALOG.md) · [W4R3Z](../../README.md)
