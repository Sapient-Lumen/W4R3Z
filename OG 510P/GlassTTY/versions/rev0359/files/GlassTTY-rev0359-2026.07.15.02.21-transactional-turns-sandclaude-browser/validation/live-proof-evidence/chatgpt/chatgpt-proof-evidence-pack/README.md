# ChatGPT live proof evidence pack

Bundle: ChatGPT — plain-chat route-first `GLASSTTY-CHECKPOINT` proof bundle
Wave: Wave 1 — text-only checkpoint wedge
Evidence pack key: `chatgpt-proof-evidence-pack`

This pack is for one narrow live run on `chatgpt.com` plain chat. Do not capture Search, Projects, GPTs, Canvas, files, voice, apps, agent/task mode, shared links, data analysis, image generation, desktop apps, mobile surfaces, or any public-support wording here.

No support claims are widened by filling this folder. The bundle must pass `scripts/chatgpt-first-proof-evaluator.py` schema v20 and a human privacy/redaction review before any downstream support/publication surface may use it.

| order | expected filename | purpose |
|---:|---|---|
| 1 | `route-witness.json` | Record `adapter: chatgpt`, host, URL, `tab_id`, and `route_posture: plain-chat` before the write. |
| 2 | `surface-screenshot.png` | Preserve the visible plain-chat surface for local review. Redaction review is mandatory before publication. |
| 3 | `receiver-posture.md` | Human note confirming no Projects/GPTs/Canvas/Search/files/voice/apps/agent branch was entered. |
| 4 | `composer-candidates.json` | Preserve selected and rejected composer candidates with selector/actionability reasons. |
| 5 | `composer-before.txt` | Composer text before write. |
| 6 | `composer-after.txt` | Composer text after write; must exactly equal the checkpoint prompt after whitespace normalization. |
| 7 | `composer-witness-receipt.json` | Machine-readable write witness with selected composer metadata. |
| 8 | `probe-prompt.txt` | Exact prompt: `Reply with exactly this text and nothing else: GLASSTTY-CHECKPOINT`. |
| 9 | `submit-evidence.json` | Operator-attested side-panel submit row with URL, adapter, `tab_id`, and sequence index. |
| 10 | `submit-prompt-readback.json` | Submit-time composer readback on the same submit row; must exactly equal the prompt. |
| 11 | `generation-timeline.json` | Route and generation state transitions after submit. |
| 12 | `transcript-latest-action.json` | Latest assistant read on `https://chatgpt.com/c/<conversation-id>` with exact `GLASSTTY-CHECKPOINT` text. |
| 13 | `assistant-output-witness.json` | Leaf-like assistant turn witness with selector, role, order, frame, and text metadata. |
| 14 | `assistant-output-text-coherence.json` | Proof that witness text exactly matches the latest reply. |
| 15 | `assistant-witness-scope.json` | Proof the assistant witness is not a parent/thread/wrapper containing user+assistant text. |
| 16 | `user-turn-witness.json` | Visible user turn witness whose text exactly equals the checkpoint prompt. |
| 17 | `user-witness-scope.json` | Proof the user witness is not a parent/thread/wrapper containing user+assistant text. |
| 18 | `turn-pair-order-witness.json` | User-before-assistant `document_order_index` evidence. |
| 19 | `turn-pair-frame-context-witness.json` | Explicit same-frame context: top frame uses `frame_depth: 0`; nested frames include `frame_path`. |
| 20 | `same-tab-context-witness.json` | Same explicit `tab_id` across write, submit, latest, and settled witness. |
| 21 | `same-conversation-route-witness.json` | Same normalized `/c/<conversation-id>` path between latest and post-latest settled witness. |
| 22 | `route-transition-witness.json` | Evidence of root/plain-chat to `/c/<conversation-id>` transition after submit. |
| 23 | `exact-readback-witness.json` | Combined write and submit exact-readback proof. |
| 24 | `settled-generation-witness.json` | Post-latest settled/idle generation state with no stop control present. |
| 25 | `settled-generation-sequence-witness.json` | Later-sequenced settled fixture/snapshot with ChatGPT URL/adapter witness. |
| 26 | `bundle-manifest.json` | Single manifest joining all artifacts under one `attempt_id`. |
| 27 | `bundle-schema-validation.json` | Structural validation against `schemas/chatgpt-first-proof-bundle.schema.json`. |
| 28 | `chatgpt-first-proof-bundle-audit.json` | Local action graph, attempt summary, and check-registry audit before evaluator review. |
| 29 | `chatgpt-first-proof-evaluation.json` | Output from the schema v20 proof evaluator. |
| 30 | `privacy-redaction-review.md` | Human redaction decision before any publication/support use. |

Recommended materiality, schema, audit, and evaluator commands after `bundle-manifest.json` exists:

```bash
python scripts/chatgpt-first-proof-artifact-ledger.py audit \
  --pack-dir validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack \
  --output-dir validation/latest/chatgpt-first-proof-artifact-ledger \
  --readiness-level evaluator-ready \
  --pretty

python scripts/chatgpt-first-proof-schema-validation.py validate \
  --input validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/bundle-manifest.json \
  --output-dir validation/latest/chatgpt-first-proof-schema-validation \
  --pretty

python scripts/chatgpt-first-proof-bundle-audit.py audit \
  --input validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/bundle-manifest.json \
  --output-dir validation/latest/chatgpt-first-proof-bundle-audit \
  --pretty

python scripts/chatgpt-first-proof-evaluator.py evaluate \
  --input validation/live-proof-evidence/chatgpt/chatgpt-proof-evidence-pack/bundle-manifest.json \
  --output-dir validation/latest/chatgpt-first-proof-evaluation \
  --pretty
```
