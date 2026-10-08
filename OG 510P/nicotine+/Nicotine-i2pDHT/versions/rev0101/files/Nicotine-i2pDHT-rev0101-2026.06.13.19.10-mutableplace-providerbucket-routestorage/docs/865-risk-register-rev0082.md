# Risk register — rev0082

Risks addressed:

- native leaf mismatch hidden by a successful compile;
- ABI drift hidden by dynamic loading;
- native artifact missing treated as a hard failure instead of portable fallback;
- native artifact mismatch treated as acceptable because fallback exists elsewhere;
- native-required profile launching without a proven native path;
- parity vectors too small or too same-shaped to catch obvious drift.

Risks deliberately not solved:

- production native ABI stability;
- sanitizer/fuzzer integration;
- constant-time crypto review;
- native parser safety;
- live router/SAM behavior;
- DHT Sybil/capture resistance.
