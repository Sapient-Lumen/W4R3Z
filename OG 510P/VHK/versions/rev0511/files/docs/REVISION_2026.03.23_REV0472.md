# Revision 0472 — receipt target evidence and selector canonicalization

This revision strengthens the resident checked-dispatch receipt lane instead of widening platform scope.

## What changed

- canonicalized dispatch-receipt selector comparison so omitted selector defaults and explicit `false` flags do not create false receipt drift
- classified `latest_dispatch.target_authority_evidence` from the stored checked-gate target witness
- mirrored receipt-scoped target-authority truth into `primary_macro_work_ticket.latest_dispatch_handoff`
- added focused tests for current receipt target proof and selected-macro handoff projection

## Why it matters

The resident control plane can now keep saying not only whether a receipt is current, but whether the last bounded X11/i3 target proof actually matched, mismatched, or was weak. That keeps the private-LLM/operator loop closer to the right next inspect/recheck command before another warm checked dispatch.
