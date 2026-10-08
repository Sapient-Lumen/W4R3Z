# AnonSync rev0841

## Mission increment

A signed transition is one exact publication, not a signature over one hand-built value
followed by JSON emission from broader live objects. Freeze the complete payload, validate
its byte and semantic contracts, derive invariant signing bytes, bind the digest and
signature to that frozen value, and emit only that value.

## Delivered

- New dependency-light C++ owner:
  `persistence::FrozenEffectTransitionIntentV3Payload`.
- New v3 wire format:
  `anonsync-effect-transition-intent-v3-framed-publication`.
- Length-prefixed, field-named signing input rather than context-sensitive newline
  concatenation.
- Locale-independent integer spelling through `std::to_chars`.
- Exact JSON integer ceiling of `2^53 - 1` for the project parser's numeric model.
- Canonical UTC, terminal-state, SHA-256, UTF-8, control-character, and byte-budget
  validation at the frozen owner.
- Signing-input SHA-256 recomputation before publication can emit JSON.
- Unpadded base64url signature validation and bounded signer/signature/output sizes.
- Production relay maps the broad claim/result model once, freezes once, signs the exact
  v3 bytes, and emits the same frozen publication.
- Verifier reads legacy v2 and current v3; production no longer mints v2.
- Every remaining `std::ostringstream` construction in `sqlite_replay_ledger.cpp` now
  explicitly uses `std::locale::classic()`.
- A 34-check standalone C++ corpus covering frozen ownership, v2 compatibility, v3 byte
  framing, exact-number limits, malformed UTF-8, impossible timestamps, controls,
  escaping, digest binding, signature grammar, budgets, and hostile global locale.
- Relay integration now executes under a custom grouped global locale and proves that
  production v3 output remains valid and verifiable.

## Parent defect reproduced

The rev0840 relay serializer used ambient stream locale for `prepared_sequence`. Under a
legal custom C++ locale, sequence `7000` became `7_000` in both the signing input and JSON.
The resulting JSON is rejected by a strict parser, and the signed bytes differ from those
created under the classic locale. The parent also constructed signing input and JSON in
separate code paths from broad live objects, preserving two sources of truth.

## Validation

- Standalone publication boundary: **34/34**.
- Legacy/current signed-transition integration: **8/8**.
- Relay crash/retry/idempotency integration under grouped locale: **11/11**.
- Snapshot-manifest compatibility: **23/23**.
- GCC 14.2 Debug all-target build: **PASS**.
- Complete final CTest inventory: **133/133**, including **39/39** registered audits.
- Clang 17 `-Werror` focused boundary/integration set: **PASS**.
- GCC 14 ASan+UBSan with leak detection: leaf **34/34** and relay **11/11**.
- Final dependency closure: `ninja: no work to do.`

## Architectural interpretation

AnonSync's strongest implemented identity is a fail-closed local authority, integrity,
and recovery kernel. It does not yet contain an executable distributed convergence
algebra, a complete cross-resource crash oracle, hostile-input worker isolation, or the
privacy/key lifecycle needed to justify “Anon” as a product guarantee. Those are now the
highest-value missing layers; more lexical audit volume is not a substitute for them.

## Scope limits

No RFC 8785/JCS compliance, canonical JSON generally, full-project sanitizer, Release
all-target build, arbitrary power-loss completeness, Windows runtime result, distributed
convergence proof, payload confidentiality, anonymity, metadata hiding, forward secrecy,
post-compromise recovery, hostile-worker sandbox, or secure erasure is claimed.

## Handoff

See `REVISION_EVIDENCE/rev0841/AUDIT.md`, `RESEARCH.md`, `NEXT_WORK.md`, and
`validation/VALIDATION_SUMMARY.json`.
