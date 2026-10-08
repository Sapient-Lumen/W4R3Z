# Control endpoint attestation page — runtime watermark, audience, and storage lineage interface spec

## Purpose

Give the operator one reviewed answer to:

- which runtime this control endpoint belongs to
- what durable storage and seat lineage back it
- what audience/auth/transport grade this endpoint currently has
- whether the current browser state is clean, stale, or residue-contaminated
- what stronger sentence the product must forbid

This page is the control-surface companion to runtime-profile, control-grade, and instance-namespace pages.
It should appear whenever a browser or web endpoint can plausibly point at more than one runtime world or continuity class.

## Inputs

- endpoint identifier
- runtime watermark / runtime id
- host label
- control modality (`webui`, `embedded-web`, `browser-handoff`, `service-web`, `unknown`)
- listener tuple (`scheme`, `host`, `port`, `bind_scope`)
- audience grade
- auth grade
- transport / certificate grade
- storage root id / path summary
- config path summary if any
- seat-lineage verdict (`same-known-seat`, `same-runtime-new-surface`, `sibling-runtime`, `fresh-runtime`, `uncertain`)
- browser residue class (`none`, `cookie-only`, `hsts-residue`, `certificate-exception`, `unknown`)
- strongest safe sentence
- stronger forbidden sentence

## Primary questions this page must answer

1. What runtime world owns this endpoint right now?
2. What storage world backs it?
3. Is this the same control world I used before?
4. How reachable is it, and by whom?
5. What browser residue or warning context is still distorting confidence?

## Layout

### A. Endpoint verdict strip

Fields:

- endpoint label
- runtime watermark
- current seat-lineage verdict
- current endpoint grade summary
- strongest safe sentence

Example verdicts:

- `Loopback endpoint; same known runtime; storage lineage preserved`
- `LAN-visible endpoint; sibling runtime suspected; storage lineage differs`
- `Endpoint reached; runtime attribution incomplete`

### B. Runtime watermark card

Show:

- runtime watermark token
- host label
- runtime kind
- principal / service account
- process / service status if known
- first-seen / last-confirmed timestamps

This card exists so the operator can stop using URL memory as identity.

### C. Storage lineage card

Show:

- storage-root fingerprint or short handle
- default vs configured storage
- config-path fingerprint if present
- seat-lineage verdict
- carryover evidence summary (`shares`, `identity`, `logs`, `settings`, `credentials`)

### D. Endpoint-grade card

Show:

- audience scope (`loopback-only`, `local-lan`, `wider-network`, `unknown`)
- auth floor (`none`, `password-optional`, `password-present`, `config-enforced`, `unknown`)
- transport posture (`http`, `https-self-signed`, `https-trusted`, `unknown`)
- browser-residue delta
- fallback control path

### E. Claim-ceiling card

Show three sentences together:

- strongest approved sentence
- stronger forbidden sentence
- what missing proof blocks the stronger claim

Example:

- approved: `You are controlling the loopback WebUI for runtime W7 backed by storage S3.`
- forbidden: `You are definitely back in the exact same admin surface as yesterday.`
- blocker: `seat-lineage confidence is still partial after service/profile switch.`

### F. Adjacent actions

Offer only actions that preserve attribution clarity:

- `Review endpoint switch`
- `Open browser target proof`
- `Compare sibling runtimes`
- `Open control access recovery`
- `Export endpoint receipt`

## Behavior rules

- This page must appear before any destructive control-plane action when endpoint identity is not already high-confidence.
- URLs, successful auth, and visible folders are supporting evidence, not sufficient identity on their own.
- If runtime watermark or storage lineage is uncertain, the page must downgrade the claim ceiling immediately.
- Browser residue findings must never be silently merged into endpoint trust; they must be shown as a separate delta.

## Output object

```text
control_endpoint_attestation {
  endpoint_id,
  runtime_watermark,
  host_label,
  modality,
  listener_tuple,
  audience_grade,
  auth_grade,
  transport_grade,
  storage_lineage,
  seat_lineage_verdict,
  browser_residue_class,
  strongest_safe_sentence,
  stronger_forbidden_sentence,
  next_review_actions[]
}
```