# Provider semantics after record ingress

`providersemantics.py` separates provider-record ingress from provider truth.

A provider record can be parsed, signed, and admitted while still being false, stale, overloaded, refused, or metadata-dangerous. The provider-semantic lane therefore requires challenge-bound proof, metadata budget, decoy budget, witness preservation, and family/path diversity before local acceptance.

Useful refusal is not success. It becomes watch/backoff evidence. False proof becomes sticky provider-false pressure. Raw content-key exposure quarantines.
