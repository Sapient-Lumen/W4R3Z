# Privacy-proof implementation profiles and cryptographic agility

## Function

The archive requires rights-grade telemetry to prove preservation, access, continuity, and non-spoliation without becoming total surveillance. rev0167 created proof bindings. rev0168 adds implementation profiles.

A privacy-proof profile says exactly what kind of evidence a filer can prove, what remains hidden, who can verify it, and when the profile must be replaced because the cryptographic or procedural method is no longer adequate.

## Profile classes

| Class | Description | Use |
|---|---|---|
| PP0 public record only | ordinary public filing, no sealed or private proof | low-risk public summaries |
| PP1 committed log | hash commitment or transparency statement proves existence/order | preservation and chain-of-custody facts |
| PP2 selective disclosure | verifier sees only necessary fields or redacted proofs | routine audit and clinic review |
| PP3 sealed private proof | tribunal / special advocate verifies more under seal | sensitive safety, privacy, or privilege material |
| PP4 advanced privacy-enhancing proof | zero-knowledge, MPC, PSI, FHE, threshold proof, or equivalent | high-risk cases where facts must be proven without revealing underlying material |

No profile class is inherently superior. A PP4 proof that hides too much from the subject can be worse than a PP2 disclosure with a better contradiction route. The test is rights-grade sufficiency, not technical glamour.

## Minimum fields

A profile must state:

- proof claim: what fact is being proven;
- method: commitment, transparency statement, selective disclosure, sealed review, ZKP, MPC, PSI, FHE, threshold seal, or hybrid;
- revelation set: exactly what is revealed to public, subject, representative, special advocate, verifier, and authority;
- non-revelation set: exactly what is not revealed;
- privilege screen: attorney, ombud, clinical, safety, third-party, or subject-private material;
- failure mode: what happens if proof cannot be generated or verified;
- cryptographic agility: replacement trigger, algorithm sunset, independent review cycle;
- fallback evidence: what plain evidence or sealed annex substitutes if advanced proof fails;
- subject contest route.

## Cryptographic agility

The archive must not lock rights to one vendor, protocol, chain, wallet, or proof system. NIST privacy-enhancing cryptography materials identify techniques such as zero-knowledge proof, secure multiparty computation, fully homomorphic encryption, and private-set intersection as tools for privacy goals, not as magic legitimacy devices [REF-0673] [REF-0679]. W3C verifiable-credential data-integrity work and OpenID Federation patterns can support proof wrapping and trust chains, but the archive uses them only as analogies and optional implementation routes [REF-0669] [REF-0674].

A valid profile therefore needs **crypto-agility text**. It should say:

- which algorithms or libraries are currently accepted;
- who reviews them;
- what breaks reliance immediately;
- what causes deprecation after notice;
- how old proofs remain verifiable or are reissued;
- how subjects and representatives receive enough information to contest proof meaning.

## Privacy failure modes

| Failure | Consequence |
|---|---|
| overcollection | telemetry profile downgraded; surveillance fields excluded; possible incident report |
| undercollection | proof cannot support reliance; preservation defect may trigger adverse inference |
| privilege leak | sealed remediation, notice, privilege repair, discipline, and possible invalidation |
| unverifiable advanced proof | fallback to sealed/plain evidence or stay reliance |
| inaccessible proof | subject/representative challenge; reduced evidence weight |
| algorithm or trust-anchor compromise | emergency revalidation and possible preservation hold |

## Proof is not consent

A proof that a log exists does not prove the intervention was lawful. A proof that no deletion occurred does not prove the subject was treated humanely. A proof that a representative accessed a file does not prove meaningful representation. Privacy-proof profiles preserve evidence and limit exposure; they do not replace appeal, welfare review, or remedy.

## Schema hook

`schemas/privacy-proof-profile.schema.json` records profile class, proof method, revelation and non-revelation sets, verification route, retention, privilege screen, cryptographic agility, fallback evidence, and public summary. The sample profile uses commitment plus selective disclosure, not because that is final, but because the archive should accept ordinary, reviewable methods before demanding advanced cryptography everywhere.
