# RecallRoot-v1 offline-guessing model

**Revision:** rev0002  
**Purpose:** make the accepted fixed-salt trade explicit and numerically inspectable, without pretending that a simple estimate is a security proof.

## Uniform v1 space

RecallRoot-v1 uses exactly eight independent choices from a 7,776-entry list:

```text
candidate space = 7776^8
                = 13,367,494,538,843,734,067,838,845,976,576
entropy         = log2(7776^8)
                ≈ 103.3985 bits
median search   ≈ 6.6837 × 10^30 candidates
```

Illustrative median-search times, assuming a fantastically constant aggregate guessing rate and no operational bottleneck:

| Aggregate guesses/second | Approximate median years |
|---:|---:|
| 1 | 2.12 × 10^23 |
| 1,000 | 2.12 × 10^20 |
| 1,000,000 | 2.12 × 10^17 |
| 1,000,000,000 | 2.12 × 10^14 |

The billion-per-second row is not a claim about Argon2id hardware. It is included to show that uniformly generated v1 phrases do not depend on optimistic estimates of one specific CPU or GPU. The search space is the primary protection; Argon2id adds substantial cost per candidate.

## What destroys the calculation

The 103.4-bit statement does not apply when:

- the owner invents words;
- a phrase is a quotation, lyric, slogan, mnemonic sentence, or themed list;
- generation is biased or modulo-reduced incorrectly;
- the same phrase is intentionally reused from another system;
- malware observes generation or entry;
- the printed card is photographed;
- the phrase enters cloud notes, screenshots, logs, argv, clipboard history, crash dumps, telemetry, or support tickets;
- implementation normalization differs from the frozen contract.

For a genuinely generated phrase, physical capture and endpoint compromise are more plausible than exhaustive guessing. That does not excuse weak generation; it clarifies where engineering and product education must concentrate.

## Fixed salt consequences

The public fixed salt is not an accidental omission. Stateless reproduction requires that a remembered phrase produce the same root without fetching a per-owner record.

The consequences are permanent:

- guesses can be tested offline;
- there is no online lockout or rate limit;
- one computed candidate applies to every user of the same contract;
- a repeated phrase produces a repeated recall root;
- a vendor-side pepper is impossible because it would reintroduce vendor dependence;
- changing parameters later creates a new contract version rather than silently strengthening v1.

## Generation requirements

The EFF list has exactly `6^5 = 7,776` entries, so five fair six-sided dice select one word without modulo bias. Eight words require forty dice outcomes.

A software generator must use a cryptographically secure random source and unbiased selection. A simple safe method is rejection sampling over random integers; `random_value % 7776` is unacceptable unless the sampled range is an exact multiple of 7,776.

Generation needs its own deterministic tests, statistical smoke tests, fault handling, and platform-specific CSPRNG review before it becomes a product feature. rev0002 validates and derives a phrase but does not generate real owner credentials.

## Collision perspective

Two independently uniform v1 phrases can collide, but the probability is negligible at plausible populations. The more important repeated-root risk is people copying or choosing the same phrase, which is why the supported creation path must generate rather than solicit prose.

## Argon2id role

RecallRoot-v1 freezes RFC 9106's 64 MiB, three-pass, four-lane Argon2id profile with a 256-bit output. Argon2id raises the memory and compute cost of every candidate and makes large parallel guessing infrastructure expensive.

Argon2id cannot compensate for a low-entropy phrase. It also does not protect a phrase already captured by a camera, keylogger, compromised controller, or malicious generator.

## Product statement

The honest user-facing contract is:

> This phrase is the permanent master key you can carry on paper or in memory. IoTox cannot reset it. Anyone who learns it can attempt to become you. Use only the generated words, keep the card physically protected, and migrate ownership immediately if exposure is suspected.
