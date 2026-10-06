# OQ-0266 isolated semantic pilot — prefreeze dispatch kit

This is the only pilot-wide kit that may be opened before all four responses freeze. Do not open the full DelayBasin cube, the postfreeze kit, the assignment plan, custody templates, scorer intakes, or score sheets during collection.

Distribute exactly one nested responder ZIP to each genuinely separate responder. Never give a responder this whole dispatch kit or another arm. Preserve every original nested ZIP.

After all four finalized response JSON files return, but before opening any postfreeze material, run from this extracted kit root:

```sh
python -S cloudtainer/tools/lock_oq0266_isolated_response_set.py \
  --response arm-7f2c=/path/to/arm-7f2c-response-final.json \
  --response arm-b91e=/path/to/arm-b91e-response-final.json \
  --response arm-d4a7=/path/to/arm-d4a7-response-final.json \
  --response arm-e263=/path/to/arm-e263-response-final.json \
  --collector-id YOUR-STABLE-COLLECTOR-ID \
  --exposure-notes 'only the prefreeze dispatch kit and four finalized responses were visible' \
  --attest-clean-batch-barrier \
  --dispatch-manifest cloudtainer/oq0266-isolated-semantic-pilot/dispatch-manifest.json \
  --commitment cloudtainer/oq0266-isolated-semantic-pilot/assignment-commitment.json \
  --out /path/to/oq0266-response-set-lock.json
```

The command revalidates each exact response from the nested one-arm bundle, verifies that every responder-visible packet projection still matches the preanswer commitment, requires four distinct responder IDs plus a distinct collector, and freezes all response hashes plus collector-local receipt times in one read-only lock. Responder-reported times remain descriptive and are not compared to the collector clock. Only after that command succeeds may the postfreeze kit open.

After opening the postfreeze kit, but before custody or scoring begins, verify that its hidden assignment, scoring rules, exact responder-visible packet projections, scorer intakes, and executable validators match the commitment fixed before response:

```sh
python -S cloudtainer/tools/verify_oq0266_isolated_postfreeze_policy.py \
  --response-set-lock /path/to/oq0266-response-set-lock.json \
  --postfreeze-root /path/to/extracted-postfreeze-kit \
  --verifier-id YOUR-STABLE-VERIFIER-ID \
  --attest-postfreeze-opened-after-lock \
  --out /path/to/oq0266-postfreeze-policy-verification.json
```

Do not begin custody or scoring unless this no-clobber verifier succeeds. The final batch scorer revalidates the receipt against the current files, so later policy or tool substitution remains detectable.

Kit surface: `cloudtainer/oq0266-isolated-semantic-pilot/prefreeze-dispatch-kit.zip`. Exact artifact hashes carry cross-operator ordering; local clocks and string identities are recorded observations, not trusted timestamping or proof of real-world independence.
