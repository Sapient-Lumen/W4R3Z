# c-toxcore 0.2.23 profile, text, receipt, and custom-packet contract — rev0006

**Evidence class:** source-reviewed plus exact-ABI mock/process tested  
**Reviewed:** 2026-08-13 America/New_York  
**Upstream target:** c-toxcore 0.2.23

## Primary sources

- https://raw.githubusercontent.com/TokTok/c-toxcore/v0.2.23/toxcore/tox.h
- https://github.com/TokTok/c-toxcore/releases/tag/v0.2.23
- https://github.com/TokTok/c-toxcore
- https://toktok.ltd/spec.html

The implementation was written against the tagged public header. The upstream source was
not downloaded or compiled in this cloudtainer, so API behavior is a source contract unless
this note explicitly says it was exercised against the exact loadable IoTox mock.

## Upstream state and caution

Version 0.2.23 was released on 2026-06-03. Its release notes identify a critical issue found
through manual review as well as additional memory-safety fixes. The upstream repository
continues to describe c-toxcore as experimental and not independently formally audited.
IoTox therefore treats toxcore as an important, actively maintained connection substrate,
not as the entire product security boundary.

## Serialization

The public API requires calls on a `Tox` instance to be serialized. rev0006 preserves one
exclusive owner thread for each `Tox*`; callbacks are normalized into bounded internal
events. Profile, messaging, typing, packets, files, friendship, and savedata all cross the
same owner-thread boundary.

## Runtime sizes are the contract

The header exposes runtime functions for public-key, address, savedata, file-ID, profile,
friend-request, message, and custom-packet limits. The header also warns that numeric
constants and public structure layouts are not permanent ABI promises. IoTox resolves and
validates the consumed function table at startup rather than spreading copied C declarations
through product code.

For 0.2.23 the reviewed limits relevant to rev0006 are:

```text
name                  128 bytes
status message        1007 bytes
friend request        921 bytes
normal/action text    1372 bytes
custom packet         1373 bytes total
```

## Presentation profile

The public API provides setters and getters for self name, status message, and user status;
user status values are available/none, away, and busy. Corresponding friend getters and
callbacks expose remote name, status message, and user status. Typing is a per-friend state.

rev0006 implements the exact consumed ABI in both dynamic and linked providers, projects raw
profile bytes into the private runtime tree, and verifies persistence through a process
restart against the ABI mock. Profile fields are transport presentation, not IoTox identity,
ownership, or authorization.

## Text and action messages

`tox_friend_send_message` accepts normal or action messages and returns a per-friend
`uint32_t` message ID. IDs begin at zero, increment, and may wrap. The corresponding friend
message callback does not supply that sender-side ID. rev0006 therefore journals:

```text
outgoing    kind + assigned message ID + exact body
incoming    kind + exact body; sender-side ID unavailable
receipt     correlated local message kind + receipt ID
```

The mock exercises normal/action send, callback echo, and receipt delivery. The process test
passes a body containing both NUL and newline through stdin, preserving the exact bytes into
the per-peer journal.

## What a receipt means

The header and protocol specification describe a receipt as evidence that the receiving
friend obtained the Tox text message. It is not an IoTox command receipt and cannot prove:

```text
authorization
durable acceptance
execution start
exactly-once behavior
physical completion
application result
```

IoTox device operations will use independent framed message IDs, correlation, expiry,
replay handling, authorization epochs, and application results.

## Lossless custom packets

The public API reserves custom lossless packet identifiers 69 and 160 through 191, provides
reliable ordered delivery within the custom-packet lane, and rejects packets above the
runtime maximum. IoTox currently uses discriminator `0xA0` (160) and a 41-byte bounded frame
header, leaving 1332 bytes for payload at the reviewed 1373-byte total limit.

rev0006 distinguishes three cases:

1. a raw lossless packet not beginning with `0xA0` remains raw transport;
2. a well-formed `0xA0` IoTox frame is decoded and placed in the private peer protocol journal;
3. a malformed `0xA0` candidate is not presented as a valid IoTox message.

The frame decoder is covered by unit tests and a Clang libFuzzer target. This is parser and
mock-process evidence, not real-peer network evidence.

## Public-key lookup

The official header exposes `tox_friend_by_public_key`. rev0006 currently resolves public
keys by asking the running agent for its peer list, then sends the local friend number over
the local control protocol. This keeps public operator syntax stable while the toxcore owner
thread remains the only API caller. A future internal optimization may use the upstream
lookup function without changing public behavior.

## Claims retained honestly

```text
source-reviewed                 official 0.2.23 profile/text/packet declarations
compiled                        IoTox-owned C++20 implementation with GCC and Clang
mock-ABI-tested                 exact consumed symbols and callbacks
process-tested                  one iotox run process plus one-binary control invocations
not source-linked here          official c-toxcore source was not compiled in this container
not real-peer-tested here       no DHT, NAT, relay, or cryptographic session claim
```
