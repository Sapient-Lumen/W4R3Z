# Second adapter brief

- generated_at: `2026-03-21T22:05:01Z`
- selected surface: `chatgpt`
- primary route hint: `https://help.openai.com/en/articles/9125172-the-chatgpt-home-page`
- first workflows: `surface-detect, receiver-resolve, composer-read, composer-write, turn-submit, latest-turn-read`

## Ordered phases

1. `route-anchor-baseline` — Prove the session is on the intended official browser surface and record the initial route, gate, and receiver posture.
2. `composer-baseline` — Find a writable composer using accessible, user-facing semantics before relying on brittle DOM details.
3. `submit-and-readback` — Prove the minimal generic chat lane: submit a benign probe turn, observe generation, and read back the latest assistant turn.
4. `bundle-and-promote` — Turn the first baseline into a named support bundle that can move the record beyond seeded planning.
