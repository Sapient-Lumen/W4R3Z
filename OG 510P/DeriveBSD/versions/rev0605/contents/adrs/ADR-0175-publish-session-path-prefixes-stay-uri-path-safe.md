# ADR-0175: Publish-session path prefixes stay URI-path-safe

- Status: Accepted
- Date: 2026-03-19

## Context

ADR-0169 made `published_endpoint.path_prefix` part of the canonical `relay-url` endpoint tuple.
ADR-0172 then required that typed path surface to stay absolute and normalized instead of relying on later separator collapse or dot-segment cleanup.

That still left one smaller but practical ambiguity inside the path string itself:

**if `published_endpoint.path_prefix` is already the typed path floor, what keeps it from carrying raw spaces, backslashes, or percent-encoded reserved characters such as `%2F` and `%2E` that force later decode/canonicalization guesses?**

Without one more narrow decision, the archive can still produce receipts where the typed path surface and the copyable URL are string-equal but operationally ambiguous because support, CLI, UI, and future implementations must decide whether percent-decoding or filesystem-style cleanup should happen before comparison, routing, or display.

DeriveBSD does not need a full URL-canonicalization subsystem here, but it does need one coherent rule for the existing typed path field.

## Decision

1. `published_endpoint.path_prefix` remains the canonical typed path surface for the `relay-url` lane.

2. If present, it must stay **URI-path-safe** as already-serialized receipt state:
   - it stays an absolute normalized path prefix,
   - it uses only ordinary URI path characters for literal segments,
   - it must not carry raw spaces or backslashes,
   - and it must not carry percent-encoding (`%xx`) at all.

3. `published_endpoint.url_hint`, when present, must keep its parsed path exactly equal to that same already-serialized `published_endpoint.path_prefix`.

4. This ADR intentionally does **not** decide Unicode path policy, trailing-slash semantics, or richer endpoint objects.

## Consequences

- The typed path floor is now comparison-safe without a second hidden decode step.
- Support/UI/export no longer need to guess whether `%2F`, `%2E`, or raw spaces were meant to be presentation text, delimiter text, or later-normalized routing state.
- Future implementation can treat `path_prefix` as a compact typed artifact field instead of a generic URL-escaping bucket.

## Alternatives considered

- **Leave `published_endpoint.path_prefix` as any normalized slash-prefixed string.** Rejected because it still leaves percent-decoding and raw-space drift in the typed path field.
- **Allow percent-encoding but only forbid encoded `/` and `.`.** Rejected because it still requires readers to decide when decoding/comparison happens.
- **Normalize the entire final URL surface now.** Rejected as too wide for this round.
