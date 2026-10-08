# Rev0864 audit

## Boundary question

Do the local socket harnesses establish a sender/receiver frame-integrity
relation before received bytes are decoded and durably admitted?

## Finding: the old evidence name exceeded the old evidence

The prior code assigned `socket_frame_digest = sha256_hex(received_frame)` and
then set `frame_digest_checked = true`. No expected digest existed at that
boundary. The code had measured one value, not checked a relation between two
values.

That is a direct instance of observation being promoted to authority. A digest
computed from received bytes cannot detect that those bytes differ from the
intended encoded frame unless it is compared with a commitment to the intended
frame.

## Correction

Rev0864 freezes the canonical encoded-frame digest before transmission and moves
received bytes into `SyncPeerTransportDigestBoundFrame::bind()`. Creation fails
unless all of the following hold:

- expected digest is canonical lowercase SHA-256;
- maximum frame bytes is positive;
- received bytes are nonempty;
- byte count round-trips through `uint64_t`;
- received bytes are within budget; and
- independently computed received digest exactly equals the frozen expected
  digest.

Only the resulting move-only owner exposes bytes to canonical decode. Both the
AF_UNIX socketpair and IPv4 loopback harnesses use the same owner. Durable ingress
enqueue is downstream of that bind point.

## Negative evidence

The focused test rejects uppercase and short expected digests, zero budget,
empty input, over-budget bytes, and sender/receiver mismatch. It also proves
binary byte preservation and move-only capability transfer.

## Scope boundary

The expected digest is generated locally by the fixture. This establishes that
the bytes received by the local socket path equal the bytes encoded before local
transmission. It does not authenticate a remote peer or establish a secure
channel. A production transport needs an authenticated transcript and sequence
or replay policy that makes the expected commitment remotely meaningful.

## Strategic finding

The local defect was worth fixing, but it is also symptomatic. AnonSync has a
large and increasingly exact authority/evidence apparatus while a production
remote peer protocol, whole-network convergence model, and anonymity threat
model remain unimplemented. The detailed evidence is in
`MISSION_GAP_MAP_rev0864.md` and `STRATEGIC_DEBT_SCAN.json`.

## Mechanical evidence

- GCC all-target build: passed;
- uninterrupted registry: 163/163;
- registered structural audits: 49/49;
- final dependency closure: zero work;
- focused GCC runtime: 11/11;
- Clang 17 `-Werror`: focused owner and integrated core built; focused 11/11;
- GCC ASan+UBSan: focused 11/11 with leak detection and halt-on-error;
- patch replay: 314/314 active files, eight intended changes, zero mismatch;
- parent verification: 26/26 ZIP and 22/22 directory.
