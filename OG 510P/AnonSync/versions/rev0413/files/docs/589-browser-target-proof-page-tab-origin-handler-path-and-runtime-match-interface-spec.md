# Browser target proof page — tab origin, handler path, and runtime match interface spec

## Purpose

Make one simple browser question first-class:

> did this tab / link / handler open the runtime I intended, or did I merely reach some endpoint that answered?

This page appears when control was reached through a browser tab, protocol handler, bookmark, new-tab auto-open, copied URL, or manual host:port entry.

## Inputs

- intended target descriptor
- actual endpoint attestation object
- entry path (`manual-url`, `bookmark`, `auto-open-after-install`, `protocol-handler`, `browser-handoff`, `unknown`)
- referrer / origin when available
- runtime watermark match verdict
- storage-lineage match verdict
- audience/auth/transport match verdict
- mismatch explanation

## Primary questions this page must answer

1. What runtime was intended?
2. What runtime actually answered?
3. Did they match strongly enough for the action the user is about to take?
4. What caused the mismatch or uncertainty?
5. What is the least-destructive next move?

## Layout

### A. Match verdict strip

Fields:

- intended target label
- actual endpoint label
- match verdict (`exact-match`, `same-seat-different-surface`, `same-host-wrong-runtime`, `reachable-but-uncertain`, `mismatch`)
- recommended next move

### B. Intended vs actual comparison

Compare:

- runtime watermark
- host
- storage root
- principal / service account
- bind scope and port
- audience/auth/transport grade
- roster / identity cues

### C. Entry-path explanation card

Explain what path led here and what that path can and cannot prove.
Examples:

- `Auto-open after service install opened a tab, but migration vs clean world still needed runtime proof.`
- `Manual localhost entry proves reachability, not same-runtime continuity.`
- `Protocol handler fallback was unavailable, so manual entry was used and target proof is partial.`

### D. Mismatch-cause ladder

Possible causes:

- sibling runtime on same host
- service/profile switch
- config-path switch
- storage-root switch
- stale bookmark / stale tab
- browser trust residue
- unknown

### E. Safe next actions

Offer the narrowest justified action first:

- `re-attest endpoint`
- `compare sibling runtimes`
- `review endpoint switch`
- `recover control access on intended runtime`
- `stop and avoid mutation`

## Behavior rules

- Reaching an endpoint is not enough to promote the match verdict above `reachable-but-uncertain` without watermark or lineage match.
- The page must not let the user perform risky mutations on a `same-host-wrong-runtime` or `uncertain` verdict without explicit review.
- When the entry path itself is weak evidence, the product must say so plainly.

## Output object

```text
browser_target_proof {
  intended_target,
  actual_endpoint,
  entry_path,
  match_verdict,
  comparison_rows[],
  mismatch_causes[],
  next_actions[],
  strongest_safe_sentence,
  stronger_forbidden_sentence
}
```