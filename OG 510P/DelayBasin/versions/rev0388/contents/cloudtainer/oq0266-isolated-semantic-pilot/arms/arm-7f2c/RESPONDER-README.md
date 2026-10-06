# OQ-0266 isolated responder arm `arm-7f2c`

You have exactly one opaque cue arm. Do not seek another arm or open any post-freeze material.

From the extracted bundle root, preserve the original ZIP and run:

```sh
python -S tools/prepare_priority_zero_external_replay_response.py init \
  --bundle-file /path/to/original-arm-7f2c-responder-bundle.zip \
  --responder-id YOUR-STABLE-ID \
  --template cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-7f2c/response-template.json \
  --packet cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-7f2c/responder-packet.json \
  --out arm-7f2c-response-draft.json
```

Fill only the single packet answer row, its positive `operator_cost_minutes`, and the equal run total. Then, before seeing custody, scorer, assignment, other-arm, archive, manifest, or prior-conversation material:

```sh
python -S tools/prepare_priority_zero_external_replay_response.py finalize \
  --draft arm-7f2c-response-draft.json \
  --bundle-file /path/to/original-arm-7f2c-responder-bundle.zip \
  --template cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-7f2c/response-template.json \
  --packet cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-7f2c/responder-packet.json \
  --exposure-notes 'only the one-arm responder bundle was visible' \
  --attest-clean-preanswer \
  --out arm-7f2c-response-final.json
```

Give the exact final file to a distinct custodian. Do not edit it. Timing is descriptive only because each arm uses a different responder.
