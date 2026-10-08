# Public trace prompt manifest contract — REV0102

Public score-path traces must include a replayable prompt manifest, not only hashes.

Required tokenizer call:

```text
add_special_tokens=True
padding=False
truncation=False
return_attention_mask=True
return_tensors="pt"
chat_template_applied=False
```

The manifest binds exact prompt text, text SHA-256, input_ids SHA-256, attention_mask SHA-256, token count, and attention-mask sum for every prompt. A dense-parity-valid trace with mismatched prompt text must fail the public gate.
