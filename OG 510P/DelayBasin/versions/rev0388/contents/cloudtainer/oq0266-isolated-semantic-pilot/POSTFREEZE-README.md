# OQ-0266 isolated semantic pilot — postfreeze batch kit

Open this kit only after the prefreeze collector has produced the exact four-response lock. Verify the newly opened policy kit before custody or scoring, and preserve both read-only receipts. Cross-operator order is carried by exact artifact hashes; each tool checks clock order only inside its own process.

For each arm, replace `ARM` with its opaque arm code and run custody with both prerequisite receipts:

```sh
python -S tools/prepare_priority_zero_clean_response_custody_record.py \
  /path/to/ARM-response-final.json \
  --custodian-id DISTINCT-CUSTODIAN-ID \
  --pre-response-exposure-notes 'only the named one-arm responder bundle was visible before response' \
  --prerequisite response-set-lock=/path/to/oq0266-response-set-lock.json \
  --prerequisite postfreeze-policy-verification=/path/to/oq0266-postfreeze-policy-verification.json \
  --attest-clean-preanswer \
  --template cloudtainer/oq0266-isolated-semantic-pilot/arms/ARM/custody-template.json \
  --response-template cloudtainer/oq0266-isolated-semantic-pilot/arms/ARM/response-template.json \
  --out /path/to/ARM-custody-final.json
```

Then initialize the score sheet, fill every metric score/rationale plus the packet note, and finalize it:

```sh
python -S tools/prepare_priority_zero_external_replay_score_sheet.py init \
  /path/to/ARM-response-final.json \
  /path/to/ARM-custody-final.json \
  --scorer-id DISTINCT-SCORER-ID \
  --scorer-intake cloudtainer/oq0266-isolated-semantic-pilot/arms/ARM/scorer-intake.json \
  --template cloudtainer/oq0266-isolated-semantic-pilot/arms/ARM/score-sheet-template.json \
  --response-template cloudtainer/oq0266-isolated-semantic-pilot/arms/ARM/response-template.json \
  --out /path/to/ARM-score-draft.json
# edit only the draft's scoring fields
python -S tools/prepare_priority_zero_external_replay_score_sheet.py finalize \
  /path/to/ARM-response-final.json \
  /path/to/ARM-custody-final.json \
  --draft /path/to/ARM-score-draft.json \
  --scorer-id DISTINCT-SCORER-ID \
  --scorer-intake cloudtainer/oq0266-isolated-semantic-pilot/arms/ARM/scorer-intake.json \
  --template cloudtainer/oq0266-isolated-semantic-pilot/arms/ARM/score-sheet-template.json \
  --response-template cloudtainer/oq0266-isolated-semantic-pilot/arms/ARM/response-template.json \
  --scorer-notes 'evidence-grounded one-arm scoring completed after custody validation' \
  --attest-separated-scoring \
  --out /path/to/ARM-score-final.json
```

After all four exact triplets exist, do **not** hand-edit hashes into the template. Preserve the original prefreeze and postfreeze ZIPs, then assemble one self-contained evidence capsule in one command:

```sh
python -S cloudtainer/tools/prepare_oq0266_isolated_run_manifest.py \
  --prefreeze-dispatch-kit /path/to/original-prefreeze-dispatch-kit.zip \
  --postfreeze-batch-kit /path/to/original-postfreeze-batch-kit.zip \
  --response-set-lock /path/to/oq0266-response-set-lock.json \
  --policy-verification /path/to/oq0266-postfreeze-policy-verification.json \
  --response arm-7f2c=/path/to/arm-7f2c-response-final.json \
  --response arm-b91e=/path/to/arm-b91e-response-final.json \
  --response arm-d4a7=/path/to/arm-d4a7-response-final.json \
  --response arm-e263=/path/to/arm-e263-response-final.json \
  --evidence-record arm-7f2c=/path/to/arm-7f2c-custody-final.json \
  --evidence-record arm-b91e=/path/to/arm-b91e-custody-final.json \
  --evidence-record arm-d4a7=/path/to/arm-d4a7-custody-final.json \
  --evidence-record arm-e263=/path/to/arm-e263-custody-final.json \
  --score-sheet arm-7f2c=/path/to/arm-7f2c-score-final.json \
  --score-sheet arm-b91e=/path/to/arm-b91e-score-final.json \
  --score-sheet arm-d4a7=/path/to/arm-d4a7-score-final.json \
  --score-sheet arm-e263=/path/to/arm-e263-score-final.json \
  --template cloudtainer/oq0266-isolated-semantic-pilot/run-manifest-template.json \
  --out /path/to/oq0266-isolated-run-bundle.zip
```

Copy the SHA-256 printed by the assembler into a separate custody note or digest file. Only then run the final aggregator against the capsule and that separately preserved digest:

```sh
python -S cloudtainer/tools/score_oq0266_isolated_semantic_pilot.py \
  --run-bundle /path/to/oq0266-isolated-run-bundle.zip \
  --expected-run-bundle-sha256 PASTE-SEPARATELY-PRESERVED-SHA256 \
  --summary-out /path/to/isolated-batch-summary.json
```

The assembler fails before publication when either source kit is malformed or differs from the executing postfreeze root, an arm is missing, a response differs from the all-response lock, custody omits or substitutes either prerequisite receipt, or a score sheet does not bind the exact response and custody bytes. It copies both exact source kits and every dynamic artifact into one deterministic evidence capsule with an internal checksum manifest. The aggregator requires the separately preserved outer SHA-256, parses every nested ZIP with path and size bounds, replays only captured source-kit bytes, and refuses causal burden or global compact-default claims. Ambient pilot files may be deleted or mutated without changing replay.

Kit surface: `cloudtainer/oq0266-isolated-semantic-pilot/postfreeze-batch-kit.zip`. Local wall clocks and string identities remain descriptive observations, not trusted timestamping or proof of real-world independence.
