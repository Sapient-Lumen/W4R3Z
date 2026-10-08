# Coercion, vote selling, and revoting

**Track:** B (Remote return / hard-mode research)


## Why this matters
Any mechanism that lets people vote outside a private polling booth creates opportunities for:
- coercion (family/employer/organized),
- vote buying (proof-of-vote),
- forced abstention.

Remote voting systems often fail here even when the crypto is correct.

---

## Receipt design rule (MUST)
Receipts MUST NOT prove vote content.  
They MAY prove *participation* (inclusion), but not choices.

---

## Revoting paradigm (best practical lever)
Revoting can reduce coercion if (and only if) the voter can re-vote later in private and the coercer cannot reliably monitor them for the full voting window.

**VoteAgain** is a well-known scalable coercion-resistant design that uses revoting to resist coercion under explicit assumptions about coercer absence at some point.  
Reference: xref: voteagain_revoting_usenix_2020_pdf

### Operational policy (if you implement revoting)
- Define deterministic “counted ballot” rule based on canonical log order (e.g., highest log index for that credential/token).
- Publish public evidence that only the counted ballot for each credential/token influenced the tally.
- Make it cheap and obvious for voters to re-vote.

---

## Fake credentials / JCJ-style families (research-heavy)
Classical coercion-resistant schemes (e.g., Juels–Catalano–Jakobsson (JCJ) and descendants) use fake credentials so voters can “comply” while still later voting privately.
- Pros: stronger coercion resistance in theory
- Cons: complex, implementation risk, and often heavy tally cost or deployment assumptions

---

## Pragmatic combined mitigation (recommended)
If you insist on remote return, combine:
1. Revoting (log-ordered last-vote counts),
2. Supervised override vote (in-person cancels remote),
3. Strong credential recovery + rapid revocation,
4. Explicit “non-claim” language about residual coercion risks.

---

## Known pitfalls
- Revoting can be broken by subtle ordering, race, or UI issues (“last vote counts” must be provably enforced).
- Any “verification code” mechanism can itself enable coercion if it becomes a proof-of-vote artifact.
- Monitoring/telemetry to detect coercion can become voter surveillance; avoid.
