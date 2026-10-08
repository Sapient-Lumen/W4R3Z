# Public trace prompt manifest audit — REV0117

Status: `pass_with_blockers`  
Promotion allowed: `false`

## Result

- good prompt manifest verified: `True`
- forged prompt manifest rejected: `True`
- forged rejection reason: `prompt manifest contract was not verified: prompt manifest entry 0 text hash mismatch`

## Interpretation

Prompt/token digests now have a replayable public manifest: exact prompt text, explicit tokenizer-call knobs, and tokenizer surface facts must agree with input_ids/attention_mask/text hashes. The forged manifest keeps dense Q/K/V parity and a valid manifest digest but changes the prompt text, and the gate rejects it.
