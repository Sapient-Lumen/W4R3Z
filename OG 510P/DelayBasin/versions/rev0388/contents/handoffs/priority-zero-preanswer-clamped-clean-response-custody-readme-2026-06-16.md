# Priority-0 preanswer-clamped post-freeze custody kit — 2026-06-16

Open this kit only after the responder-bundle helper has finalized a response produced from the responder bundle alone. The exact response must remain byte-identical.

From the extracted custody-kit root:

```bash
python -S tools/prepare_priority_zero_clean_response_custody_record.py \
  <frozen-response.json> \
  --custodian-id <id-different-from-responder> \
  --pre-response-exposure-notes "only the responder bundle was visible before response finalization" \
  --attest-clean-preanswer \
  --out <completed-custody-record.json>
```

The helper starts its custody clock when invoked, then:

1. strictly parses the response and rejects duplicate keys/non-standard numbers;
2. reruns the same scorer-free `responder-finalize-v1` contract used in the responder bundle;
3. rejects incomplete answers, invalid or unreconciled cost, hash drift, response-artifact drift, or an unfinalized/hand-built response;
4. records a custodian-local observation of the exact response bytes and binds their SHA-256;
5. verifies the expected responder ZIP and packet digests from the post-freeze custody template;
6. binds every prerequisite receipt required by that template (none for the conventional run; response-set lock and policy-verification receipt for the isolated pilot);
7. rejects self-custody;
8. captures custody-record freeze time from its local process clock; and
9. writes a new record without overwriting an existing artifact.

No response, custody-open, or custody-freeze timestamp is accepted as a CLI argument. This removes easy transcription/backfill errors. Responder and custodian clocks are descriptive and are ordered only inside their producing process; exact response and prerequisite hashes carry causality across operators or machines.

Freeze the generated custody record before opening the scorer kit, scorer intake, score-sheet template, handoff manifest, expected digest, or answer key. The custody record deliberately contains no future scorer-open time. Give the scorer the exact frozen response and exact frozen custody record. Score-sheet initialization reruns this same complete custody contract before any scoring draft is created, so a tampered or hand-built custody artifact fails at the scorer boundary rather than only at final scoring.

The custodian may later serve as scorer, but the scorer ID must differ from the responder ID, preserving a minimum of two distinct operators.

Non-claim: custody evidence establishes a local observation sequence and exact artifact identity only. It is not compact-cue confirmation, deletion authority, benchmark authority, independent certification by itself, or a review court.
