# Client malware paranoia: verification patterns

**Track:** A (Deployable core)


Assume the voting device can lie about what it encrypts and signs.

## Pattern A: cast-or-spoil challenges (statistical detection)
Voter can “spoil” a ballot:
- device reveals randomness so anyone can verify encryption correctness,
- spoiled ballots are never tallied.

Pros: can detect systematic cheating statistically.  
Cons: not a complete prevention; UX complexity.

## Pattern B: second-device verification
Vote on device A; verify receipt/inclusion on device B.
Pros: defeats single-device compromise if B is clean.  
Cons: many voters won’t do it; still vulnerable to two-device compromise.

## Pattern C: return codes / code sheets (strong but heavy)
Pre-distributed code sheet maps selections to codes.
After casting, system returns codes to check.
Pros: can detect malware altering selections.  
Cons: logistics, privacy pitfalls, operational burden.

## Pattern D: supervised hardened kiosks
Locked-down, ephemeral-boot kiosks in supervised spaces.
Pros: reduces malware + coercion vs home voting.  
Cons: requires physical infra and accessibility planning.

## Pattern E: dedicated “ballot hardware confirmer”
A hardware token with trusted display confirms ballot encoding before signing.
Pros: strong against host malware if the display is trustworthy.  
Cons: specialized hardware; ballot-style confusion risks.

## Non-negotiable for remote return
If remote return is permitted, the system SHOULD offer:
- revoting with clear “last vote counts” semantics, and/or
- supervised override vote that cancels remote ballots.