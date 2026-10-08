# ChatGPT side-panel live gate

The side-panel proof submit button is now gated. It does not send the checkpoint prompt directly.

Before `prompt.submit`, the panel runs `fixture.capture` and checks the current ChatGPT surface against the active live contract facts that matter for safe submit:

- target adapter is `chatgpt`
- URL is on `https://chatgpt.com/`
- route posture is `plain-chat`
- prompt selector is `#prompt-textarea`
- composer readback exactly matches the checkpoint prompt
- strict send selector is `#composer-submit-button`
- send signal is explicit and not disqualified
- route-safe action policy is present
- known non-send composer controls, such as `#composer-plus-btn`, remain disqualified if observed
- generation is settled/idle before submit

If any blocker is present, the panel writes a `proof-live-gate-blocked` verdict and does not submit. If the gate passes, the following fields are attached to the submit action in the proof capture:

```json
{
  "proof_live_gate_verdict": "proof-live-gate-ok",
  "proof_live_gate_ok": true,
  "proof_live_gate_checked_at": "...",
  "proof_live_gate_expected": { "send_selector": "#composer-submit-button" },
  "proof_live_gate_observed": { "submit_selector": "#composer-submit-button" }
}
```

The evaluator now requires `proof_live_gate_ok_before_submit` for a live reviewable proof. Offline rehearsal includes this field but still returns `rehearsal-harness-ok-not-live` rather than a live verdict.
