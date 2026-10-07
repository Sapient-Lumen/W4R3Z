# Redaction Risk Scan — current

rev0030 adds an automated redaction-risk scanner and applies it to the whole working cube.

Remediated public-contact digit occurrences: 21 across 14 files.
Open configured scanner findings after remediation: 0.

Rule posture: exact public contact digits are not load-bearing in this cube unless a file is explicitly marked as a live referral artifact. The cube is not a live referral artifact.

| event_id | file | redacted finding | occurrences | action |
|---|---|---:|---:|---|
| redact_rev0030_001 | `Candidate-Ledger-current.csv` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_002 | `Candidate-Ledger-current.csv` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_003 | `Candidate-Ledger-current.json` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_004 | `Candidate-Ledger-current.json` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_005 | `Candidate-Ledger-rev0020.csv` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_006 | `Candidate-Ledger-rev0020.json` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_007 | `Claim-Ledger-current.csv` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_008 | `Claim-Ledger-current.json` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_009 | `CANDIDATES/Faataua-Le-Ola-Samoa-Lifeline.txt` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_010 | `CANDIDATES/Faataua-Le-Ola-Samoa-Lifeline.txt` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_011 | `CANDIDATES/Faataua-Le-Ola-Samoa-Lifeline.txt` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_012 | `CANDIDATES/Good-Nanum-Park-Jin-ok-Korea-disconnected-dead.txt` | `public contact digit string [digits redacted]` | 2 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_013 | `CANDIDATES/Samoa-Victim-Support-Group-Campus-of-Hope.txt` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_014 | `CANDIDATES/Solomon-Islands-FSC-CCC-SAFENET-survivor-referral-shelter.txt` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_015 | `CANDIDATES/Women-and-Children-Crisis-Centre-Tonga.txt` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_016 | `OFFICE-CARDS/PACIFIC-ISLAND-CRISIS-LINE-AND-POST-DISASTER-MHPSS.txt` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_017 | `OFFICE-CARDS/PACIFIC-ISLAND-CRISIS-LINE-AND-POST-DISASTER-MHPSS.txt` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_018 | `OFFICE-CARDS/PACIFIC-ISLAND-CRISIS-LINE-AND-POST-DISASTER-MHPSS.txt` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_019 | `PUBLIC/Candidate-Index-public.csv` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |
| redact_rev0030_020 | `PUBLIC/Candidate-Index-public.json` | `public contact digit string [digits redacted]` | 1 | replaced_digits_with_non_referral_placeholder |

Scanner limits:
- This scanner catches obvious contact digits, email-like strings, exact coordinate pairs, address-like strings, and grave/case/ME-number-like identifiers.
- It does not prove that narrative case details, non-load-bearing names, or contextual privacy hazards are absent.
- Public export still requires the manual gate in `META/Public-Export-Checklist-current.md`.
