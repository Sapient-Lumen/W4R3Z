# ADR-0304: Breakglass supplementary adapter side evidence stays artifactized and off live control locators

- Status: Accepted
- Date: 2026-03-23

## Context

`ADR-0301` fixed official support handoff to stay authority-first on exact `breakglass.receipt` digests.
`ADR-0302` then fixed that if richer supplementary breakglass adapter/runtime material travels before a dedicated typed family exists, the portable story stays receipt-first on typed redaction/export/transport proof instead of raw case-attachment folklore.
`ADR-0303` then fixed that those supplementary receipt chains still need the exact `breakglass.receipt` digest in the same portable story.

That still leaves one expensive ambiguity:

**can the portable story still carry live management entry hints — console URLs, copied `ConsoleEntryCommand` values, `WebSocketEndpoint` strings, virtual-media image locators, or session tokens — as if they were evidence?**

If the archive leaves this fuzzy, implementations will drift toward another bad shortcut:

1. a support bundle or case handoff includes a live console URL, websocket endpoint, or copied entry command because it was visible during the breakglass ceremony,
2. later reviewers treat that locator as the portable identity of the supplementary side evidence,
3. but the value is really an active control entrypoint or ephemeral bootstrap hint, not stable review truth,
4. and the archive quietly leaks live management surface detail into places that are supposed to carry artifactized evidence instead.

Receipt-first plus authority-anchor is not enough if the final portable surface can still smuggle active control locators as “evidence”.

## Decision

1. Supplementary breakglass adapter/runtime material may travel portably only as **artifactized evidence** or the typed handling receipts that describe that artifact.

2. Live control locators and entry hints do **not** belong in the portable archive-facing story for supplementary breakglass adapter/runtime material. That includes console URLs, copied `ConsoleEntryCommand` values, `WebSocketEndpoint` strings, virtual-media image locators, and session ids/tokens.

3. `incident.bundle.includes.extra[]`, external case attachments, and the associated redaction/export/transport receipt chain may still refer to exported artifacts or accepted case objects, but not to active console-entry surfaces.

4. Operational re-entry or live-session coordination remains an ephemeral support channel concern, not portable evidence. If operators need to reconnect, that workflow should be satisfied by the management system or a fresh reviewed approval path, not by replaying a locator that leaked into the archive.

5. This decision does **not** mint a dedicated typed family for richer adapter-side evidence, and it does **not** standardize per-artifact/session joins. It only closes the smaller leak worth fixing immediately: portable supplementary evidence stays artifactized instead of carrying live control entrypoints.

## Consequences

Good:

- portable support/export stories stay on stable artifacts and typed receipts instead of active management entrypoints
- the archive stops implying that ephemeral console or virtual-media locators are review truth
- and detached review leaks less vendor/runtime-specific control detail

Costs:

- some operational runbooks that copied console URLs or websocket endpoints into ticket notes will now be recognized as non-portable support detail
- support/export tooling must keep live reconnect instructions out of the archive-facing evidence path
- and future richer adapter-side-evidence work still needs separate RFC/ADR treatment if stronger typed linking is desired

## Why this is the right narrow cut

The primary management sources describe these values as control surfaces rather than durable evidence identity. DMTF’s Redfish material describes `ConsoleEntryCommand` as scripted connection arguments for entering a console, Intel’s OpenBMC Redfish API specification exposes `WebSocketEndpoint` as the endpoint socket name/location for virtual-media interaction, and Dell’s iDRAC security guidance describes virtual console as a browser-launched remote-control surface. Those are exactly the kinds of values DeriveBSD should keep out of its portable evidence story: useful for live operations, but too active, volatile, and security-sensitive to masquerade as artifact truth.

## Follow-on

Still open as later work:

- whether a dedicated breakglass adapter-side-evidence family should later carry opaque external-case handles under stricter typed rules
- whether future richer typed artifacts need same-session joins or review-specific rendering
- and whether some product shapes want stricter defaults that suppress supplementary adapter/runtime material entirely
