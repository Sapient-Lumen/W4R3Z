# ADR-0099: Packet capture selector compiler boundary

- Status: Accepted
- Date: 2026-03-08

## Context

`adrs/ADR-0097-packet-capture-session-and-summary-first-export-boundary.md` made packet capture a bounded typed session,
and `adrs/ADR-0098-packet-capture-summary-review-surface-boundary.md` gave it a compact evidence-first review object.

One portability trap still remained inside the authoritative session shape:
`packet.capture.session.capture.filter` was a free-form capture-filter string.

That looks small, but it quietly reintroduces backend folklore:

- the authoritative review surface starts depending on libpcap/tcpdump expression details,
- available syntax varies with the capture stack and installed library version,
- backend-specific arithmetic and extensions become part of the archive contract by accident,
- and review diffs become harder because the durable object is "whatever filter string happened to work" rather than a typed selector.

DeriveBSD needs one narrower answer:
**the authoritative capture session should carry a typed selector, and backend filter expressions should be compiled consequences rather than the review surface itself.**

## Decision

1. Introduce `packet.capture.selector` as the canonical typed selector object for bounded packet capture.
   It records only the review-stable capture intent:
   - direction,
   - address family / transport class,
   - host / CIDR / hostname matches,
   - port matches,
   - and a small bounded set of other portable constraints.

2. Replace the free-form `capture.filter` field in `packet.capture.session` with `capture.selector`.
   - `packet.capture.session` remains the authoritative pre-capture review object,
   - the selector is what humans review and approve,
   - and backend-specific filter strings are implementation detail.

3. Treat backend filter strings as compiled consequences, not archive authority.
   - an implementation may compile a selector to a BPF/libpcap expression or another backend-specific form,
   - but that compiled form belongs in ephemeral execution state or future receipts,
   - not as the canonical reviewed session field.

4. Keep the selector vocabulary deliberately small.
   - support the common incident/maintenance cuts first,
   - do not import the full libpcap grammar into the archive,
   - and require future broadening to be explicit rather than implied by backend behavior.

## Consequences

- Packet-capture review becomes more portable and less backend-dependent.
- Session diffs become easier to reason about because they compare typed intent instead of parser folklore.
- FreeBSD `bpf(4)` / `tcpdump(1)` / libpcap remain viable implementation backends without becoming the product boundary.
- A small guardrail can keep the schema, example, and docs from drifting back toward raw filter strings.

## Why this is narrow enough

This ADR does **not** standardize:

- the exact compiler from selector → backend filter,
- the exact execution receipt for compiled backend filters,
- every protocol-specific matcher under the sun,
- or the full packet-analysis / incident workflow.

It only fixes the authoritative review surface so bounded packet capture does not quietly inherit libpcap syntax as archive law.
