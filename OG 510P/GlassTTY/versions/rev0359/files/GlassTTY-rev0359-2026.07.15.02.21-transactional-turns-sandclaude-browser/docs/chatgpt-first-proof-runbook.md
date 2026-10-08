# ChatGPT first-proof runbook — plain-chat checkpoint wedge

This runbook is intentionally narrow. It captures one text-only ChatGPT plain-chat proof for the `GLASSTTY-CHECKPOINT` prompt. It does not prove Search, Projects, GPTs, Canvas, files, voice, apps, agents, shared links, data analysis, image generation, desktop apps, mobile surfaces, or support widening.

## Stop sign

No live ChatGPT proof exists until a bundle passes `scripts/chatgpt-first-proof-evaluator.py` schema v20 and a human privacy/redaction review. A reviewable evaluator result is still local evidence only; it is not a public-citable support claim. Rev0325 also requires a top-level `privacy_redaction_review` object in the bundle before the evaluator can return reviewable.

## Required bundle shape

Use one shared `attempt_id` for every artifact. Use one explicit `tab_id` for write, submit, latest, and post-latest settled rows. Keep monotonically increasing `sequence_index` values.

Expected output folder:

```text
validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/
```

Required core files:

```text
route-witness.json
surface-screenshot.png
receiver-posture.md
composer-candidates.json
composer-before.txt
composer-after.txt
composer-witness-receipt.json
probe-prompt.txt
submit-evidence.json
submit-prompt-readback.json
generation-timeline.json
transcript-latest-action.json
assistant-output-witness.json
assistant-output-text-coherence.json
assistant-witness-scope.json
user-turn-witness.json
user-witness-scope.json
turn-pair-order-witness.json
turn-pair-frame-context-witness.json
same-tab-context-witness.json
same-conversation-route-witness.json
route-transition-witness.json
exact-readback-witness.json
settled-generation-witness.json
settled-generation-sequence-witness.json
bundle-manifest.json
bundle-schema-validation.json
chatgpt-first-proof-bundle-audit.json
chatgpt-first-proof-evaluation.json
privacy-redaction-review.md
```

## Single-path capture steps

1. Open `https://chatgpt.com/` in a normal plain-chat lane. Do not enter Projects, GPT builder, Canvas, Search, file upload, voice, apps, agent/task mode, or shared-link flows.
2. Capture the route baseline with `route_posture: plain-chat`, `adapter: chatgpt`, the active URL, and the current `tab_id`.
3. Generate one `attempt_id`, then use it for every subsequent artifact.
4. Write exactly this prompt into the active composer:

```text
Reply with exactly this text and nothing else: GLASSTTY-CHECKPOINT
```

5. Capture the winning `prompt.write` row. Its readback must exactly equal the prompt after whitespace normalization. A substring match is only a diagnostic failure.
6. Capture composer candidates and the selected composer witness. Keep at least one rejected candidate when possible.
7. Before submit, capture the submit-time composer readback on the same row that will carry `prompt.submit`.
8. Submit only through the dedicated side-panel proof submit control. The submit row must carry `operator_submit_confirmed: true`, a side-panel/manual operator click method, and the exact submit-time readback.
9. Wait for a route transition from root/plain-chat posture to `https://chatgpt.com/c/<conversation-id>`.
10. Read the latest assistant turn only after the route is on `/c/<conversation-id>`.
11. Capture the latest assistant witness from a leaf-like assistant turn node, not from a parent wrapper, thread container, main region, or mixed user+assistant text block.
12. Capture the visible user turn witness whose text exactly equals the checkpoint prompt.
13. Capture document-order evidence proving the user turn comes before the assistant turn in the same explicit frame context. Top-frame evidence must say `frame_depth: 0`; nested-frame evidence must include a stable `frame_path`.
14. Capture a later `fixture.capture` or `state.snapshot` after the latest read. It must have a later `sequence_index`, the same `tab_id`, a ChatGPT URL/adapter witness, a settled/idle generation state, `generation_stop_control_present: false`, and the same `/c/<conversation-id>` route path as the latest read.
15. Run the artifact ledger so missing files and attempt-id drift are visible before schema/evaluator review:

```bash
python scripts/chatgpt-first-proof-artifact-ledger.py audit \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --output-dir validation/latest/chatgpt-first-proof-artifact-ledger \
  --readiness-level evaluator-ready \
  --pretty
```

16. Validate the bundle manifest against the structural schema:

```bash
python scripts/chatgpt-first-proof-schema-validation.py validate \
  --input validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/bundle-manifest.json \
  --output-dir validation/latest/chatgpt-first-proof-schema-validation \
  --pretty
```

17. Run the bundle audit before human review:

```bash
python scripts/chatgpt-first-proof-bundle-audit.py audit \
  --input validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/bundle-manifest.json \
  --output-dir validation/latest/chatgpt-first-proof-bundle-audit \
  --pretty
```

18. Run the evaluator:

```bash
python scripts/chatgpt-first-proof-evaluator.py evaluate \
  --input validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/bundle-manifest.json \
  --output-dir validation/latest/chatgpt-first-proof-evaluation \
  --pretty
```

19. Complete `privacy-redaction-review.md` before copying any screenshot, trace, transcript, account label, or route artifact into publication/support surfaces.

## Acceptance gate

A bundle must pass all schema v20 evaluator checks, including exact write/submit readbacks, root-to-`/c/` route transition, one coherent attempt, same tab, same conversation, non-aggregate turn witnesses, user-before-assistant order, post-latest settled witness, route-safe submit policy, a top-level privacy-redaction-review record, and no cross-surface conflicts.
