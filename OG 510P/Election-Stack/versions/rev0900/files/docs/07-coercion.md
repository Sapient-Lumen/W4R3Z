# Coercion, vote selling, and revoting

**Track:** B (Remote return / hard-mode research)



> **Deployment honesty:** Track B documents are **exploratory** and are **not deployment guidance**.
> Before reading, review [`docs/167` non-claims](167-non-claims-and-boundaries.md) (especially **N-2**) and the [`Track B → Track A promotion protocol`](229-experiment-to-spec-promotion-protocol.md).

## Why this matters
Any mechanism that lets people vote outside a private polling booth creates opportunities for:
- coercion (family/employer/organized),
- vote buying (proof-of-vote),
- forced abstention.
## Coercion as lived experience (do not sanitize this into a threat-model checkbox)

See also: `docs/track-a/PERSONS_PATH.md` (person-centered posture). This section is the coercion-specific complement.


Many coercive environments are not “protocol attacks.” They are **social surveillance**:

- a partner controls the phone,
- an employer “suggests” and monitors,
- a community power broker makes defiance costly.

In these settings, the coerced person experiences voting as a **performance of compliance under surveillance**.
Crypto mitigations can create *windows* of freedom (revoting, supervised override), but they only help if the voter:
(a) knows the window exists, (b) believes using it is safe, and (c) can physically access a supervised environment.

**Deployment honesty rule:** if you deploy any remote voting surface, you must front‑load:
- `docs/167` N‑2 (coercion non‑claim),
- the availability and accessibility of an in‑person supervised override,
- what evidence the system can and cannot provide about coercion.

Remote voting systems often fail here even when the crypto is correct.

## Coerced person’s path (named experiences; keep the honesty)

A remote-voting “coercion mitigation” that only exists in protocol prose can still be useless to the person living inside coercion.
Name the experience so deployments can’t hide behind crypto:

- **Over-the-shoulder voting:** “I must vote while someone watches.”
- **Proof demand:** “I’m asked to show a screenshot / code / receipt.”
- **Forced abstention:** “I’m told not to vote (or to stop after a first vote).”
- **Time-window control:** “I’m forced to vote at a time chosen by someone else.”
- **Access denial:** “The ‘supervised override’ exists, but I can’t safely reach it.”
- **Verification risk:** “Trying to verify increases my personal risk.”
- **Retaliation threat:** “If I refuse, I will be punished (socially, economically, physically).”

This list is not exhaustive. It is a guardrail against sanitizing coercion into a checkbox.


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
