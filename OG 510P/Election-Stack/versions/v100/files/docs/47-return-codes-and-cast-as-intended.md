# Return codes & cast-as-intended verification (Norway-style patterns)

**Track:** B (Remote return / hard-mode research)


Return-code systems try to defend against client malware by giving the voter an **out-of-band check**
that the encrypted vote corresponds to their intended selection.

Norway’s internet voting pilots are a major reference point; this doc extracts design patterns without
assuming they “solve” coercion or malware in general.

## Core idea

- Before the election, the voter receives a **code sheet** (typically via postal mail).
- After casting, the system returns a short code per selected choice.
- The voter checks that the returned codes match the codes on their sheet.

If malware changes the vote, it is unlikely to produce the correct codes.

## Why it helps

- It reduces reliance on trusting the voting device.
- It can be checked quickly by humans.
- It is compatible with encrypted ballots + public bulletin boards.

## Why it’s hard

- Logistics: printing, distribution, replacement, lost mail, accessibility.
- Privacy: code-sheet handling can leak participation; coercers can demand to see sheets.
- Operational integrity: the code generation and mapping become a high-value secret.

## Design requirements (if you use return codes)

- Code-sheet generation must be in a **separate trust domain** with strong ceremony and audits.
- Codes must be **per-election, per-voter, spend-limited**, and protected against replay.
- Make “showing codes to a coercer” non-fatal by supporting **revoting and supervised override**.

## Evidence & observation

Independent observation reports on Norway’s pilots (e.g., Carter Center) and academic analyses of
cast-as-intended verification in Norway are valuable for governance and UX tradeoffs.

## Primary references
See `references.md` for Norway pilot observation reports and cast-as-intended verification analyses.