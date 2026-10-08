# Jurisdictional admissibility matrix (bundle usability planning) — Template

**Track:** A (Deployable core)


Goal: close the gap between **“evidence exists”** and **“evidence is usable”**.
This is *not* legal advice. It is a planning worksheet for counsel + election ops to identify what a court or administrative forum will require.

Keep it bounded. Prefer **one page per jurisdiction**.

## Jurisdiction
- State / country:
- Court(s) / forum(s):
- Typical proceeding types:
  - certification challenge / election contest
  - recount / audit dispute
  - administrative hearing
  - criminal investigation (if applicable)
- Relevant evidence rules / statutes (citations):

## Authentication plan (what the judge will accept)
- Custodian declaration source (who signs):
- Signature keys used (who controls them):
- Publication method (how the packet digest reached the public record):
- If printed exhibits are required: how do printed exhibits map to packet digests?

## Chain-of-custody expectations (bytes)
- Who packages the bundle:
- How the bundle is stored (hash-anchored storage, WORM, escrow, etc.):
- How the bundle is transferred to filing counsel / court:
- Who can testify to each step:

## Tool provenance expectations (verifier)

- **Crypto explanation expected by venue:** (none / short primer / expert testimony)
- **Hash/verification acceptance:** does the forum accept computer-verified digests directly, or require expert foundation?

- Acceptable verifier provenance in this forum:
  - reproducible build evidence required? (yes/no)
  - independent implementations required? (yes/no)
  - expert testimony required? (yes/no)
- Proposed expert witness pool / lab:

## Exhibit mapping (what humans will see)
| Exhibit | Source object (kind + digest) | Human-readable form | Redaction/transformation log? |
|---|---|---|---|
| 1 |  |  |  |

## Risk notes
- Common objections (hearsay/authentication/“black box crypto”/foundation):
- Mitigations (alternate witnesses, simplified explanations, extra receipts):

## Completion
- Prepared by (counsel):
- Reviewed by (election ops):
- Date:
- Next refresh date (if election law changes):
