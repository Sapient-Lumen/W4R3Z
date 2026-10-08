# Adapter fuzz coverage

`adapterfuzz.py` is not a production fuzzer. It is a result algebra for deterministic mismatch cases.

The cube has accumulated many side-effect gates. That makes accidental cross-scope acceptance easy to miss. The rev0053 fuzz surface records deliberate mutations and asks whether each one reached the expected decision prefix.

Current observation fields:

```text
surface
mutation
expected_prefix
observed_decision
report_digest
family_id
path_family
```

The summary rejects:

- missing required mutations;
- too little surface diversity;
- unexpected accepts;
- watch-only outcomes when quarantine was required.

This keeps adapter/profile/handler mismatch testing visible without pretending we have a generative production fuzz engine yet.
