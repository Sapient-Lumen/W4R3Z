# OQ-0266 isolated responder arm `arm-e263`

You have exactly one opaque cue arm. Do not seek another arm or open any post-freeze material.

From the extracted bundle root, preserve the original ZIP and run:

```sh
python -S tools/prepare_priority_zero_external_replay_response.py init \
  --bundle-file /path/to/original-arm-e263-responder-bundle.zip \
  --responder-id YOUR-STABLE-ID \
  --template cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-e263/response-template.json \
  --packet cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-e263/responder-packet.json \
  --out arm-e263-response-draft.json
```

Fill only the single packet answer row, its positive `operator_cost_minutes`, and the equal run total. Then, before seeing custody, scorer, assignment, other-arm, archive, manifest, or prior-conversation material:

```sh
python -S tools/prepare_priority_zero_external_replay_response.py finalize \
  --draft arm-e263-response-draft.json \
  --bundle-file /path/to/original-arm-e263-responder-bundle.zip \
  --template cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-e263/response-template.json \
  --packet cloudtainer/oq0266-isolated-semantic-pilot/arms/arm-e263/responder-packet.json \
  --exposure-notes 'only the one-arm responder bundle was visible' \
  --attest-clean-preanswer \
  --out arm-e263-response-final.json
```

Give the exact final file to a distinct custodian. Do not edit it. Timing is descriptive only because each arm uses a different responder.
